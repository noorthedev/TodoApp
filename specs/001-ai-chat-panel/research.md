# Research & Design Decisions: AI Chat Panel

**Feature**: 001-ai-chat-panel
**Date**: 2026-02-20
**Phase**: Phase 0 - Research

## Overview

This document captures research findings and design decisions for implementing the AI chat panel on the /tasks dashboard. All decisions are based on existing codebase patterns, React/Next.js best practices, and the requirement for frontend-only changes.

## Research Topic 1: Next.js App Router Layout Patterns

### Question
How should we structure the two-column layout (tasks + chat) in Next.js App Router while maintaining responsiveness?

### Options Considered

**Option A: CSS Grid**
- Pros: Native responsive capabilities, clean syntax, modern standard
- Cons: Requires understanding of grid template areas
- Browser support: Excellent (95%+)

**Option B: Flexbox**
- Pros: Simpler mental model, widely understood, flexible
- Cons: More verbose for complex layouts
- Browser support: Excellent (99%+)

**Option C: Next.js Layout Component**
- Pros: Server-side rendering benefits, nested layouts
- Cons: Overkill for client-side chat UI, adds complexity
- Browser support: N/A (framework feature)

### Decision: CSS Grid (Option A)

**Rationale**:
- CSS Grid provides clean responsive layout with media queries
- Existing dashboard uses simple inline styles, Grid is a natural evolution
- Grid template areas make responsive breakpoints explicit
- No additional dependencies required

**Implementation Pattern**:
```css
.dashboard-container {
  display: grid;
  grid-template-columns: 1fr 1fr;  /* Desktop: 50/50 split */
  gap: 2rem;
  height: calc(100vh - 200px);
}

@media (max-width: 768px) {
  .dashboard-container {
    grid-template-columns: 1fr;  /* Mobile: stacked */
    grid-template-rows: auto 1fr;
  }
}
```

### Alternatives Rejected

- **Flexbox**: More verbose for this use case, harder to manage equal-height columns
- **Layout Component**: Unnecessary complexity for client-side UI

---

## Research Topic 2: React Chat UI Patterns

### Question
What are the best practices for implementing a chat interface in React with auto-scroll, message grouping, and loading states?

### Research Findings

**Auto-scroll Behavior**:
- Use `useRef` to reference message container
- Scroll to bottom on new message using `scrollIntoView()`
- Preserve scroll position if user is viewing history (not at bottom)
- Pattern: Check if user is near bottom before auto-scrolling

**Message Display**:
- Chat bubbles are standard for conversational UI
- User messages: right-aligned, distinct color
- Assistant messages: left-aligned, different color
- Timestamps: relative time (e.g., "2 minutes ago") or absolute

**Loading States**:
- Show typing indicator while AI processes
- Disable input during processing to prevent duplicate sends
- Display inline error messages with retry option

### Decision: Chat Bubble Pattern with Smart Auto-scroll

**Rationale**:
- Chat bubbles are familiar to users (messaging apps)
- Right/left alignment provides clear visual distinction
- Smart auto-scroll respects user intent (viewing history vs following conversation)

**Implementation Pattern**:
```typescript
const messagesEndRef = useRef<HTMLDivElement>(null);
const messagesContainerRef = useRef<HTMLDivElement>(null);

const scrollToBottom = () => {
  const container = messagesContainerRef.current;
  if (!container) return;

  // Only auto-scroll if user is near bottom (within 100px)
  const isNearBottom =
    container.scrollHeight - container.scrollTop - container.clientHeight < 100;

  if (isNearBottom) {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }
};

useEffect(() => {
  scrollToBottom();
}, [messages]);
```

### Alternatives Rejected

- **List-style messages**: Less visually engaging, harder to distinguish speakers
- **Always auto-scroll**: Frustrating when user is reading history

---

## Research Topic 3: Responsive Design Strategies

### Question
How should the layout adapt across desktop, tablet, and mobile devices?

