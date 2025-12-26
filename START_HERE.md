# Quick Start Guide (No Docker/Rails Required)

Since you don't have Rails or Docker installed, we are running the **Python AI Agent** in standalone mode.

## 1. Status
✅ **Python AI Service**: Running on `http://localhost:8000`
❌ **Rails Gateway**: Skipped (Missing Ruby/Rails)
⚠️ **Gemini API**: Currently rate-limited (Free tier). If you see errors, wait 1-2 minutes.

## 2. Testing the Agent
We created a test script to simulate the Rails app sending questions to the AI.

**Run the test:**
```bash
cd python_ai_agent
python test_agent.py
```

## 3. Metrics Dashboard
You can view the real-time analytics dashboard without Rails.

1. Go to `f:\Shopify\shopify_ai_project\rails_gateway\public`
2. Double-click `dashboard.html` to open it in your browser.
3. It connects directly to the Python agent at `localhost:8000`.

## 4. Troubleshooting
If you get **"Quota exceeded"** errors:
- This is due to the free Gemini API tier.
- Wait 60 seconds and try again.
- Or check `agent.py` to switch to a different model if needed.
