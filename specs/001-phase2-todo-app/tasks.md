# Tasks: Phase 2 Todo Full-Stack Web Application

**Input**: Design documents from `/specs/001-phase2-todo-app/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: No test tasks included (not explicitly requested in specification)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/` for source code, `backend/tests/` for tests
- **Frontend**: `frontend/src/` for source code, `frontend/tests/` for tests
- Paths follow the web application structure defined in plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure: backend/src/{models,schemas,api,middleware,utils}, backend/tests/
- [x] T002 Create frontend directory structure: frontend/src/{app,components,lib,hooks}, frontend/tests/
- [x] T003 [P] Initialize backend Python project with requirements.txt (fastapi, uvicorn, sqlmodel, asyncpg, pydantic, python-jose, passlib, python-multipart)
- [x] T004 [P] Initialize frontend Next.js project with package.json (next, react, axios, typescript)
- [x] T005 [P] Create backend/.env.example with DATABASE_URL, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS, CORS_ORIGINS, DEBUG
- [x] T006 [P] Create frontend/.env.local.example with NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET, NEXT_PUBLIC_APP_URL
- [x] T007 [P] Configure TypeScript in frontend/tsconfig.json for Next.js App Router
- [x] T008 [P] Create backend/README.md with setup instructions
- [x] T009 [P] Create frontend/README.md with setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T010 Create User SQLModel in backend/src/models/user.py with id, email, hashed_password, created_at, updated_at
- [x] T011 Create Task SQLModel in backend/src/models/task.py with id, user_id, title, description, is_completed, created_at, updated_at
- [x] T012 Create database connection and session management in backend/src/database.py with async engine and get_session dependency
- [x] T013 Create environment configuration in backend/src/config.py loading from .env file
- [x] T014 [P] Create JWT utilities in backend/src/utils/jwt.py with create_access_token, decode_token, get_current_user dependency
- [x] T015 [P] Create password hashing utilities in backend/src/utils/security.py with hash_password and verify_password functions
- [x] T016 Create FastAPI application in backend/src/main.py with CORS middleware configuration
- [x] T017 Create database initialization script in backend/src/database.py with create_db_and_tables function
- [x] T018 [P] Create API client configuration in frontend/src/lib/api.ts with Axios instance, base URL, and request/response interceptors
- [x] T019 [P] Create TypeScript type definitions in frontend/src/lib/types.ts for User, Task, AuthResponse, TaskResponse

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration and Authentication (Priority: P1) 🎯 MVP

**Goal**: Enable users to register accounts and authenticate with JWT tokens

**Independent Test**: Register a new user account, log in with credentials, verify JWT token is received and grants access to protected routes

### Implementation for User Story 1

- [x] T020 [P] [US1] Create UserRegister Pydantic schema in backend/src/schemas/auth.py with email and password validation
- [x] T021 [P] [US1] Create UserLogin Pydantic schema in backend/src/schemas/auth.py with email and password fields
- [x] T022 [P] [US1] Create AuthResponse Pydantic schema in backend/src/schemas/auth.py with access_token, token_type, and user fields
- [x] T023 [P] [US1] Create UserResponse Pydantic schema in backend/src/schemas/auth.py with id, email, created_at
- [x] T024 [US1] Implement POST /auth/register endpoint in backend/src/api/auth.py with email uniqueness check, password hashing, user creation, and JWT token generation
- [x] T025 [US1] Implement POST /auth/login endpoint in backend/src/api/auth.py with credential verification and JWT token generation
- [x] T026 [US1] Register auth router in backend/src/main.py with /auth prefix
- [x] T027 [P] [US1] Create auth context provider in frontend/src/lib/auth.ts with login, logout, and user state management
- [x] T028 [P] [US1] Create useAuth custom hook in frontend/src/hooks/useAuth.ts exposing auth context
- [x] T029 [US1] Create root layout in frontend/src/app/layout.tsx wrapping children with auth context provider
- [x] T030 [US1] Create home page in frontend/src/app/page.tsx with links to login and register
- [x] T031 [P] [US1] Create LoginForm component in frontend/src/components/auth/LoginForm.tsx with email/password inputs and API call
- [x] T032 [P] [US1] Create RegisterForm component in frontend/src/components/auth/RegisterForm.tsx with email/password inputs and API call
- [x] T033 [US1] Create login page in frontend/src/app/login/page.tsx rendering LoginForm
- [x] T034 [US1] Create register page in frontend/src/app/register/page.tsx rendering RegisterForm
- [x] T035 [US1] Update API client in frontend/src/lib/api.ts to inject JWT token from localStorage in request interceptor

