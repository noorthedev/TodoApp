# Quickstart Guide: AI Chat Panel Implementation

**Feature**: 001-ai-chat-panel
**Date**: 2026-02-20
**Audience**: Frontend developers implementing the chat panel

## Overview

This guide provides step-by-step instructions for implementing the AI chat panel on the /tasks dashboard. Follow these steps in order for a smooth implementation.

## Prerequisites

- ✅ Node.js 18+ installed
- ✅ Frontend development environment set up
- ✅ Backend running on `http://localhost:8000`
- ✅ Valid JWT token for testing (login first)
- ✅ Familiarity with React, TypeScript, Next.js App Router

## Project Structure

```
frontend/src/
├── app/dashboard/page.tsx          # MODIFY: Add ChatPanel
├── components/chat/                # NEW: Create this directory
│   ├── ChatPanel.tsx               # Main chat container
│   ├── ChatPanel.module.css        # Chat panel styles
│   ├── ChatMessage.tsx             # Individual message
│   ├── ChatMessage.module.css      # Message styles
│   ├── ChatInput.tsx               # Input field
│   └── ChatInput.module.css        # Input styles
├── hooks/
│   └── useChat.ts                  # NEW: Chat state management
└── lib/
    └── types.ts                    # MODIFY: Add chat types
```

## Implementation Steps

### Step 1: Add Chat Types

**File**: `frontend/src/lib/types.ts`

Add these interfaces to the existing types file:

```typescript
// Add to existing types.ts

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
}
```

**Test**: Run `npm run build` to verify TypeScript compilation.

---

### Step 2: Create useChat Hook

**File**: `frontend/src/hooks/useChat.ts`

```typescript
'use client';

import { useState, useCallback } from 'react';
import apiClient from '../lib/api';
import { ChatMessage, ChatRequest, ChatResponse } from '../lib/types';

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [inputValue, setInputValue] = useState('');

  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim()) return;

    setError(null);
    setLoading(true);

    // Add user message immediately
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: message,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const requestData: ChatRequest = {
        message,
        ...(conversationId && { conversation_id: conversationId }),
      };

      const response = await apiClient.post<ChatResponse>('/api/chat', requestData);

      // Add assistant message
      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);

      // Store conversation ID
      if (!conversationId) {
        setConversationId(response.data.conversation_id);
      }

      return response.data.response;
    } catch (err: any) {
      let errorMessage = 'Failed to send message. Please try again.';

      if (err.response?.status === 401) {
        errorMessage = 'Your session has expired. Please log in again.';
      } else if (err.response?.status >= 500) {
        errorMessage = 'Server error. Please try again.';
      } else if (err.code === 'ECONNABORTED') {
        errorMessage = 'Request timed out. Please try again.';
      }

      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [conversationId]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    messages,
    conversationId,
    loading,
    error,
    inputValue,
    setInputValue,
    sendMessage,
    clearError,
  };
}
```

**Test**: Import the hook in a component to verify no TypeScript errors.

---

### Step 3: Create ChatMessage Component

**File**: `frontend/src/components/chat/ChatMessage.tsx`

```typescript
'use client';

import { ChatMessage as ChatMessageType } from '../../lib/types';
import styles from './ChatMessage.module.css';

interface ChatMessageProps {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`${styles.messageContainer} ${isUser ? styles.user : styles.assistant}`}>
      <div className={styles.messageBubble}>
        <p className={styles.messageContent}>{message.content}</p>
        <span className={styles.timestamp}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  );
}
```

**File**: `frontend/src/components/chat/ChatMessage.module.css`

```css
.messageContainer {
  display: flex;
  margin-bottom: 1rem;
  animation: fadeIn 0.3s ease-in;
}

.messageContainer.user {
  justify-content: flex-end;
}

.messageContainer.assistant {
  justify-content: flex-start;
}

.messageBubble {
  max-width: 70%;
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  word-wrap: break-word;
}

.user .messageBubble {
  background-color: #007bff;
  color: white;
  border-bottom-right-radius: 0.25rem;
}

.assistant .messageBubble {
  background-color: #f1f3f5;
  color: #333;
  border-bottom-left-radius: 0.25rem;
}

.messageContent {
  margin: 0 0 0.25rem 0;
  line-height: 1.5;
}

.timestamp {
  font-size: 0.75rem;
  opacity: 0.7;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

---

### Step 4: Create ChatInput Component

**File**: `frontend/src/components/chat/ChatInput.tsx`

```typescript
'use client';

import { KeyboardEvent } from 'react';
import styles from './ChatInput.module.css';

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled: boolean;
  placeholder?: string;
}

