# Quick Start: MCP Task Tools Integration

**Feature**: 005-mcp-task-tools
**Date**: 2026-02-19
**Status**: Planning Complete

## Overview

This guide helps developers quickly understand and work with the MCP Task Tools integration. The system enables natural language task management through an AI agent that calls structured MCP tools.

## Architecture at a Glance

```
Frontend (ChatKit)
    ↓ POST /api/chat
Backend (FastAPI)
    ↓ Authenticate & Load History
Agent (OpenAI Agents SDK)
    ↓ Function Calling
MCP Tools (add_task, list_tasks, etc.)
    ↓ Authorized Operations
Database (Neon PostgreSQL)
```

## Key Concepts

### 1. Stateless Architecture
- No in-memory conversation state
- All state persisted to database (Conversation, Message models)
- Each request loads history from DB
- Multiple server instances supported

### 2. Tool-Driven Execution
- Agent never accesses database directly
- All operations go through MCP tools
- Tools enforce authorization (user_id validation)
- Structured responses (success/error format)

### 3. Agent-Database Separation
- Clear boundary between AI agent and data layer
- Agent receives user_context (user_id, email)
- Tools validate ownership before operations
- Database is single source of truth

## Project Structure

```
backend/src/
├── agent/
│   ├── __init__.py
│   ├── agent.py           # Agent invocation logic
│   ├── config.py          # Agent configuration
│   └── prompts.py         # System prompts
├── tools/
│   ├── __init__.py
│   ├── registry.py        # Tool catalog
│   ├── add_task.py        # Create task tool
│   ├── list_tasks.py      # List tasks tool
│   ├── complete_task.py   # Complete task tool
│   ├── delete_task.py     # Delete task tool
│   └── update_task.py     # Update task tool
├── api/
│   └── chat.py            # POST /api/chat endpoint
├── models/
│   ├── conversation.py    # Conversation model (NEW)
│   └── message.py         # Message model (NEW)
└── utils/
    └── conversation.py    # Conversation helpers
```

## Quick Setup

### 1. Install Dependencies

```bash
cd backend
pip install mcp-sdk openai
```

### 2. Environment Variables

Add to `.env`:

```env
# OpenAI API Key
OPENAI_API_KEY=sk-...

# Existing variables (keep these)
DATABASE_URL=postgresql+asyncpg://...
JWT_SECRET_KEY=...
```

### 3. Database Migration

```bash
# Option 1: Auto-create (development)
# Tables created automatically on startup

# Option 2: Alembic (production)
alembic revision --autogenerate -m "Add conversation and message tables"
alembic upgrade head
```

### 4. Run Backend

```bash
uvicorn src.main:app --reload
```

## Working with MCP Tools

### Tool Structure

Every MCP tool follows this pattern:

```python
from typing import Dict, Any
from sqlmodel.ext.asyncio.session import AsyncSession
from mcp import tool as mcp_tool

@mcp_tool
async def tool_name(
    # Tool-specific parameters
    param1: str,
    param2: int = 0,

    # Standard parameters (automatically provided)
    user_context: Dict[str, Any] = None,
    session: AsyncSession = None,
) -> Dict[str, Any]:
    """Tool description for agent."""

    try:
        # 1. Extract user_id from user_context
        user_id = user_context["user_id"]

        # 2. Perform authorized operation
        # ... database operations ...

        # 3. Return structured success response
        return {
            "success": True,
            "data": {
                # ... result data ...
            }
        }

    except Exception as e:
        # 4. Return structured error response
        return {
            "success": False,
            "error": str(e)
        }
```

### Example: add_task Tool

```python
@mcp_tool
async def add_task(
    title: str,
    description: str = "",
    user_context: Dict[str, Any] = None,
    session: AsyncSession = None,
) -> Dict[str, Any]:
    """Creates a new task for the authenticated user."""

    try:
        user_id = user_context["user_id"]

        # Create task with forced user_id
        new_task = Task(
            user_id=user_id,
            title=title,
            description=description,
            is_completed=False,
        )

        session.add(new_task)
        await session.commit()
        await session.refresh(new_task)

        return {
            "success": True,
            "data": {
                "task_id": new_task.id,
                "title": new_task.title,
                "description": new_task.description,
                "completed": new_task.is_completed,
                "created_at": new_task.created_at.isoformat(),
            }
        }

    except Exception as e:
        await session.rollback()
        return {
            "success": False,
            "error": f"Failed to create task: {str(e)}"
        }
```

## Working with the Agent

### Agent Configuration

```python
# agent/config.py
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

AGENT_CONFIG = {
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 500,
    "timeout": 10,  # seconds
}
```

### System Prompt

```python
# agent/prompts.py
SYSTEM_PROMPT = """
You are a helpful task management assistant. You help users manage their todo list through natural language.

Available tools:
- add_task: Create a new task
- list_tasks: Show all tasks
- complete_task: Mark a task as done
- delete_task: Remove a task
- update_task: Modify task details

Guidelines:
- Be conversational and friendly
- Confirm actions after completing them
- Ask for clarification if user intent is unclear
- Use tools to perform operations (never make up data)
"""
```

### Agent Invocation

```python
# agent/agent.py
async def invoke_agent(
    user_message: str,
    conversation_history: List[Dict[str, str]],
    user_context: Dict[str, Any],
    session: AsyncSession,
) -> str:
    """Invoke OpenAI agent with tools."""

    # Build messages with history
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *conversation_history,
        {"role": "user", "content": user_message},
    ]

    # Register tools
    tools = get_tool_catalog()

    # Call agent with function calling
    response = client.chat.completions.create(
        model=AGENT_CONFIG["model"],
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    # Handle tool calls
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            # Inject user_context and session
            tool_args["user_context"] = user_context
            tool_args["session"] = session

            # Execute tool
            tool_result = await execute_tool(tool_name, tool_args)

            # Add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result),
            })

        # Get final response
        final_response = client.chat.completions.create(
            model=AGENT_CONFIG["model"],
            messages=messages,
        )

        return final_response.choices[0].message.content

    return response.choices[0].message.content
```

