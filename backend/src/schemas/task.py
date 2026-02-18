"""Task request and response schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from src.utils.sanitization import sanitize_string


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")

    @field_validator("title", mode="before")
    @classmethod
    def sanitize_title(cls, v):
        """Sanitize title before validation."""
        if isinstance(v, str):
            return sanitize_string(v)
        return v

    @field_validator("description", mode="before")
    @classmethod
    def sanitize_description(cls, v):
        """Sanitize description before validation."""
        if isinstance(v, str):
            return sanitize_string(v)
        return v


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    is_completed: Optional[bool] = Field(None, description="Task completion status")

    @field_validator("title", mode="before")
    @classmethod
    def sanitize_title(cls, v):
        """Sanitize title before validation."""
        if isinstance(v, str):
            return sanitize_string(v)
        return v

    @field_validator("description", mode="before")
    @classmethod
    def sanitize_description(cls, v):
        """Sanitize description before validation."""
        if isinstance(v, str):
            return sanitize_string(v)
        return v


class TaskResponse(BaseModel):
    """Schema for task data in responses."""
    
    id: int
    user_id: int
    title: str
    description: Optional[str]
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskList(BaseModel):
    """Schema for list of tasks with metadata."""
    
    tasks: list[TaskResponse] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks")
