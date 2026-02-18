"""Authentication request and response schemas."""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.utils.sanitization import sanitize_email


class UserRegister(BaseModel):
    """Schema for user registration request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100, description="User password (min 8 characters)")

    @field_validator("email", mode="before")
    @classmethod
    def sanitize_email_field(cls, v):
        """Sanitize email before validation."""
        if isinstance(v, str):
            return sanitize_email(v)
        return v


class UserLogin(BaseModel):
    """Schema for user login request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    @field_validator("email", mode="before")
    @classmethod
    def sanitize_email_field(cls, v):
        """Sanitize email before validation."""
        if isinstance(v, str):
            return sanitize_email(v)
        return v


class UserResponse(BaseModel):
    """Schema for user data in responses."""
    
    id: int
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Schema for authentication response with token."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="User information")
