# API Contract: Chat Endpoint

**Endpoint**: `POST /api/chat`
**Feature**: 001-ai-chat-panel
**Date**: 2026-02-20

## Overview

This endpoint processes user messages through the AI agent and returns responses. It handles conversation persistence, agent invocation, and tool execution.

## Authentication

**Required**: Yes

**Method**: JWT Bearer Token

**Header**:
```
Authorization: Bearer <jwt_token>
```

**Token Source**: Stored in `localStorage` as `auth_token` (managed by existing auth system)

**Failure Response** (401 Unauthorized):
```json
{
  "detail": "Invalid or expired token"
}
```

---

## Request

### HTTP Method
`POST`

### URL
`/api/chat`

### Headers
```
Content-Type: application/json
Authorization: Bearer <jwt_token>
```

### Request Body

```json
{
  "message": "string (required)",
  "conversation_id": "string (optional)"
}
```

**Field Descriptions**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | User's message text. Must not be empty. |
| `conversation_id` | string | No | UUID of existing conversation. Omit for new conversation. |

**Validation Rules**:
- `message`: Must not be empty or whitespace-only
- `conversation_id`: Must be valid UUID format if provided

### Example Requests

**First Message (New Conversation)**:
```json
{
  "message": "Add a task to buy groceries"
}
```

**Subsequent Message (Existing Conversation)**:
```json
{
  "message": "Mark it as high priority",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Response

### Success Response (200 OK)

```json
{
  "response": "string",
  "conversation_id": "string"
}
```

**Field Descriptions**:

| Field | Type | Description |
|-------|------|-------------|
| `response` | string | AI agent's response message |
| `conversation_id` | string | UUID of conversation (created or existing) |

**Example Response**:
```json
{
  "response": "I've added 'Buy groceries' to your task list with high priority.",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Error Responses

**400 Bad Request** (Validation Error):
```json
{
  "detail": "Message cannot be empty"
}
```

**401 Unauthorized** (Authentication Error):
```json
{
  "detail": "Invalid or expired token"
}
```

**500 Internal Server Error** (Server Error):
```json
{
  "detail": "Internal server error"
}
```

---

## Behavior

### Conversation Flow

1. **First Request**: User sends message without `conversation_id`
   - Backend creates new conversation
   - Returns response with new `conversation_id`
   - Frontend stores `conversation_id` for subsequent requests

2. **Subsequent Requests**: User sends message with `conversation_id`
   - Backend loads conversation history
   - Appends new message to conversation
   - Invokes agent with full history
   - Returns response with same `conversation_id`

### Message Persistence

- **User Message**: Persisted to database BEFORE agent invocation
- **Agent Response**: Persisted to database AFTER agent completes
- **Conversation**: Updated timestamp on each message

### Agent Processing

1. Load conversation history (last 50 messages)
2. Prepare user context (user_id, email)
3. Invoke OpenAI Agent with history and context
4. Agent selects and calls MCP tools as needed
5. Agent generates natural language response
6. Response returned to frontend

### Tool Execution

Agent may call MCP tools during processing:
- `create_task`: Creates new task
- `update_task`: Updates existing task
- `delete_task`: Deletes task
- `list_tasks`: Lists user's tasks

Tool calls are transparent to frontend. Response includes confirmation of actions taken.

---

## Response Patterns

### Task Creation Confirmation

**User**: "Add a task to buy groceries"

**Response**:
```json
{
  "response": "I've added 'Buy groceries' to your task list.",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Frontend Action**: Detect "added" keyword → Refresh task list

### Task Update Confirmation

**User**: "Mark the groceries task as complete"

**Response**:
```json
{
  "response": "I've marked 'Buy groceries' as complete.",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Frontend Action**: Detect "marked complete" keyword → Refresh task list

### Task Deletion Confirmation

**User**: "Delete the groceries task"

**Response**:
```json
{
  "response": "I've deleted 'Buy groceries' from your task list.",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Frontend Action**: Detect "deleted" keyword → Refresh task list

### Task List Response

**User**: "Show me all my tasks"

**Response**:
```json
{
  "response": "Here are your tasks:\n1. Buy groceries (incomplete)\n2. Call mom (complete)\n3. Finish report (incomplete)",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Frontend Action**: No refresh needed (informational only)

### Error Response from Agent

**User**: "Update task 999" (task doesn't exist)

**Response**:
```json
{
  "response": "I couldn't find a task with that ID. Could you describe the task you want to update?",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Frontend Action**: Display response, no refresh

---

## Performance Characteristics

### Expected Latency

- **Typical Request**: 1-5 seconds (depends on OpenAI API)
- **Simple Query**: 1-2 seconds
- **Complex Tool Calls**: 3-5 seconds
- **Network Timeout**: 30 seconds (configured in apiClient)

### Rate Limiting

- No explicit rate limiting on endpoint
- OpenAI API has rate limits (handled by backend)
- Recommend debouncing rapid user inputs on frontend

---

## Frontend Integration

### Using Axios (Existing Pattern)

```typescript
import apiClient from '../lib/api';

const sendMessage = async (message: string, conversationId?: string) => {
  const response = await apiClient.post('/api/chat', {
    message,
    conversation_id: conversationId
  });

  return response.data; // { response: string, conversation_id: string }
};
```

### Error Handling

```typescript
try {
  const data = await sendMessage(message, conversationId);
  // Handle success
} catch (error: any) {
  if (error.response?.status === 401) {
    // Redirect to login
  } else if (error.response?.status >= 500) {
    // Show server error message
  } else {
    // Show generic error message
  }
}
```

---

## Testing

### Manual Testing Scenarios

**Scenario 1: New Conversation**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"message": "Add a task to buy groceries"}'
```

**Expected**: 200 OK with response and new conversation_id

**Scenario 2: Existing Conversation**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"message": "Mark it as complete", "conversation_id": "550e8400-e29b-41d4-a716-446655440000"}'
```

**Expected**: 200 OK with response and same conversation_id

**Scenario 3: Invalid Token**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer invalid_token" \
  -d '{"message": "Hello"}'
```

**Expected**: 401 Unauthorized

**Scenario 4: Empty Message**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"message": ""}'
```

**Expected**: 400 Bad Request (if backend validates) or agent handles gracefully

---

## Security Considerations

### Authentication
- JWT token validated on every request
- Token must be valid and not expired
- User identity extracted from token

### Authorization
- MCP tools enforce per-user data isolation
- User can only access their own tasks
- conversation_id tied to user_id in database

### Input Validation
- Message content sanitized by backend
- No SQL injection risk (using ORM)
- No XSS risk (plain text responses)

### Data Privacy
- Conversations isolated per user
- No cross-user data leakage
- Messages stored securely in database

---

## Changelog

**2026-02-20**: Initial API contract documentation

---

## Related Documentation

- [Data Model](../data-model.md) - Frontend data structures
- [Backend Implementation](../../../../backend/src/api/chat.py) - Endpoint implementation
- [Agent Integration](../../../../backend/src/agent/agent.py) - Agent logic
