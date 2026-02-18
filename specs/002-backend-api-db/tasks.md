# Tasks: Backend API & Database Layer

**Input**: Design documents from `/specs/002-backend-api-db/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No test tasks included (not explicitly requested in feature specification)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/src/` for source code, `backend/tests/` for tests
- All paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend directory structure per plan.md (backend/src/, backend/tests/)
- [X] T002 Create requirements.txt with FastAPI, SQLModel, asyncpg, pydantic, python-jose, passlib dependencies
- [X] T003 [P] Create backend/.env.example with DATABASE_URL, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS, CORS_ORIGINS, DEBUG
- [X] T004 [P] Create backend/README.md with setup instructions
- [X] T005 [P] Create backend/src/__init__.py (empty module marker)
- [X] T006 [P] Create backend/tests/__init__.py (empty module marker)

**Checkpoint**: Project structure ready for implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Create backend/src/config.py with Settings class using pydantic-settings for environment variables
- [X] T008 Create backend/src/main.py with FastAPI app initialization and CORS middleware configuration
- [X] T009 [P] Create backend/src/api/__init__.py (empty module marker)
- [X] T010 [P] Create backend/src/models/__init__.py (empty module marker)
- [X] T011 [P] Create backend/src/schemas/__init__.py (empty module marker)
- [X] T012 [P] Create backend/src/utils/__init__.py (empty module marker)
- [X] T013 [P] Create backend/src/middleware/__init__.py (empty module marker)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Database Connection and Schema Setup (Priority: P1) 🎯 MVP

**Goal**: Establish reliable database connection and define data models for User and Task entities

**Independent Test**: Run application startup, verify database connection succeeds, verify tables are created automatically, execute basic CRUD operations directly against database

### Implementation for User Story 1

- [X] T014 [P] [US1] Create User model in backend/src/models/user.py with id, email, hashed_password, created_at, updated_at fields
- [X] T015 [P] [US1] Create Task model in backend/src/models/task.py with id, user_id, title, description, is_completed, created_at, updated_at fields
- [X] T016 [US1] Create backend/src/database.py with async engine, session maker, get_session dependency, and create_db_and_tables function
- [X] T017 [US1] Update backend/src/main.py to call create_db_and_tables on startup event
- [X] T018 [US1] Add database connection test by starting server and verifying tables exist

**Checkpoint**: Database connection works, User and Task tables created automatically, basic persistence layer functional

---

## Phase 4: User Story 2 - User Management API (Priority: P1) 🎯 MVP

**Goal**: Provide registration and login endpoints with JWT token generation

**Independent Test**: Make HTTP POST to /auth/register with valid credentials, verify user created and JWT returned; make HTTP POST to /auth/login, verify JWT returned; verify tokens can be decoded

**Dependencies**: Requires Phase 3 (User model must exist)

### Implementation for User Story 2

- [X] T019 [P] [US2] Create backend/src/utils/security.py with hash_password and verify_password functions using passlib bcrypt
- [X] T020 [P] [US2] Create backend/src/utils/jwt.py with create_access_token, decode_token, and get_current_user dependency functions
- [X] T021 [P] [US2] Create UserRegister schema in backend/src/schemas/auth.py with email and password fields
- [X] T022 [P] [US2] Create UserLogin schema in backend/src/schemas/auth.py with email and password fields
- [X] T023 [P] [US2] Create UserResponse schema in backend/src/schemas/auth.py with id, email, created_at fields
- [X] T024 [P] [US2] Create AuthResponse schema in backend/src/schemas/auth.py with access_token, token_type, user fields
- [X] T025 [US2] Create backend/src/api/auth.py with APIRouter for /auth prefix
- [X] T026 [US2] Implement POST /auth/register endpoint in backend/src/api/auth.py (check email uniqueness, hash password, create user, generate JWT)
- [X] T027 [US2] Implement POST /auth/login endpoint in backend/src/api/auth.py (find user, verify password, generate JWT)
- [X] T028 [US2] Implement POST /auth/logout endpoint in backend/src/api/auth.py (informational endpoint)
- [X] T029 [US2] Register auth router in backend/src/main.py with app.include_router(auth.router)

**Checkpoint**: Users can register and login, JWT tokens are generated and can be verified, authentication system fully functional

---

## Phase 5: User Story 3 - Task CRUD Operations (Priority: P2)

**Goal**: Provide complete CRUD endpoints for task management with per-user data isolation

**Independent Test**: Make authenticated HTTP requests to create, read, update, delete tasks; verify only user's own tasks are returned; verify 403 error when accessing another user's task

**Dependencies**: Requires Phase 3 (Task model) and Phase 4 (JWT authentication)

### Implementation for User Story 3

