#!/usr/bin/env python3
"""
Natural Language SQL Agent - LangChain Platform REST API
Main application entry point
"""

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.api.config import create_app, setup_sql_agent
from src.core.sql_agent import SQLAgent
from src.utils.config import Config

def main():
    """Main application entry point."""
    # Validate configuration before starting
    Config.validate()
    
    # Initialize the SQL Agent
    print("🚀 Initializing SQL Agent for LangChain Platform...")
    sql_agent = SQLAgent()
    print("✅ SQL Agent initialized and ready for requests!")
    
    # Create and configure the FastAPI app
    app = create_app()
    
    # Set up the SQL Agent for all routes
    setup_sql_agent(app, sql_agent)
    
    return app

# Create the app instance
app = main()

if __name__ == "__main__":
    import uvicorn
    
    print("🌐 Starting LangChain Platform server...")
    print("📖 API docs: http://localhost:8000/docs")
    print("💬 Chat endpoint: http://localhost:8000/chat/invoke")
    print("🌊 Stream endpoint: http://localhost:8000/chat/stream")
    print("📦 Batch endpoint: http://localhost:8000/chat/batch")
    print("🏥 Health check: http://localhost:8000/health")
    print("=" * 60)
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
