"""Message model for conversation history."""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .conversation import Conversation


class Message(SQLModel, table=True):
    """Message entity for conversation history.

    Represents individual messages in a conversation (user or assistant).
    Messages are append-only and never updated or deleted.
    """

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=20)  # "user" or "assistant"
    content: str  # No max length (TEXT column)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