**Checkpoint**: At this point, User Story 1 should be fully functional - users can register, login, and receive JWT tokens

---

## Phase 4: User Story 2 - Create and View Personal Tasks (Priority: P1) 🎯 MVP

**Goal**: Enable authenticated users to create tasks and view their personal task list with strict per-user data isolation

**Independent Test**: Log in as a user, create multiple tasks, view task list, verify only that user's tasks appear (test with multiple accounts to confirm isolation)

### Implementation for User Story 2

- [x] T036 [P] [US2] Create TaskCreate Pydantic schema in backend/src/schemas/task.py with title and description validation
- [x] T037 [P] [US2] Create TaskResponse Pydantic schema in backend/src/schemas/task.py with all task fields
- [x] T038 [P] [US2] Create TaskList Pydantic schema in backend/src/schemas/task.py with tasks array and total count
- [x] T039 [US2] Implement GET /tasks endpoint in backend/src/api/tasks.py filtering by authenticated user_id and returning TaskList
- [x] T040 [US2] Implement POST /tasks endpoint in backend/src/api/tasks.py creating task with authenticated user_id and returning TaskResponse
- [x] T041 [US2] Register tasks router in backend/src/main.py with /tasks prefix and authentication dependency
- [x] T042 [P] [US2] Create TaskList component in frontend/src/components/tasks/TaskList.tsx fetching and displaying tasks from API
- [x] T043 [P] [US2] Create TaskItem component in frontend/src/components/tasks/TaskItem.tsx displaying individual task with title, description, and completion status
- [x] T044 [P] [US2] Create TaskForm component in frontend/src/components/tasks/TaskForm.tsx with title/description inputs and create task API call
- [x] T045 [US2] Create dashboard page in frontend/src/app/dashboard/page.tsx rendering TaskForm and TaskList components
- [x] T046 [US2] Create useTasks custom hook in frontend/src/hooks/useTasks.ts with fetchTasks and createTask functions

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users can register, login, create tasks, and view their task list with proper data isolation

---

## Phase 5: User Story 3 - Update and Delete Tasks (Priority: P2)

**Goal**: Enable authenticated users to update task details, toggle completion status, and delete tasks with authorization checks

**Independent Test**: Create a task, edit its title and description, toggle completion status, delete it, verify changes persist and deleted tasks don't appear

### Implementation for User Story 3

- [x] T047 [P] [US3] Create TaskUpdate Pydantic schema in backend/src/schemas/task.py with optional title, description, and is_completed fields
- [x] T048 [US3] Implement GET /tasks/{task_id} endpoint in backend/src/api/tasks.py with user_id authorization check returning TaskResponse or 403/404
- [x] T049 [US3] Implement PUT /tasks/{task_id} endpoint in backend/src/api/tasks.py with user_id authorization check, update fields, and return TaskResponse
- [x] T050 [US3] Implement DELETE /tasks/{task_id} endpoint in backend/src/api/tasks.py with user_id authorization check returning 204 or 403/404
- [x] T051 [P] [US3] Add edit mode state and form to TaskItem component in frontend/src/components/tasks/TaskItem.tsx
- [x] T052 [P] [US3] Add delete button with confirmation to TaskItem component in frontend/src/components/tasks/TaskItem.tsx
- [x] T053 [P] [US3] Add completion toggle checkbox to TaskItem component in frontend/src/components/tasks/TaskItem.tsx
- [x] T054 [US3] Add updateTask function to useTasks hook in frontend/src/hooks/useTasks.ts calling PUT /tasks/{id}
- [x] T055 [US3] Add deleteTask function to useTasks hook in frontend/src/hooks/useTasks.ts calling DELETE /tasks/{id}
- [x] T056 [US3] Update TaskList component in frontend/src/components/tasks/TaskList.tsx to refresh after update/delete operations

**Checkpoint**: All CRUD operations should now work - users can create, read, update, and delete their tasks with proper authorization

---

