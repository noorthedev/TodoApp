# Implementation Plan: AI Chat Panel for Task Dashboard

**Branch**: `001-ai-chat-panel` | **Date**: 2026-02-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ai-chat-panel/spec.md`

## Summary

Add an AI chat panel to the existing /tasks dashboard page, enabling users to manage tasks through natural language conversation. The chat panel will integrate with the existing backend chat API (POST /api/chat), maintain conversation state, and automatically refresh the task list when the AI agent performs task operations. This is a frontend-only implementation that leverages the already-implemented backend chat endpoint, AI agent, and MCP tools.

## Technical Context

**Language/Version**: TypeScript 5.2+ with Next.js 15.5+
**Primary Dependencies**: React 18.2+, Axios 1.13+, Next.js App Router
**Storage**: Backend handles all persistence (Neon PostgreSQL via existing API)
**Testing**: Manual testing (no test framework currently configured)
**Target Platform**: Web browsers (desktop, tablet, mobile)
**Project Type**: Web application (Next.js frontend + FastAPI backend)
**Performance Goals**:
- Chat message send/receive < 5 seconds
- UI responsiveness < 100ms
- Task list refresh < 1 second
**Constraints**:
- Frontend-only changes (no backend modifications)
- Must work with existing authentication system
- Must integrate with existing task list component
- Responsive design (320px+ width)
**Scale/Scope**: Single-user chat interface, 50+ message history support

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Stateless Server Architecture ✅
- **Status**: PASS
- **Rationale**: Backend is already stateless. Frontend will not introduce server-side state. All conversation state managed by backend database.

### Security-First Design ✅
- **Status**: PASS
- **Rationale**: Using existing JWT authentication. Chat API already validates tokens. No new security vulnerabilities introduced.

### Tool-Driven Execution Pattern ✅
- **Status**: PASS (Backend concern)
- **Rationale**: Backend already implements MCP tools. Frontend only consumes the chat API.

### Agent-Database Separation ✅
- **Status**: PASS (Backend concern)
- **Rationale**: Backend already enforces separation. Frontend has no database access.

### Database as Single Source of Truth ✅
- **Status**: PASS
- **Rationale**: Backend persists all messages. Frontend loads conversation history from API.

**Overall**: All constitutional principles satisfied. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-chat-panel/
├── plan.md              # This file
├── research.md          # Phase 0 output (frontend patterns, layout strategies)
├── data-model.md        # Phase 1 output (frontend state models)
├── quickstart.md        # Phase 1 output (developer guide)
├── contracts/           # Phase 1 output (API contract documentation)
└── tasks.md             # Phase 2 output (NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/
│   │   └── dashboard/
│   │       └── page.tsx              # MODIFY: Add ChatPanel integration
│   ├── components/
│   │   ├── chat/                     # NEW: Chat components
│   │   │   ├── ChatPanel.tsx         # NEW: Main chat panel component
│   │   │   ├── ChatMessage.tsx       # NEW: Individual message display
│   │   │   ├── ChatInput.tsx         # NEW: Message input field
│   │   │   └── ChatHistory.tsx       # NEW: Message history display
│   │   └── tasks/
│   │       ├── TaskList.tsx          # EXISTING: May need refresh prop
│   │       ├── TaskForm.tsx          # EXISTING: No changes
│   │       └── TaskItem.tsx          # EXISTING: No changes
│   ├── hooks/
│   │   ├── useAuth.ts                # EXISTING: No changes
│   │   ├── useTasks.ts               # EXISTING: Expose fetchTasks
│   │   └── useChat.ts                # NEW: Chat state management
│   ├── lib/
│   │   ├── api.ts                    # EXISTING: No changes (already configured)
│   │   ├── auth.tsx                  # EXISTING: No changes
│   │   └── types.ts                  # MODIFY: Add chat types
│   └── styles/                       # NEW: Chat panel styles (if needed)
│       └── chat.module.css           # NEW: Chat-specific styles

backend/
├── src/
│   ├── api/
│   │   └── chat.py                   # EXISTING: No changes
│   ├── agent/                        # EXISTING: No changes
│   ├── tools/                        # EXISTING: No changes
│   └── models/                       # EXISTING: No changes
```

**Structure Decision**: Web application structure with frontend/backend separation. Frontend changes only in `frontend/src/` directory. Backend remains unchanged per requirements.

## Complexity Tracking

> No constitutional violations. This section is not applicable.

## Frontend Architecture Design

### Component Hierarchy

```
DashboardPage (page.tsx)
├── Header (existing)
│   ├── Title
│   └── Logout Button
├── Layout Container (NEW: two-column or stacked)
│   ├── TaskSection (existing, wrapped)
│   │   ├── TaskForm
│   │   └── TaskList
│   └── ChatPanel (NEW)
│       ├── ChatHistory
│       │   └── ChatMessage[] (user/assistant)
│       └── ChatInput
```

