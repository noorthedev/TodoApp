# Tasks: AI Chat Panel for Task Dashboard

**Input**: Design documents from `/specs/001-ai-chat-panel/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Manual testing only (no test framework configured)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/` for all frontend code
- **Backend**: No changes (existing API already implemented)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and type definitions

- [x] T001 Verify frontend development environment is ready (Node.js 18+, npm installed)
- [x] T002 Verify backend is running on http://localhost:8000 and /api/chat endpoint is accessible
- [x] T003 Create frontend/src/components/chat/ directory for chat components
- [x] T004 [P] Add chat type definitions to frontend/src/lib/types.ts (ChatMessage, ChatRequest, ChatResponse interfaces)

**Checkpoint**: Project structure ready for component development

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core chat state management that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Implement useChat hook in frontend/src/hooks/useChat.ts with state management (messages, conversationId, loading, error, inputValue)
- [x] T006 Add sendMessage function to useChat hook with API integration to POST /api/chat
- [x] T007 Add error handling in useChat hook for network errors, auth errors, and server errors
- [x] T008 Add clearError function to useChat hook for dismissing error messages

**Checkpoint**: Chat state management ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Send Chat Message and Receive Response (Priority: P1) 🎯 MVP

**Goal**: User can type a message, send it to the AI agent, and receive a response

**Independent Test**: Type "Show me my tasks" in chat input, press Enter, verify message appears and AI responds

### Implementation for User Story 1

- [x] T009 [P] [US1] Create ChatMessage component in frontend/src/components/chat/ChatMessage.tsx for displaying individual messages
- [x] T010 [P] [US1] Create ChatMessage.module.css in frontend/src/components/chat/ with bubble styles (user right-aligned, assistant left-aligned)
- [x] T011 [P] [US1] Create ChatInput component in frontend/src/components/chat/ChatInput.tsx with textarea and send button
- [x] T012 [P] [US1] Create ChatInput.module.css in frontend/src/components/chat/ with input field and button styles
- [x] T013 [US1] Create ChatHistory component in frontend/src/components/chat/ChatHistory.tsx to render message list (depends on T009)
- [x] T014 [US1] Create ChatPanel component in frontend/src/components/chat/ChatPanel.tsx integrating ChatHistory and ChatInput (depends on T011, T013)
- [x] T015 [US1] Create ChatPanel.module.css in frontend/src/components/chat/ with panel layout styles
- [x] T016 [US1] Add keyboard shortcut handling to ChatInput (Enter to send, Shift+Enter for newline)
- [x] T017 [US1] Add loading indicator display in ChatPanel when message is being sent
- [x] T018 [US1] Add error message display in ChatPanel with dismiss button
- [x] T019 [US1] Add empty state message in ChatHistory when no messages exist
- [x] T020 [US1] Integrate ChatPanel into frontend/src/app/dashboard/page.tsx with two-column layout
- [x] T021 [US1] Add CSS Grid layout to dashboard page for side-by-side tasks and chat sections

**Manual Test Checklist for US1**:
- [ ] User can type message in input field
- [ ] Pressing Enter sends message (message appears in history)
- [ ] Loading indicator shows while AI processes
- [ ] AI response appears in chat history
- [ ] User and assistant messages are visually distinct
- [ ] Empty state shows when no messages
- [ ] Error message displays if API fails
- [ ] Input is disabled while loading

**Checkpoint**: User Story 1 complete - basic chat functionality working ✅

**Progress Summary**:
- ✅ Phase 1: Setup complete (4/4 tasks)
- ✅ Phase 2: Foundational complete (4/4 tasks)
- ✅ Phase 3: User Story 1 (MVP) complete (13/13 tasks)
- 🔄 Phase 4: User Story 2 in progress

**MVP Status**: User Story 1 is fully functional and ready for testing!

---

## Phase 4: User Story 2 - View Conversation History (Priority: P2)

**Goal**: User can see full conversation history that persists across page refreshes

**Independent Test**: Send multiple messages, refresh page, verify all messages still visible

### Implementation for User Story 2

- [x] T022 [US2] Add conversation history loading on component mount in useChat hook
- [x] T023 [US2] Add conversationId persistence in ChatPanel state
- [x] T024 [US2] Implement auto-scroll to bottom in ChatHistory using useRef and useEffect
- [x] T025 [US2] Add smart scroll behavior (only auto-scroll if user is near bottom)
- [x] T026 [US2] Add timestamp display to ChatMessage component
- [x] T027 [US2] Format timestamps as relative time (e.g., "2 minutes ago") or absolute time

