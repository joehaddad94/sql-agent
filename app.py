#!/usr/bin/env python3
"""
Natural Language SQL Agent - LangChain Platform REST API
"""

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from src.core.sql_agent import SQLAgent
from src.utils.config import Config

def extract_clean_answer(result):
    """
    Extract the clean answer from the SQL Agent's response.
    
    The SQL Agent returns complex nested structures, but we want just the readable answer.
    This function handles various response formats and extracts the clean content.
    """
    if hasattr(result, 'content'):
        # If it's a message object with content
        return result.content
    elif isinstance(result, dict):
        # If it's a dictionary, look for the answer
        if 'answer' in result:
            return result['answer']
        elif 'output' in result:
            return result['output']
        elif 'result' in result:
            # Handle nested result structures
            nested_result = result['result']
            if isinstance(nested_result, dict) and 'answer' in nested_result:
                return nested_result['answer']
            else:
                return str(nested_result)
        else:
            return str(result)
    elif isinstance(result, str):
        return result
    else:
        return str(result)

# Define the input schema for chat requests
class ChatInput(BaseModel):
    input: str = Field(..., description="The natural language query to process")
    config: Optional[Dict[str, Any]] = Field(default=None, description="Optional configuration parameters")
    
    class Config:
        extra = "forbid"
        validate_assignment = True

# Define the response schema
class ChatResponse(BaseModel):
    output: str = Field(..., description="The response from the SQL agent")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata about the response")

# ------------------------------------------------------------------
# Validate configuration before starting
# ------------------------------------------------------------------
Config.validate()

# Initialize the SQL Agent
print("🚀 Initializing SQL Agent for LangChain Platform...")
sql_agent = SQLAgent()
print("✅ SQL Agent initialized and ready for requests!")

# Create FastAPI app
app = FastAPI(
    title="Natural Language SQL Agent API",
    description="A REST API for querying databases using natural language using LangChain Platform",
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
# Chat endpoint (replaces LangServe route)
# ------------------------------------------------------------------
@app.post("/chat/invoke", response_model=ChatResponse)
async def chat_invoke(request: ChatInput):
    """Process a natural language query and return the response."""
    try:
        # Use the SQL agent to process the input
        result = await sql_agent.ainvoke(request.input)
        
        # Extract the clean answer from the result
        output = extract_clean_answer(result)
        
        return ChatResponse(
            output=output,
            metadata={
                "input": request.input,
                "timestamp": "now",  # You could add proper timestamp here
                "model": "sql_agent"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# ------------------------------------------------------------------
# Stream endpoint for real-time responses
# ------------------------------------------------------------------
@app.post("/chat/stream")
async def chat_stream(request: ChatInput):
    """Stream the response from the SQL agent."""
    try:
        # Use the SQL agent to stream the response
        async for chunk in sql_agent.astream(request.input):
            # Yield each chunk as it becomes available
            if hasattr(chunk, 'content'):
                yield f"data: {chunk.content}\n\n"
            elif isinstance(chunk, dict):
                # Extract the clean answer from the chunk
                clean_chunk = extract_clean_answer(chunk)
                yield f"data: {clean_chunk}\n\n"
            elif isinstance(chunk, str):
                yield f"data: {chunk}\n\n"
            else:
                yield f"data: {str(chunk)}\n\n"
        
        # Send end marker
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: Error: {str(e)}\n\n"

# ------------------------------------------------------------------
# Batch processing endpoint
# ------------------------------------------------------------------
@app.post("/chat/batch")
async def chat_batch(requests: list[ChatInput]):
    """Process multiple requests in batch."""
    try:
        results = []
        for request in requests:
            result = await sql_agent.ainvoke(request.input)
            
            # Extract the clean answer from the result
            output = extract_clean_answer(result)
            
            results.append(ChatResponse(
                output=output,
                metadata={
                    "input": request.input,
                    "model": "sql_agent"
                }
            ))
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing batch request: {str(e)}")

# Root endpoint
@app.get("/")
async def root():
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
