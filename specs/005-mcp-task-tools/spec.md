# Feature Specification: MCP Server & Task Tools Integration

**Feature Branch**: `005-mcp-task-tools`
**Created**: 2026-02-19
**Status**: Draft
**Input**: User description: "MCP Server & Task Tools Integration (Spec-5)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and List Tasks via Natural Language (Priority: P1)

Users can create new tasks and view their task list through natural conversation with the AI assistant, without needing to understand technical concepts or use specific commands.

**Why this priority**: This is the core value proposition of the AI chatbot - enabling users to manage tasks through natural language. Without this, the chatbot cannot perform its primary function.

**Independent Test**: Can be fully tested by sending chat messages like "Add a task to buy groceries" and "Show me my tasks", then verifying tasks are created and listed correctly with proper user isolation.

**Acceptance Scenarios**:

1. **Given** user is authenticated, **When** user says "Add a task to buy groceries", **Then** system creates task with title "Buy groceries" for that user and confirms creation
2. **Given** user has 3 tasks in their list, **When** user says "Show me my tasks", **Then** system displays all 3 tasks belonging to that user only
3. **Given** user A has 5 tasks and user B has 3 tasks, **When** user A requests their tasks, **Then** system shows only user A's 5 tasks, not user B's tasks
4. **Given** user is not authenticated, **When** user attempts to create a task, **Then** system rejects the request with authentication error

---

### User Story 2 - Complete and Delete Tasks (Priority: P2)

Users can mark tasks as complete or remove tasks they no longer need through natural conversation, maintaining control over their task list.

**Why this priority**: Essential for task lifecycle management, but depends on tasks existing first (P1). Users need to complete or remove tasks to keep their list manageable.

**Independent Test**: Can be tested by creating tasks, then using phrases like "Mark the groceries task as done" or "Delete the meeting task", verifying the operations succeed and only affect the authenticated user's tasks.

**Acceptance Scenarios**:

1. **Given** user has task "Buy groceries" (incomplete), **When** user says "Mark the groceries task as complete", **Then** system updates task status to complete and confirms
2. **Given** user has task "Old meeting", **When** user says "Delete the old meeting task", **Then** system removes task and confirms deletion
3. **Given** user A has task "Report" and user B has task "Report", **When** user A says "Delete the report task", **Then** system deletes only user A's task, not user B's task
4. **Given** user requests to complete a task that doesn't exist, **When** system processes request, **Then** system responds with friendly error message

---

### User Story 3 - Update Task Details (Priority: P3)

Users can modify task titles or descriptions through conversation, allowing them to refine task information as needs change.

**Why this priority**: Nice-to-have feature that enhances usability but not critical for MVP. Users can work around this by deleting and recreating tasks.

**Independent Test**: Can be tested by creating a task, then using phrases like "Change the groceries task to 'Buy organic groceries'", verifying the update succeeds with proper authorization.

**Acceptance Scenarios**:

1. **Given** user has task "Buy groceries", **When** user says "Change the groceries task to 'Buy organic groceries'", **Then** system updates task title and confirms
2. **Given** user A has task "Report" and user B has task "Report", **When** user A updates their report task, **Then** system updates only user A's task
3. **Given** user requests to update a task that doesn't exist, **When** system processes request, **Then** system responds with friendly error message

---

### Edge Cases

- What happens when user requests an operation on a task that belongs to another user?
- How does system handle ambiguous task references (e.g., "Delete the task" when user has multiple tasks)?
- What happens when user provides incomplete information (e.g., "Add a task" without specifying what)?
- How does system handle database connection failures during task operations?
- What happens when user requests to create a task with empty or very long title?
- How does system handle concurrent operations on the same task?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide structured tools for all task operations (create, list, complete, delete, update)
- **FR-002**: System MUST validate authenticated user identity before executing any task operation
- **FR-003**: System MUST enforce per-user data isolation ensuring users can only access their own tasks
- **FR-004**: System MUST return structured responses from all tools indicating success or failure with relevant data
- **FR-005**: System MUST persist all task operations to database immediately before returning success
- **FR-006**: System MUST handle tool errors gracefully without exposing technical details to users
- **FR-007**: System MUST support natural language interpretation of user intent for task operations
- **FR-008**: System MUST validate tool inputs before executing database operations
- **FR-009**: System MUST log all authorization failures for security monitoring
- **FR-010**: System MUST maintain stateless operation with no in-memory task state
- **FR-011**: System MUST support concurrent task operations from multiple users without conflicts
- **FR-012**: System MUST provide clear error messages when operations fail

