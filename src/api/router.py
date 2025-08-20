"""
API router registry and management
"""

from fastapi import APIRouter
from src.api.routes import chat, health, root
from src.core.sql_agent import SQLAgent

def create_api_router() -> APIRouter:
    """Create and configure the main API router."""
    api_router = APIRouter()
    
    # Include all route modules
    api_router.include_router(root.router)
    api_router.include_router(health.router)
    api_router.include_router(chat.router)
    
    return api_router

def set_sql_agent_for_routes(agent: SQLAgent):
    """Set the SQL Agent instance for all routes that need it."""
    chat.set_sql_agent(agent)
    health.set_sql_agent(agent)
