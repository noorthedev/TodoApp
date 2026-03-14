# ADR-0002: MCP Tool Integration for Agent-Database Separation

**Status**: Accepted
**Date**: 2026-02-19
**Deciders**: Architecture Team
**Related**: Constitution v2.0.0, Phase-III Architecture, ADR-0001

## Context

Phase-III introduces an AI agent (OpenAI Agents SDK) that needs to interact with the database to perform task operations (create, read, update, delete, list). We need to decide how the agent accesses data while maintaining security, authorization, and separation of concerns.

### Problem Statement

AI agents need to perform data operations, but direct database access creates several problems:
- **Security Risk**: Agent could bypass authorization checks
- **Tight Coupling**: Agent code depends on database schema
- **Testing Difficulty**: Hard to test agent without database
- **Auditability**: Unclear what operations agent performed
- **Maintainability**: Database changes require agent code changes

### Requirements

1. **Security**: Enforce authorization on every data operation
2. **Separation**: Agent code independent of database implementation
3. **Auditability**: Track all agent actions
4. **Testability**: Test agent and data operations independently
5. **Discoverability**: Agent can discover available operations
6. **Structured I/O**: Clear contracts for inputs and outputs

## Decision

We will implement **MCP (Model Context Protocol) tools** as the exclusive interface between the AI agent and the database:

1. **Tool-Driven Architecture**: All data operations implemented as MCP tools
2. **Agent-Database Separation**: Agent never imports database models or ORM
3. **Authorization in Tools**: Every tool validates user ownership
4. **Structured Responses**: Tools return `{"success": bool, "data": dict}` or `{"success": bool, "error": str}`
5. **User Context Passing**: Tools receive `user_context: dict` with authenticated user info
6. **No Exceptions to Agent**: Tools catch all exceptions and return structured errors

### Architecture Pattern

```
User Request → Backend → Agent → MCP Tools → Database
                  ↓                    ↓
              JWT Auth          Authorization
              Extract user      Verify ownership
              Pass context      Return structured response
```

### Tool Implementation Standard

```python
@mcp_tool
async def tool_name(
    # Business parameters
    param1: Type,
    param2: Type,
    # Infrastructure (automatically provided)
    user_context: dict,  # {"user_id": int, "email": str}
    session: AsyncSession,
) -> dict:
    """Tool description for agent discovery."""
    user_id = user_context["user_id"]

    try:
        # 1. Validate inputs (Pydantic handles this)
        # 2. Check authorization
        # 3. Perform database operation
        # 4. Return structured response
        return {"success": True, "data": result}
    except ValidationError as e:
        return {"success": False, "error": f"Validation failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Tool error: {str(e)}", exc_info=True)
        return {"success": False, "error": "Internal error occurred"}
```

## Consequences

### Positive

1. **Security**: Authorization enforced at tool boundary, agent cannot bypass
2. **Separation**: Agent code independent of database schema
3. **Testability**: Can test tools and agent independently
4. **Auditability**: All agent actions logged at tool level
5. **Discoverability**: Agent can query tool catalog
6. **Maintainability**: Database changes isolated to tools
7. **Consistency**: Same authorization pattern across all tools
8. **Error Handling**: Structured errors prevent agent crashes

### Negative

1. **Indirection**: Extra layer between agent and database
2. **Boilerplate**: Each operation requires tool implementation
3. **Performance**: Function call overhead (~1-2ms per tool call)
4. **Learning Curve**: Developers must understand MCP protocol

### Mitigations

1. **Tool Templates**: Provide standard patterns to reduce boilerplate
2. **Code Generation**: Consider tool scaffolding scripts
3. **Documentation**: Comprehensive examples in CLAUDE.md and templates
4. **Performance**: Overhead negligible compared to OpenAI API latency (1-5s)

## Alternatives Considered

### Alternative 1: Direct Database Access from Agent

**Approach**: Agent imports SQLModel models and queries database directly

```python
# Agent code
from src.models.task import Task
from sqlalchemy import select

async def agent_logic(user_id: int, session: AsyncSession):
    result = await session.execute(
        select(Task).where(Task.user_id == user_id)
    )
    tasks = result.scalars().all()
```

**Pros**:
- Simplest implementation
- No extra layer
- Direct access

**Cons**:
- ❌ Agent can bypass authorization
- ❌ Tight coupling to database schema
- ❌ Hard to test agent without database
- ❌ No audit trail of agent actions
- ❌ Violates separation of concerns principle
- ❌ Security risk (agent has full database access)

**Rejected**: Fundamentally violates security and separation principles.

### Alternative 2: Service Layer Pattern

**Approach**: Create service classes that agent calls

```python
# Service layer
class TaskService:
    async def create_task(self, user_id: int, title: str, session: AsyncSession):
        task = Task(user_id=user_id, title=title)
        session.add(task)
        await session.commit()
        return task

# Agent calls service
task = await task_service.create_task(user_id, title, session)
```

**Pros**:
- Familiar pattern
- Reusable services
- Separation from database

**Cons**:
- ❌ Not discoverable by agent (agent must know service methods)
- ❌ No standard input/output format
- ❌ Exception handling inconsistent
- ❌ Not compatible with OpenAI function calling
- ❌ Harder to audit (no tool call logs)

**Rejected**: Doesn't integrate well with OpenAI Agents SDK function calling mechanism.

### Alternative 3: GraphQL API

**Approach**: Agent calls GraphQL API for data operations

**Pros**:
- Standard query language
- Flexible queries
- Well-defined schema

