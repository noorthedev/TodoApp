# Implementation Plan: MCP Server & Task Tools Integration

**Branch**: `005-mcp-task-tools` | **Date**: 2026-02-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-mcp-task-tools/spec.md`

## Summary

Build MCP server with 5 task management tools (add_task, list_tasks, complete_task, delete_task, update_task) that integrate with OpenAI Agents SDK to enable natural language task management. The system maintains stateless architecture with all state persisted to Neon PostgreSQL database. MCP tools enforce per-user authorization and return structured responses. Agent interprets user intent and calls appropriate tools without direct database access.

**Technical Approach**: Implement MCP server as part of FastAPI backend using Official MCP SDK. Create tool registry with Pydantic schemas for input validation. Integrate OpenAI Agents SDK to consume MCP tools via function calling. Build chat endpoint that orchestrates agent invocation, conversation persistence, and user context passing. Reuse existing Task model and authentication infrastructure from Phase-II.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.109+, SQLModel 0.0.14+, Official MCP SDK (latest), OpenAI Agents SDK (latest), asyncpg 0.29+, pydantic 2.5+, python-jose 3.3+ (JWT)
**Storage**: Neon Serverless PostgreSQL (async connection via asyncpg)
**Testing**: pytest with async support, pytest-asyncio
**Target Platform**: Linux/Windows server (FastAPI backend)
**Project Type**: Web application (backend API + frontend chat UI)
**Performance Goals**: <2 seconds per task operation, <10ms authorization checks, support 100 concurrent users
**Constraints**: Stateless architecture (no in-memory state), tool-driven execution (agent never accesses DB directly), per-user data isolation
**Scale/Scope**: 5 MCP tools, 1 chat endpoint, 2 new database models (Conversation, Message), integration with existing Task model and auth system

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Initial Evaluation (Pre-Research)

All principles passed initial evaluation. Proceeding to Phase 0 Research.

### Final Evaluation (Post-Design)

*Re-evaluated after completing research.md, data-model.md, contracts/, and quickstart.md*

### Principle I: Stateless Server Architecture ✅ PASS

**Requirements:**
- ✅ No in-memory conversation history or chat state
- ✅ All messages persisted to database before processing
- ✅ Agent interactions are stateless (each request is independent)
- ✅ Server can be restarted without losing conversation context
- ✅ Multiple server instances can handle requests for the same user
- ✅ Database is the single source of truth for all state

**Evidence from Design Artifacts:**
- **data-model.md**: Conversation and Message models defined with database persistence (lines 65-177)
- **data-model.md**: Data access pattern `get_or_create_conversation` loads from DB per request (lines 272-297)
- **data-model.md**: Data access pattern `load_conversation_history` retrieves messages from DB (lines 299-318)
- **chat-api.json**: Execution flow Step 3-4 loads conversation and history from database (steps 3-4)
- **chat-api.json**: Stateless guarantees documented: "No in-memory conversation state - all state persisted to database" (stateless_guarantees section)
- **quickstart.md**: Pattern examples show database queries for conversation state (lines 280-320)

**Compliance**: ✅ VERIFIED - All conversation state persisted to database. No in-memory state. Agent receives fresh context per request.

### Principle II: Security-First Design ✅ PASS

**Requirements:**
- ✅ JWT-based authentication using Better Auth (existing)
- ✅ All protected routes require valid token verification
- ✅ User data must be strictly isolated per user
- ✅ Input validation on all API endpoints and MCP tools
- ✅ MCP tools must validate user ownership before operations
- ✅ Agent must not bypass authorization checks

**Evidence from Design Artifacts:**
- **mcp-tools.json**: All 5 tools require user_context parameter with user_id (lines 24-36, 100-111, 191-202, 265-276, 347-358)
- **mcp-tools.json**: Authorization requirements documented for each tool (lines 92, 179, 253, 324, 411)
- **mcp-tools.json**: add_task authorization: "Tool MUST extract user_id from user_context and force it on created task" (line 92)
- **mcp-tools.json**: list_tasks authorization: "Tool MUST filter tasks by user_id from user_context" (line 179)
- **mcp-tools.json**: complete_task authorization: "Tool MUST verify task.user_id matches user_context['user_id']" (line 253)
- **chat-api.json**: Authentication required via JWT Bearer token (request.headers.Authorization)
- **chat-api.json**: Authorization rules documented: "user_context MUST be extracted from validated JWT token" (authorization section)
- **quickstart.md**: Security checklist includes JWT validation and user_context passing (lines 350-357)

**Compliance**: ✅ VERIFIED - JWT authentication enforced. All tools validate user_id. Per-user data isolation guaranteed.

### Principle III: Tool-Driven Execution Pattern ✅ PASS

**Requirements:**
- ✅ All CRUD operations on tasks implemented as MCP tools
- ✅ Tools have strict input/output schemas (Pydantic models)
- ✅ Agent calls tools with structured parameters
- ✅ Tools enforce authorization and validation
- ✅ Tools return structured responses (success/error)
- ✅ No direct database access from agent code
- ✅ Tool implementations are testable independently

**Evidence from Design Artifacts:**
- **mcp-tools.json**: 5 tools defined with complete input/output schemas (add_task, list_tasks, complete_task, delete_task, update_task)
- **mcp-tools.json**: Input schemas with type validation and constraints (e.g., title: minLength 1, maxLength 200)
- **mcp-tools.json**: Output schemas with oneOf success/error structure (lines 44-91, 120-177, etc.)
- **research.md**: Decision to use Official MCP SDK for tool implementation (lines 11-28)
- **research.md**: Structured responses strategy: {"success": True, "data": {...}} or {"success": False, "error": "..."} (lines 140-143)
- **quickstart.md**: Tool structure pattern documented with @mcp_tool decorator (lines 60-95)
- **quickstart.md**: Example add_task tool implementation shows structured response (lines 97-140)

**Compliance**: ✅ VERIFIED - All 5 CRUD operations implemented as MCP tools with strict schemas and structured responses.

### Principle IV: Agent-Database Separation ✅ PASS

**Requirements:**
- ✅ Agent code has no database connection or ORM imports
- ✅ All database operations encapsulated in MCP tools
- ✅ Tools enforce per-user data isolation
- ✅ Tools validate all inputs before database operations
- ✅ Agent receives only structured tool responses

**Evidence from Design Artifacts:**
- **research.md**: Decision Q2 - "MCP tools as part of FastAPI application" with clear separation (lines 31-51)
- **research.md**: Decision Q5 - "user_context dict parameter automatically injected by chat endpoint" (lines 100-121)
- **chat-api.json**: Execution flow shows agent receives user_context but not database session (step 6)
- **chat-api.json**: Step 7 "Invoke Agent" shows agent calls tools, not database (step 7)
- **quickstart.md**: Project structure shows agent/ and tools/ as separate modules (lines 40-52)
- **quickstart.md**: Agent invocation code shows no database imports, only tool catalog (lines 160-210)
- **quickstart.md**: Tools receive session parameter, agent does not (lines 60-95)

**Compliance**: ✅ VERIFIED - Agent module separate from database. All DB operations in tools. Agent only receives tool responses.

### Principle V: Database as Single Source of Truth ✅ PASS

**Requirements:**
- ✅ All conversations stored in database with user_id
- ✅ All messages (user and assistant) persisted immediately
- ✅ Task operations persist before returning success
- ✅ No caching of critical state in memory
- ✅ Database transactions ensure consistency

**Evidence from Design Artifacts:**
- **data-model.md**: Conversation model with user_id foreign key (lines 65-118)
- **data-model.md**: Message model with conversation_id foreign key (lines 120-177)
- **data-model.md**: Foreign key constraints with CASCADE DELETE ensure integrity (lines 386-392)
- **data-model.md**: Data access pattern `persist_message` commits immediately (lines 320-345)
- **chat-api.json**: Execution flow Step 5 persists user message BEFORE agent invocation (step 5)
- **chat-api.json**: Execution flow Step 8 persists agent response AFTER invocation (step 8)
- **chat-api.json**: Step 9 updates conversation timestamp after message persistence (step 9)
- **quickstart.md**: Pattern 3 shows immediate commit after message creation (lines 310-330)
- **quickstart.md**: Tool example shows commit before returning success (lines 120-135)

**Compliance**: ✅ VERIFIED - All state persisted to database immediately. Database transactions ensure consistency. No in-memory caching.

**GATE RESULT**: ✅ ALL CHECKS PASSED - Design artifacts fully comply with all 5 constitution principles. Ready for task breakdown (/sp.tasks).

## Project Structure

### Documentation (this feature)

```text
specs/005-mcp-task-tools/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── mcp-tools.json   # MCP tool schemas
│   └── chat-api.json    # Chat endpoint contract
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── agent/                    # NEW: OpenAI Agent integration
│   │   ├── __init__.py
│   │   ├── agent.py              # Agent initialization and invocation
│   │   ├── config.py             # Agent configuration (model, temperature)
│   │   └── prompts.py            # System prompts for agent behavior
│   ├── tools/                    # NEW: MCP tools implementation
│   │   ├── __init__.py
│   │   ├── registry.py           # Tool catalog and registration
│   │   ├── task_tools.py         # 5 task management tools
│   │   └── utils.py              # Tool decorators and helpers
│   ├── api/
│   │   ├── auth.py               # EXISTING: Authentication endpoints
│   │   ├── tasks.py              # EXISTING: Phase-II CRUD endpoints (keep for now)
│   │   ├── chat.py               # NEW: Chat endpoint for agent interaction
│   │   └── __init__.py
│   ├── models/
│   │   ├── user.py               # EXISTING: User model
│   │   ├── task.py               # EXISTING: Task model (reuse)
│   │   ├── conversation.py       # NEW: Conversation model
│   │   ├── message.py            # NEW: Message model
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── auth.py               # EXISTING: Auth schemas
│   │   ├── task.py               # EXISTING: Task schemas
│   │   ├── chat.py               # NEW: Chat request/response schemas
│   │   └── __init__.py
│   ├── utils/
│   │   ├── jwt.py                # EXISTING: JWT utilities (reuse)
│   │   ├── security.py           # EXISTING: Security utilities
│   │   └── __init__.py
│   ├── middleware/
│   │   ├── error_handler.py      # EXISTING: Error handling
│   │   └── __init__.py
│   ├── config.py                 # EXISTING: Configuration (add OpenAI API key)
│   ├── database.py               # EXISTING: Database connection
│   └── main.py                   # EXISTING: FastAPI app (add chat router)
├── tests/
│   ├── tools/                    # NEW: MCP tool tests
│   │   ├── test_add_task.py
│   │   ├── test_list_tasks.py
│   │   ├── test_complete_task.py
│   │   ├── test_delete_task.py
│   │   └── test_update_task.py
│   ├── agent/                    # NEW: Agent integration tests
│   │   ├── test_intent_recognition.py
│   │   └── test_tool_selection.py
│   ├── api/
│   │   ├── test_auth.py          # EXISTING
│   │   ├── test_tasks.py         # EXISTING
│   │   └── test_chat.py          # NEW: Chat endpoint tests
│   └── conftest.py               # EXISTING: Test fixtures
├── requirements.txt              # UPDATE: Add openai, mcp-sdk
└── .env                          # UPDATE: Add OPENAI_API_KEY

