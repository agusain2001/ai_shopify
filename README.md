# AI-Powered Shopify Analytics App

An AI-driven analytics system that lets Shopify merchants ask natural language questions about their store and receive accurate, data-backed answers. The platform connects Shopify Analytics with a Generative AI agent through a clean, secure microservices architecture.

---

## 🚀 Overview

This application is a dual-service system designed to bridge Shopify data with Generative AI.

Merchants can ask questions like:

* "What are my top selling products this month?"
* "How many orders did I receive last week?"
* "Which product category generated the most revenue?"

The system converts natural language into ShopifyQL queries, executes them against Shopify’s Analytics API, and returns human-readable insights.

**Key idea:** Rails handles security and orchestration. Python handles intelligence.

---

## 🏗 Architecture

The system follows a Docker-based microservices architecture.

### 1. Rails Gateway (API & Orchestrator)

**Role**

* Secure entry point for clients
* Handles request validation and routing
* Manages Shopify OAuth authentication
* Shields the client from AI and data complexity

**Tech Stack**

* Ruby 3.x
* Rails 7 (API mode)

---

### 2. Python AI Agent (Intelligence Layer)

**Role**

* Interprets natural language questions
* Converts questions into ShopifyQL
* Executes queries via Shopify GraphQL Analytics API
* Uses Google Gemini to interpret and summarize results

**Tech Stack**

* Python 3.9+
* FastAPI
* Google Generative AI (Gemini 1.5 Flash)

---

## ⚙️ Setup Instructions

### Prerequisites

* Docker
* Docker Compose
* Shopify Partner Account (for API credentials)
* Google Gemini API Key

---

### 1. Configure Environment Variables

Set environment variables for the Python AI service.

You can either:

* Create a `.env` file at `python_ai_agent/.env`, or
* Define variables directly in `docker-compose.yml`

**Required Variables**

```env
GEMINI_API_KEY=your_gemini_api_key
SHOPIFY_STORE_URL=test-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=your_shopify_admin_api_token
```

---

### 2. Run the Application

Start both services using Docker Compose:

```bash
docker-compose up --build
```

Once running:

* Rails Gateway: [http://localhost:3000](http://localhost:3000)
* Python AI Agent: [http://localhost:8000](http://localhost:8000)

---

## 🔌 API Usage

### Ask Question Endpoint

The primary endpoint used by clients to query store analytics.

**Endpoint**

```http
POST /api/v1/questions
```

**URL**

```http
http://localhost:3000/api/v1/questions
```

**Headers**

```http
Content-Type: application/json
```

**Request Body**

```json
{
  "store_id": "test-store.myshopify.com",
  "question": "How many orders did I receive last week?"
}
```

**Success Response (200 OK)**

```json
{
  "answer": "You received 145 orders last week, which is a 10% increase from the previous week.",
  "query_used": "SHOW count() FROM orders SINCE -1w UNTIL today",
  "confidence": "high"
}
```

---

## 🔐 Shopify Authentication (OAuth)

The Rails Gateway manages Shopify OAuth for secure access to store data.

**Install App**

```http
GET /api/v1/auth/shopify/install?shop=example.myshopify.com
```

**OAuth Callback**

```http
GET /api/v1/auth/shopify/callback
```

These endpoints handle token exchange and store authorization automatically.

---

## 📁 Project Structure

```text
shopify_ai_project/
├── rails_gateway/        # Ruby on Rails API Gateway
├── python_ai_agent/      # Python FastAPI AI Service
├── docker-compose.yml    # Docker orchestration
└── README.md             # Project documentation
```

---

## 🧠 How It Works (High-Level Flow)

1. Client sends a natural language question to Rails
2. Rails validates the request and forwards it to the Python agent
3. Python agent converts the question into ShopifyQL
4. Shopify Analytics API executes the query
5. Gemini interprets the result and generates a clear answer
6. Rails returns the final response to the client

---

## 🚧 Limitations & Notes

* Requires Shopify stores with Analytics API access
* Data accuracy depends on ShopifyQL support and store permissions
* Designed for analytical queries, not transactional operations

---

## 📌 Future Enhancements

* Multi-store support per merchant
* Query history and caching
* Dashboard UI for non-technical users
* Support for additional LLM providers

---

## 📄 License

This project is provided for educational and internal use. Review Shopify and Google Gemini API terms before deploying to production.
