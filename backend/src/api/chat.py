"""Chat endpoint for AI agent interaction."""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.user import User
from src.schemas.chat import ChatRequest, ChatResponse
from src.utils.jwt import get_current_user
from src.agent.agent import invoke_agent
from src.utils.conversation import (
    get_or_create_conversation,
    load_conversation_history,
    persist_message,
)

router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Process user message through AI agent.

    This endpoint orchestrates the complete chat flow:
    1. Authenticate user (via JWT dependency)
    2. Get or create conversation
    3. Load conversation history
    4. Persist user message
    5. Prepare user context
    6. Invoke agent with tools
    7. Persist agent response
    8. Update conversation timestamp
    9. Return response

    Args:
        request: Chat request with user message
        current_user: Authenticated user (from JWT)
        session: Database session

    Returns:
        ChatResponse with agent's response and conversation_id
    """
    # Step 1: Get or create conversation
    conversation = await get_or_create_conversation(session, current_user.id)

    # Step 2: Load conversation history (last 50 messages)
    messages = await load_conversation_history(session, conversation.id, limit=50)

    # Convert to format expected by agent
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]

    # Step 3: Persist user message
    await persist_message(session, conversation.id, "user", request.message)

    # Step 4: Prepare user context
    user_context = {
        "user_id": current_user.id,
        "email": current_user.email,
    }

    # Step 5: Invoke agent
    agent_response = await invoke_agent(
        user_message=request.message,
        conversation_history=history,
        user_context=user_context,
        session=session,
    )

    # Step 6: Persist agent response
    await persist_message(session, conversation.id, "assistant", agent_response)

    # Step 7: Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    await session.commit()

    # Step 8: Return response
    return ChatResponse(
        response=agent_response,
        conversation_id=conversation.id,
    )
