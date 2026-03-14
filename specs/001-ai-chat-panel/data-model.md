# Data Model: AI Chat Panel

**Feature**: 001-ai-chat-panel
**Date**: 2026-02-20
**Phase**: Phase 1 - Data Models

## Overview

This document defines the frontend data models for the AI chat panel feature. Since this is a frontend-only implementation, all models are TypeScript interfaces representing client-side state and API contracts.

## Frontend State Models

### ChatMessage

Represents a single message in the conversation.

```typescript
interface ChatMessage {
  id: string;              // Unique identifier (UUID or timestamp-based)
  role: 'user' | 'assistant';  // Message sender
  content: string;         // Message text
  timestamp: Date;         // When message was created
}
```

**Field Descriptions**:
- `id`: Unique identifier for the message. Generated client-side using `crypto.randomUUID()` or timestamp
- `role`: Indicates whether message is from user or AI assistant
- `content`: The actual message text (plain text, may contain markdown in future)
- `timestamp`: JavaScript Date object representing when message was created

**Validation Rules**:
- `id`: Must be unique within conversation
- `role`: Must be exactly 'user' or 'assistant'
- `content`: Must not be empty or whitespace-only
- `timestamp`: Must be valid Date object

**Example**:
```typescript
const message: ChatMessage = {
  id: 'msg-123e4567-e89b-12d3-a456-426614174000',
  role: 'user',
  content: 'Add a task to buy groceries',
  timestamp: new Date('2026-02-20T10:30:00Z')
};
```

---

### ChatState

Represents the complete state of the chat panel managed by the `useChat` hook.

```typescript
interface ChatState {
  messages: ChatMessage[];      // Array of all messages in conversation
  conversationId: string | null;  // Current conversation ID (null if not started)
  loading: boolean;             // True while waiting for AI response
  error: string | null;         // Error message if any (null if no error)
  inputValue: string;           // Current value of input field
}
```

**Field Descriptions**:
- `messages`: Ordered array of messages (oldest first)
- `conversationId`: UUID from backend identifying the conversation
- `loading`: Indicates if a message send is in progress
- `error`: User-friendly error message to display
- `inputValue`: Current text in the input field (controlled component)

**State Transitions**:
1. **Initial State**: `{ messages: [], conversationId: null, loading: false, error: null, inputValue: '' }`
2. **Loading History**: `loading: true` → fetch messages → `messages: [...], conversationId: 'uuid'`
3. **Sending Message**: `loading: true, inputValue: ''` → API call → `messages: [...new], loading: false`
4. **Error State**: `loading: false, error: 'message'` → user retries → `error: null`

**Example**:
```typescript
const chatState: ChatState = {
  messages: [
    { id: '1', role: 'user', content: 'Hello', timestamp: new Date() },
    { id: '2', role: 'assistant', content: 'Hi! How can I help?', timestamp: new Date() }
  ],
  conversationId: 'conv-123e4567-e89b-12d3-a456-426614174000',
  loading: false,
  error: null,
  inputValue: ''
};
```

---

## API Contract Models

### ChatRequest

Request payload for sending a message to the backend.

```typescript
interface ChatRequest {
  message: string;              // User's message text
  conversation_id?: string;     // Optional conversation ID (omit for new conversation)
}
```

**Field Descriptions**:
- `message`: The user's message text (required, non-empty)
- `conversation_id`: UUID of existing conversation (optional, backend creates if omitted)

**Validation Rules**:
- `message`: Required, must not be empty after trimming whitespace
- `conversation_id`: Optional, must be valid UUID format if provided

**Example**:
```typescript
// First message (no conversation_id)
const request1: ChatRequest = {
  message: 'Add a task to buy groceries'
};

// Subsequent message (with conversation_id)
const request2: ChatRequest = {
  message: 'Mark it as high priority',
  conversation_id: 'conv-123e4567-e89b-12d3-a456-426614174000'
};
```

---

### ChatResponse

Response payload from the backend after processing a message.

```typescript
interface ChatResponse {
  response: string;           // AI agent's response text
  conversation_id: string;    // Conversation ID (created or existing)
}
```

**Field Descriptions**:
- `response`: The AI agent's response message
- `conversation_id`: UUID of the conversation (created by backend if new)

**Example**:
```typescript
const response: ChatResponse = {
  response: "I've added 'Buy groceries' to your task list with high priority.",
  conversation_id: 'conv-123e4567-e89b-12d3-a456-426614174000'
};
```

---

### ConversationHistory

Response payload when loading conversation history (future endpoint).

```typescript
interface ConversationHistory {
  conversation_id: string;
  messages: Array<{
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;  // ISO 8601 format
  }>;
}
```

**Note**: This endpoint may not exist yet. If not, conversation history is reconstructed from individual messages sent/received during the session.

---

## Component Props Models

### ChatPanelProps

Props for the main ChatPanel component.

```typescript
interface ChatPanelProps {
  onTaskOperation?: () => void;  // Callback when AI performs task operation
}
```

**Field Descriptions**:
- `onTaskOperation`: Optional callback to trigger task list refresh

