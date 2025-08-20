"""
Health check API endpoints
"""

from fastapi import APIRouter
from src.core.sql_agent import SQLAgent

router = APIRouter(tags=["health"])

# SQL Agent instance (will be injected from main app)
sql_agent: SQLAgent = None

def set_sql_agent(agent: SQLAgent):
    """Set the SQL Agent instance for this router."""
    global sql_agent
    sql_agent = agent

@router.get("/health")
async def health_check():
    """Check if the SQL agent is running and healthy."""
    if not sql_agent:
        return {
            "status": "unhealthy",
            "agent": "not_initialized",
            "error": "SQL Agent not initialized"
        }
    
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
