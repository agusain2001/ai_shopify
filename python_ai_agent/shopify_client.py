import requests
import json
import logging

logger = logging.getLogger(__name__)

class ShopifyClient:
    def __init__(self, store_domain, access_token):
        self.store_domain = store_domain
        self.access_token = access_token
        # Use latest stable API version
        self.graphql_url = f"https://{store_domain}/admin/api/2024-10/graphql.json"
        self.headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": access_token
        }

    def execute_graphql(self, query: str, variables: dict = None):
        """Execute a GraphQL query against Shopify Admin API"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        try:
            response = requests.post(self.graphql_url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Shopify API Error: {str(e)}")
            return {"error": str(e)}

    def get_orders(self, first: int = 50, days_back: int = 30):
        """Fetch recent orders"""
        query = """
        query GetOrders($first: Int!) {
          orders(first: $first, sortKey: CREATED_AT, reverse: true) {
            edges {
              node {
                id
                name
                createdAt
                totalPriceSet {
                  shopMoney {
                    amount
                    currencyCode
                  }
                }
                lineItems(first: 10) {
                  edges {
                    node {
                      title
                      quantity
                      variant {
                        price
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """
        return self.execute_graphql(query, {"first": first})

    def get_products(self, first: int = 50):
        """Fetch products with inventory"""
        query = """
        query GetProducts($first: Int!) {
          products(first: $first) {
            edges {
              node {
                id
                title
                status
                totalInventory
                variants(first: 5) {
                  edges {
                    node {
                      id
                      title
                      price
                      inventoryQuantity
                    }
                  }
                }
              }
            }
          }
        }
        """
        return self.execute_graphql(query, {"first": first})

    def get_inventory_levels(self, first: int = 50):
        """Fetch inventory levels"""
        query = """
        query GetInventory($first: Int!) {
          inventoryItems(first: $first) {
            edges {
              node {
                id
                sku
                tracked
                inventoryLevels(first: 5) {
                  edges {
                    node {
                      available
                      location {
                        name
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """
        return self.execute_graphql(query, {"first": first})

    def execute_shopifyql(self, query: str):
        """
        Backward compatibility - now fetches data based on query intent
        Since ShopifyQL is not available, we use standard GraphQL instead
        """
        query_lower = query.lower()
        
        # Determine what data to fetch based on the query
        if "order" in query_lower or "sales" in query_lower or "revenue" in query_lower:
            return self.get_orders(first=100)
        elif "product" in query_lower or "inventory" in query_lower or "stock" in query_lower:
            return self.get_products(first=100)
        else:
            # Default to orders
            return self.get_orders(first=50)