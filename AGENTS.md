# 🤖 Agent Design & Workflow Architecture

This document describes the design, responsibilities, and internal workflow of the AI Agent used in the Shopify Analytics system. It is intended for developers and reviewers who want to understand how natural language questions are translated into reliable, data-grounded answers.

---

## 🎯 Purpose of the Agent

The AI Agent acts as an intelligent translation layer between non-technical user questions and Shopify's structured GraphQL API.

**Primary Goals:**

- ✅ Translate natural language into valid Shopify GraphQL queries
- ✅ Execute queries safely against real Shopify data
- ✅ Prevent hallucinations by grounding all answers in API responses
- ✅ Return clear, business-friendly insights

The agent follows a **ReAct-style pattern (Reason → Act → Observe → Respond)** to ensure transparency and reliability at every step.

---

## 🧠 Agentic Pipeline Overview

The agent runs a deterministic four-stage pipeline implemented in:

```
python_ai_agent/agent.py
```

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AGENTIC WORKFLOW                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐           │
│  │ 1. CLASSIFY  │ -> │ 2. FETCH     │ -> │ 3. ANALYZE   │           │
│  │    Intent    │    │    Data      │    │    with LLM  │           │
│  └──────────────┘    └──────────────┘    └──────────────┘           │
│         │                   │                   │                    │
│         ▼                   ▼                   ▼                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐           │
│  │ sales_analysis│   │ Shopify      │    │ Gemini 2.5   │           │
│  │ inventory    │    │ GraphQL API  │    │ Flash        │           │
│  │ product_info │    │              │    │              │           │
│  │ order_info   │    │              │    │              │           │
│  └──────────────┘    └──────────────┘    └──────────────┘           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1️⃣ Stage 1: Intent Classification

**Objective:** Understand what the user is asking and map it to the correct Shopify data source.

| User Keywords | Detected Intent | Data Fetched |
|---------------|-----------------|--------------|
| sell, sold, sales, revenue, top, best | `sales_analysis` | Orders |
| inventory, stock, reorder, out of stock | `inventory_check` | Products |
| product, item | `product_info` | Products |
| order, recent | `order_info` | Orders |
| Other | `general` | Orders + Products |

**Example:**

> User: "What are my top selling products?"

```python
Intent: sales_analysis
→ Fetch: Orders (last 100)
```

---

## 2️⃣ Stage 2: Data Fetching

**Objective:** Retrieve relevant data from Shopify using the Admin GraphQL API.

**Supported Queries:**

| Method | Purpose | API Used |
|--------|---------|----------|
| `get_orders()` | Fetch recent orders with line items | GraphQL |
| `get_products()` | Fetch products with inventory | GraphQL |
| `get_inventory_levels()` | Fetch detailed inventory | GraphQL |

**Example GraphQL Query:**

```graphql
query GetOrders($first: Int!) {
  orders(first: $first, sortKey: CREATED_AT, reverse: true) {
    edges {
      node {
        id
        name
        totalPriceSet {
          shopMoney { amount, currencyCode }
        }
        lineItems(first: 10) {
          edges {
            node { title, quantity }
          }
        }
      }
    }
  }
}
```

---

## 3️⃣ Stage 3: LLM Analysis

**Objective:** Use Gemini AI to analyze raw data and generate a human-friendly response.

**Model Used:** Google Gemini 2.5 Flash

**Prompt Engineering:**

```
You are a helpful Shopify business analyst assistant.

User Question: "{question}"
Intent: {intent}

Here is the store data from Shopify:
{data_summary}

INSTRUCTIONS:
1. Analyze the data to answer the user's question
2. Provide specific numbers and insights
3. For sales questions: identify top products by quantity or revenue
4. For inventory questions: identify low stock items
5. Be conversational and business-friendly
6. NEVER mention technical terms like JSON, GraphQL, API, etc.
7. Format large numbers nicely (e.g., $1,234.56)
```

---

## 4️⃣ Stage 4: Response Delivery

**Output Structure:**

```json
{
  "answer": "Your top selling product last week was...",
  "intent": "sales_analysis",
  "confidence": "high",
  "cached": false
}
```

---

## ⚡ Caching Strategy

To improve performance and reduce API calls:

| Feature | Implementation |
|---------|---------------|
| Cache Type | In-memory dictionary |
| TTL | 5 minutes |
| Key | MD5 hash of `store_id:question` |

```python
# Cache lookup
cache_key = hashlib.md5(f"{store_id}:{question}").hexdigest()
if cache_key in query_cache:
    return cached_result  # ⚡ Fast response
```

---

## 🛡️ Error Handling & Recovery

| Scenario | Agent Behavior |
|----------|---------------|
| Ambiguous Question | Uses `general` intent, fetches both orders and products |
| Shopify API Error | Returns structured error with suggestion |
| Invalid Token | Reports authentication failure |
| Empty Results | Explains no data found, suggests alternatives |
| Rate Limited | Automatic retry with exponential backoff |

**Error Response Example:**

```json
{
  "error": "Failed to fetch data from Shopify",
  "details": "402 Payment Required",
  "suggestion": "Please check your Shopify API credentials."
}
```

---

## 🔒 Security Principles

- ✅ **No hardcoded credentials** - All secrets in `.env` files
- ✅ **Token passed per-request** - Uses environment variables
- ✅ **No data persistence** - Raw Shopify data not stored
- ✅ **Gitignored secrets** - `.env` files excluded from version control
- ✅ **OAuth 2.0 flow** - Secure Shopify app authentication

---

## 📊 Metrics & Monitoring

The agent tracks:

| Metric | Description |
|--------|-------------|
| `total_requests` | Total API calls received |
| `successful_requests` | Requests that returned valid data |
| `failed_requests` | Requests that encountered errors |
| `avg_response_time` | Average processing time in ms |
| `cache_hit_rate` | Percentage of cached responses |

Available at: `GET /metrics`

---

## 🎨 Design Principles

1. **Deterministic over Creative** - Consistent, predictable responses
2. **Data-Backed Only** - Every answer traces to real API data
3. **Separation of Concerns** - Classification → Fetching → Analysis → Response
4. **Safe Defaults** - When uncertain, fetch more data rather than guess
5. **User-Friendly Output** - No technical jargon in responses

---

## 📝 Summary

The AI Agent is **not a chatbot** - it's a controlled analytical system designed to:

| Action | Description |
|--------|-------------|
| **Reason** | Classify user intent accurately |
| **Act** | Fetch only relevant Shopify data |
| **Observe** | Validate API responses for errors |
| **Respond** | Deliver clear, business-friendly insights |

Every answer can be traced back to a concrete GraphQL query and a real API response.

---

## 📚 References

- [Shopify Admin GraphQL API](https://shopify.dev/docs/api/admin-graphql)
- [Google Gemini API](https://ai.google.dev/docs)
- [ReAct Pattern Paper](https://arxiv.org/abs/2210.03629)