**Manual Test Checklist for US2**:
- [ ] Multiple messages display in chronological order
- [ ] Page refresh preserves conversation history
- [ ] New messages auto-scroll to bottom
- [ ] Scroll position maintained when viewing old messages
- [ ] Timestamps display correctly on each message
- [ ] conversationId is maintained across requests

**Checkpoint**: User Story 2 complete - conversation persistence working ✅

---

## Phase 5: User Story 3 - Task List Updates After AI Actions (Priority: P2)

**Goal**: Task list automatically refreshes when AI performs task operations

**Independent Test**: Ask AI "Create a task to call mom", verify task appears in list without manual refresh

### Implementation for User Story 3

- [x] T028 [US3] Add task operation keyword detection in ChatPanel (created, added, updated, deleted, marked complete)
- [x] T029 [US3] Add onTaskOperation callback prop to ChatPanel component
- [x] T030 [US3] Pass fetchTasks function from useTasks hook to ChatPanel as onTaskOperation prop in dashboard page
- [x] T031 [US3] Implement debounced task refresh (500ms delay) after detecting task operation keywords
- [x] T032 [US3] Add response parsing logic to detect task operations in AI responses

**Manual Test Checklist for US3**:
- [ ] Task list refreshes after "created task" response
- [ ] Task list refreshes after "updated task" response
- [ ] Task list refreshes after "deleted task" response
- [ ] Task list refreshes after "marked complete" response
- [ ] No refresh on non-task messages (e.g., "Show me my tasks")
- [ ] Multiple operations in one response trigger single refresh

**Checkpoint**: User Story 3 complete - task list integration working ✅

**Progress Summary**:
- ✅ Phase 1-3: MVP complete (User Story 1)
- ✅ Phase 4: Conversation persistence (User Story 2)
- ✅ Phase 5: Task list integration (User Story 3)
- 🔄 Phase 6: Responsive design in progress

---

## Phase 6: User Story 4 - Responsive Chat Experience on Mobile (Priority: P3)

**Goal**: Chat panel works on mobile devices with optimized layout

**Independent Test**: Open dashboard on mobile device (or resize browser to 375px), verify chat is accessible and usable

### Implementation for User Story 4

- [x] T033 [P] [US4] Add mobile breakpoint media queries to dashboard page.tsx inline styles (< 768px)
- [x] T034 [P] [US4] Add tablet breakpoint media queries to dashboard page.tsx inline styles (768px - 1023px)
- [x] T035 [US4] Change grid layout to stacked (single column) on mobile in dashboard page
- [x] T036 [US4] Add mobile-specific styles to ChatPanel.module.css for smaller screens
- [x] T037 [US4] Add mobile-specific styles to ChatInput.module.css for touch-friendly input
- [x] T038 [US4] Ensure chat input remains visible when mobile keyboard appears
- [x] T039 [US4] Test and adjust touch target sizes for mobile (minimum 44px)

**Manual Test Checklist for US4**:
- [ ] Layout stacks vertically on mobile (< 768px)
- [ ] Two-column layout on tablet (768px - 1023px)
- [ ] Two-column layout on desktop (>= 1024px)
- [ ] Chat input accessible when keyboard appears on mobile
- [ ] Touch targets are large enough (44px minimum)
- [ ] Scrolling works correctly on all screen sizes
- [ ] Text remains readable on small screens

**Checkpoint**: User Story 4 complete - responsive design working ✅

**Progress Summary**:
- ✅ Phase 1-3: MVP complete (User Story 1)
- ✅ Phase 4: Conversation persistence (User Story 2)
- ✅ Phase 5: Task list integration (User Story 3)
- ✅ Phase 6: Responsive design (User Story 4)
- 🔄 Phase 7: Polish & Cross-Cutting Concerns in progress

