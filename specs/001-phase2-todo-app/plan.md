# Implementation Plan: Phase 2 Todo Full-Stack Web Application

**Branch**: `001-phase2-todo-app` | **Date**: 2026-02-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-phase2-todo-app/spec.md`

## Summary

Building a secure multi-user task management web application with JWT-based authentication and authorization. The system enables users to register, authenticate, and perform CRUD operations on their personal tasks with strict per-user data isolation. The application uses Next.js 16+ (App Router) for the frontend, FastAPI for the backend API, SQLModel for ORM, and Neon Serverless PostgreSQL for persistent storage. Better Auth provides JWT token generation and validation for secure authentication flows.

## Technical Context

**Language/Version**:
- Backend: Python 3.11+
- Frontend: TypeScript/JavaScript (Next.js 16+)

**Primary Dependencies**:
- Frontend: Next.js 16+ (App Router), React, Axios/Fetch, Better Auth client
- Backend: FastAPI, SQLModel, Pydantic, Better Auth (JWT plugin), python-jose (JWT handling)
- Database: Neon Serverless PostgreSQL, psycopg2/asyncpg

**Storage**: Neon Serverless PostgreSQL with SQLModel ORM

**Testing**:
- Backend: pytest, pytest-asyncio, httpx (for FastAPI testing)
- Frontend: Jest or Vitest, React Testing Library
- Integration: End-to-end tests with Playwright or Cypress

**Target Platform**: Web application (modern browsers: Chrome, Firefox, Safari, Edge)

**Project Type**: Web (separate frontend and backend repositories/directories)

**Performance Goals**:
- User registration: <1 minute end-to-end
- Login and dashboard access: <5 seconds
- Task creation with UI update: <2 seconds
- API response time: <200ms p95 for CRUD operations
- Support 100 concurrent users without degradation

**Constraints**:
- Must use Next.js App Router (no Pages Router)
- Must use FastAPI for backend (no Flask, Django, etc.)
- Must use SQLModel for ORM (no SQLAlchemy directly, no raw SQL)
- Must use Neon Serverless PostgreSQL (no other databases)
- Must use Better Auth with JWT enabled
- RESTful API design principles
- JWT tokens in Authorization header
- All secrets in environment variables
- CORS configured for frontend-backend communication

**Scale/Scope**:
- Multi-user system (100+ concurrent users)
- 2 primary entities (User, Task)
- 5 user stories (authentication, CRUD, logout, error handling)
- 20 functional requirements
- Hackathon phase timeline

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Functional Correctness Across All Layers
- ✅ **PASS**: All API endpoints will have request/response validation via Pydantic
- ✅ **PASS**: Frontend components will handle all user interactions with proper state management
- ✅ **PASS**: Database operations use SQLModel with type safety and constraints
- ✅ **PASS**: Integration tested via acceptance scenarios in spec
- ✅ **PASS**: Error handling planned for all layers (validation, auth, network)

### Principle II: Security-First Design
- ✅ **PASS**: JWT-based authentication using Better Auth
- ✅ **PASS**: All protected routes require token verification (middleware planned)
- ✅ **PASS**: Passwords hashed via Better Auth (never plaintext)
- ✅ **PASS**: Per-user data isolation enforced in all queries (user_id filter)
- ✅ **PASS**: Secrets in `.env` files (DATABASE_URL, JWT_SECRET, BETTER_AUTH_SECRET)
- ✅ **PASS**: Input validation on both frontend (forms) and backend (Pydantic)
- ✅ **PASS**: Protection against XSS (React escaping), SQL injection (SQLModel parameterized queries)

### Principle III: Clear Separation of Concerns
- ✅ **PASS**: Frontend handles UI rendering, user interaction, client-side routing
- ✅ **PASS**: Backend handles business logic, authentication, data validation
- ✅ **PASS**: Database handles persistence via SQLModel models
- ✅ **PASS**: No direct database access from frontend
- ✅ **PASS**: No UI logic in backend
- ✅ **PASS**: Authentication centralized in Better Auth integration

### Principle IV: Spec-Driven Development
- ✅ **PASS**: Specification complete in `specs/001-phase2-todo-app/spec.md`
- ✅ **PASS**: This plan documents architecture and decisions
- ✅ **PASS**: Tasks will be generated in `specs/001-phase2-todo-app/tasks.md`
- ✅ **PASS**: ADRs will be created for significant decisions
- ✅ **PASS**: PHRs track all AI interactions

### Principle V: Production-Oriented Development
- ✅ **PASS**: Environment variables for all configuration
- ✅ **PASS**: Proper error handling with meaningful messages planned
- ✅ **PASS**: HTTP status codes follow standards (200, 201, 400, 401, 403, 404, 500)
- ✅ **PASS**: Logging for debugging and monitoring
- ✅ **PASS**: Framework best practices (Next.js App Router, FastAPI async)
- ✅ **PASS**: Performance considerations (database indexing, query optimization)
- ✅ **PASS**: Responsive design for desktop and mobile

**Gate Status**: ✅ ALL CHECKS PASSED - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/001-phase2-todo-app/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file - implementation plan
├── research.md          # Phase 0 output - technology research
├── data-model.md        # Phase 1 output - database schema design
├── quickstart.md        # Phase 1 output - setup instructions
├── contracts/           # Phase 1 output - API contracts
│   ├── openapi.yaml     # OpenAPI 3.0 specification
│   └── README.md        # Contract documentation
├── checklists/          # Quality validation checklists
│   └── requirements.md  # Spec quality checklist (complete)
└── tasks.md             # Phase 2 output - implementation tasks (NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Environment configuration
│   ├── database.py             # Database connection and session management
│   ├── models/                 # SQLModel database models
│   │   ├── __init__.py
│   │   ├── user.py             # User model
│   │   └── task.py             # Task model
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── auth.py             # Auth schemas (login, register, token)
│   │   └── task.py             # Task schemas (create, update, response)
│   ├── api/                    # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication endpoints
│   │   └── tasks.py            # Task CRUD endpoints
│   ├── middleware/             # Custom middleware
│   │   ├── __init__.py
│   │   └── jwt_auth.py         # JWT verification middleware
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       ├── jwt.py              # JWT token utilities
│       └── security.py         # Security utilities
├── tests/
│   ├── conftest.py             # Pytest fixtures
│   ├── test_auth.py            # Authentication tests
│   ├── test_tasks.py           # Task CRUD tests
│   └── test_integration.py     # Integration tests
├── .env.example                # Example environment variables
├── requirements.txt            # Python dependencies
└── README.md                   # Backend setup instructions

frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home page
│   │   ├── login/              # Login page
│   │   │   └── page.tsx
│   │   ├── register/           # Registration page
│   │   │   └── page.tsx
│   │   └── dashboard/          # Protected dashboard
│   │       └── page.tsx
│   ├── components/             # React components
│   │   ├── auth/               # Authentication components
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   ├── tasks/              # Task management components
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskItem.tsx
│   │   │   ├── TaskForm.tsx
│   │   │   └── TaskActions.tsx
│   │   └── ui/                 # Reusable UI components
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       └── ErrorMessage.tsx
│   ├── lib/                    # Utility libraries
│   │   ├── api.ts              # API client configuration (Axios)
│   │   ├── auth.ts             # Better Auth client setup
│   │   └── types.ts            # TypeScript type definitions
│   └── hooks/                  # Custom React hooks
│       ├── useAuth.ts          # Authentication hook
│       └── useTasks.ts         # Task management hook
├── tests/
│   ├── components/             # Component tests
│   └── integration/            # E2E tests
├── .env.local.example          # Example environment variables
├── package.json                # Node dependencies
├── tsconfig.json               # TypeScript configuration
└── README.md                   # Frontend setup instructions

.env                            # Environment variables (gitignored)
docker-compose.yml              # Optional: local development setup
README.md                       # Project overview and setup
```

