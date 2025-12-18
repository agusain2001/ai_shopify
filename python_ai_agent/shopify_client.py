import requests
import json
import logging

logger = logging.getLogger(__name__)

class ShopifyClient:
    def __init__(self, store_domain, access_token):
        self.store_domain = store_domain
        self.access_token = access_token
        # The GraphQL endpoint for ShopifyQL (Admin API)
        self.graphql_url = f"https://{store_domain}/admin/api/2024-01/graphql.json"

    def execute_shopifyql(self, query: str):
        """
        Executes a raw ShopifyQL query string against the Shopify GraphQL API.
        """
        # We must wrap the ShopifyQL string inside a GraphQL mutation/query
        graphql_payload = {
            "query": """
            query TableQuery($query: String!) {
              shopifyqlQuery(query: $query) {
                __typename
                ... on TableResponse {
                  tableData {
                    rowData
                    columns {
                      name
                      dataType
                    }
                  }
                }
                ... on ResponseError {
                  message
                }
              }
            }
            """,
            "variables": {
                "query": query
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.access_token
        }

        try:
            response = requests.post(self.graphql_url, json=graphql_payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Shopify API Connection Error: {str(e)}")
            return {"error": str(e), "details": "Failed to connect to Shopify"}