### Key Entities

- **Task**: Represents a user's todo item with title, description, completion status, and ownership
- **User Context**: Contains authenticated user identity (user_id, email) passed to all tool operations
- **Tool Response**: Structured result from tool execution containing success status, data, or error message
- **MCP Tool**: Callable operation exposed to AI agent for task management

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create tasks through natural language with 95% success rate on first attempt
- **SC-002**: System correctly isolates user data with zero cross-user access incidents
- **SC-003**: Task operations complete within 2 seconds from user message to response
- **SC-004**: System handles 100 concurrent users performing task operations without errors
- **SC-005**: Agent correctly interprets user intent for task operations 90% of the time
- **SC-006**: All tool operations return structured responses with consistent format
- **SC-007**: System maintains 99.9% uptime for task operations
- **SC-008**: Authorization checks complete in under 10 milliseconds per operation

## MCP Tool Specifications *(include if feature involves MCP tools)*

### Tool 1: add_task

**Purpose**: Creates a new task for the authenticated user. Agent should use this when user expresses intent to create, add, or remember something.

**Input Schema**:
```python
{
    "title": "str (required, 1-200 characters)",
    "description": "str (optional, max 1000 characters)",
    "user_context": "dict (automatically provided)",
    "session": "AsyncSession (automatically provided)"
}
```

**Output Schema**:
```python
{
    "success": "bool",
    "data": {
        "task_id": "int",
        "title": "str",
        "description": "str",
        "completed": "bool",
        "created_at": "str (ISO 8601)"
    },
    "error": "str (on failure)"
}
```

**Authorization Requirements**:
- Tool MUST extract user_id from user_context
- Tool MUST force user_id on created task (never trust input)
- Tool MUST return error if user_context is missing or invalid

**Example Usage**:
```
Agent receives: "Add a task to buy groceries"
Agent calls: add_task(title="Buy groceries", description="")
Tool returns: {"success": true, "data": {"task_id": 123, "title": "Buy groceries", ...}}
```

---

### Tool 2: list_tasks

**Purpose**: Retrieves all tasks belonging to the authenticated user. Agent should use this when user wants to see, view, or check their tasks.

**Input Schema**:
```python
{
    "user_context": "dict (automatically provided)",
    "session": "AsyncSession (automatically provided)"
}
```

**Output Schema**:
```python
{
    "success": "bool",
    "data": {
        "tasks": [
            {
                "task_id": "int",
                "title": "str",
                "description": "str",
                "completed": "bool",
                "created_at": "str (ISO 8601)"
            }
        ],
        "count": "int"
    },
    "error": "str (on failure)"
}
```

**Authorization Requirements**:
- Tool MUST filter tasks by user_id from user_context
- Tool MUST return only tasks belonging to authenticated user
- Tool MUST return empty list if user has no tasks (not error)

**Example Usage**:
```
Agent receives: "Show me my tasks"
Agent calls: list_tasks()
Tool returns: {"success": true, "data": {"tasks": [...], "count": 5}}
```

---

### Tool 3: complete_task

**Purpose**: Marks a task as completed for the authenticated user. Agent should use this when user indicates a task is done, finished, or complete.

**Input Schema**:
```python
{
    "task_id": "int (required)",
    "user_context": "dict (automatically provided)",
    "session": "AsyncSession (automatically provided)"
}
```

**Output Schema**:
```python
{
    "success": "bool",
    "data": {
        "task_id": "int",
        "title": "str",
        "completed": "bool"
    },
    "error": "str (on failure)"
}
```

**Authorization Requirements**:
- Tool MUST verify task exists before updating
- Tool MUST verify task.user_id matches user_context["user_id"]
- Tool MUST return error if task not found or unauthorized

**Example Usage**:
```
Agent receives: "Mark the groceries task as done"
Agent calls: complete_task(task_id=123)
Tool returns: {"success": true, "data": {"task_id": 123, "completed": true}}
```

---

### Tool 4: delete_task