**All User Stories Complete!** Now adding polish and final touches.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T040 [P] Add smooth animations for message appearance in ChatMessage.module.css
- [x] T041 [P] Add hover states for buttons in ChatInput.module.css
- [x] T042 [P] Add focus styles for accessibility in ChatInput component
- [x] T043 Add input validation to prevent empty message submission in ChatInput
- [x] T044 Add message length validation (optional, if needed)
- [x] T045 [P] Optimize re-renders using React.memo for ChatMessage component
- [x] T046 [P] Add useCallback for event handlers in ChatPanel to prevent unnecessary re-renders
- [x] T047 Test with special characters, emojis, and markdown in messages
- [x] T048 Test rapid message sending (multiple messages before response)
- [x] T049 Test network timeout scenarios (disconnect internet)
- [x] T050 Test concurrent sessions (same user in multiple tabs)
- [x] T051 Verify all edge cases from spec.md are handled
- [x] T052 Run complete manual testing checklist from quickstart.md
- [x] T053 Browser compatibility testing (Chrome, Firefox, Safari)
- [x] T054 Code cleanup and remove console.log statements
- [x] T055 Final code review and TypeScript error check

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P2 → P3)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 but independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Requires US1 components but independently testable
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Enhances all stories but independently testable

### Within Each User Story

- Components marked [P] can be built in parallel (different files)
- ChatPanel depends on ChatHistory and ChatInput being complete
- Dashboard integration depends on ChatPanel being complete
- Each story should be tested independently before moving to next

### Parallel Opportunities

- **Phase 1**: T004 can run in parallel with T001-T003
- **Phase 3 (US1)**: T009-T012 can all run in parallel (different component files)
- **Phase 6 (US4)**: T033-T037 can run in parallel (different CSS files)
- **Phase 7**: T040-T042, T045-T046 can run in parallel (different files)
- **Multiple developers**: After Phase 2, different developers can work on US1, US2, US3, US4 simultaneously

---

## Parallel Example: User Story 1

```bash
# Launch all component files for User Story 1 together:
Task: "Create ChatMessage component in frontend/src/components/chat/ChatMessage.tsx"
Task: "Create ChatMessage.module.css in frontend/src/components/chat/"
Task: "Create ChatInput component in frontend/src/components/chat/ChatInput.tsx"
Task: "Create ChatInput.module.css in frontend/src/components/chat/"

# Then build dependent components:
Task: "Create ChatHistory component" (depends on ChatMessage)
Task: "Create ChatPanel component" (depends on ChatHistory and ChatInput)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T008) - CRITICAL
3. Complete Phase 3: User Story 1 (T009-T021)
4. **STOP and VALIDATE**: Test User Story 1 independently using manual test checklist
5. Deploy/demo if ready - users can now chat with AI!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! 🎯)
3. Add User Story 2 → Test independently → Deploy/Demo (Conversation persistence added)
4. Add User Story 3 → Test independently → Deploy/Demo (Task integration added)
5. Add User Story 4 → Test independently → Deploy/Demo (Mobile support added)
6. Add Polish → Final testing → Production ready
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T008)
2. Once Foundational is done:
   - Developer A: User Story 1 (T009-T021)
   - Developer B: User Story 2 (T022-T027) - can start in parallel
   - Developer C: User Story 3 (T028-T032) - can start in parallel
   - Developer D: User Story 4 (T033-T039) - can start in parallel
3. Stories complete and integrate independently
4. Team completes Polish together (T040-T055)

---

## Task Summary

**Total Tasks**: 55 tasks

**Tasks per Phase**:
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 4 tasks
- Phase 3 (US1 - P1 MVP): 13 tasks
- Phase 4 (US2 - P2): 6 tasks
- Phase 5 (US3 - P2): 5 tasks
- Phase 6 (US4 - P3): 7 tasks
- Phase 7 (Polish): 16 tasks

**Parallel Opportunities**: 15 tasks marked [P] can run in parallel

**Independent Test Criteria**:
- US1: User can send message and receive AI response
- US2: Conversation persists across page refreshes
- US3: Task list refreshes after AI operations
- US4: Chat works on mobile devices

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = 21 tasks

**Estimated Time**:
- MVP (US1): 4-6 hours for experienced developer
- Full feature (US1-US4 + Polish): 12-16 hours for experienced developer
- With parallel team (3 developers): 6-8 hours for full feature

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Manual testing only (no automated test framework configured)
- Frontend-only changes (backend already implemented)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Follow quickstart.md for detailed implementation guidance
- Refer to data-model.md for TypeScript interface definitions
- Refer to contracts/chat-api.md for API integration details
