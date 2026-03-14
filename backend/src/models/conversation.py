"""Conversation model for chat history persistence."""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User
    from .message import Message


class Conversation(SQLModel, table=True):
    """Conversation entity for chat history.

    Represents a chat conversation between user and AI agent.
    All messages in a conversation are linked via conversation_id.
    """

    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")
