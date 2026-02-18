# Todo Full-Stack Web Application Constitution
<!-- Hackathon Phase-2: Multi-user Todo Web Application -->

<!--
═══════════════════════════════════════════════════════════════════════════════
CONSTITUTION SYNC IMPACT REPORT
═══════════════════════════════════════════════════════════════════════════════

Validation Date: 2026-02-15
Constitution Version: 1.0.1 (patch)
Action: Minor update to align with user input and refresh date

VALIDATION SUMMARY:
- Constitution already complete and fully aligned with project requirements
- All 5 core principles properly defined with requirements and rationale
- Technical standards comprehensive (API, Authentication, Database, Code Quality)
- Technology constraints clearly specified
- Success criteria measurable and testable
- Governance section complete with amendment process

TEMPLATE CONSISTENCY CHECK:
✅ .specify/templates/spec-template.md
   - User story prioritization aligns with spec-driven principle
   - Acceptance criteria format supports testability requirements
   - Edge cases section supports production-oriented development

✅ .specify/templates/plan-template.md
   - Constitution Check gate present (line 30-34)
   - Technical context aligns with technology constraints
   - Project structure options match stack separation principles

✅ .specify/templates/tasks-template.md
   - Task organization by user story supports spec-driven workflow
   - Parallel execution markers align with efficiency principles
   - Test-first approach supports quality standards

✅ CLAUDE.md (project instructions)
   - Specialized agent usage aligns with separation of concerns
   - Authentication flow documentation matches security-first principle
   - PHR and ADR requirements support governance standards

PRINCIPLES VALIDATED:
1. Functional Correctness Across All Layers - Complete
2. Security-First Design - Complete
3. Clear Separation of Concerns - Complete
4. Spec-Driven Development - Complete
5. Production-Oriented Development - Complete

FOLLOW-UP ACTIONS:
None required - constitution is complete and all dependent artifacts are aligned.

═══════════════════════════════════════════════════════════════════════════════
-->

<!--
═══════════════════════════════════════════════════════════════════════════════
CONSTITUTION SYNC IMPACT REPORT
═══════════════════════════════════════════════════════════════════════════════

Validation Date: 2026-02-15
Constitution Version: 1.0.1 (patch)
Action: Minor update to align with user input and refresh date

VALIDATION SUMMARY:
- Constitution already complete and fully aligned with project requirements
- All 5 core principles properly defined with requirements and rationale
- Technical standards comprehensive (API, Authentication, Database, Code Quality)
- Technology constraints clearly specified
- Success criteria measurable and testable
- Governance section complete with amendment process

TEMPLATE CONSISTENCY CHECK:
✅ .specify/templates/spec-template.md
   - User story prioritization aligns with spec-driven principle
   - Acceptance criteria format supports testability requirements
   - Edge cases section supports production-oriented development

✅ .specify/templates/plan-template.md
   - Constitution Check gate present (line 30-34)
   - Technical context aligns with technology constraints
   - Project structure options match stack separation principles

✅ .specify/templates/tasks-template.md
   - Task organization by user story supports spec-driven workflow
   - Parallel execution markers align with efficiency principles
   - Test-first approach supports quality standards

✅ CLAUDE.md (project instructions)
   - Specialized agent usage aligns with separation of concerns
   - Authentication flow documentation matches security-first principle
   - PHR and ADR requirements support governance standards

PRINCIPLES VALIDATED:
1. Functional Correctness Across All Layers - Complete
2. Security-First Design - Complete
3. Clear Separation of Concerns - Complete
4. Spec-Driven Development - Complete
5. Production-Oriented Development - Complete

FOLLOW-UP ACTIONS:
None required - constitution is complete and all dependent artifacts are aligned.

═══════════════════════════════════════════════════════════════════════════════
-->

## Core Principles

### I. Functional Correctness Across All Layers
Every component—frontend, backend, and database—must function correctly in isolation and integration. All features must be testable, verifiable, and meet acceptance criteria before being considered complete.

**Requirements:**
- All API endpoints return correct responses for valid and invalid inputs
- Frontend components render correctly and handle all user interactions
- Database operations maintain data integrity and consistency
- Integration between layers works seamlessly
- Error states are handled gracefully at every layer

