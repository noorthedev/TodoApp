# Phase-II to Phase-III Migration Guide

**Document Version**: 1.0.0
**Date**: 2026-02-19
**Status**: Active

## Overview

This guide documents the migration path from Phase-II (traditional CRUD web application) to Phase-III (AI-powered chatbot with MCP tools). It provides a step-by-step approach to transforming the existing application while preserving working functionality.

## Architecture Comparison

### Phase-II Architecture (Before)

```
Frontend (Next.js) → Backend API (FastAPI) → Database (Neon PostgreSQL)
     ↓                      ↓
  React UI            RESTful CRUD
  Forms               Endpoints
  Axios               Direct DB access
```

**Characteristics:**
- Traditional CRUD operations
- RESTful API endpoints
- Direct database access from endpoints
- Next.js frontend with forms
- Synchronous request-response pattern

### Phase-III Architecture (After)

```
Frontend (ChatKit) → Backend API → Agent (OpenAI) → MCP Tools → Database
     ↓                    ↓              ↓              ↓
  Chat UI          JWT Auth      Natural Lang.   Authorization
  Messages         Conversation   Tool Selection  Structured I/O
                   Persistence
```

**Characteristics:**
- Natural language interaction
- AI agent interprets user intent
- MCP tools for all data operations
- Stateless server architecture
- Conversation persistence
- Agent-database separation

## What Changes

### Components to Replace

| Phase-II Component | Phase-III Replacement | Reason |
|-------------------|----------------------|---------|
| Next.js frontend | OpenAI ChatKit | Chat-based UI instead of forms |
| CRUD API endpoints | Chat endpoint + MCP tools | Natural language instead of REST |
| Direct DB access | MCP tools | Agent-database separation |
| Axios API client | ChatKit built-in | Different interaction model |

### Components to Keep

| Component | Status | Notes |
|-----------|--------|-------|
| FastAPI backend | ✅ Keep | Still serves as API layer |
| Neon PostgreSQL | ✅ Keep | Still database of choice |
| SQLModel ORM | ✅ Keep | Still used in MCP tools |
| Better Auth + JWT | ✅ Keep | Still handles authentication |
| User model | ✅ Keep | Same authentication system |
| Task model | ✅ Keep | Same data structure |

### Components to Add

| Component | Purpose | Location |
|-----------|---------|----------|
| OpenAI Agents SDK | AI agent implementation | `backend/src/agent/` |
| MCP SDK | Tool implementation | `backend/src/tools/` |
| Conversation model | Store chat history | `backend/src/models/conversation.py` |
| Message model | Store individual messages | `backend/src/models/message.py` |
| Chat endpoint | Handle chat requests | `backend/src/api/chat.py` |
| Tool registry | Register MCP tools | `backend/src/tools/registry.py` |
| ChatKit frontend | Chat UI | `frontend/` |

## Migration Strategy

### Option 1: Parallel Implementation (Recommended)

**Approach**: Build Phase-III alongside Phase-II, then switch over

**Advantages:**
- ✅ Zero downtime
- ✅ Can test Phase-III thoroughly before switching
- ✅ Easy rollback if issues arise
- ✅ Users can continue using Phase-II during development

**Process:**
1. Keep existing Phase-II code running
2. Add Phase-III components in parallel
3. Test Phase-III thoroughly
4. Switch frontend to ChatKit
5. Deprecate Phase-II endpoints (optional)

**Timeline**: 2-3 weeks

### Option 2: Incremental Migration

**Approach**: Gradually replace Phase-II components with Phase-III

**Advantages:**
- ✅ Smaller changes per step
- ✅ Can validate each step before proceeding

**Disadvantages:**
- ⚠️ More complex (two systems running simultaneously)
- ⚠️ Longer migration period

**Process:**
1. Add conversation/message models
2. Add MCP tools alongside existing endpoints
3. Add agent integration
4. Add chat endpoint
5. Replace frontend
6. Remove old endpoints

**Timeline**: 3-4 weeks

### Option 3: Clean Slate (Not Recommended)

**Approach**: Delete Phase-II code and rebuild from scratch

**Disadvantages:**
- ❌ Downtime required
- ❌ Higher risk
- ❌ Loses working code
- ❌ No rollback option

**Not recommended** unless starting fresh project.

## Step-by-Step Migration (Parallel Implementation)

### Phase 0: Preparation (1 day)

**Goal**: Set up Phase-III infrastructure without breaking Phase-II

**Tasks:**
1. Review constitution v2.0.0 and ADRs
2. Install new dependencies:
   ```bash
   # Backend
   pip install openai mcp-sdk

   # Frontend (new project)
   npx create-chatkit-app frontend-chatkit
   ```
