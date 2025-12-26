import os
import json
import logging
import hashlib
from datetime import datetime, timedelta
import google.generativeai as genai
from shopify_client import ShopifyClient
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

logger = logging.getLogger(__name__)

# Simple in-memory cache (in production, use Redis)
query_cache = {}
CACHE_TTL = 300  # 5 minutes

class AnalyticsAgent:
    def __init__(self, store_id: str, conversation_history=None):
        self.client = ShopifyClient(
            store_domain=os.getenv("SHOPIFY_STORE_URL"),
            access_token=os.getenv("SHOPIFY_ACCESS_TOKEN")
        )
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.store_id = store_id
        # Conversation memory for follow-up questions
        self.conversation_history = conversation_history or []

    def validate_shopifyql(self, query: str) -> dict:
        """
        Pre-validation layer for ShopifyQL queries
        Returns: {"valid": bool, "errors": list}
        """
        errors = []
        query_upper = query.upper()
        
        # Check for required keywords
        if "SHOW" not in query_upper and "FROM" not in query_upper:
            errors.append("Query must contain SHOW and FROM clauses")
        
        # Check for valid tables
        valid_tables = ["ORDERS", "PRODUCTS", "SALES", "CUSTOMERS", "INVENTORY_LEVELS"]
        has_valid_table = any(table in query_upper for table in valid_tables)
        if not has_valid_table:
            errors.append(f"Query must reference a valid table: {', '.join(valid_tables)}")
        
        # Check for hardcoded dates (forbidden)
        import re
        if re.search(r'\d{4}-\d{2}-\d{2}', query):
            errors.append("Hardcoded dates not allowed. Use relative dates like SINCE -7d")
        
        # Check for dangerous operations (DELETE, DROP, etc.)
        dangerous_keywords = ["DELETE", "DROP", "UPDATE", "INSERT", "ALTER"]
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                errors.append(f"Dangerous operation '{keyword}' not allowed")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def get_cache_key(self, query: str) -> str:
        """Generate cache key for query"""
        return hashlib.md5(f"{self.store_id}:{query}".encode()).hexdigest()

    def get_cached_result(self, query: str):
        """Check if query result is cached"""
        cache_key = self.get_cache_key(query)
        if cache_key in query_cache:
            cached_data, timestamp = query_cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=CACHE_TTL):
                logger.info(f"Cache HIT for query: {query[:50]}...")
                return cached_data
            else:
                # Expired
                del query_cache[cache_key]
        return None

    def cache_result(self, query: str, result: dict):
        """Store query result in cache"""
        cache_key = self.get_cache_key(query)
        query_cache[cache_key] = (result, datetime.now())
        logger.info(f"Cached result for query: {query[:50]}...")

    def process_question(self, user_question: str, max_retries=2):
        """
        Enhanced Agentic Workflow with:
        - Conversation memory
        - Query validation
        - Caching
        - Retry logic
        - Explicit planning stage
        """
        
        # --- Stage 0: Planning (New!) ---
        # Build context from conversation history
        context = ""
        if self.conversation_history:
            context = "\n".join([
                f"Previous Q: {item['question']}\nA: {item['answer'][:100]}..."
                for item in self.conversation_history[-3:]  # Last 3 exchanges
            ])
        
        planning_prompt = f"""
        You are a Shopify Analytics strategist. Analyze this question and create a plan.
        
        {f"Previous conversation context:\n{context}\n" if context else ""}
        
        Current question: "{user_question}"
        
        Output a JSON plan with:
        {{
            "intent": "sales_analysis | inventory_check | customer_insights | product_performance",
            "target_metric": "specific metric name",
            "target_table": "orders | products | sales | customers",
            "time_range": "relative time period",
            "filters": ["list of filters needed"]
        }}
        
        Output ONLY the JSON, no explanation.
        """
        
        try:
            plan_response = self.model.generate_content(planning_prompt)
            plan_text = plan_response.text.strip().replace('```json', '').replace('```', '')
            plan = json.loads(plan_text)
            logger.info(f"Generated Plan: {json.dumps(plan, indent=2)}")
        except Exception as e:
            logger.warning(f"Planning stage failed: {e}. Proceeding with direct query generation.")
            plan = None
        
        # --- Stage 1: Generate ShopifyQL with Retry Logic ---
        attempt = 0
        last_error = None
        
        while attempt < max_retries:
            attempt += 1
            
            query_prompt = f"""
            You are a Shopify Analytics expert. Convert this question into valid ShopifyQL.
            
            {"PLAN: " + json.dumps(plan) if plan else ""}
            {f"Context:\n{context}\n" if context else ""}
            
            Schema:
            - orders: id, net_sales, created_at, processed_at, total_price
            - products: product_title, product_type, total_inventory, vendor
            - sales: total_sales, gross_sales, orders_count, quantity, net_sales
            - customers: customer_id, email, orders_count, total_spent
            
            RULES:
            1. Output ONLY the raw ShopifyQL query (no markdown, no explanation)
            2. Use relative dates: SINCE -7d, SINCE -1m, etc. (NEVER hardcoded dates)
            3. For revenue/sales → use 'sales' or 'orders' table
            4. For inventory → use 'products' table
            5. SHOW [metric] FROM [table] SINCE [time] UNTIL today
            
            {f"Previous attempt failed with: {last_error}. Try a different approach." if last_error else ""}
            
            Question: "{user_question}"
            """
            
            try:
                query_response = self.model.generate_content(query_prompt)
                generated_query = query_response.text.strip().replace('`', '').replace('sql', '').replace('shopifyql', '').strip()
                logger.info(f"Generated Query (Attempt {attempt}): {generated_query}")
                
                # --- Stage 1.5: Validate Query ---
                validation = self.validate_shopifyql(generated_query)
                if not validation["valid"]:
                    last_error = f"Validation errors: {', '.join(validation['errors'])}"
                    logger.warning(f"Query validation failed: {last_error}")
                    continue  # Retry with error context
                
                # --- Stage 2: Check Cache ---
                cached_result = self.get_cached_result(generated_query)
                if cached_result:
                    return self._format_response(
                        user_question, 
                        generated_query, 
                        cached_result, 
                        from_cache=True
                    )
                
                # --- Stage 3: Execute Query ---
                raw_data = self.client.execute_shopifyql(generated_query)
                
                # Check for API errors
                data_node = raw_data.get("data", {}).get("shopifyqlQuery", {})
                
                if "message" in data_node:
                    last_error = data_node["message"]
                    logger.warning(f"Shopify API error: {last_error}")
                    continue  # Retry
                    
                if "errors" in raw_data:
                    last_error = str(raw_data["errors"])
                    logger.error(f"GraphQL error: {last_error}")
                    continue  # Retry
                
                # Success! Cache the result
                self.cache_result(generated_query, raw_data)
                
                return self._format_response(
                    user_question, 
                    generated_query, 
                    raw_data,
                    from_cache=False
                )
                
            except Exception as e:
                last_error = str(e)
                logger.error(f"Attempt {attempt} failed: {last_error}")
        
        # All retries exhausted
        return {
            "error": "Failed to generate valid query after multiple attempts",
            "details": last_error,
            "suggestion": "Try rephrasing your question or being more specific about the time range."
        }
    
    def _format_response(self, question, query, raw_data, from_cache=False):
        """Stage 4: Insight Synthesis"""
        
        explanation_prompt = f"""
        You are a helpful business assistant.
        
        User Question: "{question}"
        Query Used: {query}
        Data Retrieved: {json.dumps(raw_data)}
        
        Task:
        1. Answer clearly based on the data
        2. If empty results, say so and suggest alternatives
        3. Provide actionable insights where possible
        4. Never mention technical terms (JSON, arrays, API, etc.)
        5. Be conversational and helpful
        """
        
        try:
            explanation_response = self.model.generate_content(explanation_prompt)
            answer = explanation_response.text
        except Exception as e:
            answer = "I found the data but had trouble explaining it. Please try again."
            logger.error(f"Explanation generation failed: {e}")
        
        # Store in conversation history
        self.conversation_history.append({
            "question": question,
            "answer": answer,
            "query": query
        })
        
        return {
            "answer": answer,
            "query_used": query,
            "confidence": "high" if not from_cache else "high (cached)",
            "cached": from_cache
        }