### II. Security-First Design
Security is not optional. All authentication, authorization, and data handling must follow industry best practices and be implemented correctly from the start.

**Requirements:**
- JWT-based authentication using Better Auth
- All protected routes require valid token verification
- Passwords must be hashed (never stored in plaintext)
- User data must be strictly isolated per user
- No secrets or credentials hardcoded in source code
- All secrets stored in `.env` files (excluded from version control)
- Input validation on both frontend and backend
- Protection against common vulnerabilities (XSS, SQL injection, CSRF)

### III. Clear Separation of Concerns
Each layer of the stack has distinct responsibilities. Frontend handles presentation and user interaction, backend handles business logic and data access, database handles persistence.

**Layer Responsibilities:**
- **Frontend (Next.js)**: UI rendering, user interaction, client-side routing, API consumption
- **Backend (FastAPI)**: RESTful API endpoints, business logic, authentication/authorization, data validation
- **Database (Neon PostgreSQL)**: Data persistence, relationships, constraints, queries
- **ORM (SQLModel)**: Database model definitions, type safety, query building

**Boundaries:**
- Frontend never directly accesses the database
- Backend never contains UI logic
- Database logic stays in SQLModel models and migrations
- Authentication logic centralized in Better Auth integration

### IV. Spec-Driven Development
All features begin with specifications. Implementation follows the spec → plan → tasks → implement → test workflow. No code is written without clear requirements and acceptance criteria.

**Workflow:**
1. **Spec**: Define requirements, acceptance criteria, constraints
2. **Plan**: Design architecture, identify decisions, plan implementation
3. **Tasks**: Break down into testable, dependency-ordered tasks
4. **Implement**: Execute tasks following the plan
5. **Test**: Verify against acceptance criteria

**Documentation:**
- All features documented in `specs/<feature>/spec.md`
- Architecture decisions in `specs/<feature>/plan.md`
- Tasks in `specs/<feature>/tasks.md`
- Significant decisions in `history/adr/`
- All AI interactions in `history/prompts/`

### V. Production-Oriented Development
Code is written for production from day one. This means proper error handling, logging, environment configuration, and deployment readiness.

**Requirements:**
- Environment variables for all configuration
- Proper error handling with meaningful messages
- HTTP status codes follow standards
- Logging for debugging and monitoring
- Code follows framework best practices
- Performance considerations (database queries, API response times)
- Responsive design for desktop and mobile

## Technical Standards

