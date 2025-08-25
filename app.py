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
    print(f"📖 API docs: http://localhost:{Config.SERVER_PORT}/docs")
    print(f"💬 Chat endpoint: http://localhost:{Config.SERVER_PORT}/chat/invoke")
    print(f"🌊 Stream endpoint: http://localhost:{Config.SERVER_PORT}/chat/stream")
    print(f"📦 Batch endpoint: http://localhost:{Config.SERVER_PORT}/chat/batch")
    print(f"🏥 Health check: http://localhost:{Config.SERVER_PORT}/health")
    print(f"🔧 Server config: {Config.SERVER_HOST}:{Config.SERVER_PORT}")
    print(f"🔄 Auto-reload: {Config.SERVER_RELOAD}")
    print(f"📝 Log level: {Config.SERVER_LOG_LEVEL}")
    print("=" * 60)
    
    uvicorn.run(
        "app:app",
        host=Config.SERVER_HOST,
        port=Config.SERVER_PORT,
        reload=Config.SERVER_RELOAD,
        log_level=Config.SERVER_LOG_LEVEL
    )