export default function ChatInput({
  value,
  onChange,
  onSubmit,
  disabled,
  placeholder = 'Type a message...'
}: ChatInputProps) {
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!disabled && value.trim()) {
        onSubmit();
      }
    }
  };

  return (
    <div className={styles.inputContainer}>
      <textarea
        className={styles.textarea}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder={placeholder}
        rows={1}
      />
      <button
        className={styles.sendButton}
        onClick={onSubmit}
        disabled={disabled || !value.trim()}
      >
        {disabled ? 'Sending...' : 'Send'}
      </button>
    </div>
  );
}
```

**File**: `frontend/src/components/chat/ChatInput.module.css`

```css
.inputContainer {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  border-top: 1px solid #e0e0e0;
  background-color: white;
}

.textarea {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-family: inherit;
  resize: none;
  min-height: 44px;
  max-height: 120px;
}

.textarea:focus {
  outline: none;
  border-color: #007bff;
}

.textarea:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.sendButton {
  padding: 0.75rem 1.5rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  cursor: pointer;
  white-space: nowrap;
}

.sendButton:hover:not(:disabled) {
  background-color: #0056b3;
}

.sendButton:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
```

---

### Step 5: Create ChatPanel Component

**File**: `frontend/src/components/chat/ChatPanel.tsx`

```typescript
'use client';

import { useEffect, useRef } from 'react';
import { useChat } from '../../hooks/useChat';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import styles from './ChatPanel.module.css';

interface ChatPanelProps {
  onTaskOperation?: () => void;
}

const TASK_KEYWORDS = ['created', 'added', 'updated', 'modified', 'deleted', 'removed', 'marked complete', 'completed'];

export default function ChatPanel({ onTaskOperation }: ChatPanelProps) {
  const {
    messages,
    loading,
    error,
    inputValue,
    setInputValue,
    sendMessage,
    clearError,
  } = useChat();

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const isNearBottom =
      container.scrollHeight - container.scrollTop - container.clientHeight < 100;

    if (isNearBottom) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSubmit = async () => {
    const message = inputValue.trim();
    if (!message || loading) return;

    setInputValue('');

    try {
      const response = await sendMessage(message);

      // Check if response indicates task operation
      if (response && onTaskOperation) {
        const lowerResponse = response.toLowerCase();
        const hasTaskOperation = TASK_KEYWORDS.some(keyword =>
          lowerResponse.includes(keyword)
        );

        if (hasTaskOperation) {
          // Debounce refresh
          setTimeout(() => {
            onTaskOperation();
          }, 500);
        }
      }
    } catch (err) {
      // Error already handled in useChat
    }
  };

  return (
    <div className={styles.chatPanel}>
      <div className={styles.header}>
        <h2>AI Assistant</h2>
      </div>

      <div className={styles.messagesContainer} ref={messagesContainerRef}>
        {messages.length === 0 && (
          <div className={styles.emptyState}>
            <p>👋 Hi! I can help you manage your tasks.</p>
            <p>Try saying: "Add a task to buy groceries"</p>
          </div>
        )}

        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {loading && (
          <div className={styles.loadingIndicator}>
            <span>AI is thinking...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className={styles.errorContainer}>
          <p>{error}</p>
          <button onClick={clearError}>Dismiss</button>
        </div>
      )}

      <ChatInput
        value={inputValue}
        onChange={setInputValue}
        onSubmit={handleSubmit}
        disabled={loading}
        placeholder="Ask me to manage your tasks..."
      />
    </div>
  );
}
```

**File**: `frontend/src/components/chat/ChatPanel.module.css`

```css
.chatPanel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 0.5rem;
  overflow: hidden;
}

.header {
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
  background-color: #f8f9fa;
}

.header h2 {
  margin: 0;
  font-size: 1.25rem;
  color: #333;
}

.messagesContainer {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
}

.emptyState {
  text-align: center;
  color: #666;
  margin-top: 2rem;
}

.emptyState p {
  margin: 0.5rem 0;
}

.loadingIndicator {
  display: flex;
  justify-content: center;
  padding: 1rem;
  color: #666;
  font-style: italic;
}

.errorContainer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background-color: #f8d7da;
  color: #721c24;
  border-top: 1px solid #f5c6cb;
}

.errorContainer p {
  margin: 0;
  flex: 1;
}

.errorContainer button {
  padding: 0.25rem 0.75rem;
  background-color: transparent;
  color: #721c24;
  border: 1px solid #721c24;
  border-radius: 0.25rem;
  cursor: pointer;
}

