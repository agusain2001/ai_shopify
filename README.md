# 🤖 Shopify AI Analytics Assistant

A powerful AI-powered analytics assistant for Shopify stores. Ask questions in plain English like *"What are my top selling products?"* and get instant, data-driven insights powered by **Google Gemini AI**.

![License](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Ruby](https://img.shields.io/badge/Ruby-3.2+-red.svg)
![Shopify](https://img.shields.io/badge/Shopify-API-96bf48.svg)

---

## ✨ Features

### 🎯 AI-Powered Chat Interface
- **Natural Language Understanding**: Uses Google Gemini 2.5 Flash for intelligent query understanding
- **Interactive Chat UI**: Modern, responsive dark-themed interface
- **Quick Actions**: One-click buttons for common analytics questions

### 📊 Advanced Analytics Agent
- **Intent Classification**: Automatically detects sales, inventory, product, or order queries
- **Standard GraphQL API**: Works with **ALL** Shopify stores (not just Plus)
- **Intelligent Analysis**: AI analyzes raw data to provide actionable business insights
- **Conversation Memory**: Context-aware follow-up questions

### ⚡ Performance & Reliability
- **5-Minute Caching**: Fast responses with intelligent in-memory cache
- **Retry Logic**: Automatic handling of API rate limits and errors
- **Metrics Dashboard**: Real-time monitoring with response times and success rates

### 🔒 Security & Architecture
- **Rails Gateway**: Secure API proxy with request logging
- **Python AI Microservice**: Dedicated service for AI/ML processing
- **Environment Variables**: Secure credential management via `.env` files
- **OAuth 2.0**: Shopify's secure authentication flow

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Browser UI    │ ──▶ │  Rails Gateway   │ ──▶ │  Python Agent   │
│  (Chat/Dashboard)     │   (Port 3000)    │     │   (Port 8000)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │                        │
                               ▼                        ▼
                        ┌──────────────┐         ┌──────────────┐
                        │  SQLite DB   │         │ Shopify API  │
                        └──────────────┘         │ + Gemini AI  │
                                                 └──────────────┘
```

---

## 🛠️ Prerequisites

- **Ruby 3.2+** with Rails 8.x
- **Python 3.9+**
- **Shopify Partner Account** (for development store)
- **Google Gemini API Key** ([Get one free](https://makersuite.google.com/app/apikey))

---

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/agusain2001/ai_shopify.git
cd ai_shopify
```

### 2. Setup Rails Gateway
```bash
cd rails_gateway
gem install bundler
bundle install
rails db:migrate
```

### 3. Setup Python Agent
```bash
cd python_ai_agent
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create `.env` files with your credentials:

**`python_ai_agent/.env`**
```env
GOOGLE_API_KEY="your_gemini_api_key"
SHOPIFY_STORE_URL="your-store.myshopify.com"
SHOPIFY_ACCESS_TOKEN="shpat_xxxxxxxxxxxxx"
```

**`rails_gateway/.env`**
```env
PYTHON_AGENT_URL="http://localhost:8000"
```

---

## 🚀 Running the Application

Open **two terminal windows**:

### Terminal 1: Rails Server
```bash
cd rails_gateway
rails server
```

### Terminal 2: Python Agent
```bash
cd python_ai_agent
python main.py
```

---

## 💻 Usage

### Chat Interface
Open in your browser:
👉 **http://localhost:3000/index.html**

### Metrics Dashboard
Monitor performance:
👉 **http://localhost:3000/dashboard.html**

### API Usage (cURL)

**Get Top Products:**
```bash
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{"store_id": "your-store.myshopify.com", "question": "What are my top selling products?"}'
```

**Check Inventory:**
```bash
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{"store_id": "your-store.myshopify.com", "question": "Which products are low in stock?"}'
```

---

## 📁 Project Structure

```
ai_shopify/
├── rails_gateway/          # Ruby on Rails API Gateway
│   ├── app/
│   │   ├── controllers/    # API endpoints
│   │   └── models/         # Data models
│   ├── public/             # Static frontend (HTML/CSS/JS)
│   └── config/             # Rails configuration
│
├── python_ai_agent/        # Python AI Microservice
│   ├── agent.py            # Core AI agent logic
│   ├── shopify_client.py   # Shopify GraphQL client
│   ├── metrics.py          # Performance metrics
│   └── main.py             # FastAPI server
│
├── AGENTS.md               # Agent architecture documentation
└── README.md               # This file
```

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Aashish Gusain**
- GitHub: [@agusain2001](https://github.com/agusain2001)

---

## 🙏 Acknowledgments

- [Shopify Admin API](https://shopify.dev/docs/api/admin-graphql)
- [Google Gemini AI](https://ai.google.dev/)
- [Ruby on Rails](https://rubyonrails.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
