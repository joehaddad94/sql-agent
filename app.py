#!/usr/bin/env python3
"""
Natural Language SQL Agent - LangServe REST API
"""

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from fastapi import FastAPI
from langserve import add_routes
from src.core.sql_agent import SQLAgent
from src.utils.config import Config

# Validate configuration before starting
Config.validate()

# Initialize the SQL Agent (will stay running)
print("🚀 Initializing SQL Agent for LangServe...")
sql_agent = SQLAgent()
print("✅ SQL Agent initialized and ready for requests!")

# Create FastAPI app
app = FastAPI(
    title="Natural Language SQL Agent API",
    description="A REST API for querying databases using natural language",
    version="1.0.0"
)

# Add health check endpoint
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

# Add the SQL agent as a LangServe runnable
add_routes(
    app,
    sql_agent,  # Use the agent instance directly since it now implements Runnable
    path="/chat",
    input_type=str,  # Use simple string input to avoid schema issues
    config_keys=["configurable"],
    enable_feedback_endpoint=False,  # Disable feedback endpoint to avoid schema issues
)

# Add a simple status endpoint
@app.get("/")
async def root():
    """Root endpoint with basic information."""
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
    print("📖 API documentation available at: http://localhost:8000/docs")
    print("💬 Chat endpoint available at: http://localhost:8000/chat/invoke")
    print("🏥 Health check available at: http://localhost:8000/health")
    print("=" * 60)
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload since we want agent to stay running
        log_level="info"
    )
