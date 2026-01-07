"""
FastAPI Entry Point
Exposes /chat endpoint for the agentic call center
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from dotenv import load_dotenv
from app.graph import AgenticCallCenterGraph
from app.state import GraphState
import uuid
import logging
import os

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agentic Call Center API",
    description="Production-grade Agentic AI Call Center using LangGraph",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize graph
graph = AgenticCallCenterGraph()


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str
    agent: Optional[str] = None
    requires_human_review: bool = False
    safety_flags: list = []
    risk_score: float = 0.0
    session_id: str
    routing_info: Optional[dict] = None


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Agentic Call Center API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "graph_initialized": graph is not None
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - processes user queries through the agentic system.
    
    Flow:
    1. Orchestrator routes to appropriate domain agent
    2. Domain agent processes query and calls tools
    3. Safety sentinel validates response
    4. Returns response (or flags for human review)
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"Processing chat request - Session: {session_id}, Query: {request.message}")
        
        # Invoke the graph
        result: GraphState = graph.invoke(
            user_query=request.message,
            session_id=session_id
        )
        
        # Extract response
        response_text = result.get("agent_response", "I apologize, but I couldn't process your request.")
        
        # If sentinel flagged for review, prepend warning
        if result.get("requires_human_review", False):
            response_text = f"[REQUIRES HUMAN REVIEW] {response_text}"
        
        return ChatResponse(
            response=response_text,
            agent=result.get("agent_name"),
            requires_human_review=result.get("requires_human_review", False),
            safety_flags=result.get("safety_flags", []),
            risk_score=result.get("risk_score", 0.0),
            session_id=session_id,
            routing_info={
                "next_agent": result.get("next_agent"),
                "routing_confidence": result.get("routing_confidence"),
                "routing_reasoning": result.get("routing_reasoning")
            }
        )
    
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