## Working with the Chat Endpoint

### Endpoint Implementation

```python
# api/chat.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.models.user import User
from src.utils.jwt import get_current_user
from src.agent.agent import invoke_agent
from src.utils.conversation import (
    get_or_create_conversation,
    load_conversation_history,
    persist_message,
)

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    conversation_id: int

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Process user message through AI agent."""

    # 1. Get or create conversation
    conversation = await get_or_create_conversation(session, current_user.id)

    # 2. Load conversation history
    history = await load_conversation_history(session, conversation.id)

    # 3. Persist user message
    await persist_message(session, conversation.id, "user", request.message)

    # 4. Prepare user context
    user_context = {
        "user_id": current_user.id,
        "email": current_user.email,
    }

    # 5. Invoke agent
    agent_response = await invoke_agent(
        user_message=request.message,
        conversation_history=history,
        user_context=user_context,
        session=session,
    )

    # 6. Persist agent response
    await persist_message(session, conversation.id, "assistant", agent_response)

    # 7. Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    await session.commit()

    return ChatResponse(
        response=agent_response,
        conversation_id=conversation.id,
    )
```

## Testing

### Unit Test: MCP Tool

```python
import pytest
from src.tools.add_task import add_task

@pytest.mark.asyncio
async def test_add_task_success(session, user):
    """Test successful task creation."""

    user_context = {"user_id": user.id, "email": user.email}

    result = await add_task(
        title="Test task",
        description="Test description",
        user_context=user_context,
        session=session,
    )

    assert result["success"] is True
    assert result["data"]["title"] == "Test task"
    assert result["data"]["task_id"] is not None
```

### Integration Test: Chat Endpoint

```python
@pytest.mark.asyncio
async def test_chat_endpoint(client, auth_headers):
    """Test chat endpoint with agent invocation."""

    response = await client.post(
        "/api/chat",
        json={"message": "Add a task to buy groceries"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "conversation_id" in data
```

## Common Patterns

### Pattern 1: Get or Create Conversation

```python
async def get_or_create_conversation(
    session: AsyncSession,
    user_id: int,
) -> Conversation:
    """Get active conversation or create new one."""

    result = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(1)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)

    return conversation
```

### Pattern 2: Load Conversation History

```python
async def load_conversation_history(
    session: AsyncSession,
    conversation_id: int,
    limit: int = 50,
) -> List[Dict[str, str]]:
    """Load recent messages for agent context."""

    result = await session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.timestamp.desc())
        .limit(limit)
    )
    messages = result.scalars().all()

    # Reverse to chronological order
    return [
        {"role": msg.role, "content": msg.content}
        for msg in reversed(messages)
    ]
```

### Pattern 3: Persist Message

```python
async def persist_message(
    session: AsyncSession,
    conversation_id: int,
    role: str,
    content: str,
) -> Message:
    """Save message to database."""

    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)

    return message
```

## Troubleshooting

### Issue: Agent not calling tools

**Symptoms**: Agent responds without using tools

**Solution**: Check system prompt and tool descriptions. Ensure tools are registered in catalog.

### Issue: Authorization failures

**Symptoms**: 403 errors when accessing tasks

**Solution**: Verify user_context is passed to tools. Check user_id extraction from JWT.

### Issue: Conversation history not loading

**Symptoms**: Agent has no context of previous messages

**Solution**: Verify conversation_id is correct. Check database indexes on conversation_id.

### Issue: OpenAI API timeout

**Symptoms**: 503 errors after 10 seconds

**Solution**: Check OpenAI API status. Verify API key. Consider increasing timeout.

## Performance Tips

1. **Limit conversation history**: Load only last 50 messages to reduce token usage
2. **Index database queries**: Ensure indexes on user_id and conversation_id
3. **Connection pooling**: Use async database connections with pooling
4. **Cache tool catalog**: Build tool catalog once at startup
5. **Timeout handling**: Set reasonable timeouts for OpenAI API calls

## Security Checklist

- [ ] JWT validation on all chat requests
- [ ] user_context passed to all tool calls
- [ ] Tools validate user_id before operations
- [ ] Database queries filtered by user_id
- [ ] OpenAI API key in .env (not hardcoded)
- [ ] Error messages don't expose internal details
- [ ] Authorization failures logged for monitoring

## Next Steps

1. **Implement MCP tools** in `backend/src/tools/`
2. **Configure agent** in `backend/src/agent/`
3. **Create chat endpoint** in `backend/src/api/chat.py`
4. **Add database models** (Conversation, Message)
5. **Write tests** for tools and endpoint
6. **Integrate frontend** with ChatKit

## References

- **Specification**: `specs/005-mcp-task-tools/spec.md`
- **Implementation Plan**: `specs/005-mcp-task-tools/plan.md`
- **Data Model**: `specs/005-mcp-task-tools/data-model.md`
- **API Contracts**: `specs/005-mcp-task-tools/contracts/`
- **Research**: `specs/005-mcp-task-tools/research.md`
- **Constitution**: `.specify/memory/constitution.md`
- **ADR-0001**: `history/adr/0001-stateless-server-architecture.md`
- **ADR-0002**: `history/adr/0002-mcp-tool-integration.md`