**Structure Decision**: Web application structure with separate `backend/` and `frontend/` directories. This separation aligns with Principle III (Clear Separation of Concerns) and enables independent development, testing, and deployment of each layer. The backend uses a layered architecture (models, schemas, API routes, middleware) following FastAPI best practices. The frontend uses Next.js App Router with a component-based architecture and custom hooks for state management.

## Complexity Tracking

No violations detected. All constitution checks passed without requiring justification.

## Phase 0: Research & Technology Decisions

### Research Tasks

1. **Better Auth JWT Integration**
   - Research: How to configure Better Auth to issue JWT tokens
   - Research: JWT token structure and claims needed for user identification
   - Research: Shared secret configuration between frontend and backend

2. **FastAPI JWT Verification**
   - Research: Best practices for JWT verification middleware in FastAPI
   - Research: python-jose vs PyJWT for token decoding
   - Research: Dependency injection pattern for authenticated user context

3. **SQLModel with Neon PostgreSQL**
   - Research: Connection pooling best practices for Neon Serverless
   - Research: Async vs sync SQLModel operations with FastAPI
   - Research: Migration strategy (Alembic integration or manual)

4. **Next.js App Router Authentication**
   - Research: Client vs Server Components for auth state
   - Research: Middleware for route protection
   - Research: Token storage (httpOnly cookies vs localStorage)

