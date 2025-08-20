"""
Chat-related API endpoints
"""

from fastapi import APIRouter, HTTPException
from src.api.models import ChatInput, ChatResponse
from src.api.utils import extract_clean_answer
from src.core.sql_agent import SQLAgent

router = APIRouter(prefix="/chat", tags=["chat"])

# SQL Agent instance (will be injected from main app)
sql_agent: SQLAgent = None

def set_sql_agent(agent: SQLAgent):
    """Set the SQL Agent instance for this router."""
    global sql_agent
    sql_agent = agent

@router.post("/invoke", response_model=ChatResponse)
async def chat_invoke(request: ChatInput):
    """Process a natural language query and return the response."""
    if not sql_agent:
        raise HTTPException(status_code=500, detail="SQL Agent not initialized")
    
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

@router.post("/stream")
async def chat_stream(request: ChatInput):
    """Stream the response from the SQL agent."""
    if not sql_agent:
        raise HTTPException(status_code=500, detail="SQL Agent not initialized")
    
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

@router.post("/batch")
async def chat_batch(requests: list[ChatInput]):
    """Process multiple requests in batch."""
    if not sql_agent:
        raise HTTPException(status_code=500, detail="SQL Agent not initialized")
    
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
