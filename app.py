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
    
    # Create and configure the FastAPI app
    app = create_app()
    
    return app

# Create the app instance (without SQL Agent)
app = main()

if __name__ == "__main__":
    import uvicorn
    
    # Initialize the SQL Agent only when running the server
    sql_agent = SQLAgent()
    print("✅ SQL Agent ready")
    
    # Set up the SQL Agent for all routes
    setup_sql_agent(app, sql_agent)
    
    print(f"🚀 Server starting on port {Config.SERVER_PORT}")
    print(f"📖 API docs: http://localhost:{Config.SERVER_PORT}/docs")
    
    uvicorn.run(
        "app:app",
        host=Config.SERVER_HOST,
        port=Config.SERVER_PORT,
        reload=Config.SERVER_RELOAD,
        log_level=Config.SERVER_LOG_LEVEL
    )