### API Design Standards
- **RESTful Conventions**: Use standard HTTP methods (GET, POST, PUT, DELETE)
- **Resource Naming**: Plural nouns for collections (`/tasks`, `/users`)
- **Status Codes**:
  - 200 OK (success)
  - 201 Created (resource created)
  - 400 Bad Request (validation error)
  - 401 Unauthorized (missing/invalid token)
  - 403 Forbidden (insufficient permissions)
  - 404 Not Found (resource doesn't exist)
  - 500 Internal Server Error (server error)
- **Response Format**: Consistent JSON structure
- **Error Format**: `{"detail": "error message"}` or structured error objects

### Authentication Standards
- **Better Auth Integration**: Use Better Auth for user management
- **JWT Tokens**: Issue JWT tokens on successful authentication
- **Token Format**: `Authorization: Bearer <token>` header
- **Token Verification**: Backend verifies signature using shared secret
- **User Identity**: Extract user ID/email from verified token
- **Session Management**: Handle token expiration and refresh

### Database Standards
- **SQLModel Models**: All database entities defined as SQLModel classes
- **Type Safety**: Use Python type hints for all fields
- **Relationships**: Define foreign keys and relationships explicitly
- **Constraints**: Add NOT NULL, UNIQUE, CHECK constraints where appropriate
- **Migrations**: Track schema changes (manual or automated)
- **Queries**: Use SQLModel query API, avoid raw SQL unless necessary

### Code Quality Standards
- **Next.js Best Practices**:
  - Use App Router (not Pages Router)
  - Server Components by default, Client Components when needed
  - Proper data fetching patterns
  - File-based routing
- **FastAPI Best Practices**:
  - Pydantic models for request/response validation
  - Dependency injection for database sessions
  - Async/await for I/O operations
  - Proper exception handling
- **Python Standards**: Follow PEP 8 style guide
- **TypeScript Standards**: Use strict mode, proper typing

## Technology Constraints

### Required Stack
| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | Next.js (App Router) | 16+ |
| Backend | Python FastAPI | Latest |
| ORM | SQLModel | Latest |
| Database | Neon Serverless PostgreSQL | Latest |
| Authentication | Better Auth | Latest |
| API Client | Axios or Fetch | Latest |

### Communication Protocols
- **Frontend ↔ Backend**: HTTPS REST API
- **Backend ↔ Database**: PostgreSQL protocol via SQLModel
- **Authentication**: JWT tokens in Authorization header

### Environment Configuration
- **Development**: Local `.env` file with development credentials
- **Production**: Environment variables set in deployment platform
- **Required Variables**:
  - `DATABASE_URL`: Neon PostgreSQL connection string
  - `JWT_SECRET`: Secret key for JWT signing/verification
  - `BETTER_AUTH_SECRET`: Better Auth configuration secret
  - `NEXT_PUBLIC_API_URL`: Backend API base URL (for frontend)

### Prohibited Practices
- ❌ Hardcoded secrets or credentials in source code
- ❌ Direct database access from frontend
- ❌ Storing passwords in plaintext
- ❌ Mixing Server and Client Components incorrectly
- ❌ Skipping authentication checks on protected routes
- ❌ Returning other users' data (data leakage)
- ❌ Using deprecated APIs or patterns

## Success Criteria

### Authentication & Authorization
- ✅ Users can sign up with email and password
- ✅ Users can sign in and receive JWT token
- ✅ JWT tokens are validated on every protected API request
- ✅ Tokens expire after configured duration
- ✅ Invalid/expired tokens are rejected with 401 status
- ✅ Users can only access their own data

### Task Management (CRUD)
- ✅ Users can create new tasks
- ✅ Users can view their task list
- ✅ Users can update existing tasks
- ✅ Users can delete tasks
- ✅ All operations persist to database
- ✅ All operations enforce per-user isolation

### API Correctness
- ✅ All endpoints return correct status codes
- ✅ Request validation rejects invalid data
- ✅ Error responses include meaningful messages
- ✅ API follows RESTful conventions
- ✅ Protected endpoints require authentication

### Frontend Quality
- ✅ UI is responsive (desktop and mobile)
- ✅ Forms have proper validation
- ✅ Loading states are shown during API calls
- ✅ Error messages are displayed to users
- ✅ Navigation works correctly
- ✅ Authentication state is managed properly

### System Quality
- ✅ Application passes integration tests
- ✅ Security vulnerabilities are addressed
- ✅ Application can be deployed successfully
- ✅ Environment configuration works correctly
- ✅ Database migrations run successfully

## Governance

### Constitution Authority
This constitution supersedes all other development practices and guidelines. When conflicts arise between this document and other sources, this constitution takes precedence.

### Compliance Requirements
- All code changes must comply with these principles
- All pull requests must be reviewed for constitutional compliance
- Violations must be corrected before merging
- Exceptions require explicit documentation and justification

### Amendment Process
1. Propose amendment with clear rationale
2. Document impact on existing code/practices
3. Get stakeholder approval
4. Update constitution with version increment
5. Create migration plan if needed
6. Communicate changes to team

### Quality Gates
- ✅ All features have specifications before implementation
- ✅ All code follows framework best practices
- ✅ All authentication/authorization is implemented correctly
- ✅ All user data is properly isolated
- ✅ All secrets are in environment variables
- ✅ All tests pass before deployment

### Architectural Decision Records
Significant architectural decisions must be documented in ADRs (`history/adr/`). A decision is significant if it:
- Has long-term consequences
- Involves multiple valid alternatives
- Is cross-cutting and influences system design

**Version**: 1.0.1 | **Ratified**: 2026-02-08 | **Last Amended**: 2026-02-15
