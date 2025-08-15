#!/usr/bin/env python3
"""
Natural Language SQL Agent - LangServe REST API
"""

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from fastapi import FastAPI
from pydantic import BaseModel, Field
from langserve import add_routes
from langserve import validation  # Needed for manual model rebuild
from src.core.sql_agent import SQLAgent
from src.utils.config import Config

# Define the input schema that LangServe expects
class ChatInput(BaseModel):
    input: str = Field(..., description="The natural language query to process")
    
    class Config:
        # This ensures the model works properly with LangServe
        extra = "forbid"
        validate_assignment = True

# ------------------------------------------------------------------
# PATCH: Ensure all Pydantic models in LangServe are rebuilt
# ------------------------------------------------------------------
try:
    for name in dir(validation):
        obj = getattr(validation, name)
        if hasattr(obj, "model_rebuild"):
            obj.model_rebuild()
except Exception as e:
    print(f"⚠️ Could not rebuild LangServe models: {e}")

# ------------------------------------------------------------------
# Validate configuration before starting
# ------------------------------------------------------------------
Config.validate()

# Initialize the SQL Agent
print("🚀 Initializing SQL Agent for LangServe...")
sql_agent = SQLAgent()
print("✅ SQL Agent initialized and ready for requests!")

# Create FastAPI app
app = FastAPI(
    title="Natural Language SQL Agent API",
    description="A REST API for querying databases using natural language",
    version="1.0.0"
)

# ------------------------------------------------------------------
# Health check endpoint
# ------------------------------------------------------------------
@app.get("/health")
async def health_check():
    """Check if the SQL agent is running and healthy."""
    try:
        db_info = sql_agent.get_database_info()
        if "error" not in db_info:
            return {
                "status": "healthy",
                "agent": "running",
                "database": "connected" if db_info['connection_status'] else "disconnected",
                "tables": len(db_info.get('tables', [])),
                "available_tools": len(db_info.get('available_tools', []))
            }
        else:
            return {
                "status": "unhealthy",
                "agent": "running",
                "database": "error",
                "error": db_info['error']
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "agent": "error",
            "error": str(e)
        }

# ------------------------------------------------------------------
# LangServe route
# ------------------------------------------------------------------
add_routes(
    app,
    sql_agent,       # Runnable instance
    path="/chat",
    input_type=ChatInput,  # Use our custom input schema
    config_keys=["configurable"],
    enable_feedback_endpoint=False,
    per_req_config_modifier=lambda config: config,
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Natural Language SQL Agent API",
        "status": "running",
        "endpoints": {
            "chat": "/chat/invoke",
            "stream": "/chat/stream",
            "health": "/health",
            "docs": "/docs"
        },
        "usage": "Send natural language queries to /chat/invoke"
    }

if __name__ == "__main__":
    import uvicorn

    print("🌐 Starting LangServe server...")
    print("📖 API docs: http://localhost:8000/docs")
    print("💬 Chat endpoint: http://localhost:8000/chat/invoke")
    print("🏥 Health check: http://localhost:8000/health")
    print("=" * 60)

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