### Breakpoint Analysis

**Desktop (>= 1024px)**:
- Two-column side-by-side layout
- Tasks: 50% width, Chat: 50% width
- Both sections visible simultaneously
- Fixed heights with internal scrolling

**Tablet (768px - 1023px)**:
- Two-column layout with adjusted ratio
- Tasks: 40% width, Chat: 60% width
- Or stacked with toggle button (user preference)

**Mobile (< 768px)**:
- Stacked vertical layout
- Tasks section above, Chat section below
- Full width for each section
- Consider collapsible chat panel

### Decision: Responsive Grid with Stacked Mobile Layout

**Rationale**:
- Desktop users benefit from side-by-side view (see tasks while chatting)
- Mobile users need full-width for readability
- Stacked layout is simpler than toggle/tabs for MVP
- Can enhance with toggle button in future iteration

**Breakpoints**:
- Desktop: >= 1024px (two columns)
- Tablet: 768px - 1023px (two columns, adjusted ratio)
- Mobile: < 768px (stacked)

**Implementation**:
```css
/* Desktop */
@media (min-width: 1024px) {
  .dashboard-container {
    grid-template-columns: 1fr 1fr;
  }
}

/* Tablet */
@media (min-width: 768px) and (max-width: 1023px) {
  .dashboard-container {
    grid-template-columns: 2fr 3fr;
  }
}

/* Mobile */
@media (max-width: 767px) {
  .dashboard-container {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }
}
```

### Alternatives Rejected

- **Tabbed interface**: More complex, requires state management for active tab
- **Overlay modal**: Hides task list, breaks integration goal
- **Toggle button**: Adds complexity for MVP, can be future enhancement

---

## Research Topic 4: Task Refresh Detection

### Question
How can we detect when the AI agent has performed a task operation and trigger a task list refresh?

### Options Considered

**Option A: Response Text Parsing**
- Parse AI response for keywords: "created", "added", "updated", "deleted", "marked complete"
- Trigger `fetchTasks()` when keyword detected
- Pros: Simple, no backend changes, works immediately
- Cons: May have false positives, relies on AI response format

**Option B: Backend Metadata**
- Backend returns `tool_calls_made: ["create_task"]` in response
- Frontend checks metadata array
- Pros: Accurate, explicit, no false positives
- Cons: Requires backend changes (out of scope)

**Option C: WebSocket Events**
- Backend emits task change events via WebSocket
- Frontend listens and refreshes
- Pros: Real-time, accurate, supports multi-tab
- Cons: Requires WebSocket infrastructure (out of scope)

**Option D: Polling**
- Poll task list every N seconds
- Pros: Simple, always up-to-date
- Cons: Inefficient, unnecessary API calls, poor UX

### Decision: Response Text Parsing (Option A)

**Rationale**:
- Meets requirement for frontend-only changes
- AI responses are conversational and include action confirmations
- False positives are acceptable (extra refresh is harmless)
- Can be enhanced with backend metadata in future

**Implementation Pattern**:
```typescript
const TASK_OPERATION_KEYWORDS = [
  'created',
  'added',
  'updated',
  'modified',
  'deleted',
  'removed',
  'marked complete',
  'marked as complete',
  'completed',
];

const detectTaskOperation = (response: string): boolean => {
  const lowerResponse = response.toLowerCase();
  return TASK_OPERATION_KEYWORDS.some(keyword =>
    lowerResponse.includes(keyword)
  );
};

// After receiving AI response
if (detectTaskOperation(aiResponse)) {
  await fetchTasks();
}
```

**Debouncing Strategy**:
- Debounce refresh calls by 500ms to handle multiple operations in one response
- Use `setTimeout` to batch refreshes

### Alternatives Rejected

- **Backend metadata**: Requires backend changes (out of scope)
- **WebSocket**: Too complex for MVP, infrastructure not in place
- **Polling**: Inefficient, poor user experience

---

## Research Topic 5: Conversation History Management