5. **API Client Configuration**
   - Research: Axios interceptors for JWT token injection
   - Research: Token refresh flow implementation
   - Research: Error handling and retry strategies

### Output: research.md

*This file will be generated in Phase 0 with consolidated findings from all research tasks.*

## Phase 1: Design & Contracts

### Data Model Design

**Output**: `data-model.md`

Entities to be designed:
1. **User Entity**
   - Fields: id (UUID/int), email (unique), hashed_password, created_at, updated_at
   - Constraints: email unique, NOT NULL on required fields
   - Relationships: One-to-many with Task

2. **Task Entity**
   - Fields: id (UUID/int), user_id (FK), title, description, is_completed, created_at, updated_at
   - Constraints: title NOT NULL, user_id FK to User
   - Relationships: Many-to-one with User
   - Indexes: user_id (for efficient per-user queries)

### API Contracts

**Output**: `contracts/openapi.yaml`

Endpoints to be specified:

**Authentication Endpoints**:
- `POST /auth/register` - User registration
- `POST /auth/login` - User login (returns JWT)
- `POST /auth/logout` - User logout (optional token invalidation)

**Task Endpoints**:
- `GET /tasks` - List all tasks for authenticated user
- `POST /tasks` - Create new task
- `GET /tasks/{task_id}` - Get single task
- `PUT /tasks/{task_id}` - Update task
- `DELETE /tasks/{task_id}` - Delete task

Each endpoint will include:
- Request schema (Pydantic models)
- Response schema (success and error cases)
- Status codes
- Authentication requirements
- Example requests/responses

### Quickstart Guide

**Output**: `quickstart.md`

Sections:
1. Prerequisites (Python 3.11+, Node.js 18+, Neon account)
2. Environment Setup (clone, install dependencies)
3. Database Setup (Neon connection, migrations)
4. Backend Setup (install, configure, run)
5. Frontend Setup (install, configure, run)
6. Testing (run tests, verify functionality)
7. Common Issues and Troubleshooting

### Agent Context Update

After Phase 1 design completion, run:
```bash
.specify/scripts/bash/update-agent-context.sh claude
```

This will update the agent-specific context file with:
- Technology stack from this plan
- Project structure
- Key architectural decisions
- Preserve any manual additions

## Phase 2: Constitution Re-Check

*After Phase 1 design artifacts are complete, re-evaluate all constitution checks to ensure design decisions maintain compliance.*

**Re-check Status**: To be completed after Phase 1

## Implementation Phases (High-Level)

Based on user input and spec requirements, implementation will follow these phases:

### Phase 1: Architecture & Environment Setup
- Initialize backend and frontend projects
- Configure Neon PostgreSQL connection
- Set up environment variables and secrets
- Initialize Better Auth in both frontend and backend
- Verify basic connectivity

### Phase 2: Authentication Implementation
- Integrate Better Auth in frontend (signup/login UI)
- Enable JWT plugin in Better Auth
- Configure shared JWT secret
- Implement login/signup flows
- Test token generation and storage
- Verify token format and claims

### Phase 3: Database & Backend API
- Design and implement SQLModel schemas (User, Task)
- Create database migrations
- Implement CRUD endpoints for tasks
- Add request/response validation (Pydantic)
- Implement error handling
- Add database indexes for performance

### Phase 4: Security & Authorization Layer
- Build JWT verification middleware
- Decode and validate tokens in backend
- Extract user identity from token
- Enforce user ownership on all task queries
- Implement 401/403 responses
- Test unauthorized access scenarios

### Phase 5: Frontend Integration
- Build task management UI components
- Implement API client with auth headers (Axios interceptors)
- Handle loading and error states
- Protect authenticated routes (middleware)
- Implement responsive layout
- Add form validation

### Phase 6: Testing & Stabilization
- Write unit tests for backend endpoints
- Write integration tests for auth flows
- Perform security testing (auth bypass, data leakage)
- Fix bugs and edge cases
- Optimize performance (query optimization, caching)
- Load testing with 100 concurrent users

