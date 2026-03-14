"""Conversation utility functions for stateless chat persistence."""
from datetime import datetime
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.conversation import Conversation
from src.models.message import Message


async def get_or_create_conversation(
    session: AsyncSession,
    user_id: int
) -> Conversation:
    """Get active conversation for user or create new one.

    Args:
        session: Database session
        user_id: ID of the authenticated user

    Returns:
        Conversation object (existing or newly created)
    """
    # Try to get most recent conversation
    result = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(1)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        # Create new conversation
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)

    return conversation


async def load_conversation_history(
    session: AsyncSession,
    conversation_id: int,
    limit: int = 50
) -> List[Message]:
    """Load recent messages from conversation.

    Args:
        session: Database session
        conversation_id: ID of the conversation
        limit: Maximum number of messages to load (default 50)

    Returns:
        List of Message objects in chronological order
    """
    result = await session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.timestamp.desc())
        .limit(limit)
    )
    messages = result.scalars().all()

    # Reverse to get chronological order
    return list(reversed(messages))


async def persist_message(
    session: AsyncSession,
    conversation_id: int,
    role: str,
    content: str
) -> Message:
    """Persist a message to the conversation.

    Args:
        session: Database session
        conversation_id: ID of the conversation
        role: Message role ("user" or "assistant")
        content: Message content

    Returns:
        Created Message object
    """
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)

    # Update conversation timestamp
    conversation = await session.get(Conversation, conversation_id)
    if conversation:
        conversation.updated_at = datetime.utcnow()
        await session.commit()

    return message
