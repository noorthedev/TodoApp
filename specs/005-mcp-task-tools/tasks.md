# Tasks: MCP Server & Task Tools Integration

**Input**: Design documents from `/specs/005-mcp-task-tools/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in specification - focusing on implementation tasks only

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/src/`, `frontend/src/`
- Backend: FastAPI with SQLModel
- Frontend: Next.js (no changes in this feature)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [x] T001 Install MCP SDK and OpenAI SDK dependencies in backend/requirements.txt
- [x] T002 Add OPENAI_API_KEY to backend/.env configuration file
- [x] T003 [P] Update backend/src/config.py to load OpenAI API key from environment

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create Conversation model in backend/src/models/conversation.py with user_id foreign key
- [x] T005 [P] Create Message model in backend/src/models/message.py with conversation_id foreign key and role field
- [x] T006 [P] Update backend/src/models/__init__.py to export Conversation and Message models
- [x] T007 Run database migration to create conversations and messages tables (Alembic or auto-create)
- [x] T008 Create conversation utility functions in backend/src/utils/conversation.py (get_or_create_conversation, load_conversation_history, persist_message)

**Checkpoint**: Database models ready - AI agent infrastructure can now begin

---

## Phase 2b: Foundational (Phase-III AI Agent Infrastructure)

**Purpose**: AI agent and MCP tool infrastructure that MUST be complete before agent-driven user stories

**⚠️ CRITICAL**: No agent-driven user story work can begin until this phase is complete

- [x] T009 Create agent configuration in backend/src/agent/config.py with OpenAI client initialization
- [x] T010 [P] Create system prompts in backend/src/agent/prompts.py defining agent behavior and tool usage guidelines
- [x] T011 [P] Create MCP tool registry in backend/src/tools/registry.py with tool catalog structure
- [x] T012 [P] Create tool decorator in backend/src/tools/utils.py for consistent error handling and structured responses
- [x] T013 Create agent invocation logic in backend/src/agent/agent.py with function calling support
- [x] T014 [P] Create chat request/response schemas in backend/src/schemas/chat.py (ChatRequest with message field, ChatResponse with response and conversation_id)
- [x] T015 Create chat endpoint skeleton in backend/src/api/chat.py with JWT authentication dependency
- [x] T016 Implement conversation persistence flow in chat endpoint (steps 1-4: authenticate, get conversation, load history, persist user message)
- [x] T017 Implement agent invocation flow in chat endpoint (steps 5-7: prepare context, invoke agent, handle response)
- [x] T018 Implement response persistence flow in chat endpoint (steps 8-10: persist agent message, update conversation timestamp, return response)
- [x] T019 [P] Update backend/src/main.py to register chat router
- [x] T020 [P] Update backend/src/agent/__init__.py to export agent invocation function

**Checkpoint**: AI agent infrastructure ready - agent-driven user stories can now begin in parallel

---

## Phase 3: User Story 1 - Create and List Tasks (Priority P1)

**Story Goal**: Users can create new tasks and view their task list through natural conversation with the AI assistant

**Independent Test**: Send chat messages "Add a task to buy groceries" and "Show me my tasks", verify tasks are created and listed correctly with proper user isolation

**Dependencies**: Phase 2b must be complete

### Implementation Tasks

- [x] T021 [P] [US1] Implement add_task tool in backend/src/tools/task_tools.py with title and description parameters
- [x] T022 [P] [US1] Implement list_tasks tool in backend/src/tools/task_tools.py with user_id filtering
- [x] T023 [US1] Add authorization validation to add_task tool (extract user_id from user_context, force on created task)
- [x] T024 [US1] Add authorization validation to list_tasks tool (filter tasks by user_id from user_context)
- [x] T025 [US1] Implement structured response format for add_task tool (success with task data or error message)
- [x] T026 [US1] Implement structured response format for list_tasks tool (success with tasks array and count or error message)
- [x] T027 [US1] Register add_task and list_tasks tools in backend/src/tools/registry.py with input/output schemas
- [x] T028 [US1] Update backend/src/tools/__init__.py to export add_task and list_tasks functions
- [x] T029 [US1] Update agent system prompt in backend/src/agent/prompts.py to include add_task and list_tasks tool descriptions
- [x] T030 [US1] Verify agent can discover and call add_task tool when user says "Add a task to buy groceries"
- [x] T031 [US1] Verify agent can discover and call list_tasks tool when user says "Show me my tasks"

