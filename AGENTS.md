# Agent Design & Workflow Architecture

This document describes the design, responsibilities, and internal workflow of the AI Agent used in the Shopify Analytics system. It is intended for developers and reviewers who want to understand how natural language questions are translated into reliable, data-grounded answers.

---

## 🎯 Purpose of the Agent

The AI Agent acts as an intelligent translation layer between non-technical user questions and Shopify’s structured analytics interface.

Its primary goals are:

* Translate natural language into valid ShopifyQL
* Execute queries safely against real Shopify data
* Prevent hallucinations by grounding all answers in API responses
* Return clear, business-friendly insights

The agent follows a **ReAct-style pattern (Reason → Act → Observe → Respond)** to ensure transparency and reliability at every step.

---

## 🧠 Agentic Pipeline Overview

The agent runs a deterministic four-stage pipeline implemented in:

```text
python_ai_agent/agent.py
```

Each stage has a single responsibility and clear input/output boundaries.

---

## 1️⃣ Intent Classification & Schema Mapping

**Objective**

Understand what the user is asking and map it to the correct Shopify Analytics schema before generating any query.

**Inputs**

* User’s natural language question

**Outputs**

* Target metric (e.g., `total_inventory`, `net_sales`)
* Shopify table (e.g., `products`, `orders`, `sales`)
* Filters (product name, date range, etc.)

**Example**

User question:

> How much inventory do I have for the red t-shirt?

Agent interpretation:

* Metric: `total_inventory`
* Table: `products`
* Filter: `product_title CONTAINS "red t-shirt"`

This step prevents common errors such as querying `orders` when the question clearly relates to `products`.

---

## 2️⃣ Query Generation (Text → ShopifyQL)

**Objective**

Convert the structured intent into a syntactically correct ShopifyQL query.

**Model Used**

* Google Gemini 1.5 Flash

**Prompt Constraints**

* Output **only** the raw ShopifyQL query string
* No explanations
* No Markdown formatting

**Date Handling Rules**

To ensure future-safe queries:

* Only relative dates are allowed
* Hardcoded dates are explicitly forbidden

Examples:

* ✅ `SINCE -7d UNTIL today`
* ❌ `SINCE 2024-01-01`

**Sanitization**

After generation, the output is:

* Stripped of Markdown fences
* Trimmed to a single-line query

**Example**

User:

> What were my sales yesterday?

Generated ShopifyQL:

```text
SHOW total_sales FROM sales SINCE -1d UNTIL today
```

---

## 3️⃣ Execution & Validation (The "Hands")

**Objective**

Safely execute the generated query and validate the response.

**Execution Flow**

1. ShopifyQL string is wrapped inside a `shopifyqlQuery` GraphQL mutation
2. Request is sent to the Shopify GraphQL Admin API via `ShopifyClient`
3. Response is parsed and validated

**Guardrails**

* **Syntax Errors**

  * Invalid columns or tables are caught
  * Error context is preserved for recovery or explanation

* **Empty Results**

  * Queries returning zero rows are flagged
  * This context is passed to the final response stage

This step ensures the agent never fabricates results and always reacts to real API feedback.

---

## 4️⃣ Insight Synthesis (The "Voice")

**Objective**

Translate raw API data into clear, business-friendly insights.

**Inputs**

* Original user question
* Generated ShopifyQL query
* Raw JSON response from Shopify

**Persona**

* Business Analyst

**Rules**

* No technical jargon (no "JSON", "arrays", "null", etc.)
* Focus on insights, trends, and clarity
* Be concise and direct

**Example Output**

> You received 145 orders last week, which is a 10% increase compared to the previous week.

---

## 🛡 Failure Modes & Recovery Strategies

| Scenario           | Agent Behavior                                                        |
| ------------------ | --------------------------------------------------------------------- |
| Ambiguous Question | Defaults to a standard health-check query (sales over last 7 days)    |
| Shopify API Error  | Returns a structured error object to the Rails Gateway                |
| Invalid Token      | Stops execution and reports authentication failure                    |
| Zero Results       | Clearly explains no matching data was found and suggests alternatives |

The agent never fails silently and never guesses.

---

## 📝 Prompt Engineering Strategy

All prompts are defined inside:

```text
python_ai_agent/agent.py
```

**Key Techniques Used**

* Few-shot prompting with valid ShopifyQL examples
* Explicit schema reminders (e.g., `net_sales` → `orders`, `total_inventory` → `products`)
* Hard constraints to prevent:

  * Hallucinated columns
  * Invalid tables
  * Hardcoded dates

This approach significantly reduces query errors and improves consistency.

---

## 🔒 Design Principles

* Deterministic over creative
* Data-backed responses only
* Clear separation of reasoning, execution, and narration
* Safe defaults over ambiguous interpretations

---

## 📌 Summary

The AI Agent is not a chatbot. It is a controlled analytical system designed to:

* Reason carefully
* Act on real data
* Speak clearly to business users

Every answer can be traced back to a concrete ShopifyQL query and a real API response.
