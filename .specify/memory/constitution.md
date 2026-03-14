# Todo AI Chatbot Constitution
<!-- Hackathon Phase-III: AI-Powered Task Management with MCP Tools -->

<!--
═══════════════════════════════════════════════════════════════════════════════
CONSTITUTION SYNC IMPACT REPORT
═══════════════════════════════════════════════════════════════════════════════

Validation Date: 2026-02-19
Constitution Version: 2.0.0 (major)
Action: Major architectural shift from Phase-II to Phase-III

VERSION CHANGE RATIONALE:
- MAJOR bump (1.0.1 → 2.0.0) due to backward-incompatible architectural changes
- Fundamental shift from traditional CRUD web app to AI agent-driven system
- New technology stack: OpenAI Agents SDK, MCP SDK, ChatKit frontend
- New architectural paradigm: stateless server, tool-driven execution
- Principles redefined to support agent-based architecture

MODIFIED PRINCIPLES:
1. Functional Correctness Across All Layers → Stateless Server Architecture
2. Security-First Design → Security-First Design (retained, updated for MCP)
3. Clear Separation of Concerns → Tool-Driven Execution Pattern
4. Spec-Driven Development → Agent-Database Separation (new focus)
5. Production-Oriented Development → Database as Single Source of Truth (new)

ADDED SECTIONS:
- MCP Tool Standards
- Agent Integration Standards
- Conversation State Management
- OpenAI Agents SDK requirements

REMOVED SECTIONS:
- Next.js specific frontend standards (replaced with ChatKit)
- Traditional CRUD API patterns (replaced with tool-driven patterns)

TECHNOLOGY CHANGES:
- Frontend: Next.js 16+ → OpenAI ChatKit
- AI Layer: None → OpenAI Agents SDK
- MCP Layer: None → Official MCP SDK
- Backend: FastAPI (retained)
- Database: Neon PostgreSQL (retained)
- Auth: Better Auth JWT (retained)

TEMPLATE CONSISTENCY CHECK:
⚠ .specify/templates/spec-template.md
   - Requires update: Add MCP tool specification sections
   - Requires update: Add agent interaction acceptance criteria patterns

⚠ .specify/templates/plan-template.md
   - Requires update: Add MCP architecture decision sections
   - Requires update: Add agent-tool integration planning guidance

⚠ .specify/templates/tasks-template.md
   - Requires update: Add MCP tool implementation task patterns
   - Requires update: Add agent integration testing task types

⚠ CLAUDE.md (project instructions)
   - Requires update: Add MCP-specific agent usage guidelines
   - Requires update: Update technology stack references
   - Requires update: Add stateless architecture patterns

FOLLOW-UP ACTIONS:
1. Update all template files to reflect Phase-III architecture
2. Create ADR for stateless architecture decision
3. Create ADR for MCP tool integration approach
4. Update CLAUDE.md with Phase-III specific agent guidelines
5. Document migration path from Phase-II to Phase-III

═══════════════════════════════════════════════════════════════════════════════
-->

## Core Principles

### I. Stateless Server Architecture
The server must maintain no in-memory state for conversations or agent interactions. All state must be persisted to the database immediately. This ensures scalability, reliability, and enables horizontal scaling.

**Requirements:**
- No in-memory conversation history or chat state
- All messages persisted to database before processing
- Agent interactions are stateless (each request is independent)
- Server can be restarted without losing conversation context
- Multiple server instances can handle requests for the same user
- Database is the single source of truth for all state

**Rationale:**
Stateless architecture enables horizontal scaling, simplifies deployment, prevents data loss on server restart, and ensures consistent behavior across distributed systems.

### II. Security-First Design
Security is not optional. All authentication, authorization, and data handling must follow industry best practices and be implemented correctly from the start. MCP tools must enforce security boundaries.

**Requirements:**
- JWT-based authentication using Better Auth
- All protected routes require valid token verification
- Passwords must be hashed (never stored in plaintext)
- User data must be strictly isolated per user
- No secrets or credentials hardcoded in source code
- All secrets stored in `.env` files (excluded from version control)
- Input validation on all API endpoints and MCP tools
- Protection against common vulnerabilities (XSS, SQL injection, CSRF, IDOR)
- MCP tools must validate user ownership before operations
- Agent must not bypass authorization checks

**Rationale:**
Security vulnerabilities in AI-powered systems can have amplified impact. MCP tools provide direct database access patterns that require strict authorization enforcement.

### III. Tool-Driven Execution Pattern
All task operations must be executed through MCP tools. The AI agent must not directly access the database or implement business logic. Tools provide the interface between agent intent and system actions.

**Requirements:**
- All CRUD operations on tasks implemented as MCP tools
- Tools have strict input/output schemas (Pydantic models)
- Agent calls tools with structured parameters
- Tools enforce authorization and validation
- Tools return structured responses (success/error)
- No direct database access from agent code
- Tool implementations are testable independently
- Tool catalog is discoverable by the agent

**Rationale:**
Tool-driven architecture provides clear separation of concerns, enables independent testing, enforces security boundaries, and makes agent behavior auditable and controllable.

