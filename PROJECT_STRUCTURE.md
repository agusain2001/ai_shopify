shopify_ai_project/
│
├── 📄 README.md                  # Setup instructions, architecture overview, and usage guide
├── 📄 AGENTS.md                  # Detailed description of the Agentic Workflow and Prompt Engineering
├── 📄 docker-compose.yml         # Orchestrates both services (Rails + Python) for easy startup
├── 📄 PROJECT_STRUCTURE.md       # This file (Project map)
│
├── 📂 rails_gateway/             # [Service 1] Ruby on Rails API (The Gateway)
│   ├── 📄 Dockerfile             # Container definition for Rails
│   ├── 📄 Gemfile                # Ruby dependencies (HTTParty, Dotenv, etc.)
│   ├── 📄 Gemfile.lock
│   ├── 📂 config/
│   │   └── 📄 routes.rb          # Defines endpoints: POST /questions, OAuth callbacks
│   │
│   └── 📂 app/
│       ├── 📂 controllers/
│       │   └── 📂 api/
│       │       └── 📂 v1/
│       │           ├── 📄 questions_controller.rb  # Main endpoint: Validates input -> calls Python Service
│       │           └── 📄 auth_controller.rb       # Handles Shopify OAuth (Install & Callback)
│       │
│       └── 📂 services/
│           └── 📄 python_ai_service.rb             # Service class to communicate with the Python backend
│
└── 📂 python_ai_agent/           # [Service 2] Python FastAPI + Gemini (The Brain)
    ├── 📄 Dockerfile             # Container definition for Python
    ├── 📄 requirements.txt       # Python deps: fastapi, uvicorn, google-generativeai, requests
    ├── 📄 .env                   # Environment variables (API Keys, Store URL)
    │
    ├── 📄 main.py                # FastAPI Entry point: Defines POST /analyze
    ├── 📄 agent.py               # Core Logic: "Brain" of the operation (Intent -> Query -> Explain)
    └── 📄 shopify_client.py      # Execution Layer: "Hands" that run GraphQL/ShopifyQL queries 