- [X] T030 [P] [US3] Create TaskCreate schema in backend/src/schemas/task.py with title and description fields
- [X] T031 [P] [US3] Create TaskUpdate schema in backend/src/schemas/task.py with optional title, description, is_completed fields
- [X] T032 [P] [US3] Create TaskResponse schema in backend/src/schemas/task.py with all task fields
- [X] T033 [P] [US3] Create TaskList schema in backend/src/schemas/task.py with tasks array and total count
- [X] T034 [US3] Create backend/src/api/tasks.py with APIRouter for /tasks prefix
- [X] T035 [US3] Implement GET /tasks endpoint in backend/src/api/tasks.py (filter by user_id, order by created_at desc)
- [X] T036 [US3] Implement POST /tasks endpoint in backend/src/api/tasks.py (create task with authenticated user_id)
- [X] T037 [US3] Implement GET /tasks/{task_id} endpoint in backend/src/api/tasks.py (verify ownership, return 403 if not owner)
- [X] T038 [US3] Implement PUT /tasks/{task_id} endpoint in backend/src/api/tasks.py (verify ownership, update fields, update updated_at)
- [X] T039 [US3] Implement DELETE /tasks/{task_id} endpoint in backend/src/api/tasks.py (verify ownership, delete task)
- [X] T040 [US3] Register tasks router in backend/src/main.py with app.include_router(tasks.router)

**Checkpoint**: Complete task CRUD functionality working, per-user data isolation enforced, authorization checks passing

---

## Phase 6: User Story 4 - Data Validation and Error Handling (Priority: P2)

**Goal**: Add comprehensive input validation and standardized error responses

**Independent Test**: Send invalid requests to all endpoints (missing fields, malformed JSON, invalid IDs), verify appropriate error responses with clear messages

**Dependencies**: Requires Phase 4 and Phase 5 (endpoints must exist to add validation)

### Implementation for User Story 4

- [X] T041 [P] [US4] Create backend/src/utils/sanitization.py with sanitize_string and sanitize_email functions
- [X] T042 [US4] Add field validators to UserRegister schema in backend/src/schemas/auth.py (sanitize email)
- [X] T043 [US4] Add field validators to UserLogin schema in backend/src/schemas/auth.py (sanitize email)
- [X] T044 [US4] Add field validators to TaskCreate schema in backend/src/schemas/task.py (sanitize title and description)
- [X] T045 [US4] Add field validators to TaskUpdate schema in backend/src/schemas/task.py (sanitize title and description)
- [X] T046 [P] [US4] Create backend/src/middleware/error_handler.py with http_exception_handler function
- [X] T047 [P] [US4] Create validation_exception_handler in backend/src/middleware/error_handler.py for RequestValidationError
- [X] T048 [P] [US4] Create general_exception_handler in backend/src/middleware/error_handler.py for generic exceptions
- [X] T049 [US4] Register exception handlers in backend/src/main.py (HTTPException, RequestValidationError, Exception)

**Checkpoint**: All endpoints validate input, sanitize user data, return standardized error responses, no internal details exposed

---

## Phase 7: User Story 5 - API Performance and Optimization (Priority: P3)

**Goal**: Optimize database queries and add performance monitoring

**Independent Test**: Run load tests, measure response times (should be <200ms p95), verify indexes are used in queries, verify connection pooling works

**Dependencies**: Requires Phase 3, 4, 5 (all endpoints must exist to optimize)

### Implementation for User Story 5

- [X] T050 [P] [US5] Add index=True to email field in User model (backend/src/models/user.py)
- [X] T051 [P] [US5] Add index=True to user_id field in Task model (backend/src/models/task.py)
- [X] T052 [P] [US5] Add logging to POST /auth/register endpoint in backend/src/api/auth.py (log registration attempts)
- [X] T053 [P] [US5] Add logging to POST /auth/login endpoint in backend/src/api/auth.py (log login attempts and failures)
- [X] T054 [P] [US5] Add logging to task operations in backend/src/api/tasks.py (log create, update, delete)
- [X] T055 [US5] Verify async operations are used throughout (all route handlers and database operations)
- [X] T056 [US5] Configure connection pool settings in backend/src/database.py (set appropriate pool size)

**Checkpoint**: Database queries optimized with indexes, logging in place for debugging, performance targets met

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final production readiness improvements

- [X] T057 [P] Verify all environment variables documented in backend/.env.example
- [X] T058 [P] Add API documentation metadata to backend/src/main.py (title, description, version)
- [X] T059 [P] Verify OpenAPI docs accessible at /docs endpoint
- [X] T060 [P] Add health check endpoint GET / in backend/src/main.py
- [X] T061 Review security: verify no hardcoded secrets, passwords hashed, CORS configured
- [X] T062 Review error handling: verify all endpoints return appropriate status codes
- [X] T063 Final integration test: register user, login, create task, update task, delete task, logout

