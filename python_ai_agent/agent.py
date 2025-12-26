import os
import json
import logging
import hashlib
from datetime import datetime, timedelta
import google.generativeai as genai
from shopify_client import ShopifyClient
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini - using direct key for reliability
GEMINI_API_KEY = "AIzaSyDrNnwYdTnFO2JPSTG6DiMziqg17w-vbNE"
genai.configure(api_key=GEMINI_API_KEY)

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
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.store_id = store_id
        # Conversation memory for follow-up questions
        self.conversation_history = conversation_history or []

    def get_cache_key(self, question: str) -> str:
        """Generate cache key for question"""
        return hashlib.md5(f"{self.store_id}:{question}".encode()).hexdigest()

    def get_cached_result(self, question: str):
        """Check if result is cached"""
        cache_key = self.get_cache_key(question)
        if cache_key in query_cache:
            cached_data, timestamp = query_cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=CACHE_TTL):
                logger.info(f"Cache HIT for question: {question[:50]}...")
                return cached_data
            else:
                del query_cache[cache_key]
        return None

    def cache_result(self, question: str, result: dict):
        """Store result in cache"""
        cache_key = self.get_cache_key(question)
        query_cache[cache_key] = (result, datetime.now())
        logger.info(f"Cached result for question: {question[:50]}...")

    def classify_intent(self, question: str) -> str:
        """Classify the user's question intent"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['sell', 'sold', 'sales', 'revenue', 'top', 'best']):
            return 'sales_analysis'
        elif any(word in question_lower for word in ['inventory', 'stock', 'reorder', 'out of stock']):
            return 'inventory_check'
        elif any(word in question_lower for word in ['product', 'item']):
            return 'product_info'
        elif any(word in question_lower for word in ['order', 'recent']):
            return 'order_info'
        else:
            return 'general'

    def fetch_relevant_data(self, intent: str) -> dict:
        """Fetch data from Shopify based on intent"""
        logger.info(f"Fetching data for intent: {intent}")
        
        if intent in ['sales_analysis', 'order_info']:
            return self.client.get_orders(first=100)
        elif intent in ['inventory_check', 'product_info']:
            return self.client.get_products(first=100)
        else:
            # Fetch both for general questions
            orders = self.client.get_orders(first=50)
            products = self.client.get_products(first=50)
            return {"orders": orders, "products": products}

    def process_question(self, user_question: str):
        """
        Simplified Agentic Workflow using standard GraphQL:
        1. Check cache
        2. Classify intent
        3. Fetch relevant data from Shopify
        4. Use LLM to analyze and explain
        """
        
        # --- Check Cache ---
        cached_result = self.get_cached_result(user_question)
        if cached_result:
            return cached_result
        
        # --- Build conversation context ---
        context = ""
        if self.conversation_history:
            context = "\n".join([
                f"Previous Q: {item['question']}\nA: {item['answer'][:200]}..."
                for item in self.conversation_history[-3:]
            ])
        
        # --- Classify Intent ---
        intent = self.classify_intent(user_question)
        logger.info(f"Classified intent: {intent}")
        
        # --- Fetch Data from Shopify ---
        try:
            raw_data = self.fetch_relevant_data(intent)
            
            # Check for errors
            if "error" in raw_data:
                return {
                    "error": "Failed to fetch data from Shopify",
                    "details": raw_data.get("error", "Unknown error"),
                    "suggestion": "Please check your Shopify API credentials."
                }
            
            if "errors" in raw_data:
                return {
                    "error": "Shopify API returned errors",
                    "details": str(raw_data["errors"]),
                    "suggestion": "Please check your API permissions."
                }
                
        except Exception as e:
            logger.error(f"Shopify API error: {e}")
            return {
                "error": "Failed to connect to Shopify",
                "details": str(e),
                "suggestion": "Check your store URL and access token."
            }
        
        # --- Analyze with LLM ---
        result = self._analyze_and_respond(user_question, raw_data, intent, context)
        
        # Cache the result
        self.cache_result(user_question, result)
        
        return result
    
    def _analyze_and_respond(self, question: str, data: dict, intent: str, context: str) -> dict:
        """Use LLM to analyze data and generate response"""
        
        # Prepare a summary of the data (limit size for LLM)
        data_summary = json.dumps(data, indent=2)[:8000]  # Limit to 8k chars
        
        analysis_prompt = f"""
        You are a helpful Shopify business analyst assistant.
        
        User Question: "{question}"
        Intent: {intent}
        
        {f"Previous conversation:\\n{context}\\n" if context else ""}
        
        Here is the store data from Shopify:
        {data_summary}
        
        INSTRUCTIONS:
        1. Analyze the data to answer the user's question
        2. Provide specific numbers and insights
        3. For sales questions: identify top products by quantity or revenue
        4. For inventory questions: identify low stock items
        5. Be conversational and business-friendly
        6. If data is insufficient, say so and suggest what might help
        7. NEVER mention technical terms like JSON, GraphQL, API, edges, nodes, etc.
        8. Format large numbers nicely (e.g., $1,234.56)
        
        Provide a clear, actionable answer:
        """
        
        try:
            response = self.model.generate_content(analysis_prompt)
            answer = response.text
            
            # Determine confidence based on data quality
            confidence = "high"
            if not data or (isinstance(data, dict) and not data.get("data")):
                confidence = "low"
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            answer = "I was able to retrieve your store data, but had trouble analyzing it. Please try asking a more specific question."
            confidence = "low"
        
        # Store in conversation history
        self.conversation_history.append({
            "question": question,
            "answer": answer[:500]  # Store truncated version
        })
        
        return {
            "answer": answer,
            "intent": intent,
            "confidence": confidence,
            "cached": False
        }