frontend/
├── src/
│   ├── app/                      # EXISTING: Next.js App Router
│   ├── components/               # EXISTING: React components
│   └── lib/                      # EXISTING: Utilities
└── [existing frontend structure - no changes for this feature]
```

**Structure Decision**: Web application structure (Option 2). Backend contains MCP tools, agent integration, and chat endpoint. Frontend remains Next.js for now (ChatKit migration is separate feature). New directories: `backend/src/agent/` for OpenAI Agent, `backend/src/tools/` for MCP tools, `backend/src/models/conversation.py` and `message.py` for conversation persistence.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - all constitution checks passed.

## MCP Tool Architecture

### Tool Catalog

| Tool Name | Purpose | Input Parameters | Authorization Check |
|-----------|---------|------------------|---------------------|
| add_task | Create new task | title (str), description (str, optional) | Force user_id from user_context |
| list_tasks | Retrieve all user's tasks | None | Filter by user_id from user_context |
| complete_task | Mark task as done | task_id (int) | Verify task.user_id == user_context["user_id"] |
| delete_task | Remove task | task_id (int) | Verify task.user_id == user_context["user_id"] |
| update_task | Modify task details | task_id (int), title (str, optional), description (str, optional) | Verify task.user_id == user_context["user_id"] |

### Tool Design Decisions

**Decision 1: Tool Granularity**
- **Options Considered**:
  - Single tool for all operations (e.g., manage_task with action parameter)
  - Separate tools per operation (add_task, list_tasks, etc.)
- **Choice**: Separate tools per operation
- **Rationale**: Better discoverability for agent (clear tool names), simpler schemas (fewer conditional parameters), easier to test independently, aligns with single responsibility principle

**Decision 2: Error Handling Strategy**
- **Options Considered**:
  - Raise exceptions from tools (let FastAPI handle)
  - Return structured responses with success/error fields
- **Choice**: Return structured responses
- **Rationale**: Agent can handle errors gracefully without crashing, consistent response format across all tools, enables agent to retry or provide user-friendly messages, prevents exception propagation to agent

**Decision 3: Authorization Enforcement**
- **Options Considered**:
  - Middleware-based authorization (check before tool invocation)
  - Per-tool validation (each tool checks user_context)
- **Choice**: Per-tool validation
- **Rationale**: Explicit authorization in each tool (fail-secure), easier to audit (authorization logic visible in tool code), no hidden middleware magic, consistent with constitution principle of tool-level security

**Decision 4: Tool Response Format**
- **Options Considered**:
  - Simple return values (e.g., return task object directly)
  - Structured responses with success/error wrapper
- **Choice**: Structured responses {"success": bool, "data": dict} or {"success": bool, "error": str}
- **Rationale**: Agent can distinguish success from failure without parsing exceptions, consistent format across all tools, enables structured error messages, supports future extensions (warnings, metadata)

### Tool Implementation Pattern

```python
# Standard pattern for all MCP tools in this feature
from functools import wraps
import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Tool decorator for consistent error handling
def mcp_tool(func):
    """Decorator for MCP tools with error handling."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Tool error in {func.__name__}: {str(e)}", exc_info=True)
            return {"success": False, "error": "Internal error occurred"}
    return wrapper

# Example tool implementation
@mcp_tool
async def add_task(
    title: str,
    description: str = "",
    user_context: Dict[str, Any] = None,
    session: AsyncSession = None,
) -> Dict[str, Any]:
    """
    Create a new task for the authenticated user.

    Args:
        title: Task title (1-200 characters)
        description: Optional task description (max 1000 characters)
        user_context: Authenticated user context (user_id, email)
        session: Database session

    Returns:
        {"success": True, "data": {...}} or {"success": False, "error": "..."}
    """
    # 1. Validate user_context
    if not user_context or "user_id" not in user_context:
        return {"success": False, "error": "User context missing"}

    user_id = user_context["user_id"]

    # 2. Validate inputs (Pydantic handles this at schema level)
    if not title or len(title) > 200:
        return {"success": False, "error": "Invalid title length"}

    # 3. Create task with forced user_id
    new_task = Task(
        user_id=user_id,  # CRITICAL: Force from context, never trust input
        title=title,
        description=description,
        is_completed=False,
    )

    # 4. Persist to database
    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    # 5. Return structured response
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
```

### Tool Authorization Matrix

| Tool | Resource Type | Authorization Rule | Failure Response |
|------|---------------|-------------------|------------------|
| add_task | Task | Force user_id from user_context | {"success": false, "error": "User context missing"} |
| list_tasks | Task | Filter by user_id from user_context | {"success": true, "data": {"tasks": [], "count": 0}} |
| complete_task | Task | Verify task.user_id == user_context["user_id"] | {"success": false, "error": "Not authorized"} |
| delete_task | Task | Verify task.user_id == user_context["user_id"] | {"success": false, "error": "Not authorized"} |
| update_task | Task | Verify task.user_id == user_context["user_id"] | {"success": false, "error": "Not authorized"} |

## Agent Integration Planning

### Agent Configuration

**Agent Type**: OpenAI Agents SDK with function calling

**System Prompt Design**:
```
You are a helpful task management assistant. You help users manage their tasks through natural conversation.

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

Available tools: add_task, list_tasks, complete_task, delete_task, update_task
```

**Tool Registration**:
- Tool 1: add_task - When user wants to create, add, or remember something
- Tool 2: list_tasks - When user wants to see, view, or check their tasks
- Tool 3: complete_task - When user indicates a task is done, finished, or complete
- Tool 4: delete_task - When user wants to delete, remove, or discard a task
- Tool 5: update_task - When user wants to change, edit, or update task details

### Intent Recognition Strategy

**Primary Intents**:

1. **Create Task Intent**:
   - Trigger phrases: "Add a task", "Create task", "I need to", "Remind me to"
   - Required information: Task title
   - Tool to call: add_task
   - Response pattern: "I've added '[title]' to your task list."

2. **List Tasks Intent**:
   - Trigger phrases: "Show my tasks", "What tasks do I have", "List tasks"
   - Required information: None
   - Tool to call: list_tasks
   - Response pattern: "You have [count] tasks: [list]"

3. **Complete Task Intent**:
   - Trigger phrases: "Mark [task] as done", "Complete [task]", "[task] is finished"
   - Required information: Task identifier (title or ID)
   - Tool to call: complete_task
   - Response pattern: "Great! I've marked '[title]' as complete."

4. **Delete Task Intent**:
   - Trigger phrases: "Delete [task]", "Remove [task]", "Get rid of [task]"
   - Required information: Task identifier (title or ID)
   - Tool to call: delete_task
   - Response pattern: "I've deleted '[title]' from your list."

5. **Update Task Intent**:
   - Trigger phrases: "Change [task] to [new title]", "Update [task]", "Rename [task]"
   - Required information: Task identifier and new title/description
   - Tool to call: update_task
   - Response pattern: "I've updated your task from '[old]' to '[new]'."

**Ambiguity Handling**:
- When user says "Delete the task" with multiple tasks: Ask "Which task would you like to delete? You have: [list]"
- When user says "Add a task" without title: Ask "What would you like to add to your task list?"
- When task not found: Respond "I couldn't find that task. Could you be more specific?"

### Context Management Strategy

**Conversation State**:
- **Persisted to Database**: All messages (user and assistant) with timestamps, conversation_id, user_id
- **Loaded per Request**: Last 50 messages from database (for context window management)
- **User Context**: user_id, email passed to all tool calls automatically

**Context Window Management**:
- **Max Messages**: 50 messages or 4000 tokens (whichever is smaller)
- **Truncation Strategy**: Keep system prompt + last N messages that fit in token limit
- **Context Reset**: Start new conversation after 24 hours of inactivity (optional)

**Stateless Guarantee**:
- Agent has NO memory between requests
- All context loaded from database each time
- Server restart does not affect conversation continuity
- Multiple server instances can handle same user

### Agent Error Handling

**Tool Error Scenarios**:

1. **Tool returns validation error**:
   - Agent behavior: Extract error message, rephrase in user-friendly terms, ask for correction
   - Example: Tool returns {"success": false, "error": "Invalid title length"} → Agent says "That title is too long. Please keep it under 200 characters."

2. **Tool returns authorization error**:
   - Agent behavior: Inform user they don't have access without exposing technical details
   - Example: Tool returns {"success": false, "error": "Not authorized"} → Agent says "You don't have permission to access that task."

3. **Tool returns not found error**:
   - Agent behavior: Inform user resource doesn't exist, suggest alternatives
   - Example: Tool returns {"success": false, "error": "Task not found"} → Agent says "I couldn't find that task. Would you like to see all your tasks?"

4. **Tool returns internal error**:
   - Agent behavior: Apologize and suggest trying again, don't expose technical details
   - Example: Tool returns {"success": false, "error": "Internal error occurred"} → Agent says "Something went wrong. Please try again."

**Agent Failure Scenarios**:

1. **Agent can't determine intent**: Fallback to asking clarifying questions
2. **Agent selects wrong tool**: Tool will return error, agent should try different tool or ask for clarification
3. **Agent exceeds token limit**: Truncate conversation history, keep only recent messages

## Stateless Architecture Considerations

### State Persistence Strategy

**What Gets Persisted**:
- User messages (immediately upon receipt, before agent invocation)
- Agent responses (immediately after generation, before returning to user)
- Tool call results (for debugging/auditing - optional)
- Conversation metadata (created_at, updated_at, user_id)

**Persistence Timing**:
- User message: BEFORE agent invocation (ensures no data loss if agent fails)
- Agent response: AFTER agent completes, BEFORE returning to user
- Database transactions: Committed immediately (no buffering)

**State Reconstruction**:
- On each request, load conversation history from database
- Pass history to agent as fresh context
- Agent processes with no prior memory

### Horizontal Scaling Readiness

**Stateless Guarantees**:
- ✅ No in-memory conversation state
- ✅ No session affinity required
- ✅ Any server instance can handle any request
- ✅ Server restart safe (all state in database)

**Shared Resources**:
- Database: Neon PostgreSQL (shared across instances)
- OpenAI API: Stateless (no server-side state)
- MCP Tools: Stateless (receive context per call)

### Performance Considerations

**Database Query Optimization**:
- Index on `conversation.user_id` for fast filtering
- Index on `message.conversation_id` for history loading
- Index on `task.user_id` for task filtering (already exists)
- Limit conversation history queries (last 50 messages)

**Agent Invocation Optimization**:
- Cache system prompts (static, reusable)
- Reuse agent configuration (stateless but reusable)
- Stream responses when possible (better UX)

**Expected Latency**:
- Message persistence: <10ms
- History loading: <50ms
- Agent processing: 1-5s (depends on OpenAI API)
- Tool execution: <100ms per tool
- Total request: 1-5s (dominated by agent)

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

## MCP Tool Architecture *(include if feature involves MCP tools)*

<!--
  ACTION REQUIRED: For Phase-III features that require AI agent interaction with data,
  design the MCP tool architecture here. Define which tools are needed, their responsibilities,
  and how they enforce authorization.
-->

### Tool Catalog

| Tool Name | Purpose | Input Parameters | Authorization Check |
|-----------|---------|------------------|---------------------|
| [tool_name] | [What it does] | [param1, param2, ...] | [How it verifies user ownership] |
| [tool_name] | [What it does] | [param1, param2, ...] | [How it verifies user ownership] |

### Tool Design Decisions

**Decision 1: Tool Granularity**
- **Options Considered**: [e.g., Single tool for all operations vs. separate tools per operation]
- **Choice**: [Selected approach]
- **Rationale**: [Why this approach, considering discoverability, maintainability, security]

**Decision 2: Error Handling Strategy**
- **Options Considered**: [e.g., Exceptions vs. structured responses]
- **Choice**: [Selected approach]
- **Rationale**: [Why this approach, considering agent behavior, debugging, user experience]

**Decision 3: Authorization Enforcement**
- **Options Considered**: [e.g., Middleware vs. per-tool validation]
- **Choice**: [Selected approach]
- **Rationale**: [Why this approach, considering security, consistency, performance]

### Tool Implementation Pattern

```python
# Standard pattern for all MCP tools in this feature
@mcp_tool
async def tool_name(
    # Business parameters
    param1: Type,
    param2: Type,
    # Required infrastructure
    user_context: dict,  # Contains user_id, email
    session: AsyncSession,
) -> dict:
    """
    [Tool description]

    Args:
        param1: [Description]
        param2: [Description]
        user_context: Authenticated user context
        session: Database session

    Returns:
        {"success": bool, "data": dict} or {"success": bool, "error": str}
    """
    user_id = user_context["user_id"]

    try:
        # 1. Validate inputs
        # 2. Check authorization (user ownership)
        # 3. Perform operation
        # 4. Return structured response

        return {"success": True, "data": result}
    except ValidationError as e:
        return {"success": False, "error": f"Validation failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Tool error: {str(e)}", exc_info=True)
        return {"success": False, "error": "Internal error occurred"}
```

### Tool Authorization Matrix

| Tool | Resource Type | Authorization Rule | Failure Response |
|------|---------------|-------------------|------------------|
| [tool_name] | [Resource] | [user_id must match resource.user_id] | [{"success": false, "error": "Not authorized"}] |
| [tool_name] | [Resource] | [Filter by user_id] | [Empty list if no access] |

## Agent Integration Planning *(include if feature involves AI agent)*

<!--
  ACTION REQUIRED: Plan how the OpenAI Agent will integrate with this feature.
  Define agent configuration, system prompts, tool registration, and context management.
-->

### Agent Configuration

**Agent Type**: [e.g., OpenAI Agents SDK with function calling]

**System Prompt Design**:
```
You are a helpful task management assistant. You help users manage their tasks through natural conversation.

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

Available tools: [list of MCP tools]
```

**Tool Registration**:
- Tool 1: [tool_name] - [When agent should use it]
- Tool 2: [tool_name] - [When agent should use it]
- Tool 3: [tool_name] - [When agent should use it]

### Intent Recognition Strategy

**Primary Intents**:
1. **[Intent Name]**: [Description]
   - Trigger phrases: [Examples]
   - Required information: [What agent needs to extract]
   - Tool to call: [tool_name]
   - Response pattern: [How agent should respond]

2. **[Intent Name]**: [Description]
   - Trigger phrases: [Examples]
   - Required information: [What agent needs to extract]
   - Tool to call: [tool_name]
   - Response pattern: [How agent should respond]

**Ambiguity Handling**:
- When [scenario], agent should [behavior]
- When [scenario], agent should [behavior]

### Context Management Strategy

**Conversation State**:
- **Persisted to Database**: All messages (user and assistant) with timestamps
- **Loaded per Request**: Last N messages from database (for context window)
- **User Context**: user_id, email passed to all tool calls

**Context Window Management**:
- **Max Messages**: [e.g., 50 messages or 4000 tokens]
- **Truncation Strategy**: [e.g., Keep system prompt + last N messages]
- **Context Reset**: [When to start fresh conversation]

**Stateless Guarantee**:
- Agent has NO memory between requests
- All context loaded from database each time
- Server restart does not affect conversation continuity

### Agent Error Handling

**Tool Error Scenarios**:
1. **Tool returns validation error**: Agent should [behavior, e.g., "Ask user for correct input"]
2. **Tool returns authorization error**: Agent should [behavior, e.g., "Inform user they don't have access"]
3. **Tool returns not found error**: Agent should [behavior, e.g., "Inform user resource doesn't exist"]
4. **Tool returns internal error**: Agent should [behavior, e.g., "Apologize and suggest trying again"]

**Agent Failure Scenarios**:
1. **Agent can't determine intent**: [Fallback behavior]
2. **Agent selects wrong tool**: [Recovery strategy]
3. **Agent exceeds token limit**: [Truncation strategy]

## Stateless Architecture Considerations *(mandatory for Phase-III)*

<!--
  ACTION REQUIRED: Document how this feature maintains stateless architecture.
  All conversation state must be persisted to database immediately.
-->

### State Persistence Strategy

**What Gets Persisted**:
- User messages (immediately upon receipt)
- Agent responses (immediately after generation)
- Tool call results (for debugging/auditing)
- Conversation metadata (created_at, updated_at, user_id)

**Persistence Timing**:
- User message: BEFORE agent invocation
- Agent response: AFTER agent completes, BEFORE returning to user
- Database transactions: Committed immediately (no buffering)

**State Reconstruction**:
- On each request, load conversation history from database
- Pass history to agent as fresh context
- Agent processes with no prior memory

### Horizontal Scaling Readiness

**Stateless Guarantees**:
- ✅ No in-memory conversation state
- ✅ No session affinity required
- ✅ Any server instance can handle any request
- ✅ Server restart safe (all state in database)

**Shared Resources**:
- Database: Neon PostgreSQL (shared across instances)
- OpenAI API: Stateless (no server-side state)
- MCP Tools: Stateless (receive context per call)

### Performance Considerations

**Database Query Optimization**:
- Index on `conversation.user_id` for fast filtering
- Index on `message.conversation_id` for history loading
- Limit conversation history queries (e.g., last 50 messages)

**Agent Invocation Optimization**:
- Cache system prompts (static)
- Reuse agent configuration (stateless but reusable)
- Stream responses when possible (better UX)

**Expected Latency**:
- Message persistence: <10ms
- History loading: <50ms
- Agent processing: 1-5s (depends on OpenAI API)
- Total request: 1-5s (dominated by agent)