### Question
How should we load and display conversation history, especially for long conversations?

### Options Considered

**Option A: Load All Messages on Mount**
- Fetch all messages when component mounts
- Display all in scrollable container
- Pros: Simple, no pagination logic
- Cons: Performance issues with 100+ messages

**Option B: Pagination (Load More)**
- Load last 50 messages initially
- "Load More" button to fetch older messages
- Pros: Better performance, user control
- Cons: More complex, requires pagination API

**Option C: Infinite Scroll**
- Load messages as user scrolls up
- Automatically fetch older messages
- Pros: Seamless UX, good performance
- Cons: Complex implementation, requires scroll detection

**Option D: Limit to Recent Messages**
- Always show last 50 messages only
- No access to older messages
- Pros: Simple, performant
- Cons: User loses access to history

### Decision: Load Last 50 Messages (Option D with future enhancement path)

**Rationale**:
- Spec requires support for "at least 50 messages"
- Backend already limits to 50 messages (per chat.py implementation)
- Simple implementation for MVP
- Performance is acceptable for 50 messages
- Can add pagination in future if needed

**Implementation Pattern**:
```typescript
const useChat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  useEffect(() => {
    const loadHistory = async () => {
      // Backend returns last 50 messages
      const response = await apiClient.get('/api/chat/history');
      setMessages(response.data.messages);
    };

    loadHistory();
  }, []);

  return { messages, /* ... */ };
};
```

**Future Enhancement Path**:
- Add pagination API endpoint
- Implement "Load More" button
- Or implement infinite scroll

### Alternatives Rejected

- **Load all messages**: Performance risk for long conversations
- **Pagination**: Too complex for MVP, backend doesn't support yet
- **Infinite scroll**: Complex implementation, not needed for 50 messages

---

## Research Topic 6: Input Handling & Keyboard Shortcuts

### Question
How should the message input field handle multiline text and keyboard shortcuts?

### Research Findings

**Standard Chat Patterns**:
- Enter key: Send message
- Shift+Enter: New line (multiline support)
- Disabled state: While message is sending
- Empty message: Prevent submission

**Textarea vs Input**:
- `<textarea>`: Supports multiline, better for longer messages
- `<input>`: Single line only, simpler
- Decision: Use `<textarea>` for flexibility

### Decision: Textarea with Enter/Shift+Enter Shortcuts

**Implementation Pattern**:
```typescript
const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleSubmit();
  }
  // Shift+Enter allows newline (default textarea behavior)
};
```

**Validation**:
- Trim whitespace before checking if empty
- Prevent submission of empty/whitespace-only messages
- Show visual feedback (disabled button) when input is empty

---

## Research Topic 7: Error Handling & Recovery

### Question
How should we handle and display errors from the chat API?

### Error Scenarios

1. **Network Error**: No internet connection
2. **Authentication Error**: Token expired or invalid
3. **Server Error**: Backend 500 error
4. **Timeout**: Request takes too long
5. **Validation Error**: Invalid input (unlikely for chat)

### Decision: Inline Error Display with Retry

**Rationale**:
- Inline errors keep user in context
- Retry button provides clear action
- Error messages should be user-friendly, not technical

**Implementation Pattern**:
```typescript
const [error, setError] = useState<string | null>(null);

const sendMessage = async (message: string) => {
  setError(null);
  setLoading(true);

  try {
    const response = await apiClient.post('/api/chat', { message });
    // Handle success
  } catch (err: any) {
    if (err.response?.status === 401) {
      setError('Your session has expired. Please log in again.');
    } else if (err.response?.status >= 500) {
      setError('Server error. Please try again.');
    } else if (err.code === 'ECONNABORTED') {
      setError('Request timed out. Please try again.');
    } else {
      setError('Failed to send message. Please try again.');
    }
  } finally {
    setLoading(false);
  }
};
```

**Error Display**:
- Show error message above input field
- Red background, white text
- Include retry button
- Auto-dismiss after successful retry