**Story Completion Criteria**:
- ✅ Users can create tasks through natural language
- ✅ Users can view their task list through natural language
- ✅ Tasks are correctly isolated per user (user A cannot see user B's tasks)
- ✅ Agent correctly interprets create and list intents
- ✅ All tool responses follow structured format

---

## Phase 4: User Story 2 - Complete and Delete Tasks (Priority P2)

**Story Goal**: Users can mark tasks as complete or remove tasks they no longer need through natural conversation

**Independent Test**: Create tasks, then use phrases like "Mark the groceries task as done" or "Delete the meeting task", verify operations succeed and only affect authenticated user's tasks

**Dependencies**: Phase 3 (US1) must be complete (requires tasks to exist)

### Implementation Tasks

- [x] T032 [P] [US2] Implement complete_task tool in backend/src/tools/task_tools.py with task_id parameter
- [x] T033 [P] [US2] Implement delete_task tool in backend/src/tools/task_tools.py with task_id parameter
- [x] T034 [US2] Add ownership verification to complete_task tool (verify task exists and task.user_id matches user_context user_id)
- [x] T035 [US2] Add ownership verification to delete_task tool (verify task exists and task.user_id matches user_context user_id)
- [x] T036 [US2] Implement structured response format for complete_task tool (success with updated task or error message)
- [x] T037 [US2] Implement structured response format for delete_task tool (success with deleted flag or error message)
- [x] T038 [US2] Add audit logging to delete_task tool for deletion tracking
- [x] T039 [US2] Register complete_task and delete_task tools in backend/src/tools/registry.py with input/output schemas
- [x] T040 [US2] Update backend/src/tools/__init__.py to export complete_task and delete_task functions
- [x] T041 [US2] Update agent system prompt in backend/src/agent/prompts.py to include complete_task and delete_task tool descriptions
- [x] T042 [US2] Verify agent can discover and call complete_task tool when user says "Mark the groceries task as done"
- [x] T043 [US2] Verify agent can discover and call delete_task tool when user says "Delete the meeting task"

**Story Completion Criteria**:
- ✅ Users can mark tasks as complete through natural language
- ✅ Users can delete tasks through natural language
- ✅ Operations only affect authenticated user's tasks (cross-user protection)
- ✅ Agent correctly interprets complete and delete intents
- ✅ Deletion operations are logged for audit trail
- ✅ All tool responses follow structured format

---

## Phase 5: User Story 3 - Update Task Details (Priority P3)

**Story Goal**: Users can modify task titles or descriptions through conversation, allowing them to refine task information as needs change

**Independent Test**: Create a task, then use phrases like "Change the groceries task to 'Buy organic groceries'", verify update succeeds with proper authorization

**Dependencies**: Phase 3 (US1) must be complete (requires tasks to exist)

### Implementation Tasks

- [x] T044 [P] [US3] Implement update_task tool in backend/src/tools/task_tools.py with task_id, title, and description parameters
- [x] T045 [US3] Add ownership verification to update_task tool (verify task exists and task.user_id matches user_context user_id)
- [x] T046 [US3] Add validation to update_task tool (ensure at least one field - title or description - is provided)
- [x] T047 [US3] Implement structured response format for update_task tool (success with updated task or error message)
- [x] T048 [US3] Register update_task tool in backend/src/tools/registry.py with input/output schema
- [x] T049 [US3] Update backend/src/tools/__init__.py to export update_task function
- [x] T050 [US3] Update agent system prompt in backend/src/agent/prompts.py to include update_task tool description
- [x] T051 [US3] Verify agent can discover and call update_task tool when user says "Change the groceries task to 'Buy organic groceries'"

**Story Completion Criteria**:
- ✅ Users can update task titles through natural language
- ✅ Users can update task descriptions through natural language
- ✅ Updates only affect authenticated user's tasks (cross-user protection)
- ✅ Agent correctly interprets update intents
- ✅ Tool validates at least one field is provided
- ✅ All tool responses follow structured format

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements, error handling improvements, and documentation

- [x] T052 [P] Add comprehensive error handling to all MCP tools (database errors, validation errors, authorization failures)
- [x] T053 [P] Add logging to all MCP tools for debugging and monitoring (tool invocation, authorization checks, errors)
- [x] T054 [P] Implement timeout handling for OpenAI API calls in backend/src/agent/agent.py (10 second timeout)
- [x] T055 [P] Add user-friendly error messages for common failure scenarios (task not found, unauthorized access, validation errors)
- [x] T056 [P] Verify conversation history truncation works correctly (limit to 50 messages for token management)
- [x] T057 [P] Add API documentation for chat endpoint in backend/src/api/chat.py (docstrings with request/response examples)
- [x] T058 [P] Update README.md with setup instructions for OpenAI API key and MCP tools
- [x] T059 Perform end-to-end integration test (Frontend → Chat API → Agent → MCP Tool → DB → Response)
- [x] T060 [P] Verify authorization isolation across all tools (user A cannot access user B's tasks)
- [x] T061 [P] Verify stateless architecture (server restart does not lose conversation state)
- [x] T062 [P] Performance test: Verify chat endpoint responds within 5 seconds under normal load
- [x] T063 [P] Performance test: Verify system handles 100 concurrent users without errors

---

## Dependencies & Execution Strategy

### User Story Completion Order

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational - Database Models)
    ↓
Phase 2b (AI Agent Infrastructure)
    ↓
Phase 3 (US1 - Create & List) ← MVP SCOPE
    ↓
Phase 4 (US2 - Complete & Delete) ← Can run in parallel with Phase 5
    ↓
Phase 5 (US3 - Update) ← Can run in parallel with Phase 4
    ↓
Phase 6 (Polish)
```

### Parallel Execution Opportunities

**Within Phase 2 (Foundational)**:
- T005 (Message model) can run parallel with T004 (Conversation model)
- T006 (Update __init__.py) can run parallel with T008 (conversation utilities)

**Within Phase 2b (AI Agent Infrastructure)**:
- T010 (system prompts) can run parallel with T009 (agent config)
- T011 (tool registry) can run parallel with T010
- T012 (tool decorator) can run parallel with T011
- T014 (chat schemas) can run parallel with T013 (agent invocation)
- T019 (update main.py) can run parallel with T020 (update agent __init__.py)

**Within Phase 3 (US1)**:
- T021 (add_task tool) can run parallel with T022 (list_tasks tool)
- T025 (add_task response) can run parallel with T026 (list_tasks response)

**Within Phase 4 (US2)**:
- T032 (complete_task tool) can run parallel with T033 (delete_task tool)
- T036 (complete_task response) can run parallel with T037 (delete_task response)

**Phase 4 and Phase 5 can run in parallel** (US2 and US3 are independent)

**Within Phase 6 (Polish)**:
- Most tasks (T052-T058, T060-T063) can run in parallel as they are independent refinements

### MVP Scope Recommendation

**Minimum Viable Product**: Phase 1 + Phase 2 + Phase 2b + Phase 3 (US1 only)

This delivers:
- ✅ Users can create tasks via natural language
- ✅ Users can view their task list via natural language
- ✅ Full AI agent integration with MCP tools
- ✅ Stateless conversation persistence
- ✅ Per-user data isolation
- ✅ JWT authentication

**Incremental Delivery**:
1. **Sprint 1**: MVP (Phases 1-3) - Core value proposition
2. **Sprint 2**: US2 (Phase 4) - Task lifecycle management
3. **Sprint 3**: US3 (Phase 5) - Task editing capability
4. **Sprint 4**: Polish (Phase 6) - Production readiness

---

## Implementation Strategy

### Approach

**Incremental Delivery by User Story**: Each user story phase delivers a complete, independently testable increment of functionality. This enables:
- Early user feedback on core features (US1)
- Parallel development of US2 and US3 after US1 is complete
- Flexible prioritization (can ship MVP with just US1)
- Clear acceptance criteria per story

### Risk Mitigation

**High-Risk Areas**:
1. **Agent Intent Recognition**: Agent may misinterpret user intent
   - Mitigation: Clear system prompts (T010), comprehensive tool descriptions (T029, T041, T050)

2. **Authorization Bypass**: Tools might not properly validate user_id
   - Mitigation: Explicit authorization checks in every tool (T023, T024, T034, T035, T045)

3. **OpenAI API Failures**: External API may timeout or fail
   - Mitigation: Timeout handling (T054), graceful error messages (T055)

4. **Conversation State Loss**: Stateless architecture must persist all state
   - Mitigation: Immediate persistence (T016, T018), verification test (T061)

### Testing Strategy

**Per User Story**:
- Each story has independent test criteria
- Verify authorization isolation for each story
- Test natural language variations for each story

**Integration Testing**:
- End-to-end flow test (T059)
- Cross-user isolation test (T060)
- Stateless architecture test (T061)
- Performance tests (T062, T063)

---

## Task Summary

**Total Tasks**: 63 tasks

**Tasks per Phase**:
- Phase 1 (Setup): 3 tasks
- Phase 2 (Foundational): 5 tasks
- Phase 2b (AI Agent Infrastructure): 12 tasks
- Phase 3 (US1 - Create & List): 11 tasks
- Phase 4 (US2 - Complete & Delete): 12 tasks
- Phase 5 (US3 - Update): 8 tasks
- Phase 6 (Polish): 12 tasks

**Tasks per User Story**:
- US1 (P1): 11 tasks
- US2 (P2): 12 tasks
- US3 (P3): 8 tasks
- Infrastructure: 20 tasks
- Polish: 12 tasks

**Parallel Opportunities**: 28 tasks marked with [P] can run in parallel with other tasks in their phase

**MVP Scope**: 31 tasks (Phases 1-3) deliver core value proposition

**Format Validation**: ✅ All tasks follow checklist format with ID, optional [P] marker, [Story] label for user story tasks, and file paths