### IV. Agent-Database Separation
The AI agent must never directly access the database. All data operations must go through MCP tools that enforce authorization, validation, and business rules.

**Requirements:**
- Agent code has no database connection or ORM imports
- All database operations encapsulated in MCP tools
- Tools enforce per-user data isolation
- Tools validate all inputs before database operations
- Agent receives only structured tool responses
- Database schema changes do not affect agent code
- Tools provide abstraction layer for data access

**Rationale:**
Separation prevents the agent from bypassing security checks, ensures consistent authorization enforcement, enables independent evolution of agent and database layers, and makes the system more maintainable.

### V. Database as Single Source of Truth
All application state—tasks, conversations, messages, user data—must be persisted in the database. No critical state exists only in memory or external systems.

**Requirements:**
- All conversations stored in database with user_id
- All messages (user and assistant) persisted immediately
- Task operations persist before returning success
- No caching of critical state in memory
- Database transactions ensure consistency
- State can be fully reconstructed from database
- Audit trail for all state changes

**Rationale:**
Database as single source of truth ensures data durability, enables recovery from failures, supports debugging and auditing, and allows multiple server instances to share state.

## Technical Standards

### API Design Standards
- **RESTful Conventions**: Use standard HTTP methods (GET, POST, PUT, DELETE)
- **Resource Naming**: Plural nouns for collections (`/tasks`, `/conversations`)
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

### MCP Tool Standards
- **Tool Definition**: Each tool has clear name, description, and schema
- **Input Schema**: Pydantic models with strict validation
- **Output Schema**: Structured responses (success/error with data)
- **Authorization**: Every tool validates user ownership
- **Error Handling**: Tools return structured errors, never raise exceptions to agent
- **Idempotency**: Tools should be idempotent where possible
- **Atomicity**: Database operations in tools use transactions
- **Discoverability**: Tool catalog available to agent at runtime

### Agent Integration Standards
- **OpenAI Agents SDK**: Use official SDK for agent implementation
- **Tool Calling**: Agent uses function calling to invoke MCP tools
- **Context Management**: Agent receives conversation history from database
- **Response Streaming**: Support streaming responses to frontend
- **Error Recovery**: Agent handles tool errors gracefully
- **Prompt Engineering**: System prompts define agent behavior and constraints
- **Token Management**: Monitor and optimize token usage

### Conversation State Management
- **Persistence**: All messages saved to database immediately
- **Retrieval**: Conversation history loaded from database per request
- **User Isolation**: Conversations filtered by user_id
- **Message Format**: Structured format (role, content, timestamp, metadata)
- **Context Window**: Manage conversation length for token limits
- **Cleanup**: Archive or delete old conversations per retention policy

### Authentication Standards
- **Better Auth Integration**: Use Better Auth for user management
- **JWT Tokens**: Issue JWT tokens on successful authentication
- **Token Format**: `Authorization: Bearer <token>` header
- **Token Verification**: Backend verifies signature using shared secret
- **User Identity**: Extract user ID/email from verified token
- **Session Management**: Handle token expiration and refresh
- **MCP Tool Auth**: Tools receive authenticated user context

### Database Standards
- **SQLModel Models**: All database entities defined as SQLModel classes
- **Type Safety**: Use Python type hints for all fields
- **Relationships**: Define foreign keys and relationships explicitly
- **Constraints**: Add NOT NULL, UNIQUE, CHECK constraints where appropriate
- **Migrations**: Track schema changes (manual or automated)
- **Queries**: Use SQLModel query API, avoid raw SQL unless necessary
- **Async Operations**: Use async database connections for performance

### Code Quality Standards
- **FastAPI Best Practices**:
  - Pydantic models for request/response validation
  - Dependency injection for database sessions
  - Async/await for I/O operations
  - Proper exception handling
- **MCP Tool Best Practices**:
  - One tool per operation (create_task, update_task, etc.)
  - Clear naming conventions
  - Comprehensive input validation
  - Structured error responses
- **Agent Best Practices**:
  - Clear system prompts
  - Proper tool selection logic
  - Error handling and recovery
  - Token usage optimization
- **Python Standards**: Follow PEP 8 style guide
- **TypeScript Standards**: Use strict mode, proper typing (for ChatKit frontend)

## Technology Constraints

### Required Stack
| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | OpenAI ChatKit | Latest |
| AI Agent | OpenAI Agents SDK | Latest |
| MCP Tools | Official MCP SDK | Latest |
| Backend | Python FastAPI | Latest |
| ORM | SQLModel | Latest |
| Database | Neon Serverless PostgreSQL | Latest |
| Authentication | Better Auth (JWT) | Latest |

### Communication Protocols
- **Frontend ↔ Backend**: HTTPS REST API (chat endpoint)
- **Backend ↔ Agent**: OpenAI Agents SDK function calling
- **Agent ↔ Tools**: MCP protocol (function calls with schemas)
- **Backend ↔ Database**: PostgreSQL protocol via SQLModel
- **Authentication**: JWT tokens in Authorization header