---

## Technology Stack Confirmation

### Frontend Dependencies (Existing)

- **React**: 18.2.0 ✅
- **Next.js**: 15.5.12 ✅
- **TypeScript**: 5.2.2 ✅
- **Axios**: 1.13.5 ✅

**No new dependencies required**. All functionality can be implemented with existing stack.

### Styling Approach

**Options**:
1. Inline styles (existing pattern in dashboard)
2. CSS Modules
3. Styled Components
4. Tailwind CSS

**Decision**: CSS Modules

**Rationale**:
- Existing dashboard uses inline styles (simple but not scalable)
- CSS Modules provide scoped styles without additional dependencies
- TypeScript support built-in
- Better organization for complex chat UI

**File Structure**:
```
components/chat/
├── ChatPanel.tsx
├── ChatPanel.module.css
├── ChatMessage.tsx
├── ChatMessage.module.css
├── ChatInput.tsx
├── ChatInput.module.css
```

---

## Architecture Decisions Summary

| Decision Area | Choice | Rationale |
|--------------|--------|-----------|
| Layout Strategy | CSS Grid with responsive breakpoints | Clean, modern, no dependencies |
| Message Display | Chat bubbles (right/left aligned) | Familiar pattern, clear distinction |
| Auto-scroll | Smart scroll (only if near bottom) | Respects user intent |
| Responsive Design | Stacked on mobile, side-by-side on desktop | Simple, effective |
| Task Refresh | Response text parsing | Frontend-only, no backend changes |
| History Loading | Last 50 messages on mount | Simple, performant, matches backend |
| Input Handling | Textarea with Enter/Shift+Enter | Standard chat pattern |
| Error Handling | Inline errors with retry | Clear, actionable |
| Styling | CSS Modules | Scoped, organized, no new deps |

---

## Implementation Priorities

### P1 (MVP - Must Have)
1. Basic chat UI (send/receive messages)
2. Message display (user/assistant distinction)
3. Loading states
4. Error handling
5. Task refresh on AI operations

### P2 (Important - Should Have)
1. Conversation history loading
2. Auto-scroll behavior
3. Responsive layout (desktop/mobile)
4. Keyboard shortcuts (Enter/Shift+Enter)

### P3 (Nice to Have - Could Have)
1. Timestamps on messages
2. Empty state message
3. Message length validation
4. Smooth animations
5. Accessibility improvements

---

## Open Questions & Future Enhancements

### Open Questions
None. All design decisions finalized.

### Future Enhancements
1. **Pagination**: Load older messages beyond 50
2. **Backend Metadata**: Explicit tool_calls_made field for accurate refresh
3. **WebSocket**: Real-time updates for multi-tab support
4. **Message Editing**: Allow users to edit sent messages
5. **Conversation Management**: Multiple conversations, conversation list
6. **Export**: Export conversation history
7. **Voice Input**: Speech-to-text for mobile users

---

## Risk Mitigation

### Technical Risks

**Risk**: Task refresh false positives
- **Mitigation**: Conservative keyword matching, manual refresh option

**Risk**: Mobile layout complexity
- **Mitigation**: Start simple (stacked), iterate based on feedback

**Risk**: Performance with many messages
- **Mitigation**: Limit to 50 messages, virtualize if needed

### User Experience Risks

**Risk**: Confusing layout on small screens
- **Mitigation**: Clear visual separation, test on real devices

**Risk**: Unclear task operation feedback
- **Mitigation**: Explicit AI confirmation messages, visual task updates

---

## Conclusion

All research topics have been addressed with concrete decisions. The implementation approach is:
- **Simple**: Leverages existing patterns and dependencies
- **Pragmatic**: Frontend-only changes as required
- **Scalable**: Clear path for future enhancements
- **User-Friendly**: Familiar chat patterns, responsive design

**Status**: ✅ Research complete - Ready for Phase 1 (Data Models & Contracts)
