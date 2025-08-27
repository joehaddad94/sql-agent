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

@router.post("/stream/clean")
async def chat_stream_clean(request: ChatInput):
    """Stream the response from the SQL agent in clean text format for direct display."""
    if not hasattr(sql_agent, 'ainvoke'):
        raise HTTPException(status_code=500, detail="SQL Agent not initialized")
    
    # Log the clean stream request
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Clean stream request received: {request.input}")
    logger.info(f"Request metadata: {request.langsmith_metadata}")
    
    # Store all chunks for logging
    all_chunks = []
    final_output = ""
    
    async def generate_clean_stream():
        nonlocal all_chunks, final_output
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
                    "api_endpoint": "chat_stream_clean"
                })
            
            logger.info(f"Starting clean stream processing with metadata: {metadata}")
            
            # Process the request with metadata
            chunk_count = 0
            async for chunk in sql_agent.astream({
                "input": request.input,
                "metadata": metadata
            }):
                chunk_count += 1
                
                # Log each chunk
                logger.info(f"Clean stream chunk {chunk_count}: Type={type(chunk)}, Content={chunk}")
                
                # Store chunk for final logging
                all_chunks.append({
                    "chunk_number": chunk_count,
                    "type": str(type(chunk)),
                    "content": str(chunk),
                    "has_content_attr": hasattr(chunk, 'content'),
                    "content_attr_value": getattr(chunk, 'content', None) if hasattr(chunk, 'content') else None
                })
                
                # Process chunk and yield clean content
                if hasattr(chunk, 'content'):
                    content = chunk.content
                    logger.info(f"Clean stream chunk {chunk_count} has content attribute: {content}")
                    final_output += str(content)
                    yield content
                elif isinstance(chunk, dict):
                    clean_chunk = extract_clean_answer(chunk)
                    logger.info(f"Clean stream chunk {chunk_count} is dict, cleaned: {clean_chunk}")
                    final_output += str(clean_chunk)
                    yield clean_chunk
                elif isinstance(chunk, str):
                    logger.info(f"Clean stream chunk {chunk_count} is string: {chunk}")
                    final_output += chunk
                    yield chunk
                else:
                    chunk_str = str(chunk)
                    logger.info(f"Clean stream chunk {chunk_count} is other type: {chunk_str}")
                    final_output += chunk_str
                    yield chunk_str
            
            # Log completion
            logger.info(f"Clean stream completed. Total chunks: {chunk_count}")
            logger.info(f"Final output length: {len(final_output)}")
            logger.info(f"Final output preview: {final_output[:200]}...")
            
            # Log all chunks summary
            logger.info("Clean stream chunks summary:")
            for chunk_info in all_chunks:
                logger.info(f"  Chunk {chunk_info['chunk_number']}: {chunk_info['type']} - {chunk_info['content'][:100]}...")
            
            # Log what was actually sent to frontend
            logger.info("=== FRONTEND OUTPUT LOG ===")
            logger.info(f"Total content sent to frontend: {len(final_output)} characters")
            logger.info(f"Content sent to frontend:\n{final_output}")
            logger.info("=== END FRONTEND OUTPUT LOG ===")
            
        except Exception as e:
            error_msg = f"Error in clean stream processing: {str(e)}"
            logger.error(error_msg, exc_info=True)
            logger.error(f"Chunks processed before error: {len(all_chunks)}")
            logger.error(f"Partial output before error: {final_output}")
            yield f"Error: {str(e)}"
    
    return StreamingResponse(
        generate_clean_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/plain; charset=utf-8"
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