**Checkpoint**: Backend API fully functional, documented, secure, and production-ready

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P1): Depends on User Story 1 (needs User model)
  - User Story 3 (P2): Depends on User Story 1 (needs Task model) and User Story 2 (needs JWT auth)
  - User Story 4 (P2): Depends on User Story 2 and 3 (needs endpoints to validate)
  - User Story 5 (P3): Depends on User Story 1, 2, 3 (needs code to optimize)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundation only - No dependencies on other stories
- **User Story 2 (P1)**: Depends on User Story 1 (User model must exist)
- **User Story 3 (P2)**: Depends on User Story 1 (Task model) and User Story 2 (JWT authentication)
- **User Story 4 (P2)**: Depends on User Story 2 and 3 (endpoints must exist)
- **User Story 5 (P3)**: Depends on User Story 1, 2, 3 (code must exist to optimize)

### Within Each User Story

- Models before endpoints
- Schemas before endpoints
- Utilities before endpoints that use them
- Core implementation before optimization

### Parallel Opportunities

**Phase 1 (Setup)**: Tasks T003-T006 can all run in parallel (different files)

**Phase 2 (Foundational)**: Tasks T009-T013 can all run in parallel (different __init__.py files)

**Phase 3 (US1)**:
- Tasks T014-T015 can run in parallel (different model files)

**Phase 4 (US2)**:
- Tasks T019-T020 can run in parallel (different utility files)
- Tasks T021-T024 can run in parallel (different schema classes in same file)

**Phase 5 (US3)**:
- Tasks T030-T033 can run in parallel (different schema classes in same file)

**Phase 6 (US4)**:
- Tasks T046-T048 can run in parallel (different handler functions in same file)

**Phase 7 (US5)**:
- Tasks T050-T054 can run in parallel (different files)

**Phase 8 (Polish)**:
- Tasks T057-T060 can run in parallel (different concerns)

---

## Parallel Example: User Story 2

```bash
# Launch all utility files together:
Task T019: "Create backend/src/utils/security.py with password hashing"
Task T020: "Create backend/src/utils/jwt.py with JWT functions"

# Launch all schema classes together:
Task T021: "Create UserRegister schema"
Task T022: "Create UserLogin schema"
Task T023: "Create UserResponse schema"
Task T024: "Create AuthResponse schema"

# Then sequentially:
Task T025: "Create auth router"
Task T026: "Implement register endpoint"
Task T027: "Implement login endpoint"
Task T028: "Implement logout endpoint"
Task T029: "Register router in main.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T013) - CRITICAL
3. Complete Phase 3: User Story 1 (T014-T018) - Database & Models
4. Complete Phase 4: User Story 2 (T019-T029) - Authentication
5. **STOP and VALIDATE**: Test registration, login, JWT generation, database persistence
6. Deploy/demo if ready - this is a functional MVP!

### Incremental Delivery

1. **Foundation** (Phases 1-2) → Project structure and configuration ready
2. **MVP** (Phases 3-4) → Database connection and user authentication working
3. **Core Functionality** (Phase 5) → Complete task CRUD operations
4. **Production Ready** (Phases 6-7) → Validation, error handling, performance optimization
5. **Polish** (Phase 8) → Final checks and documentation

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (Phases 1-2)
2. **Once Foundational is done, split work**:
   - Developer A: User Story 1 (Database & Models)
   - Developer B: User Story 2 (Authentication) - starts after US1 models exist
   - Developer C: User Story 3 (Task CRUD) - starts after US1 and US2 complete
3. **Stories integrate sequentially** due to dependencies, but parallel work possible within each story

---

## Task Summary

**Total Tasks**: 63 tasks

**Tasks per User Story**:
- Setup: 6 tasks
- Foundational: 7 tasks (BLOCKS all stories)
- User Story 1 (P1): 5 tasks - Database Connection and Schema Setup
- User Story 2 (P1): 11 tasks - User Management API
- User Story 3 (P2): 11 tasks - Task CRUD Operations
- User Story 4 (P2): 9 tasks - Data Validation and Error Handling
- User Story 5 (P3): 7 tasks - API Performance and Optimization
- Polish: 7 tasks

**Parallel Opportunities**: 24 tasks marked [P] can run in parallel

**Independent Test Criteria**:
- US1: Start server, verify database connection, verify tables created, execute basic queries
- US2: Register user, login, verify JWT token generated and can be decoded
- US3: Create task, get tasks, update task, delete task, verify per-user isolation
- US4: Send invalid requests, verify error responses with clear messages
- US5: Run load tests, verify response times <200ms, verify indexes used

**Suggested MVP Scope**: Phases 1-4 (Setup + Foundational + US1 + US2) = 29 tasks

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All file paths are explicit for immediate execution
- No test tasks included (not requested in specification)
