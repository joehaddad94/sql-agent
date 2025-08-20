"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class ChatInput(BaseModel):
    """Input schema for chat requests."""
    input: str = Field(..., description="The natural language query to process")
    config: Optional[Dict[str, Any]] = Field(default=None, description="Optional configuration parameters")
    
    class Config:
        extra = "forbid"
        validate_assignment = True

class ChatResponse(BaseModel):
    """Response schema for chat requests."""
    output: str = Field(..., description="The response from the SQL agent")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata about the response")