### Phase 7: Deployment Preparation
- Document deployment process
- Configure production environment variables
- Set up CORS for production domains
- Prepare database migrations for production
- Create deployment checklist

## Key Architectural Decisions

### Decision 1: JWT Token Storage Strategy
**Context**: Frontend needs to store JWT tokens securely and include them in API requests.

**Options Considered**:
1. localStorage - Simple but vulnerable to XSS
2. httpOnly cookies - More secure but requires backend cookie handling
3. sessionStorage - Similar to localStorage, lost on tab close

**Decision**: Use localStorage with XSS protection via React's built-in escaping and Content Security Policy headers.

**Rationale**:
- Simpler implementation for hackathon timeline
- Better Auth can be configured to work with localStorage
- Next.js App Router provides good XSS protection by default
- Can be upgraded to httpOnly cookies in future iteration

**Trade-offs**: Slightly less secure than httpOnly cookies, but acceptable for Phase 2 with proper XSS protections.

### Decision 2: Database Migration Strategy
**Context**: Need to manage database schema changes during development and deployment.

**Options Considered**:
1. Alembic (SQLAlchemy migration tool)
2. Manual SQL scripts
3. SQLModel create_all() for development

**Decision**: Use SQLModel create_all() for development, prepare manual migration scripts for production.

**Rationale**:
- Faster development iteration
- Simpler for hackathon timeline
- Manual scripts provide explicit control for production
- Can integrate Alembic later if needed

**Trade-offs**: Less automated than Alembic, but more transparent and controllable.

### Decision 3: API Client Architecture
**Context**: Frontend needs centralized API client with authentication and error handling.

**Options Considered**:
1. Axios with interceptors
2. Fetch with wrapper functions
3. React Query with custom fetcher

**Decision**: Axios with interceptors for request/response handling.

**Rationale**:
- Interceptors provide clean way to inject JWT tokens
- Built-in request/response transformation
- Better error handling than raw Fetch
- Widely used and well-documented

**Trade-offs**: Additional dependency, but worth it for cleaner code.

### Decision 4: Frontend State Management
**Context**: Need to manage authentication state and task data across components.

**Options Considered**:
1. Redux/Redux Toolkit
2. Zustand
3. React Context + custom hooks
4. React Query for server state

**Decision**: React Context for auth state + custom hooks for task operations.

**Rationale**:
- Simpler than Redux for this scope
- Next.js App Router works well with Context
- Custom hooks provide clean API for components
- No additional state management library needed

**Trade-offs**: May need to refactor if state complexity grows significantly.

## Risk Analysis

### Risk 1: Better Auth JWT Configuration Complexity
**Likelihood**: Medium | **Impact**: High

**Mitigation**:
- Allocate dedicated research time in Phase 0
- Test JWT generation/verification early
- Have fallback plan to implement custom JWT handling if needed

### Risk 2: Per-User Data Isolation Bugs
**Likelihood**: Medium | **Impact**: Critical

**Mitigation**:
- Write comprehensive tests for data isolation
- Code review all database queries for user_id filtering
- Test with multiple user accounts
- Add database-level constraints where possible

### Risk 3: CORS Configuration Issues
**Likelihood**: Low | **Impact**: Medium

**Mitigation**:
- Configure CORS early in backend setup
- Test frontend-backend communication immediately
- Document CORS settings clearly

### Risk 4: Token Expiration Handling
**Likelihood**: Medium | **Impact**: Medium

**Mitigation**:
- Implement clear error messages for expired tokens
- Add token refresh flow if time permits
- Document token expiration behavior

## Success Metrics

Implementation will be considered successful when:

1. ✅ All 20 functional requirements are implemented and tested
2. ✅ All 5 user stories pass acceptance scenarios
3. ✅ All 12 success criteria are met and measurable
4. ✅ Constitution checks pass (all 5 principles complied with)
5. ✅ Security testing shows no critical vulnerabilities
6. ✅ Performance testing confirms <2s task creation, <5s login
7. ✅ 100 concurrent users can use the system without errors
8. ✅ All tests pass (unit, integration, security)

## Next Steps

1. **Immediate**: Execute Phase 0 research tasks and generate `research.md`
2. **After Research**: Execute Phase 1 design and generate `data-model.md`, `contracts/`, `quickstart.md`
3. **After Design**: Update agent context with technology decisions
4. **After Planning**: Run `/sp.tasks` to generate implementation tasks
5. **After Tasks**: Begin implementation following task order

**Command to proceed**: `/sp.tasks` (after this plan is complete)