**Cons**:
- ❌ Over-engineered for internal agent-database communication
- ❌ Additional complexity (GraphQL server, schema, resolvers)
- ❌ Network overhead (HTTP calls)
- ❌ Not designed for function calling pattern
- ❌ Harder to pass user context securely

**Rejected**: Too complex for internal communication; MCP is purpose-built for agent-tool interaction.

### Alternative 4: REST API Endpoints

**Approach**: Agent calls internal REST API endpoints

**Pros**:
- Standard HTTP protocol
- Well-understood pattern

**Cons**:
- ❌ Network overhead (HTTP calls within same process)
- ❌ Serialization/deserialization overhead
- ❌ Not designed for function calling
- ❌ Harder to pass user context
- ❌ More complex than direct function calls

**Rejected**: Unnecessary network layer for in-process communication.

## Implementation Details

### Tool Catalog

Phase-III requires these core MCP tools:

| Tool Name | Purpose | Authorization |
|-----------|---------|---------------|
| `create_task` | Create new task | Force user_id from context |
| `list_tasks` | List user's tasks | Filter by user_id from context |
| `update_task` | Update existing task | Verify task.user_id == context.user_id |
| `delete_task` | Delete task | Verify task.user_id == context.user_id |
| `get_task` | Get single task | Verify task.user_id == context.user_id |

### Tool Registration

```python
# backend/src/tools/registry.py
from src.tools.task_tools import create_task, list_tasks, update_task, delete_task, get_task

MCP_TOOL_CATALOG = [
    create_task,
    list_tasks,
    update_task,
    delete_task,
    get_task,
]

def get_tool_catalog():
    """Return all available MCP tools for agent."""
    return MCP_TOOL_CATALOG
```

### Agent Integration

```python
# backend/src/agent/agent.py
from openai import OpenAI
from src.tools.registry import get_tool_catalog

def create_agent():
    """Create OpenAI agent with MCP tools."""
    tools = get_tool_catalog()

    agent = OpenAI.Agent(
        model="gpt-4",
        tools=tools,  # Register MCP tools
        system_prompt=get_system_prompt(),
    )

    return agent

async def invoke_agent(history, user_context):
    """Invoke agent with conversation history and user context."""
    agent = create_agent()

    # Agent calls tools with user_context automatically passed
    response = await agent.run(
        messages=history,
        context=user_context,  # Passed to all tool calls
    )

    return response
```

### Authorization Pattern

Every tool follows this pattern:

```python
@mcp_tool
async def update_task(
    task_id: int,
    title: Optional[str] = None,
    completed: Optional[bool] = None,
    user_context: dict = None,
    session: AsyncSession = None,
) -> dict:
    """Update an existing task."""
    user_id = user_context["user_id"]

    # Fetch task
    task = await session.get(Task, task_id)
    if not task:
        return {"success": False, "error": "Task not found"}

    # CRITICAL: Verify ownership
    if task.user_id != user_id:
        logger.warning(f"Authorization failed: user {user_id} attempted to update task {task_id}")
        return {"success": False, "error": "Not authorized"}

    # Update task
    if title is not None:
        task.title = title
    if completed is not None:
        task.completed = completed

    await session.commit()
    return {"success": True, "task": task.dict()}
```

## Security Guarantees

1. **No Bypass**: Agent cannot access database without going through tools
2. **Consistent Authorization**: All tools use same authorization pattern
3. **User Context Required**: Tools fail if user_context missing
4. **Ownership Verification**: Every operation verifies user owns resource
5. **Audit Trail**: All tool calls logged with user_id and parameters
6. **Structured Errors**: No exception leakage to agent

## Testing Strategy

### Tool Testing (Unit Tests)

```python
async def test_update_task_authorization():
    """Test that update_task rejects cross-user access."""
    # User 1 creates task
    task = await create_task(
        title="Test",
        user_context={"user_id": 1},
        session=session,
    )

    # User 2 tries to update (should fail)
    result = await update_task(
        task_id=task["data"]["id"],
        title="Hacked",
        user_context={"user_id": 2},
        session=session,
    )

    assert result["success"] is False
    assert "Not authorized" in result["error"]
```

### Agent Testing (Integration Tests)

```python
async def test_agent_creates_task():
    """Test that agent correctly uses create_task tool."""
    user_context = {"user_id": 1, "email": "test@example.com"}

    response = await invoke_agent(
        history=[{"role": "user", "content": "Add a task to buy groceries"}],
        user_context=user_context,
    )

    # Verify agent called create_task tool
    assert "groceries" in response.lower()

    # Verify task was created with correct user_id
    tasks = await list_tasks(user_context=user_context, session=session)
    assert len(tasks["data"]) == 1
    assert tasks["data"][0]["user_id"] == 1
```

## Performance Impact

- Tool call overhead: ~1-2ms per call
- Authorization check: ~1-2ms per call
- Total overhead: ~2-4ms per operation
- OpenAI API latency: 1000-5000ms (dominates)

**Conclusion**: MCP tool overhead is <0.5% of total request latency, negligible.

## Success Metrics

1. **Security**: Zero authorization bypass incidents
2. **Maintainability**: Database schema changes don't require agent code changes
3. **Testability**: 100% tool test coverage, agent tests independent of database
4. **Auditability**: All agent actions logged with user_id and parameters

## References

- Constitution v2.0.0: Principle III (Tool-Driven Execution), Principle IV (Agent-Database Separation)
- CLAUDE.md: MCP Tool Standards, Authorization Patterns
- ADR-0001: Stateless Server Architecture
- Official MCP SDK Documentation
