"""Chat request and response schemas."""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's natural language message to the AI agent"
    )


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    response: str = Field(
        ...,
        description="AI agent's natural language response to user"
    )
    conversation_id: int = Field(
        ...,
        description="ID of the conversation for tracking"
    )