## Phase 6: User Story 4 - User Logout and Session Management (Priority: P2)

**Goal**: Enable users to securely log out and implement route protection for authenticated pages

**Independent Test**: Log in, perform actions, log out, verify subsequent requests without re-authentication are rejected and user is redirected to login

### Implementation for User Story 4

- [x] T057 [US4] Implement POST /auth/logout endpoint in backend/src/api/auth.py returning success message (client-side token invalidation)
- [x] T058 [P] [US4] Add logout function to auth context in frontend/src/lib/auth.ts clearing localStorage and resetting state
- [x] T059 [P] [US4] Create logout button component in frontend/src/components/auth/LogoutButton.tsx calling logout function
- [x] T060 [US4] Add LogoutButton to dashboard layout in frontend/src/app/dashboard/page.tsx
- [x] T061 [US4] Create Next.js middleware in frontend/src/middleware.ts protecting /dashboard routes and redirecting unauthenticated users to /login
- [x] T062 [US4] Update API client response interceptor in frontend/src/lib/api.ts to handle 401 errors by clearing token and redirecting to login

**Checkpoint**: Session management should be complete - users can log out, tokens are cleared, and protected routes redirect unauthenticated users

---

## Phase 7: User Story 5 - Error Handling and User Feedback (Priority: P3)

**Goal**: Provide clear, user-friendly error messages for validation errors, network failures, and authorization issues

**Independent Test**: Simulate various error conditions (invalid inputs, network failures, unauthorized access) and verify appropriate error messages are displayed

### Implementation for User Story 5

- [x] T063 [P] [US5] Create error handling middleware in backend/src/middleware/error_handler.py formatting validation errors and exceptions
- [x] T064 [P] [US5] Create ErrorMessage component in frontend/src/components/ui/ErrorMessage.tsx displaying error text with styling
- [x] T065 [P] [US5] Create LoadingSpinner component in frontend/src/components/ui/LoadingSpinner.tsx for loading states
- [x] T066 [US5] Add error state handling to LoginForm component in frontend/src/components/auth/LoginForm.tsx displaying validation and authentication errors
- [x] T067 [US5] Add error state handling to RegisterForm component in frontend/src/components/auth/RegisterForm.tsx displaying validation and duplicate email errors
- [x] T068 [US5] Add error state handling to TaskForm component in frontend/src/components/tasks/TaskForm.tsx displaying validation errors
- [x] T069 [US5] Add error state handling to TaskList component in frontend/src/components/tasks/TaskList.tsx displaying network errors
- [x] T070 [US5] Add loading states to all API calls in useTasks hook in frontend/src/hooks/useTasks.ts
- [x] T071 [US5] Register error handling middleware in backend/src/main.py

**Checkpoint**: Error handling should be comprehensive - users receive clear feedback for all error conditions

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final production readiness

- [x] T072 [P] Add input validation and sanitization for XSS prevention in all backend endpoints
- [x] T073 [P] Add database indexes on user.email and task.user_id in backend/src/models/ for query performance
- [x] T074 [P] Create Button component in frontend/src/components/ui/Button.tsx for consistent styling
- [x] T075 [P] Create Input component in frontend/src/components/ui/Input.tsx for consistent form styling
- [x] T076 [P] Add responsive CSS styling to all frontend components for mobile and desktop
- [x] T077 Add logging for authentication events in backend/src/api/auth.py
- [x] T078 Add logging for task operations in backend/src/api/tasks.py
- [x] T079 Verify all environment variables are documented in .env.example files
- [x] T080 Run through quickstart.md validation to ensure setup instructions work
- [x] T081 Security review: verify JWT secrets are not hardcoded, passwords are hashed, CORS is configured correctly
- [x] T082 Performance review: verify database queries use indexes, API responses are under 200ms
- [x] T083 Create root README.md with project overview, setup instructions, and architecture diagram

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P1): Can start after Foundational - No dependencies on other stories (but typically done after US1 for auth)
  - User Story 3 (P2): Can start after Foundational - Integrates with US2 but independently testable
  - User Story 4 (P2): Can start after Foundational - Integrates with US1 but independently testable
  - User Story 5 (P3): Can start after Foundational - Enhances all stories but independently testable
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundation only - No dependencies on other stories
- **User Story 2 (P1)**: Foundation only - Requires US1 for authentication but can be tested independently
- **User Story 3 (P2)**: Foundation only - Extends US2 but independently testable
- **User Story 4 (P2)**: Foundation only - Extends US1 but independently testable
- **User Story 5 (P3)**: Foundation only - Enhances all stories but independently testable

