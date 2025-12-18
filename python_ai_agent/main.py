from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import AnalyticsAgent
import uvicorn
import os
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class QuestionRequest(BaseModel):
    store_id: str
    question: str
    access_token: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze_store(request: QuestionRequest):
    logger.info(f"Received request for store: {request.store_id}")
    try:
        # Pass the token to the agent
       agent = AnalyticsAgent(store_id=request.store_id, access_token=request.access_token)
        
        result = agent.process_question(request.question)
        return result
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