3. Create new directory structure:
   ```
   backend/src/
   ├── agent/          # NEW: OpenAI agent
   ├── tools/          # NEW: MCP tools
   ├── api/
   │   ├── tasks.py    # KEEP: Phase-II endpoints
   │   └── chat.py     # NEW: Phase-III chat endpoint
   └── models/
       ├── user.py     # KEEP: Existing
       ├── task.py     # KEEP: Existing
       ├── conversation.py  # NEW
       └── message.py       # NEW
   ```

**Validation:**
- Phase-II still works
- New directories created
- Dependencies installed

---

### Phase 1: Database Schema Extension (1 day)

**Goal**: Add conversation and message tables without affecting existing tables

**Tasks:**

1. Create Conversation model:
   ```python
   # backend/src/models/conversation.py
   from sqlmodel import SQLModel, Field, Relationship
   from datetime import datetime
   from typing import Optional, List

   class Conversation(SQLModel, table=True):
       id: Optional[int] = Field(default=None, primary_key=True)
       user_id: int = Field(foreign_key="user.id", index=True)
       created_at: datetime = Field(default_factory=datetime.utcnow)
       updated_at: datetime = Field(default_factory=datetime.utcnow)

       # Relationships
       user: "User" = Relationship(back_populates="conversations")
       messages: List["Message"] = Relationship(back_populates="conversation")
   ```

2. Create Message model:
   ```python
   # backend/src/models/message.py
   from sqlmodel import SQLModel, Field, Relationship
   from datetime import datetime
   from typing import Optional

   class Message(SQLModel, table=True):
       id: Optional[int] = Field(default=None, primary_key=True)
       conversation_id: int = Field(foreign_key="conversation.id", index=True)
       role: str = Field(max_length=20)  # 'user' or 'assistant'
       content: str
       timestamp: datetime = Field(default_factory=datetime.utcnow)

       # Relationships
       conversation: "Conversation" = Relationship(back_populates="messages")
   ```

3. Run migration:
   ```bash
   # Create migration
   alembic revision --autogenerate -m "Add conversation and message tables"

   # Apply migration
   alembic upgrade head
   ```

**Validation:**
- New tables created in database
- Phase-II endpoints still work
- No data loss

---

### Phase 2: MCP Tools Implementation (2-3 days)

**Goal**: Implement MCP tools for all task operations

**Tasks:**

1. Create tool utilities:
   ```python
   # backend/src/tools/utils.py
   from functools import wraps
   import logging

   logger = logging.getLogger(__name__)

   def mcp_tool(func):
       """Decorator for MCP tools."""
       @wraps(func)
       async def wrapper(*args, **kwargs):
           try:
               return await func(*args, **kwargs)
           except Exception as e:
               logger.error(f"Tool error in {func.__name__}: {str(e)}", exc_info=True)
               return {"success": False, "error": "Internal error occurred"}
       return wrapper
   ```

2. Implement create_task tool:
   ```python
   # backend/src/tools/task_tools.py
   from src.tools.utils import mcp_tool
   from src.models.task import Task
   from sqlalchemy.ext.asyncio import AsyncSession

   @mcp_tool
   async def create_task(
       title: str,
       description: str = "",
       user_context: dict = None,
       session: AsyncSession = None,
   ) -> dict:
       """Create a new task for the authenticated user."""
       user_id = user_context["user_id"]

       new_task = Task(
           user_id=user_id,
           title=title,
           description=description,
           completed=False,
       )

       session.add(new_task)
       await session.commit()
       await session.refresh(new_task)

       return {
           "success": True,
           "task": {
               "id": new_task.id,
               "title": new_task.title,
               "description": new_task.description,
               "completed": new_task.completed,
           }
       }
   ```

3. Implement remaining tools (list_tasks, update_task, delete_task, get_task)

4. Create tool registry:
   ```python
   # backend/src/tools/registry.py
   from src.tools.task_tools import (
       create_task,
       list_tasks,
       update_task,
       delete_task,
       get_task,
   )

   MCP_TOOL_CATALOG = [
       create_task,
       list_tasks,
       update_task,
       delete_task,
       get_task,
   ]

   def get_tool_catalog():
       return MCP_TOOL_CATALOG
   ```

**Validation:**
- All tools implemented
- Tools have authorization checks
- Tools return structured responses
- Unit tests pass

---

### Phase 3: Agent Integration (2-3 days)

**Goal**: Integrate OpenAI Agents SDK with MCP tools

**Tasks:**

