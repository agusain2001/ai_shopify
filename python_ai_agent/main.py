import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import AnalyticsAgent
from metrics import metrics
import uvicorn
import os
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Shopify AI Analytics Agent",
    description="LLM-powered analytics service for Shopify stores",
    version="1.0.0"
)

# Enable CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    store_id: str
    question: str
    access_token: str

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "python-ai-agent"}

@app.get("/metrics")
def get_metrics():
    """Expose metrics for monitoring and dashboard"""
    return metrics.get_metrics()

@app.post("/analyze")
async def analyze_store(request: QuestionRequest):
    start_time = time.time()
    logger.info(f"Received request for store: {request.store_id}")
    
    success = False
    error_type = None
    intent = None
    cache_hit = False
    
    try:
        # Pass the token to the agent
        agent = AnalyticsAgent(store_id=request.store_id, access_token=request.access_token)
        
        result = agent.process_question(request.question)
        
        # Extract metadata for metrics
        success = "error" not in result
        cache_hit = result.get("cached", False)
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        error_type = type(e).__name__
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Always record metrics
        response_time_ms = (time.time() - start_time) * 1000
        metrics.record_request(
            store_id=request.store_id,
            success=success,
            response_time_ms=response_time_ms,
            intent=intent,
            error_type=error_type,
            cache_hit=cache_hit
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