**Purpose**: Permanently removes a task for the authenticated user. Agent should use this when user wants to delete, remove, or discard a task.

**Input Schema**:
```python
{
    "task_id": "int (required)",
    "user_context": "dict (automatically provided)",
    "session": "AsyncSession (automatically provided)"
}
```

**Output Schema**:
```python
{
    "success": "bool",
    "data": {
        "task_id": "int",
        "deleted": "bool"
    },
    "error": "str (on failure)"
}
```

**Authorization Requirements**:
- Tool MUST verify task exists before deleting
- Tool MUST verify task.user_id matches user_context["user_id"]
- Tool MUST return error if task not found or unauthorized
- Tool MUST log deletion for audit trail

**Example Usage**:
```
Agent receives: "Delete the meeting task"
Agent calls: delete_task(task_id=456)
Tool returns: {"success": true, "data": {"task_id": 456, "deleted": true}}
```

---

### Tool 5: update_task

**Purpose**: Modifies task title or description for the authenticated user. Agent should use this when user wants to change, edit, or update task details.

**Input Schema**:
```python
{
    "task_id": "int (required)",
    "title": "str (optional, 1-200 characters)",
    "description": "str (optional, max 1000 characters)",
    "user_context": "dict (automatically provided)",
    "session": "AsyncSession (automatically provided)"
}
```

**Output Schema**:
```python
{
    "success": "bool",
    "data": {
        "task_id": "int",
        "title": "str",
        "description": "str",
        "completed": "bool"
    },
    "error": "str (on failure)"
}
```

**Authorization Requirements**:
- Tool MUST verify task exists before updating
- Tool MUST verify task.user_id matches user_context["user_id"]
- Tool MUST return error if task not found or unauthorized
- Tool MUST validate at least one field (title or description) is provided

**Example Usage**:
```
Agent receives: "Change the groceries task to 'Buy organic groceries'"
Agent calls: update_task(task_id=123, title="Buy organic groceries")
Tool returns: {"success": true, "data": {"task_id": 123, "title": "Buy organic groceries", ...}}
```

---

## Agent Interaction Patterns *(include if feature involves AI agent)*

### Intent Recognition

**User Intent 1**: User wants to create a new task

**Natural Language Patterns**:
- "Add a task to [description]"
- "Create a task: [description]"
- "I need to [description]"
- "Remind me to [description]"
- "New task: [description]"
- "Add [description] to my list"

**Agent Behavior**:
1. Extract task title from user message
2. Extract optional description if provided
3. Call `add_task` MCP tool with extracted parameters
4. Confirm task creation with user-friendly response including task title

**Example Interaction**:
```
User: "Add a task to buy groceries tomorrow"
Agent: *calls add_task(title="Buy groceries tomorrow")*
Agent: "I've added 'Buy groceries tomorrow' to your task list."
```

---

**User Intent 2**: User wants to view their tasks

**Natural Language Patterns**:
- "Show me my tasks"
- "What tasks do I have?"
- "List my tasks"
- "What's on my list?"
- "Show my todo list"

**Agent Behavior**:
1. Call `list_tasks` MCP tool
2. Format tasks in readable list
3. Include task count and completion status

**Example Interaction**:
```
User: "Show me my tasks"
Agent: *calls list_tasks()*
Agent: "You have 3 tasks:
1. Buy groceries (not complete)
2. Finish report (not complete)
3. Call dentist (complete)"
```

---

**User Intent 3**: User wants to mark task as complete

**Natural Language Patterns**:
- "Mark [task] as done"
- "Complete [task]"
- "[task] is finished"
- "I finished [task]"
- "Check off [task]"

**Agent Behavior**:
1. Identify which task user is referring to
2. If ambiguous, ask for clarification
3. Call `complete_task` MCP tool with task_id
4. Confirm completion with task title

**Example Interaction**:
```
User: "Mark the groceries task as done"
Agent: *calls complete_task(task_id=123)*
Agent: "Great! I've marked 'Buy groceries' as complete."
```

---

**User Intent 4**: User wants to delete a task

**Natural Language Patterns**:
- "Delete [task]"
- "Remove [task]"
- "Get rid of [task]"
- "I don't need [task] anymore"