### Architecture Layers
```
┌─────────────────────────────────────────────────────────┐
│ Frontend (OpenAI ChatKit)                               │
│ - Chat UI                                               │
│ - Message display                                       │
│ - User input                                            │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTPS REST API
                      │ POST /api/chat
                      │ Authorization: Bearer <JWT>
┌─────────────────────▼───────────────────────────────────┐
│ Backend (FastAPI)                                       │
│ - JWT validation                                        │
│ - Conversation persistence                              │
│ - Agent orchestration                                   │
└─────────────────────┬───────────────────────────────────┘
                      │ OpenAI Agents SDK
                      │ Function calling
┌─────────────────────▼───────────────────────────────────┐
│ AI Agent (OpenAI Agents SDK)                            │
│ - Natural language understanding                        │
│ - Tool selection                                        │
│ - Response generation                                   │
└─────────────────────┬───────────────────────────────────┘
                      │ MCP Protocol
                      │ Tool calls with schemas
┌─────────────────────▼───────────────────────────────────┐
│ MCP Tools (Official MCP SDK)                            │
│ - create_task, update_task, delete_task, list_tasks     │
│ - Authorization enforcement                             │
│ - Input validation                                      │
│ - Database operations                                   │
└─────────────────────┬───────────────────────────────────┘
                      │ SQLModel ORM
                      │ Async queries
┌─────────────────────▼───────────────────────────────────┐
│ Database (Neon PostgreSQL)                              │
│ - Users, Tasks, Conversations, Messages                 │
│ - Single source of truth                                │
└─────────────────────────────────────────────────────────┘
```

### Environment Configuration
- **Development**: Local `.env` file with development credentials
- **Production**: Environment variables set in deployment platform
- **Required Variables**:
  - `DATABASE_URL`: Neon PostgreSQL connection string
  - `JWT_SECRET`: Secret key for JWT signing/verification
  - `BETTER_AUTH_SECRET`: Better Auth configuration secret
  - `OPENAI_API_KEY`: OpenAI API key for agent
  - `MCP_SERVER_URL`: MCP server endpoint (if separate)

### Prohibited Practices
- ❌ Hardcoded secrets or credentials in source code
- ❌ Direct database access from agent code
- ❌ Storing conversation state in memory only
- ❌ Agent bypassing MCP tools for data operations
- ❌ MCP tools without authorization checks
- ❌ Storing passwords in plaintext
- ❌ Returning other users' data (data leakage)
- ❌ Using deprecated APIs or patterns
- ❌ Synchronous blocking operations in async endpoints

## Success Criteria

### Authentication & Authorization
- ✅ Users can sign up with email and password
- ✅ Users can sign in and receive JWT token
- ✅ JWT tokens are validated on every protected API request
- ✅ Tokens expire after configured duration
- ✅ Invalid/expired tokens are rejected with 401 status
- ✅ Users can only access their own data
- ✅ MCP tools enforce per-user authorization

### AI Agent Functionality
- ✅ Agent understands natural language task requests
- ✅ Agent correctly selects appropriate MCP tools
- ✅ Agent creates tasks via create_task tool
- ✅ Agent updates tasks via update_task tool
- ✅ Agent deletes tasks via delete_task tool
- ✅ Agent lists tasks via list_tasks tool
- ✅ Agent provides helpful responses to user queries
- ✅ Agent handles tool errors gracefully

### MCP Tool Correctness
- ✅ All tools validate user ownership before operations
- ✅ All tools validate input schemas
- ✅ All tools return structured responses
- ✅ Tools enforce database constraints
- ✅ Tools use transactions for consistency
- ✅ Tools handle errors without crashing
- ✅ Tool catalog is discoverable by agent

### Conversation Management
- ✅ All messages persisted to database immediately
- ✅ Conversation history loaded from database per request
- ✅ Users can only access their own conversations
- ✅ Message order preserved correctly
- ✅ Conversation context maintained across requests
- ✅ Server restart does not lose conversation state

### Stateless Architecture
- ✅ Server maintains no in-memory conversation state
- ✅ Multiple server instances can handle same user
- ✅ Server can be restarted without data loss
- ✅ All state reconstructable from database
- ✅ Horizontal scaling works correctly

### Frontend Quality
- ✅ Chat UI renders correctly
- ✅ Messages display in correct order
- ✅ User input is captured and sent
- ✅ Loading states shown during API calls
- ✅ Error messages displayed to users
- ✅ Authentication state managed properly
- ✅ Streaming responses work (if implemented)

### System Quality
- ✅ Application passes integration tests
- ✅ Security vulnerabilities are addressed
- ✅ Application can be deployed successfully
- ✅ Environment configuration works correctly
- ✅ Database migrations run successfully
- ✅ Agent-tool integration works end-to-end

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
- ✅ All MCP tools enforce authorization
- ✅ Agent never directly accesses database
- ✅ All state persisted to database
- ✅ All tests pass before deployment

### Architectural Decision Records
Significant architectural decisions must be documented in ADRs (`history/adr/`). A decision is significant if it:
- Has long-term consequences
- Involves multiple valid alternatives
- Is cross-cutting and influences system design

**Version**: 2.0.0 | **Ratified**: 2026-02-19 | **Last Amended**: 2026-02-19
