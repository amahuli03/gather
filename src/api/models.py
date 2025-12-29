"""Request and response models for the API."""
from pydantic import BaseModel
from typing import Optional, List


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    user_id: str = "me"  # Default to "me" if not provided
    context: Optional[dict] = None  # Optional context (e.g., current event, location)
    oauth_token: Optional[str] = None  # OAuth access token from Apps Script (for Calendar API)


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    tool_calls: List[dict] = []  # List of tools used during processing
    user_id: str


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None