### State Management Strategy

**Local Component State** (React hooks):
- `useChat` hook manages:
  - `messages`: Array of chat messages
  - `conversationId`: Current conversation ID
  - `loading`: Message send in progress
  - `error`: Error message if any
  - `inputValue`: Current input field value

**Shared State** (via props/callbacks):
- `fetchTasks` from `useTasks` passed to ChatPanel for refresh trigger

**No Global State**: Using React Context for auth only (existing pattern)

### Layout Strategy

**Desktop (>= 1024px)**:
- Two-column layout: Tasks (left 50%) | Chat (right 50%)
- Both sections visible simultaneously
- Fixed heights with internal scrolling

**Tablet (768px - 1023px)**:
- Two-column layout: Tasks (left 40%) | Chat (right 60%)
- Or stacked layout with toggle button

**Mobile (< 768px)**:
- Stacked layout: Tasks above, Chat below
- Or tabbed interface to switch between views
- Chat panel collapsible/expandable

### API Integration Pattern

**Existing Pattern** (from useTasks.ts):
```typescript
const response = await apiClient.post('/endpoint', data);
```

**Chat API Integration**:
```typescript
// POST /api/chat
// Headers: Authorization: Bearer <token> (handled by apiClient)
// Body: { message: string, conversation_id?: string }
// Response: { response: string, conversation_id: string }
```

### Task Refresh Trigger Strategy

**Option 1: Response Parsing** (Recommended)
- Parse AI response text for keywords: "created", "updated", "deleted", "marked complete"
- Trigger `fetchTasks()` when task operation detected
- Simple, no backend changes needed

**Option 2: Backend Metadata** (Future enhancement)
- Backend returns `tool_calls_made: ["create_task", "update_task"]` in response
- Frontend checks metadata and refreshes accordingly
- Requires backend changes (out of scope)

**Decision**: Use Option 1 (response parsing) for initial implementation.

## Stateless Architecture Considerations

### Frontend State Management

**What Gets Stored Locally**:
- Current conversation_id (in component state, not localStorage)
- Message history (loaded from backend on mount)
- UI state (loading, error, input value)

**What Gets Persisted to Backend**:
- All user messages (via POST /api/chat)
- All assistant responses (backend persists automatically)

**State Reconstruction**:
- On page load: Fetch conversation history from backend
- On page refresh: Reload conversation from backend using conversation_id
- No localStorage for messages (backend is source of truth)

### Conversation Lifecycle

1. **First Visit**: No conversation_id → Backend creates new conversation
2. **Subsequent Messages**: Include conversation_id in requests
3. **Page Refresh**: Load conversation history from backend
4. **New Session**: Backend returns existing conversation for user

### Horizontal Scaling Compatibility

- ✅ No frontend-side session state
- ✅ All state in backend database
- ✅ conversation_id tracks conversation across requests
- ✅ Multiple tabs can share same conversation (if desired)

## Phase 0: Research & Design Decisions

### Research Topics

1. **Next.js App Router Layout Patterns**
   - Best practices for two-column layouts in App Router
   - CSS Grid vs Flexbox for responsive chat layouts
   - Scroll behavior management in chat interfaces

2. **React Chat UI Patterns**
   - Auto-scroll to bottom on new messages
   - Message grouping and timestamps
   - Loading indicators for async operations
   - Error handling and retry mechanisms

3. **Responsive Design Strategies**
   - Mobile-first vs desktop-first approach
   - Breakpoint selection for task/chat layout
   - Touch-friendly input areas
   - Keyboard accessibility (Enter to send, Shift+Enter for newline)

4. **Task Refresh Detection**
   - Natural language parsing for task operations
   - Regex patterns for detecting task actions
   - Debouncing refresh calls

5. **Conversation History Management**
   - Pagination vs infinite scroll
   - Message limit (50 messages per spec)
   - Initial load strategy

### Design Decisions to Document

**Decision 1: Layout Approach**
- Options: Side-by-side, Stacked, Tabbed, Overlay
- Evaluation criteria: Usability, responsiveness, implementation complexity
- Recommendation: Side-by-side on desktop, stacked on mobile

**Decision 2: Message Display**
- Options: Bubbles, List, Card-based
- Evaluation criteria: Readability, space efficiency, visual distinction
- Recommendation: Chat bubbles (user right-aligned, assistant left-aligned)

**Decision 3: Input Handling**
- Options: Single-line, Multi-line, Auto-expanding
- Evaluation criteria: User experience, mobile compatibility
- Recommendation: Multi-line textarea with Enter to send, Shift+Enter for newline

**Decision 4: Error Recovery**
- Options: Inline errors, Toast notifications, Retry buttons
- Evaluation criteria: User awareness, action clarity
- Recommendation: Inline error messages with retry button

