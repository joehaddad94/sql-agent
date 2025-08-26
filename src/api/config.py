"""
FastAPI application configuration and setup
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.router import create_api_router, set_sql_agent_for_routes
from src.core.sql_agent import SQLAgent

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Natural Language SQL Agent API",
        description="A REST API for querying databases using natural language using LangChain Platform",
        version="1.0.0"
    )
    
    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods including OPTIONS
        allow_headers=["*"],  # Allow all headers
    )
    
    # Create and include the API router
    api_router = create_api_router()
    app.include_router(api_router)
    
    return app

def setup_sql_agent(app: FastAPI, agent: SQLAgent):
    """Set up the SQL Agent for all routes."""
    set_sql_agent_for_routes(agent)
