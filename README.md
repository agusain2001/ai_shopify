# Shopify AI Analytics Assistant

A powerful AI-powered analytics assistant for Shopify stores. It allows merchants to ask questions in plain English (e.g., "What are my top selling products?") and get instant, data-driven insights.

## 🚀 Features

### **1. AI-Powered Chat Interface**
- **Natural Language Understanding**: Uses Gemini 1.5 Flash to understand user intent.
- **Interactive Chat UI**: A modern, responsive web interface for easy interaction.
- **Quick Actions**: One-click buttons for common questions (sales, inventory, orders).

### **2. Advanced Analytics Agent**
- **Smart Planning**: The agent plans its approach before executing.
- **Intent Classification**: Automatically detects if you asked about sales, inventory, products, etc.
- **Standard GraphQL API**: Works with **ALL** Shopify stores (not just Plus).
- **Intelligent Analysis**: The AI analyzes raw data to provide actionable business insights.

### **3. Performance & Reliability**
- **Caching**: 5-minute in-memory cache for fast responses.
- **Retry Logic**: Automatically handles API hiccups.
- **Metrics Dashboard**: Real-time monitoring of response times, success rates, and errors.

### **4. Security & Architecture**
- **Rails Gateway**: Secure API handling authentication and request logging.
- **Python AI Service**: Dedicated microservice for AI processing.
- **SQLite Database**: Lightweight, zero-config database.
- **Environment Variables**: Sensitive credentials managed via `.env`.

---

## 🛠️ Installation & Setup

### **1. Prerequisites**
- Ruby 3.2+
- Python 3.9+
- A Shopify Store (Partner account recommended)
- A Google Gemini API Key (Free tier works)

### **2. Setup Rails Gateway (Backend)**
```powershell
cd rails_gateway
gem install rails bundler
bundle install
rails db:migrate
```

### **3. Setup Python Agent (AI Service)**
```powershell
cd python_ai_agent
pip install -r requirements.txt
```

### **4. Configure Environment**
Update `.env` files in both directories with your credentials:
- `rails_gateway/.env`: API keys, Ports
- `python_ai_agent/.env`: Gemini Key, Shopify Token

---

## ▶️ Running the Application

You need to run **two terminal windows**:

**Terminal 1: Rails Server**
```powershell
cd rails_gateway
rails server
```

**Terminal 2: Python Agent**
```powershell
cd python_ai_agent
python main.py
```

---

## 💻 Usage

### **1. Chat Interface** 
Open your browser to:
👉 **[http://localhost:3000/index.html](http://localhost:3000/index.html)**

### **2. Metrics Dashboard**
Monitor system performance at:
👉 **[http://localhost:3000/dashboard.html](http://localhost:3000/dashboard.html)**

### **3. API Usage (Curl)**

**Top Selling Products:**
```bash
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{"store_id": "your-store.myshopify.com", "question": "What are my top products?"}'
```

**Inventory Check:**
```bash
curl -X POST http://localhost:3000/api/v1/questions \
  -H "Content-Type: application/json" \
  -d '{"store_id": "your-store.myshopify.com", "question": "Which items are low in stock?"}'
```

---

## 🏗️ Architecture

```
┌──────────────┐      ┌───────────────┐      ┌──────────────┐
│  Browser UI  │  ->  │ Rails Gateway │  ->  │ Python Agent │
└──────┬───────┘      └───────┬───────┘      └──────┬───────┘
       │                      │                     │
       ▼                      ▼                     ▼
┌──────────────┐      ┌───────────────┐      ┌──────────────┐
│  Dashboard   │      │   SQLite DB   │      │  Shopify API │
└──────────────┘      └───────────────┘      └──────────────┘
```

## 📝 License
MIT License. Free to use and modify.