## Phase 1: Data Models & Contracts

### Frontend Data Models

**ChatMessage** (TypeScript interface):
```typescript
interface ChatMessage {
  id: string;              // Unique message ID (generated client-side or from backend)
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}
```

**ChatState** (useChat hook state):
```typescript
interface ChatState {
  messages: ChatMessage[];
  conversationId: string | null;
  loading: boolean;
  error: string | null;
  inputValue: string;
}
```

**API Request/Response Types**:
```typescript
interface ChatRequest {
  message: string;
  conversation_id?: string;
}

interface ChatResponse {
  response: string;
  conversation_id: string;
}
```

### API Contract Documentation

**Endpoint**: `POST /api/chat`

**Authentication**: Required (JWT token in Authorization header)

**Request**:
```json
{
  "message": "Add a task to buy groceries",
  "conversation_id": "optional-uuid-string"
}
```

**Response** (Success - 200):
```json
{
  "response": "I've added 'Buy groceries' to your task list.",
  "conversation_id": "uuid-string"
}
```

**Response** (Error - 401):
```json
{
  "detail": "Invalid or expired token"
}
```

**Response** (Error - 500):
```json
{
  "detail": "Internal server error"
}
```

### Component Props Interfaces

**ChatPanel**:
```typescript
interface ChatPanelProps {
  onTaskOperation?: () => void;  // Callback to refresh tasks
}
```

**ChatMessage**:
```typescript
interface ChatMessageProps {
  message: ChatMessage;
}
```

**ChatInput**:
```typescript
interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled: boolean;
  placeholder?: string;
}
```

**ChatHistory**:
```typescript
interface ChatHistoryProps {
  messages: ChatMessage[];
  loading: boolean;
}
```

## Implementation Phases

### Phase 1: Core Chat UI (P1 - MVP)

**Files to Create**:
1. `frontend/src/hooks/useChat.ts` - Chat state management
2. `frontend/src/components/chat/ChatPanel.tsx` - Main container
3. `frontend/src/components/chat/ChatMessage.tsx` - Message display
4. `frontend/src/components/chat/ChatInput.tsx` - Input field
5. `frontend/src/components/chat/ChatHistory.tsx` - Message list

**Files to Modify**:
1. `frontend/src/app/dashboard/page.tsx` - Integrate ChatPanel
2. `frontend/src/lib/types.ts` - Add chat types

**Acceptance Criteria**:
- User can type message and press Enter to send
- Message appears in chat history
- AI response appears after backend processes
- Loading indicator shows during processing
- Error messages display on failure

### Phase 2: Conversation Persistence (P2)

**Implementation**:
- Load conversation history on component mount
- Include conversation_id in subsequent requests
- Handle page refresh (reload conversation)

**Acceptance Criteria**:
- Conversation history loads on page load
- Messages persist across page refreshes
- conversation_id maintained correctly

### Phase 3: Task List Integration (P2)

**Implementation**:
- Parse AI responses for task operation keywords
- Call `fetchTasks()` when operation detected
- Debounce refresh calls (avoid multiple refreshes)

**Acceptance Criteria**:
- Task list refreshes after "created task" response
- Task list refreshes after "updated task" response
- Task list refreshes after "deleted task" response
- No unnecessary refreshes on non-task messages

### Phase 4: Responsive Layout (P3)

**Implementation**:
- CSS Grid/Flexbox for responsive layout
- Media queries for breakpoints
- Mobile-optimized input area

**Acceptance Criteria**:
- Side-by-side layout on desktop (>= 1024px)
- Stacked layout on mobile (< 768px)
- Chat input remains accessible on mobile keyboard
- Scrolling works correctly on all screen sizes

### Phase 5: Polish & Edge Cases (P3)

**Implementation**:
- Auto-scroll to latest message
- Timestamp display
- Empty state message
- Keyboard shortcuts (Enter/Shift+Enter)
- Message length validation
- Network timeout handling

**Acceptance Criteria**:
- Chat auto-scrolls to bottom on new message
- Timestamps display correctly
- Empty state shows welcome message
- Enter sends, Shift+Enter adds newline
- Long messages handled gracefully
- Timeout errors display user-friendly message

## Testing Strategy

### Manual Testing Checklist

**Authentication**:
- [ ] Chat panel only accessible when logged in
- [ ] JWT token included in API requests
- [ ] 401 errors handled gracefully

**Message Flow**:
- [ ] User can send message
- [ ] Message appears in history immediately
- [ ] AI response appears after processing
- [ ] Loading indicator shows during processing
- [ ] Error messages display on failure

**Conversation Persistence**:
- [ ] Conversation history loads on page load
- [ ] Messages persist across page refresh
- [ ] conversation_id maintained correctly

