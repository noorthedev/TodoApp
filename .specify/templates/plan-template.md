# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]  
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]  
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]  
**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]  
**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]
**Project Type**: [single/web/mobile - determines source structure]  
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]  
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]  
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]

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
