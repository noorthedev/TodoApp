# Tasks: Frontend UI & API Integration Layer

**Input**: Design documents from `/specs/004-frontend-ui-integration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not included - tests are optional and not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend project**: `frontend/src/` for source code
- **Tests**: `frontend/tests/` for test files
- All paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create frontend project directory structure per plan.md
- [ ] T002 Initialize Next.js 16+ project with TypeScript in frontend/
- [ ] T003 [P] Install core dependencies: next@16+, react@18+, typescript@5+
- [ ] T004 [P] Install Better Auth dependency: better-auth@latest
- [ ] T005 [P] Install Axios dependency: axios@1.x
- [ ] T006 [P] Install TailwindCSS dependencies: tailwindcss@3.x, postcss, autoprefixer
- [ ] T007 Configure TailwindCSS in frontend/tailwind.config.js
- [ ] T008 Configure TypeScript in frontend/tsconfig.json with strict mode
- [ ] T009 Create environment variables template in frontend/.env.local.example
- [ ] T010 [P] Setup global styles with TailwindCSS directives in frontend/src/app/globals.css
- [ ] T011 [P] Configure Next.js in frontend/next.config.js (API URL, environment variables)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T012 [P] Create TypeScript type definitions for auth in frontend/src/lib/types/auth.ts
- [ ] T013 [P] Create TypeScript type definitions for tasks in frontend/src/lib/types/task.ts
- [ ] T014 [P] Create TypeScript type definitions for API responses in frontend/src/lib/types/api.ts
- [ ] T015 Create Axios API client instance with base configuration in frontend/src/lib/api/client.ts
- [ ] T016 Implement request interceptor for JWT token attachment in frontend/src/lib/api/client.ts
- [ ] T017 Implement response interceptor for error handling in frontend/src/lib/api/client.ts
- [ ] T018 Create Next.js middleware for route protection in frontend/src/middleware.ts
- [ ] T019 Configure Better Auth in frontend/src/lib/auth/better-auth.ts
- [ ] T020 [P] Create session management utilities in frontend/src/lib/auth/session.ts
- [ ] T021 [P] Create root layout component in frontend/src/app/layout.tsx
- [ ] T022 [P] Create auth route group layout in frontend/src/app/(auth)/layout.tsx
- [ ] T023 [P] Create protected route group layout in frontend/src/app/(protected)/layout.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Authentication & Session Management (Priority: P1) 🎯 MVP

**Goal**: Enable users to register, login, maintain sessions with JWT tokens, and logout

**Independent Test**: Register a new account, login, verify JWT token is stored in localStorage, navigate between pages while maintaining session, logout and verify token is removed

### Implementation for User Story 1

- [ ] T024 [P] [US1] Create AuthContext provider in frontend/src/context/AuthContext.tsx
- [ ] T025 [P] [US1] Create useAuth custom hook in frontend/src/lib/hooks/useAuth.ts
- [ ] T026 [P] [US1] Implement register API function in frontend/src/lib/api/auth.ts
- [ ] T027 [P] [US1] Implement login API function in frontend/src/lib/api/auth.ts
- [ ] T028 [P] [US1] Implement logout API function in frontend/src/lib/api/auth.ts
- [ ] T029 [US1] Create LoginForm component in frontend/src/components/auth/LoginForm.tsx
- [ ] T030 [US1] Create RegisterForm component in frontend/src/components/auth/RegisterForm.tsx
- [ ] T031 [US1] Create LogoutButton component in frontend/src/components/auth/LogoutButton.tsx
- [ ] T032 [US1] Create login page in frontend/src/app/(auth)/login/page.tsx
- [ ] T033 [US1] Create register page in frontend/src/app/(auth)/register/page.tsx
- [ ] T034 [US1] Create landing page with auth redirects in frontend/src/app/page.tsx
- [ ] T035 [US1] Implement protected layout with auth check in frontend/src/app/(protected)/layout.tsx
- [ ] T036 [US1] Add session persistence logic to AuthContext (check localStorage on mount)
- [ ] T037 [US1] Add token expiration handling to response interceptor (401 → logout)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can register, login, maintain sessions, and logout

---

## Phase 4: User Story 2 - Task List Display & Navigation (Priority: P2)

**Goal**: Enable authenticated users to view their task list with loading and error states

**Independent Test**: Login as a user with existing tasks, verify task list loads from API with JWT authentication, confirm only the user's tasks are displayed, check UI updates when navigating

### Implementation for User Story 2

- [ ] T038 [P] [US2] Create TaskContext provider in frontend/src/context/TaskContext.tsx
- [ ] T039 [P] [US2] Create useTasks custom hook in frontend/src/lib/hooks/useTasks.ts
- [ ] T040 [P] [US2] Implement getTasks API function in frontend/src/lib/api/tasks.ts
- [ ] T041 [P] [US2] Create LoadingSpinner component in frontend/src/components/ui/LoadingSpinner.tsx
- [ ] T042 [US2] Create TaskList component in frontend/src/components/tasks/TaskList.tsx
- [ ] T043 [US2] Create TaskItem component in frontend/src/components/tasks/TaskItem.tsx
- [ ] T044 [US2] Create Header component in frontend/src/components/layout/Header.tsx
- [ ] T045 [US2] Create Navigation component in frontend/src/components/layout/Navigation.tsx
- [ ] T046 [US2] Create dashboard page in frontend/src/app/(protected)/dashboard/page.tsx
- [ ] T047 [US2] Integrate TaskContext provider in root layout
- [ ] T048 [US2] Add task fetching on dashboard mount with loading and error states
- [ ] T049 [US2] Add empty state handling to TaskList component
- [ ] T050 [US2] Add Header and Navigation to protected layout

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can login and view their task list

---

## Phase 5: User Story 3 - Task CRUD Operations (Priority: P3)

**Goal**: Enable authenticated users to create, update, delete, and toggle completion of tasks

**Independent Test**: Create a new task via form, verify it appears in the list, edit an existing task and confirm changes persist, mark a task as complete, delete a task with confirmation

### Implementation for User Story 3

- [ ] T051 [P] [US3] Implement createTask API function in frontend/src/lib/api/tasks.ts
- [ ] T052 [P] [US3] Implement updateTask API function in frontend/src/lib/api/tasks.ts
- [ ] T053 [P] [US3] Implement deleteTask API function in frontend/src/lib/api/tasks.ts
- [ ] T054 [P] [US3] Implement toggleTaskComplete API function in frontend/src/lib/api/tasks.ts
- [ ] T055 [P] [US3] Create Button component in frontend/src/components/ui/Button.tsx
- [ ] T056 [P] [US3] Create Input component in frontend/src/components/ui/Input.tsx
- [ ] T057 [P] [US3] Create Modal component in frontend/src/components/ui/Modal.tsx
- [ ] T058 [US3] Create TaskForm component in frontend/src/components/tasks/TaskForm.tsx
- [ ] T059 [US3] Create TaskDeleteConfirm component in frontend/src/components/tasks/TaskDeleteConfirm.tsx
- [ ] T060 [US3] Add createTask method to TaskContext
- [ ] T061 [US3] Add updateTask method to TaskContext
- [ ] T062 [US3] Add deleteTask method to TaskContext
- [ ] T063 [US3] Add toggleComplete method to TaskContext
- [ ] T064 [US3] Add "Add Task" button and modal to dashboard page
- [ ] T065 [US3] Add edit functionality to TaskItem component
- [ ] T066 [US3] Add delete functionality with confirmation to TaskItem component
- [ ] T067 [US3] Add completion toggle checkbox to TaskItem component
- [ ] T068 [US3] Add form validation to TaskForm component

**Checkpoint**: All core user stories should now be independently functional - users can fully manage their tasks

---

## Phase 6: User Story 4 - Error Handling & UX Polish (Priority: P4)

**Goal**: Handle all error scenarios gracefully, provide clear feedback, and deliver polished responsive UX

**Independent Test**: Simulate various error scenarios (network failures, expired tokens, validation errors), verify appropriate error messages, check loading states, test responsive behavior on different screen sizes

### Implementation for User Story 4

- [ ] T069 [P] [US4] Enhance error handling in API client response interceptor (network errors, 403, 404, 422, 500)
- [ ] T070 [P] [US4] Add loading states to all form submissions (disable buttons during API calls)
- [ ] T071 [P] [US4] Add inline validation errors to LoginForm component
- [ ] T072 [P] [US4] Add inline validation errors to RegisterForm component
- [ ] T073 [P] [US4] Add inline validation errors to TaskForm component
- [ ] T074 [P] [US4] Add responsive design utilities to TailwindCSS config (breakpoints, mobile-first)
- [ ] T075 [US4] Create error boundary component in frontend/src/components/ErrorBoundary.tsx
- [ ] T076 [US4] Create 404 not found page in frontend/src/app/not-found.tsx
- [ ] T077 [US4] Create error page in frontend/src/app/error.tsx
- [ ] T078 [US4] Add responsive layout to Header component (hamburger menu on mobile)
- [ ] T079 [US4] Add responsive layout to TaskList component (stack on mobile)
- [ ] T080 [US4] Add responsive layout to TaskForm component (full-width on mobile)
- [ ] T081 [US4] Add success/error toast notifications to UI state
- [ ] T082 [US4] Add loading page for dashboard in frontend/src/app/(protected)/dashboard/loading.tsx
- [ ] T083 [US4] Test and fix responsive behavior on 320px, 768px, 1024px, 1920px screen sizes
- [ ] T084 [US4] Add accessibility attributes (aria-labels, roles) to interactive components

**Checkpoint**: Application should now be production-ready with comprehensive error handling and responsive design

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T085 [P] Add page metadata (titles, descriptions) to all pages
- [ ] T086 [P] Add loading transitions between routes
- [ ] T087 [P] Optimize bundle size (check Next.js build output)
- [ ] T088 [P] Add favicon and app icons to frontend/public/
- [ ] T089 Code cleanup and remove console.logs
- [ ] T090 Run quickstart.md validation scenarios (all 10 scenarios)
- [ ] T091 Update CLAUDE.md with frontend implementation notes
- [ ] T092 Create frontend README.md with setup instructions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 (uses AuthContext) but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Extends US2 (uses TaskContext) but independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Enhances all stories but independently testable

### Within Each User Story

- Context providers before hooks
- API functions before components that use them
- UI components before pages that use them
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003-T006, T010-T011)
- All Foundational tasks marked [P] can run in parallel (T012-T014, T020-T023)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within User Story 1: T024-T028, T029-T031, T032-T034 can run in parallel
- Within User Story 2: T038-T041, T042-T045 can run in parallel
- Within User Story 3: T051-T054, T055-T057 can run in parallel
- Within User Story 4: T069-T074, T078-T080 can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all API functions for User Story 1 together:
Task T026: "Implement register API function in frontend/src/lib/api/auth.ts"
Task T027: "Implement login API function in frontend/src/lib/api/auth.ts"
Task T028: "Implement logout API function in frontend/src/lib/api/auth.ts"

# Launch all form components for User Story 1 together:
Task T029: "Create LoginForm component in frontend/src/components/auth/LoginForm.tsx"
Task T030: "Create RegisterForm component in frontend/src/components/auth/RegisterForm.tsx"
Task T031: "Create LogoutButton component in frontend/src/components/auth/LogoutButton.tsx"

# Launch all pages for User Story 1 together:
Task T032: "Create login page in frontend/src/app/(auth)/login/page.tsx"
Task T033: "Create register page in frontend/src/app/(auth)/register/page.tsx"
Task T034: "Create landing page with auth redirects in frontend/src/app/page.tsx"
```