**Task Integration**:
- [ ] Task list refreshes after create operation
- [ ] Task list refreshes after update operation
- [ ] Task list refreshes after delete operation
- [ ] No refresh on non-task messages

**Responsive Design**:
- [ ] Layout works on desktop (1920px)
- [ ] Layout works on tablet (768px)
- [ ] Layout works on mobile (375px)
- [ ] Input accessible on mobile keyboard

**Edge Cases**:
- [ ] Empty message submission prevented
- [ ] Very long messages handled
- [ ] Network timeout handled
- [ ] Rapid message sending handled
- [ ] Special characters/emojis display correctly

### Integration Testing

**End-to-End Scenarios**:
1. Login → Send message → Receive response → Verify task list
2. Create task via chat → Verify task appears in list
3. Update task via chat → Verify task updates in list
4. Delete task via chat → Verify task removed from list
5. Refresh page → Verify conversation persists

## Performance Considerations

### Optimization Strategies

**Message Rendering**:
- Use React.memo for ChatMessage components
- Virtualize message list if > 100 messages (future enhancement)
- Debounce scroll events

**API Calls**:
- Debounce task refresh calls (500ms)
- Cancel in-flight requests on unmount
- Implement request timeout (30s)

**State Updates**:
- Batch state updates where possible
- Avoid unnecessary re-renders
- Use useCallback for event handlers

### Expected Performance

- **Initial Load**: < 2 seconds (conversation history fetch)
- **Message Send**: < 5 seconds (backend processing time)
- **Task Refresh**: < 1 second (existing API)
- **UI Responsiveness**: < 100ms (input typing, scrolling)

## Risk Analysis

### Technical Risks

**Risk 1: Backend API Changes**
- **Probability**: Low
- **Impact**: High
- **Mitigation**: Document API contract, version API if needed

**Risk 2: Task Refresh Detection Accuracy**
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Use conservative keyword matching, allow manual refresh

**Risk 3: Mobile Layout Complexity**
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Start with simple stacked layout, iterate based on feedback

**Risk 4: Conversation History Performance**
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Limit to 50 messages, implement pagination if needed

### User Experience Risks

**Risk 1: Confusing Layout on Small Screens**
- **Mitigation**: User testing, clear visual separation, toggle button

**Risk 2: Unclear Task Operation Feedback**
- **Mitigation**: Explicit confirmation messages, visual task list updates

**Risk 3: Error Messages Too Technical**
- **Mitigation**: User-friendly error messages, actionable guidance

## Dependencies & Prerequisites

### External Dependencies

- ✅ Backend chat API (`POST /api/chat`) - Already implemented
- ✅ Authentication system (JWT) - Already implemented
- ✅ Task list API - Already implemented
- ✅ AI agent with MCP tools - Already implemented

### Internal Dependencies

- ✅ `apiClient` configured with auth interceptor
- ✅ `useAuth` hook for authentication state
- ✅ `useTasks` hook with `fetchTasks` method
- ✅ Existing dashboard layout structure

### No Blockers

All prerequisites are met. Implementation can proceed immediately.

## Deployment Considerations

### Environment Variables

No new environment variables required. Existing configuration sufficient:
- `NEXT_PUBLIC_API_URL` - Already configured for backend API

### Build Process

No changes to build process. Standard Next.js build:
```bash
cd frontend
npm run build
npm start
```

### Rollback Strategy

If issues arise:
1. Revert frontend changes (git revert)
2. Backend remains unchanged (no rollback needed)
3. Users can still access task list without chat panel

## Success Metrics

### Functional Metrics

- ✅ User can send message and receive response
- ✅ Conversation persists across page refreshes
- ✅ Task list refreshes after AI operations
- ✅ Layout responsive on all screen sizes
- ✅ Error handling works correctly

### Performance Metrics

- ✅ Message send/receive < 5 seconds
- ✅ Conversation history load < 2 seconds
- ✅ Task list refresh < 1 second
- ✅ UI responsiveness < 100ms

### Quality Metrics

- ✅ No console errors in browser
- ✅ No authentication bypass vulnerabilities
- ✅ No data leakage between users
- ✅ Accessible keyboard navigation
- ✅ Mobile-friendly touch targets

## Next Steps

1. **Phase 0**: Create `research.md` with detailed design decisions
2. **Phase 1**: Create `data-model.md` and `contracts/` documentation
3. **Phase 1**: Create `quickstart.md` for developers
4. **Phase 2**: Run `/sp.tasks` to generate implementation tasks
5. **Implementation**: Execute tasks in priority order (P1 → P2 → P3)
6. **Testing**: Manual testing checklist
7. **Review**: Code review and QA
8. **Deploy**: Merge to main and deploy

---

**Plan Status**: ✅ Complete - Ready for Phase 0 (Research)
**Next Command**: Create research.md with detailed design decisions
