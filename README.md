# Shopify AI Analytics Project

## Overview
This project consists of two main services:
1. **Rails Gateway**: A Ruby on Rails API acting as the gateway and handling Shopify OAuth.
2. **Python AI Agent**: A Python FastAPI service powered by Gemini to analyze data and execute ShopifyQL queries.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User/Client   │────▶│  Rails Gateway  │────▶│  Python Agent   │
│                 │     │   (Port 3000)   │     │   (Port 8000)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                        │
                               ▼                        ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │  SQLite DB      │     │  Shopify API    │
                        │  (shops, logs)  │     │  (ShopifyQL)    │
                        └─────────────────┘     └─────────────────┘
```

## Features

### Core Features
- ✅ OAuth-based Shopify authentication with HMAC verification
- ✅ Natural language question processing
- ✅ LLM-powered ShopifyQL generation (Gemini)
- ✅ Business-friendly response formatting

### Agentic Workflow
- ✅ Intent understanding and planning
- ✅ Schema-aware query generation
- ✅ Query validation layer
- ✅ Retry logic with error context
- ✅ Conversation memory for follow-ups

### Bonus Features
- ✅ Caching with TTL (5 minutes)
- ✅ Request logging to database
- ✅ Metrics tracking (success rates, response times, cache hits)
- ✅ Metrics dashboard at `/dashboard.html`
- ✅ Secure token storage in database

## Setup

### Prerequisites
- Docker & Docker Compose (recommended)
- OR Ruby 3.2+ and Python 3.9+

### Environment Variables

Create a `.env` file in the root:

```env
# Shopify OAuth
SHOPIFY_API_KEY=your_api_key
SHOPIFY_API_SECRET=your_api_secret
SHOPIFY_REDIRECT_URI=http://localhost:3000/api/v1/auth/shopify/callback

# Shopify Store (for queries)
SHOPIFY_STORE_URL=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=your_access_token

# AI Service
GEMINI_API_KEY=your_gemini_api_key

# Rails
SECRET_KEY_BASE=generate_with_rails_secret
```

### Running with Docker

```bash
docker-compose up --build
```

### Running Locally

**Rails Gateway:**
```bash
cd rails_gateway
bundle install
rails db:migrate
rails server
```

**Python Agent:**
```bash
cd python_ai_agent
pip install -r requirements.txt
python main.py
```

## API Endpoints

### Rails Gateway (Port 3000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/questions` | Submit a natural language question |
| GET | `/api/v1/auth/shopify/install?shop=xxx` | Start OAuth flow |
| GET | `/api/v1/auth/shopify/callback` | OAuth callback |
| GET | `/up` | Health check |

### Python Agent (Port 8000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze` | Analyze question (internal) |
| GET | `/metrics` | Get service metrics |
| GET | `/health` | Health check |

## Example Request

```bash
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{
    "store_id": "my-store.myshopify.com",
    "question": "What were my top 5 selling products last week?"
  }'
```

## Metrics Dashboard

Access the metrics dashboard at: `http://localhost:3000/dashboard.html`

Features:
- Total requests and success rates
- Cache hit rates
- Response time percentiles (P50, P95, P99)
- Breakdown by store, intent, and error type
- Auto-refresh every 30 seconds