---

## Parallel Example: User Story 2

```bash
# Launch all foundational pieces for User Story 2 together:
Task T038: "Create TaskContext provider in frontend/src/context/TaskContext.tsx"
Task T039: "Create useTasks custom hook in frontend/src/lib/hooks/useTasks.ts"
Task T040: "Implement getTasks API function in frontend/src/lib/api/tasks.ts"
Task T041: "Create LoadingSpinner component in frontend/src/components/ui/LoadingSpinner.tsx"

# Launch all task display components together:
Task T042: "Create TaskList component in frontend/src/components/tasks/TaskList.tsx"
Task T043: "Create TaskItem component in frontend/src/components/tasks/TaskItem.tsx"
Task T044: "Create Header component in frontend/src/components/layout/Header.tsx"
Task T045: "Create Navigation component in frontend/src/components/layout/Navigation.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T011)
2. Complete Phase 2: Foundational (T012-T023) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T024-T037)
4. **STOP and VALIDATE**: Test User Story 1 independently using quickstart.md scenarios 1-8
5. Deploy/demo if ready

**MVP Deliverable**: Users can register, login, maintain sessions, and logout. This is the minimum viable product that secures the application and enables user identification.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP - Authentication!)
3. Add User Story 2 → Test independently → Deploy/Demo (Read-only task viewing)
4. Add User Story 3 → Test independently → Deploy/Demo (Full CRUD functionality)
5. Add User Story 4 → Test independently → Deploy/Demo (Production-ready polish)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T023)
2. Once Foundational is done:
   - Developer A: User Story 1 (T024-T037) - Authentication
   - Developer B: User Story 2 (T038-T050) - Task Display
   - Developer C: User Story 3 (T051-T068) - Task CRUD
   - Developer D: User Story 4 (T069-T084) - Error Handling & Polish
3. Stories complete and integrate independently
4. Team completes Polish phase together (T085-T092)

---

## Task Summary

**Total Tasks**: 92 tasks across 7 phases

**Task Count by Phase**:
- Phase 1 (Setup): 11 tasks
- Phase 2 (Foundational): 12 tasks (BLOCKING)
- Phase 3 (User Story 1 - Authentication): 14 tasks 🎯 MVP
- Phase 4 (User Story 2 - Task Display): 13 tasks
- Phase 5 (User Story 3 - Task CRUD): 18 tasks
- Phase 6 (User Story 4 - Error Handling): 16 tasks
- Phase 7 (Polish): 8 tasks

**Parallel Opportunities**: 45 tasks marked [P] can run in parallel within their phase

**Independent Test Criteria**:
- US1: Register, login, session persistence, logout
- US2: View task list with loading/error states
- US3: Create, update, delete, toggle tasks
- US4: Error handling, responsive design, UX polish

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = 37 tasks

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are NOT included - optional and not requested in spec
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Frontend paths use `frontend/src/` prefix
- All API calls use JWT tokens via Axios interceptors
- All routes protected by Next.js middleware
- Responsive design mobile-first (320px-1920px)
