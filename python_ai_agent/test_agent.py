import requests
import json
import time

def test_agent():
    print("🧪 Testing Shopify AI Agent connection...")
    url = "http://localhost:8000/analyze"
    
    # payload matches the Rails API contract
    payload = {
        "store_id": "test-store.myshopify.com",  # Agent uses .env creds, this is just for logging
        "question": "What are my total sales for the last 30 days?"
    }
    
    print(f"📝 Sending Question: '{payload['question']}'")
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ SUCCESS! Received Response:")
            print("-" * 50)
            print(f"📦 Full Response: {json.dumps(data, indent=2)}")
            print("-" * 50)
        else:
            print(f"\n❌ Error {response.status_code}:")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to the agent at http://localhost:8000")
        print("Make sure the python service is running.")

if __name__ == "__main__":
    test_agent()
