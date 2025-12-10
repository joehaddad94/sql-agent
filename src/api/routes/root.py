"""
Root API endpoints
"""

from fastapi import APIRouter

router = APIRouter(tags=["root"])

@router.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Natural Language SQL Agent API (LangChain Platform)",
        "status": "running",
        "endpoints": {
            "chat": "/chat/invoke",
            "stream": "/chat/stream",
            "batch": "/chat/batch",
            "health": "/health",
            "docs": "/docs"
        },
        "usage": "Send natural language queries to /chat/invoke",
        "platform": "LangChain Platform"
    }
