"""
Chat-related API endpoints
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from src.api.models import ChatInput, ChatResponse
from src.api.utils import extract_clean_answer
from src.core.sql_agent import SQLAgent

router = APIRouter(prefix="/chat", tags=["chat"])

sql_agent: SQLAgent = None

def set_sql_agent(agent: SQLAgent):
    """Set the SQL Agent instance for this router."""
    global sql_agent
    sql_agent = agent

@router.post("/invoke", response_model=ChatResponse)
async def chat_invoke(request: ChatInput):
    """Process a natural language query and return the response."""
    if not hasattr(sql_agent, 'ainvoke'):
        raise HTTPException(status_code=500, detail="SQL Agent not initialized")
    
    try:
        # Prepare metadata for LangSmith tracing
        metadata = {}
        if request.langsmith_metadata:
            metadata.update({
                "user_id": request.langsmith_metadata.user_id,
                "session_id": request.langsmith_metadata.session_id,
                "query_category": request.langsmith_metadata.query_category,
                "tags": request.langsmith_metadata.tags,
                "custom_fields": request.langsmith_metadata.custom_fields,
                "api_endpoint": "chat_invoke"
            })
        
        # Process the request with metadata
        result = await sql_agent.ainvoke({
            "input": request.input,
            "metadata": metadata
        })
        
        output = extract_clean_answer(result)
        
        # Extract LangSmith information from result
        langsmith_info = {
            "enabled": result.get("langsmith_enabled", False),
            "project": result.get("project", "local"),
            "trace_id": getattr(result.get("raw_result", {}), "id", None)
        }
        
        return ChatResponse(
            output=output,
            metadata={
                "input": request.input,
                "timestamp": "now",
                "model": "sql_agent"
            },
            langsmith_info=langsmith_info
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@router.post("/stream")
async def chat_stream(request: ChatInput):
    """Stream the response from the SQL agent."""
    if not hasattr(sql_agent, 'ainvoke'):
        raise HTTPException(status_code=500, detail="SQL Agent not initialized")
    
    async def generate_stream():
        try:
            # Prepare metadata for LangSmith tracing
            metadata = {}
            if request.langsmith_metadata:
                metadata.update({
                    "user_id": request.langsmith_metadata.user_id,
                    "session_id": request.langsmith_metadata.session_id,
                    "query_category": request.langsmith_metadata.query_category,
                    "tags": request.langsmith_metadata.tags,
                    "custom_fields": request.langsmith_metadata.custom_fields,
                    "api_endpoint": "chat_stream"
                })
            
            # Process the request with metadata
            async for chunk in sql_agent.astream({
                "input": request.input,
                "metadata": metadata
            }):
                if hasattr(chunk, 'content'):
                    yield f"data: {chunk.content}\n\n"
                elif isinstance(chunk, dict):
                    clean_chunk = extract_clean_answer(chunk)
                    yield f"data: {clean_chunk}\n\n"
                elif isinstance(chunk, str):
                    yield f"data: {chunk}\n\n"
                else:
                    yield f"data: {str(chunk)}\n\n"
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@router.post("/batch")
async def chat_batch(requests: list[ChatInput]):
    """Process multiple requests in batch."""
    if not hasattr(sql_agent, 'ainvoke'):
        raise HTTPException(status_code=500, detail="SQL Agent not initialized")
    
    try:
        results = []
        for request in requests:
            # Prepare metadata for LangSmith tracing
            metadata = {}
            if request.langsmith_metadata:
                metadata.update({
                    "user_id": request.langsmith_metadata.user_id,
                    "session_id": request.langsmith_metadata.session_id,
                    "query_category": request.langsmith_metadata.query_category,
                    "tags": request.langsmith_metadata.tags,
                    "custom_fields": request.langsmith_metadata.custom_fields,
                    "api_endpoint": "chat_batch"
                })
            
            # Process the request with metadata
            result = await sql_agent.ainvoke({
                "input": request.input,
                "metadata": metadata
            })
            
            output = extract_clean_answer(result)
            
            # Extract LangSmith information from result
            langsmith_info = {
                "enabled": result.get("langsmith_enabled", False),
                "project": result.get("project", "local"),
                "trace_id": getattr(result.get("raw_result", {}), "id", None)
            }
            
            results.append(ChatResponse(
                output=output,
                metadata={
                    "input": request.input,
                    "model": "sql_agent"
                },
                langsmith_info=langsmith_info
            ))
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing batch request: {str(e)}")