**Usage**:
```typescript
<ChatPanel onTaskOperation={fetchTasks} />
```

---

### ChatMessageProps

Props for the ChatMessage component.

```typescript
interface ChatMessageProps {
  message: ChatMessage;  // Message to display
}
```

**Field Descriptions**:
- `message`: The message object to render

**Usage**:
```typescript
<ChatMessage message={message} />
```

---

### ChatInputProps

Props for the ChatInput component.

```typescript
interface ChatInputProps {
  value: string;                    // Current input value
  onChange: (value: string) => void;  // Input change handler
  onSubmit: () => void;             // Submit handler
  disabled: boolean;                // Whether input is disabled
  placeholder?: string;             // Optional placeholder text
}
```

**Field Descriptions**:
- `value`: Controlled input value
- `onChange`: Called when user types
- `onSubmit`: Called when user presses Enter (without Shift)
- `disabled`: True while message is sending
- `placeholder`: Optional placeholder text (default: "Type a message...")

**Usage**:
```typescript
<ChatInput
  value={inputValue}
  onChange={setInputValue}
  onSubmit={handleSubmit}
  disabled={loading}
  placeholder="Ask me to manage your tasks..."
/>
```

---

### ChatHistoryProps

Props for the ChatHistory component.

```typescript
interface ChatHistoryProps {
  messages: ChatMessage[];  // Array of messages to display
  loading: boolean;         // Whether messages are loading
}
```

**Field Descriptions**:
- `messages`: Array of messages to render
- `loading`: True while loading history or waiting for response

**Usage**:
```typescript
<ChatHistory messages={messages} loading={loading} />
```

---

## Type Definitions File

All types should be defined in `frontend/src/lib/types.ts`:

```typescript
// frontend/src/lib/types.ts

// Existing types (tasks)
export interface Task {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  completed?: boolean;
}

// NEW: Chat types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ChatState {
  messages: ChatMessage[];
  conversationId: string | null;
  loading: boolean;
  error: string | null;
  inputValue: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
}

export interface ConversationHistory {
  conversation_id: string;
  messages: Array<{
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
  }>;
}
```

---

## State Management Pattern

### useChat Hook

The `useChat` hook encapsulates all chat state management:

```typescript
// frontend/src/hooks/useChat.ts

export function useChat() {
  const [state, setState] = useState<ChatState>({
    messages: [],
    conversationId: null,
    loading: false,
    error: null,
    inputValue: ''
  });

  // Methods: sendMessage, loadHistory, setInputValue, clearError
  // Returns: { ...state, sendMessage, loadHistory, setInputValue, clearError }
}
```

**State Updates**:
- All state updates use `setState` with partial updates
- Loading states set before async operations
- Errors cleared on successful operations
- Messages appended to array (immutable updates)

---

## Data Flow Diagram

```
User Input
    ↓
ChatInput Component
    ↓
useChat.sendMessage()
    ↓
API Request (POST /api/chat)
    ↓
Backend Processing
    ↓
API Response (ChatResponse)
    ↓
useChat updates state
    ↓
ChatHistory re-renders
    ↓
New message displayed
    ↓
Task refresh triggered (if operation detected)
```

---

## Validation & Error Handling

### Client-Side Validation

**Before Sending Message**:
1. Trim whitespace from input
2. Check if empty → prevent send
3. Check if loading → prevent duplicate send
4. Check if authenticated → redirect to login

**After Receiving Response**:
1. Validate response structure
2. Check for conversation_id
3. Parse response text for task operations
4. Update state accordingly

### Error States

**Network Error**:
```typescript
error: 'Unable to connect. Please check your internet connection.'
```

**Authentication Error (401)**:
```typescript
error: 'Your session has expired. Please log in again.'
// Optionally redirect to login
```

**Server Error (500)**:
```typescript
error: 'Server error. Please try again.'
```

**Timeout Error**:
```typescript
error: 'Request timed out. Please try again.'
```

---

## Performance Considerations

### Message Array Management

- **Limit**: Keep last 50 messages in state (matches backend limit)
- **Immutability**: Use spread operator for updates: `[...messages, newMessage]`
- **Memoization**: Use `React.memo` for ChatMessage components

### State Updates

- **Batching**: React automatically batches state updates
- **Debouncing**: Debounce task refresh calls (500ms)
- **Optimization**: Use `useCallback` for event handlers

---

## Testing Considerations

### Unit Tests (Future)

**ChatMessage Model**:
- Validate required fields
- Test role enum values
- Test timestamp parsing

**ChatState Model**:
- Test state transitions
- Test error state handling
- Test loading state management

### Integration Tests (Future)

**useChat Hook**:
- Test sendMessage flow
- Test error handling
- Test conversation persistence

---

## Summary

All data models are defined as TypeScript interfaces with clear validation rules and usage examples. The models support:
- ✅ Message display and management
- ✅ Conversation state tracking
- ✅ API request/response contracts
- ✅ Component prop typing
- ✅ Error handling
- ✅ Future extensibility

**Status**: ✅ Data models complete - Ready for implementation