1. Create agent configuration:
   ```python
   # backend/src/agent/config.py
   import os

   OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
   AGENT_MODEL = "gpt-4"
   AGENT_TEMPERATURE = 0.7
   ```

2. Create system prompt:
   ```python
   # backend/src/agent/prompts.py
   SYSTEM_PROMPT = """You are a helpful task management assistant. You help users manage their tasks through natural conversation.

   Your capabilities:
   - Create new tasks when users describe things they need to do
   - Update existing tasks when users want to change details or mark them complete
   - Delete tasks when users no longer need them
   - List tasks when users want to see what they have

   Guidelines:
   - Be conversational and friendly
   - Confirm actions before executing them if ambiguous
   - Ask for clarification when user intent is unclear
   - Never expose technical details or error messages
   - Always use the provided tools; never make up information

   Available tools: create_task, list_tasks, update_task, delete_task, get_task
   """

   def get_system_prompt():
       return SYSTEM_PROMPT
   ```

3. Create agent implementation:
   ```python
   # backend/src/agent/agent.py
   from openai import OpenAI
   from src.agent.config import OPENAI_API_KEY, AGENT_MODEL
   from src.agent.prompts import get_system_prompt
   from src.tools.registry import get_tool_catalog

   client = OpenAI(api_key=OPENAI_API_KEY)

   async def invoke_agent(
       conversation_history: list,
       user_context: dict,
   ) -> str:
       """Invoke OpenAI agent with conversation history and user context."""
       tools = get_tool_catalog()

       # Prepare messages
       messages = [
           {"role": "system", "content": get_system_prompt()},
           *conversation_history,
       ]

       # Call OpenAI with function calling
       response = client.chat.completions.create(
           model=AGENT_MODEL,
           messages=messages,
           tools=[tool.to_openai_format() for tool in tools],
           tool_choice="auto",
       )

       # Handle tool calls if any
       if response.choices[0].message.tool_calls:
           # Execute tools and get results
           # (Implementation details omitted for brevity)
           pass

       return response.choices[0].message.content
   ```

**Validation:**
- Agent can be invoked
- Agent selects correct tools
- Agent handles tool responses
- Agent generates natural responses

---

### Phase 4: Chat Endpoint (1 day)

**Goal**: Create chat endpoint that orchestrates agent and persistence

**Tasks:**

1. Create chat endpoint:
   ```python
   # backend/src/api/chat.py
   from fastapi import APIRouter, Depends
   from sqlalchemy.ext.asyncio import AsyncSession
   from src.models.user import User
   from src.models.conversation import Conversation
   from src.models.message import Message
   from src.utils.jwt import get_current_user
   from src.utils.database import get_session
   from src.agent.agent import invoke_agent
   from datetime import datetime

   router = APIRouter()

   @router.post("/api/chat")
   async def chat_endpoint(
       message: str,
       current_user: User = Depends(get_current_user),
       session: AsyncSession = Depends(get_session),
   ):
       """Handle chat messages with AI agent."""
       # 1. Get or create conversation
       conversation = await get_or_create_conversation(session, current_user.id)

       # 2. Persist user message
       user_message = Message(
           conversation_id=conversation.id,
           role="user",
           content=message,
           timestamp=datetime.utcnow(),
       )
       session.add(user_message)
       await session.commit()

       # 3. Load conversation history
       history = await load_conversation_history(session, conversation.id, limit=50)

       # 4. Invoke agent
       user_context = {"user_id": current_user.id, "email": current_user.email}
       response = await invoke_agent(history, user_context)

       # 5. Persist agent response
       assistant_message = Message(
           conversation_id=conversation.id,
           role="assistant",
           content=response,
           timestamp=datetime.utcnow(),
       )
       session.add(assistant_message)
       await session.commit()

       return {"response": response}
   ```

**Validation:**
- Chat endpoint works
- Messages persisted to database
- Agent invoked correctly
- Responses returned to client

---

### Phase 5: Frontend Migration (2-3 days)

**Goal**: Replace Next.js frontend with ChatKit

**Tasks:**

1. Set up ChatKit project:
   ```bash
   npx create-chatkit-app frontend-chatkit
   cd frontend-chatkit
   npm install
   ```

2. Configure API endpoint:
   ```javascript
   // frontend-chatkit/src/config.js
   export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
   export const CHAT_ENDPOINT = `${API_BASE_URL}/api/chat`;
   ```

3. Implement authentication:
   ```javascript
   // frontend-chatkit/src/auth.js
   // Reuse existing Better Auth JWT tokens
   ```

4. Implement chat interface:
   ```javascript
   // frontend-chatkit/src/components/Chat.jsx
   // Use ChatKit components
   ```