**Agent Behavior**:
1. Identify which task user is referring to
2. If ambiguous, ask for clarification
3. Call `delete_task` MCP tool with task_id
4. Confirm deletion with task title

**Example Interaction**:
```
User: "Delete the meeting task"
Agent: *calls delete_task(task_id=456)*
Agent: "I've deleted 'Team meeting' from your list."
```

---

**User Intent 5**: User wants to update task details

**Natural Language Patterns**:
- "Change [task] to [new title]"
- "Update [task] to [new title]"
- "Rename [task] to [new title]"
- "Edit [task]"

**Agent Behavior**:
1. Identify which task user is referring to
2. Extract new title or description
3. Call `update_task` MCP tool with task_id and new values
4. Confirm update with old and new titles

**Example Interaction**:
```
User: "Change the groceries task to 'Buy organic groceries'"
Agent: *calls update_task(task_id=123, title="Buy organic groceries")*
Agent: "I've updated your task from 'Buy groceries' to 'Buy organic groceries'."
```

---

### Agent Response Guidelines

**Success Responses**:
- Confirm action taken in natural language
- Include relevant details (task title, count, status)
- Be concise and friendly
- Use past tense for completed actions ("I've added", "I've marked")

**Error Responses**:
- Explain what went wrong in user-friendly terms
- Suggest corrective action if applicable
- Never expose technical error details (database errors, stack traces)
- Examples:
  - "I couldn't find that task. Could you be more specific?"
  - "Something went wrong. Please try again."
  - "You don't have permission to access that task."

**Clarification Requests**:
- Ask for missing information politely
- Provide examples of valid inputs
- Guide user toward successful completion
- Examples:
  - "Which task would you like to complete? You have: [list]"
  - "What would you like to add to your task list?"
  - "I found multiple tasks with that name. Which one did you mean?"

### Conversation State Requirements

**Context to Maintain**:
- Current task being discussed (for follow-up operations)
- Recently created task IDs (for immediate operations like "mark it as done")
- User's task list (loaded once per conversation turn)

**Context to Reset**:
- After task operation completes successfully
- After user switches to different topic
- After error occurs (don't persist failed state)

## Agent Acceptance Criteria *(include if feature involves AI agent)*

### Natural Language Understanding

- **AAC-001**: Agent MUST correctly identify user intent from natural language input for all 5 task operations
- **AAC-002**: Agent MUST extract task title from user message with 90% accuracy
- **AAC-003**: Agent MUST handle ambiguous requests by asking clarifying questions
- **AAC-004**: Agent MUST recognize when user provides insufficient information and request details

### Tool Selection and Execution

- **AAC-005**: Agent MUST select the correct MCP tool for user intent with 95% accuracy
- **AAC-006**: Agent MUST pass correct parameters to MCP tools (task_id, title, description)
- **AAC-007**: Agent MUST handle tool errors gracefully without crashing or exposing technical details
- **AAC-008**: Agent MUST retry with corrected parameters if tool returns validation error

### Response Quality

- **AAC-009**: Agent responses MUST be natural and conversational (not robotic or technical)
- **AAC-010**: Agent MUST confirm successful operations with relevant details (task title, status)
- **AAC-011**: Agent MUST explain errors in user-friendly language without technical jargon
- **AAC-012**: Agent MUST not expose technical implementation details (database, tool names, error codes)

### Authorization and Security

- **AAC-013**: Agent MUST never bypass MCP tool authorization checks
- **AAC-014**: Agent MUST not access database directly (only through MCP tools)
- **AAC-015**: Agent MUST pass user context to all tool calls automatically
- **AAC-016**: Agent MUST handle authorization failures appropriately with user-friendly messages

## Assumptions

- User authentication is handled by existing Better Auth + JWT system
- User context (user_id, email) is extracted from JWT token before agent invocation
- Database schema for Task model already exists from Phase-II
- Chat endpoint orchestrates agent invocation and conversation persistence
- Frontend (ChatKit) sends user messages to chat endpoint with JWT token
- MCP server runs as part of backend application (not separate process)
- Tool responses are synchronous (no async callbacks)
- Task IDs are unique integers assigned by database
- Task titles are required, descriptions are optional
- Completed status is boolean (true/false)
- No task priority, due dates, or categories in this phase (future enhancement)