.errorContainer button:hover {
  background-color: #721c24;
  color: white;
}
```

---

### Step 6: Integrate ChatPanel into Dashboard

**File**: `frontend/src/app/dashboard/page.tsx`

Modify the existing dashboard page:

```typescript
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../hooks/useAuth';
import { useTasks } from '../../hooks/useTasks';
import TaskForm from '../../components/tasks/TaskForm';
import TaskList from '../../components/tasks/TaskList';
import ChatPanel from '../../components/chat/ChatPanel';  // NEW

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const { tasks, loading, error, createTask, updateTask, deleteTask, fetchTasks } = useTasks();

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  const handleLogout = () => {
    logout();
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '2rem',
        paddingBottom: '1rem',
        borderBottom: '2px solid #eee'
      }}>
        <div>
          <h1 style={{ margin: '0 0 0.5rem 0' }}>Task Dashboard</h1>
          {user && <p style={{ margin: 0, color: '#666' }}>Welcome, {user.email}</p>}
        </div>
        <button
          onClick={handleLogout}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '1rem'
          }}
        >
          Logout
        </button>
      </div>

      {/* NEW: Two-column layout */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '2rem',
        height: 'calc(100vh - 200px)',
      }}>
        {/* Tasks Section */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', overflow: 'auto' }}>
          <TaskForm onSubmit={createTask} />
          <TaskList
            tasks={tasks}
            loading={loading}
            error={error}
            onUpdate={updateTask}
            onDelete={deleteTask}
            onRefresh={fetchTasks}
          />
        </div>

        {/* Chat Section - NEW */}
        <div>
          <ChatPanel onTaskOperation={fetchTasks} />
        </div>
      </div>
    </div>
  );
}
```

---

### Step 7: Add Responsive Styles

Add media queries to make the layout responsive. Create a new CSS module or add to globals.css:

```css
/* Add to app/globals.css or create dashboard.module.css */

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr !important;
    grid-template-rows: auto 1fr;
    height: auto !important;
  }
}
```

---

## Testing Checklist

### Manual Testing

1. **Login and Access Dashboard**
   - [ ] Navigate to `/login`
   - [ ] Login with valid credentials
   - [ ] Verify redirect to `/dashboard`
   - [ ] Verify chat panel is visible

2. **Send First Message**
   - [ ] Type "Add a task to buy groceries"
   - [ ] Press Enter
   - [ ] Verify message appears in chat history
   - [ ] Verify loading indicator shows
   - [ ] Verify AI response appears
   - [ ] Verify task appears in task list

3. **Send Follow-up Message**
   - [ ] Type "Mark it as complete"
   - [ ] Press Enter
   - [ ] Verify conversation continues
   - [ ] Verify task updates in task list

4. **Test Error Handling**
   - [ ] Disconnect internet
   - [ ] Try sending message
   - [ ] Verify error message displays
   - [ ] Reconnect internet
   - [ ] Click retry or send again
   - [ ] Verify success

5. **Test Responsive Layout**
   - [ ] Resize browser to mobile width (< 768px)
   - [ ] Verify layout stacks vertically
   - [ ] Verify chat input remains accessible
   - [ ] Test on actual mobile device

6. **Test Keyboard Shortcuts**
   - [ ] Type message and press Enter → Should send
   - [ ] Type message and press Shift+Enter → Should add newline
   - [ ] Verify input disabled while loading

---

## Troubleshooting

### Issue: "Cannot find module 'useChat'"

**Solution**: Verify file path is correct: `frontend/src/hooks/useChat.ts`

### Issue: Chat panel not showing

**Solution**: Check browser console for errors. Verify all imports are correct.

### Issue: Messages not sending

**Solution**:
1. Check backend is running on `http://localhost:8000`
2. Verify JWT token is valid (check localStorage)
3. Check browser network tab for API errors

### Issue: Task list not refreshing

**Solution**: Verify `onTaskOperation={fetchTasks}` prop is passed to ChatPanel

### Issue: Styles not applying

**Solution**: Verify CSS module files are named correctly (`.module.css`)

---

## Next Steps

After completing implementation:

1. **Test thoroughly** using the checklist above
2. **Review code** for TypeScript errors
3. **Test on multiple browsers** (Chrome, Firefox, Safari)
4. **Test on mobile devices**
5. **Create pull request** with description of changes
6. **Request code review** from team

---

## Additional Resources

- [React Hooks Documentation](https://react.dev/reference/react)
- [Next.js App Router](https://nextjs.org/docs/app)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [API Contract](./contracts/chat-api.md)
- [Data Model](./data-model.md)

---

**Status**: ✅ Ready for implementation
**Estimated Time**: 4-6 hours for experienced developer
**Difficulty**: Intermediate
