import os
import json
import logging
import google.generativeai as genai
from shopify_client import ShopifyClient
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

logger = logging.getLogger(__name__)

class AnalyticsAgent:
    def __init__(self, store_id: str): # <--- MISSING access_token argument
    # ...
    self.client = ShopifyClient(
        store_domain=store_id, 
        access_token=access_token # <--- Undefined variable error
    )
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def process_question(self, user_question: str):
        """
        Main Agentic Workflow:
        1. Intent -> Query (Gemini)
        2. Execute Query (Shopify API)
        3. Result -> Explanation (Gemini)
        """
        
        # --- Step 1: Generate ShopifyQL ---
        prompt_for_query = f"""
        You are a Shopify Analytics expert. Convert the user's natural language question into a valid ShopifyQL query.
        
        Schema Context:
        - "orders": id, net_sales, created_at, processed_at
        - "products": product_title, product_type, total_inventory
        - "sales": used for revenue and quantity metrics (common fields: total_sales, gross_sales, orders_count, quantity)
        
        Rules:
        1. OUTPUT ONLY the raw query string. Do not include markdown (```sql) or explanations.
        2. Format dates relative to today using 'SINCE' and 'UNTIL' (e.g., SINCE -1m UNTIL today).
        3. For "sales" or "how much", usually query the 'sales' table or 'orders' table.
        
        User Question: "{user_question}"
        """
        
        try:
            query_response = self.model.generate_content(prompt_for_query)
            # Clean up potential markdown formatting from LLM
            generated_query = query_response.text.strip().replace('`', '').replace('sql', '').replace('shopifyql', '').strip()
            logger.info(f"Generated Query: {generated_query}")
        except Exception as e:
            return {"error": "Failed to generate query from LLM", "details": str(e)}

        # --- Step 2: Execute Query ---
        raw_data = self.client.execute_shopifyql(generated_query)
        
        # Check for API errors
        data_node = raw_data.get("data", {}).get("shopifyqlQuery", {})
        if "message" in data_node:
             return {
                "answer": "I couldn't process that specific data request.",
                "technical_error": data_node["message"],
                "query_attempted": generated_query
            }
            
        if "errors" in raw_data:
             return {
                "answer": "I encountered an error connecting to Shopify.",
                "technical_error": raw_data["errors"],
                "query_attempted": generated_query
            }

        # --- Step 3: Explain Results ---
        prompt_for_explanation = f"""
        You are a helpful business assistant.
        User Question: "{user_question}"
        Data Retrieved (JSON): {json.dumps(raw_data)}
        
        Task:
        1. Answer the user's question clearly based on the data.
        2. If the data is empty (rows are empty), say so politely and suggest they try a different date range.
        3. Do not mention "JSON" or technical terms.
        """
        
        explanation_response = self.model.generate_content(prompt_for_explanation)
        
        return {
            "answer": explanation_response.text,
            "query_used": generated_query,
            # "raw_data": raw_data # Uncomment for debugging
        }