### Within Each User Story

- Backend schemas before endpoints
- Backend endpoints before frontend components
- API client setup before frontend API calls
- Core implementation before integration

### Parallel Opportunities

**Phase 1 (Setup)**: Tasks T003-T009 can all run in parallel (different files)

**Phase 2 (Foundational)**: Tasks T014-T015, T018-T019 can run in parallel (different files)

**Phase 3 (US1)**:
- Tasks T020-T023 can run in parallel (different schema files)
- Tasks T027-T028 can run in parallel (different files)
- Tasks T031-T032 can run in parallel (different components)

**Phase 4 (US2)**:
- Tasks T036-T038 can run in parallel (different schema files)
- Tasks T042-T044 can run in parallel (different components)

**Phase 5 (US3)**:
- Tasks T051-T053 can run in parallel (different parts of same component)

**Phase 6 (US4)**:
- Tasks T058-T059 can run in parallel (different files)

**Phase 7 (US5)**:
- Tasks T063-T065 can run in parallel (different files)

**Phase 8 (Polish)**:
- Tasks T072-T076 can run in parallel (different files)

---

## Parallel Example: User Story 1

```bash
# Launch all backend schemas together:
Task T020: "Create UserRegister schema in backend/src/schemas/auth.py"
Task T021: "Create UserLogin schema in backend/src/schemas/auth.py"
Task T022: "Create AuthResponse schema in backend/src/schemas/auth.py"
Task T023: "Create UserResponse schema in backend/src/schemas/auth.py"

# Launch frontend auth setup together:
Task T027: "Create auth context provider in frontend/src/lib/auth.ts"
Task T028: "Create useAuth hook in frontend/src/hooks/useAuth.ts"

# Launch frontend forms together:
Task T031: "Create LoginForm component"
Task T032: "Create RegisterForm component"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (T001-T009)
2. Complete Phase 2: Foundational (T010-T019) - CRITICAL
3. Complete Phase 3: User Story 1 (T020-T035) - Authentication
4. Complete Phase 4: User Story 2 (T036-T046) - Task CRUD (Create + Read)
5. **STOP and VALIDATE**: Test registration, login, create tasks, view tasks
6. Deploy/demo if ready - this is a functional MVP!

### Incremental Delivery

1. **Foundation** (Phases 1-2) → Database and auth infrastructure ready
2. **MVP** (Phases 3-4) → Users can register, login, create and view tasks
3. **Full CRUD** (Phase 5) → Add update and delete operations
4. **Session Management** (Phase 6) → Add logout and route protection
5. **Polish** (Phases 7-8) → Error handling and production readiness

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (Phases 1-2)
2. **Once Foundational is done, split work**:
   - Developer A: User Story 1 (Authentication)
   - Developer B: User Story 2 (Task CRUD - Create/Read)
   - Developer C: User Story 3 (Task CRUD - Update/Delete)
3. **Stories integrate independently** - each developer can test their story in isolation

---

## Task Summary

**Total Tasks**: 83 tasks

**Tasks per User Story**:
- Setup: 9 tasks
- Foundational: 10 tasks (BLOCKS all stories)
- User Story 1 (P1): 16 tasks - Authentication
- User Story 2 (P1): 11 tasks - Create and View Tasks
- User Story 3 (P2): 10 tasks - Update and Delete Tasks
- User Story 4 (P2): 6 tasks - Logout and Session Management
- User Story 5 (P3): 9 tasks - Error Handling
- Polish: 12 tasks

**Parallel Opportunities**: 35 tasks marked [P] can run in parallel

**Independent Test Criteria**:
- US1: Register user, login, receive JWT token
- US2: Create tasks, view task list, verify data isolation
- US3: Update task, delete task, verify authorization
- US4: Logout, verify token cleared, verify route protection
- US5: Trigger errors, verify user-friendly messages displayed

**Suggested MVP Scope**: Phases 1-4 (Setup + Foundational + US1 + US2) = 46 tasks

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All file paths are explicit for immediate execution
- No test tasks included (not requested in specification)