**Validation:**
- ChatKit UI renders
- Authentication works
- Messages sent to backend
- Responses displayed

---

### Phase 6: Testing & Validation (2-3 days)

**Goal**: Comprehensive testing of Phase-III system

**Tasks:**

1. Unit tests for MCP tools
2. Integration tests for agent
3. End-to-end tests for chat flow
4. Authorization tests
5. Performance tests
6. User acceptance testing

**Validation:**
- All tests pass
- Performance acceptable
- Security verified
- User feedback positive

---

### Phase 7: Deployment & Cutover (1 day)

**Goal**: Deploy Phase-III and switch users over

**Tasks:**

1. Deploy Phase-III backend (alongside Phase-II)
2. Deploy ChatKit frontend
3. Update DNS/routing to point to ChatKit
4. Monitor for issues
5. Keep Phase-II running as fallback

**Validation:**
- Phase-III deployed successfully
- Users can access chat interface
- No critical issues
- Rollback plan ready

---

### Phase 8: Deprecation (Optional)

**Goal**: Remove Phase-II code after Phase-III proven stable

**Tasks:**

1. Monitor Phase-III for 1-2 weeks
2. Verify no users accessing Phase-II endpoints
3. Remove Phase-II frontend code
4. Mark Phase-II endpoints as deprecated
5. Eventually remove Phase-II endpoints

**Timeline**: 2-4 weeks after cutover

## Data Migration

### No Data Migration Required

**Good News**: Phase-III reuses existing User and Task tables, so no data migration is needed.

**What Gets Preserved:**
- ✅ All existing users
- ✅ All existing tasks
- ✅ All user-task relationships
- ✅ Authentication credentials

**What Gets Added:**
- New: Conversation table (starts empty)
- New: Message table (starts empty)

**Migration Script**: Not needed (schema extension only)

## Rollback Plan

### If Phase-III Has Issues

1. **Immediate Rollback** (< 5 minutes):
   - Switch DNS/routing back to Phase-II frontend
   - Phase-II backend still running
   - Zero data loss (Phase-III only added tables)

2. **Database Rollback** (if needed):
   ```bash
   # Rollback conversation/message tables
   alembic downgrade -1
   ```

3. **Code Rollback**:
   - Phase-II code still in repository
   - Can redeploy Phase-II if needed

## Testing Checklist

### Before Cutover

- [ ] All MCP tools have authorization tests
- [ ] Agent correctly interprets common user intents
- [ ] Chat endpoint persists messages correctly
- [ ] Conversation history loads correctly
- [ ] Agent handles tool errors gracefully
- [ ] Frontend displays messages correctly
- [ ] Authentication works end-to-end
- [ ] Performance is acceptable (<5s per message)
- [ ] Security audit passed
- [ ] Load testing completed

### After Cutover

- [ ] Monitor error rates
- [ ] Monitor response times
- [ ] Monitor user feedback
- [ ] Verify no Phase-II traffic
- [ ] Check database performance
- [ ] Verify conversation persistence

## Common Issues & Solutions

### Issue 1: Agent Selects Wrong Tool

**Symptom**: Agent calls wrong MCP tool for user intent

**Solution**:
- Improve system prompt with more examples
- Add intent recognition patterns
- Provide clearer tool descriptions

### Issue 2: Slow Response Times

**Symptom**: Chat responses take >10 seconds

**Solution**:
- Optimize conversation history query (add indexes)
- Limit conversation history (last 50 messages)
- Consider response streaming
- Check OpenAI API latency

### Issue 3: Authorization Failures

**Symptom**: Tools reject valid user requests

**Solution**:
- Verify user_context passed correctly
- Check JWT token validation
- Verify user_id in context matches database

### Issue 4: Conversation State Lost

**Symptom**: Agent doesn't remember previous messages

**Solution**:
- Verify messages persisted to database
- Check conversation history loading
- Verify conversation_id consistent

## Success Metrics

### Technical Metrics

- Response time: <5 seconds per message
- Uptime: >99.9%
- Error rate: <1%
- Authorization bypass: 0 incidents

### User Metrics

- User satisfaction: >80% positive
- Task completion rate: >90%
- Agent accuracy: >85% correct intent recognition

## References

- Constitution v2.0.0
- ADR-0001: Stateless Server Architecture
- ADR-0002: MCP Tool Integration
- CLAUDE.md: Phase-III Architecture Guidance
- Updated Templates (spec, plan, tasks)

## Support

For questions or issues during migration:
- Review ADRs for architectural decisions
- Check CLAUDE.md for implementation patterns
- Refer to constitution for principles
- Create GitHub issues for bugs
