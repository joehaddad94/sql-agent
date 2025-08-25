"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class LangSmithMetadata(BaseModel):
    """Metadata for LangSmith tracing and monitoring."""
    user_id: Optional[str] = Field(default=None, description="User identifier for tracing")
    session_id: Optional[str] = Field(default=None, description="Session identifier for tracing")
    query_category: Optional[str] = Field(default=None, description="Category of the query")
    tags: Optional[list[str]] = Field(default=None, description="Tags for organizing traces")
    custom_fields: Optional[Dict[str, Any]] = Field(default=None, description="Additional custom metadata")

class ChatInput(BaseModel):
    """Input schema for chat requests."""
    input: str = Field(..., description="The natural language query to process")
    config: Optional[Dict[str, Any]] = Field(default=None, description="Optional configuration parameters")
    langsmith_metadata: Optional[LangSmithMetadata] = Field(default=None, description="LangSmith tracing metadata")
    
    class Config:
        extra = "forbid"
        validate_assignment = True

class ChatResponse(BaseModel):
    """Response schema for chat requests."""
    output: str = Field(..., description="The response from the SQL agent")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata about the response")
    langsmith_info: Optional[Dict[str, Any]] = Field(default=None, description="LangSmith tracing information")
