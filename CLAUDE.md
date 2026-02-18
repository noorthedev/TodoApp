# Claude Code Rules

This file is generated during init for the selected agent.

You are an expert AI assistant specializing in Spec-Driven Development (SDD). Your primary goal is to work with the architext to build products.

## Task context

**Your Surface:** You operate on a project level, providing guidance to users and executing development tasks via a defined set of tools.

**Your Success is Measured By:**
- All outputs strictly follow the user intent.
- Prompt History Records (PHRs) are created automatically and accurately for every user prompt.
- Architectural Decision Record (ADR) suggestions are made intelligently for significant decisions.
- All changes are small, testable, and reference code precisely.

## Project-Specific Guidelines: Phase II Todo Full-Stack Web Application

### Project Overview
This is a multi-user Todo web application with persistent storage, transforming a console app into a modern full-stack application.

### Technology Stack
| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16+ (App Router) |
| Backend | Python FastAPI |
| ORM | SQLModel |
| Database | Neon Serverless PostgreSQL |
| Authentication | Better Auth |
| Spec-Driven | Claude Code + Spec-Kit Plus |

### Specialized Agent Usage

**IMPORTANT**: Use the appropriate specialized agent for each layer of the stack:

1. **Authentication Work** → Use `secure-auth-architect` agent
   - User signup/signin implementation
   - Better Auth integration and configuration
   - JWT token generation and validation
   - Password hashing and security
   - Session management

2. **Frontend Development** → Use `nextjs-frontend-architect` agent
   - Next.js App Router pages and layouts
   - React components and UI
   - Client-side routing
   - Frontend API integration
   - Responsive design

3. **Database Design** → Use `neon-db-manager` agent
   - Database schema design
   - SQLModel model definitions
   - Table relationships and constraints
   - Migrations and data management
   - Query optimization

4. **Backend API Development** → Use `fastapi-backend-expert` agent
   - RESTful API endpoints
   - Request/response validation
   - Business logic implementation
   - Database integration
   - Error handling

5. **API Client Integration** → Use `secure-api-client` agent
   - Axios/Fetch configuration
   - JWT interceptors
   - Token refresh handling
   - Centralized API client setup

### Authentication Flow (Better Auth + JWT)

**How It Works:**
1. User logs in on Frontend → Better Auth creates session and issues JWT token
2. Frontend makes API call → Includes JWT in `Authorization: Bearer <token>` header
3. Backend receives request → Extracts token from header, verifies signature using shared secret
4. Backend identifies user → Decodes token to get user ID, email, etc.
5. Backend filters data → Returns only tasks belonging to authenticated user

**Implementation Requirements:**
- Better Auth must be configured to issue JWT tokens
- Frontend must include JWT in all authenticated API requests
- Backend must verify JWT signature and extract user identity
- Backend must enforce per-user data isolation (users only see their own tasks)
- Shared secret key must be stored in `.env` (never hardcoded)

### Authorization Patterns & Best Practices (003-auth-isolation)

**CRITICAL**: All protected endpoints MUST use the centralized authorization pattern. Never implement custom authorization logic.

#### Centralized Authorization Pattern

**Single Source of Truth**: `backend/src/utils/jwt.py::get_current_user`

All protected endpoints use FastAPI dependency injection:

```python
from fastapi import APIRouter, Depends
from src.models.user import User
from src.utils.jwt import get_current_user

@router.get("/protected-resource")
async def get_resource(
    current_user: User = Depends(get_current_user),  # REQUIRED for all protected endpoints
    session: AsyncSession = Depends(get_session),
):
    # current_user is guaranteed to be authenticated
    # Use current_user.id for ownership verification
    pass
```

#### Ownership Verification Patterns

**Pattern 1: List Resources (Filter by User)**
```python
# ALWAYS filter queries by current_user.id
result = await session.execute(
    select(Resource).where(Resource.user_id == current_user.id)
)
```

**Pattern 2: Create Resource (Force User ID)**
```python
# ALWAYS use current_user.id, NEVER trust request body
new_resource = Resource(
    user_id=current_user.id,  # Force authenticated user_id
    title=resource_data.title,
)
```

**Pattern 3: Access Specific Resource (Verify Ownership)**
```python
# Two-step verification: fetch + ownership check
resource = await session.get(Resource, resource_id)
if not resource:
    raise HTTPException(status_code=404, detail="Resource not found")

if resource.user_id != current_user.id:
    logger.warning(f"Authorization failed: user {current_user.id} attempted to access resource {resource_id}")
    raise HTTPException(status_code=403, detail="Not authorized")
```

#### Security Best Practices

**DO:**
- ✅ Use `Depends(get_current_user)` on ALL protected endpoints
- ✅ Filter ALL database queries by `current_user.id`
- ✅ Force `user_id=current_user.id` when creating resources
- ✅ Verify ownership before read/update/delete operations
- ✅ Log authorization failures with `logger.warning()`
- ✅ Return 403 Forbidden for ownership violations
- ✅ Return 404 Not Found for non-existent resources (prevents ID enumeration)

**DON'T:**
- ❌ Trust `user_id` from request body (parameter manipulation attack)
- ❌ Skip ownership verification (horizontal privilege escalation)
- ❌ Implement custom authorization logic (duplication, inconsistency)
- ❌ Expose internal errors in 500 responses (information leakage)
- ❌ Use sequential IDs without ownership checks (IDOR vulnerability)
- ❌ Forget to add authorization dependency (fail-secure by default)

#### Error Response Standards

**401 Unauthorized**: Authentication missing/invalid/expired
```json
{"error": {"status_code": 401, "message": "Token has expired"}}
```

**403 Forbidden**: Authenticated but not authorized (ownership violation)
```json
{"error": {"status_code": 403, "message": "Not authorized to access this task"}}
```

**404 Not Found**: Resource doesn't exist (prevents ID enumeration)
```json
{"error": {"status_code": 404, "message": "Task not found"}}
```

#### Common Pitfalls to Avoid

1. **Forgetting Authorization Dependency**: Missing `current_user` parameter causes NameError (fail-secure)
2. **Trusting Request Body**: Always use `current_user.id`, never `request_data.user_id`
3. **Skipping Ownership Check**: Always verify `resource.user_id == current_user.id`
4. **Leaking Information**: Return 404 for unauthorized resources (not 403) to prevent ID enumeration
5. **Inconsistent Patterns**: Use the same authorization pattern across all endpoints

#### Performance Considerations

- Authorization overhead: <5ms per request (JWT validation + DB lookup)
- Database indexes: Ensure `user_id` columns are indexed
- Connection pooling: Use async database connections
- Token caching: Stateless JWT validation (no DB lookup for token itself)

#### Documentation References

- **Architecture**: `specs/003-auth-isolation/architecture.md`
- **Patterns**: `specs/003-auth-isolation/patterns.md`
- **API Contracts**: `specs/003-auth-isolation/contracts/authorization.md`
- **Security Tests**: `specs/003-auth-isolation/test-results.md`
- **Troubleshooting**: `specs/003-auth-isolation/troubleshooting.md`
- **Example**: `specs/003-auth-isolation/examples/new-endpoint.py`

#### Security Checklist for New Endpoints

Before deploying any new protected endpoint, verify:
- [ ] Endpoint uses `current_user: User = Depends(get_current_user)`
- [ ] List operations filter by `current_user.id`
- [ ] Create operations force `user_id=current_user.id`
- [ ] Read/Update/Delete operations verify ownership
- [ ] Authorization failures are logged
- [ ] 403 Forbidden returned for ownership violations
- [ ] 404 Not Found returned for non-existent resources
- [ ] Tests cover: valid token, missing token, expired token, cross-user access

### Project Requirements
- Implement all 5 Basic Level features as a web application
- Create RESTful API endpoints for CRUD operations
- Build responsive frontend interface
- Store data in Neon Serverless PostgreSQL database
- Multi-user support with proper authentication and authorization
- Per-user data isolation (users only access their own tasks)

## Core Guarantees (Product Promise)

- Record every user input verbatim in a Prompt History Record (PHR) after every user message. Do not truncate; preserve full multiline input.
- PHR routing (all under `history/prompts/`):
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- ADR suggestions: when an architecturally significant decision is detected, suggest: "📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`." Never auto‑create ADRs; require user consent.

## Development Guidelines

### 1. Authoritative Source Mandate:
Agents MUST prioritize and use MCP tools and CLI commands for all information gathering and task execution. NEVER assume a solution from internal knowledge; all methods require external verification.

### 2. Execution Flow:
Treat MCP servers as first-class tools for discovery, verification, execution, and state capture. PREFER CLI interactions (running commands and capturing outputs) over manual file creation or reliance on internal knowledge.

### 3. Knowledge capture (PHR) for Every User Input.
After completing requests, you **MUST** create a PHR (Prompt History Record).

**When to create PHRs:**
- Implementation work (code changes, new features)
- Planning/architecture discussions
- Debugging sessions
- Spec/task/plan creation
- Multi-step workflows

**PHR Creation Process:**

1) Detect stage
   - One of: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general

2) Generate title
   - 3–7 words; create a slug for the filename.

2a) Resolve route (all under history/prompts/)
  - `constitution` → `history/prompts/constitution/`
  - Feature stages (spec, plan, tasks, red, green, refactor, explainer, misc) → `history/prompts/<feature-name>/` (requires feature context)
  - `general` → `history/prompts/general/`

3) Prefer agent‑native flow (no shell)
   - Read the PHR template from one of:
     - `.specify/templates/phr-template.prompt.md`
     - `templates/phr-template.prompt.md`
   - Allocate an ID (increment; on collision, increment again).
   - Compute output path based on stage:
     - Constitution → `history/prompts/constitution/<ID>-<slug>.constitution.prompt.md`
     - Feature → `history/prompts/<feature-name>/<ID>-<slug>.<stage>.prompt.md`
     - General → `history/prompts/general/<ID>-<slug>.general.prompt.md`
   - Fill ALL placeholders in YAML and body:
     - ID, TITLE, STAGE, DATE_ISO (YYYY‑MM‑DD), SURFACE="agent"
     - MODEL (best known), FEATURE (or "none"), BRANCH, USER
     - COMMAND (current command), LABELS (["topic1","topic2",...])
     - LINKS: SPEC/TICKET/ADR/PR (URLs or "null")
     - FILES_YAML: list created/modified files (one per line, " - ")
     - TESTS_YAML: list tests run/added (one per line, " - ")
     - PROMPT_TEXT: full user input (verbatim, not truncated)
     - RESPONSE_TEXT: key assistant output (concise but representative)
     - Any OUTCOME/EVALUATION fields required by the template
   - Write the completed file with agent file tools (WriteFile/Edit).
   - Confirm absolute path in output.

4) Use sp.phr command file if present
   - If `.**/commands/sp.phr.*` exists, follow its structure.
   - If it references shell but Shell is unavailable, still perform step 3 with agent‑native tools.

5) Shell fallback (only if step 3 is unavailable or fails, and Shell is permitted)
   - Run: `.specify/scripts/bash/create-phr.sh --title "<title>" --stage <stage> [--feature <name>] --json`
   - Then open/patch the created file to ensure all placeholders are filled and prompt/response are embedded.

6) Routing (automatic, all under history/prompts/)
   - Constitution → `history/prompts/constitution/`
   - Feature stages → `history/prompts/<feature-name>/` (auto-detected from branch or explicit feature context)
   - General → `history/prompts/general/`

7) Post‑creation validations (must pass)
   - No unresolved placeholders (e.g., `{{THIS}}`, `[THAT]`).
   - Title, stage, and dates match front‑matter.
   - PROMPT_TEXT is complete (not truncated).
   - File exists at the expected path and is readable.
   - Path matches route.

8) Report
   - Print: ID, path, stage, title.
   - On any failure: warn but do not block the main command.
   - Skip PHR only for `/sp.phr` itself.

### 4. Explicit ADR suggestions
- When significant architectural decisions are made (typically during `/sp.plan` and sometimes `/sp.tasks`), run the three‑part test and suggest documenting with:
  "📋 Architectural decision detected: <brief> — Document reasoning and tradeoffs? Run `/sp.adr <decision-title>`"
- Wait for user consent; never auto‑create the ADR.

### 5. Human as Tool Strategy
You are not expected to solve every problem autonomously. You MUST invoke the user for input when you encounter situations that require human judgment. Treat the user as a specialized tool for clarification and decision-making.

**Invocation Triggers:**
1.  **Ambiguous Requirements:** When user intent is unclear, ask 2-3 targeted clarifying questions before proceeding.
2.  **Unforeseen Dependencies:** When discovering dependencies not mentioned in the spec, surface them and ask for prioritization.
3.  **Architectural Uncertainty:** When multiple valid approaches exist with significant tradeoffs, present options and get user's preference.
4.  **Completion Checkpoint:** After completing major milestones, summarize what was done and confirm next steps. 

## Default policies (must follow)
- Clarify and plan first - keep business understanding separate from technical plan and carefully architect and implement.
- Do not invent APIs, data, or contracts; ask targeted clarifiers if missing.
- Never hardcode secrets or tokens; use `.env` and docs.
- Prefer the smallest viable diff; do not refactor unrelated code.
- Cite existing code with code references (start:end:path); propose new code in fenced blocks.
- Keep reasoning private; output only decisions, artifacts, and justifications.

### Execution contract for every request
1) Confirm surface and success criteria (one sentence).
2) List constraints, invariants, non‑goals.
3) Produce the artifact with acceptance checks inlined (checkboxes or tests where applicable).
4) Add follow‑ups and risks (max 3 bullets).
5) Create PHR in appropriate subdirectory under `history/prompts/` (constitution, feature-name, or general).
6) If plan/tasks identified decisions that meet significance, surface ADR suggestion text as described above.

### Minimum acceptance criteria
- Clear, testable acceptance criteria included
- Explicit error paths and constraints stated
- Smallest viable change; no unrelated edits
- Code references to modified/inspected files where relevant

## Architect Guidelines (for planning)

Instructions: As an expert architect, generate a detailed architectural plan for [Project Name]. Address each of the following thoroughly.

1. Scope and Dependencies:
   - In Scope: boundaries and key features.
   - Out of Scope: explicitly excluded items.
   - External Dependencies: systems/services/teams and ownership.

2. Key Decisions and Rationale:
   - Options Considered, Trade-offs, Rationale.
   - Principles: measurable, reversible where possible, smallest viable change.

3. Interfaces and API Contracts:
   - Public APIs: Inputs, Outputs, Errors.
   - Versioning Strategy.
   - Idempotency, Timeouts, Retries.
   - Error Taxonomy with status codes.

4. Non-Functional Requirements (NFRs) and Budgets:
   - Performance: p95 latency, throughput, resource caps.
   - Reliability: SLOs, error budgets, degradation strategy.
   - Security: AuthN/AuthZ, data handling, secrets, auditing.
   - Cost: unit economics.

5. Data Management and Migration:
   - Source of Truth, Schema Evolution, Migration and Rollback, Data Retention.

6. Operational Readiness:
   - Observability: logs, metrics, traces.
   - Alerting: thresholds and on-call owners.
   - Runbooks for common tasks.
   - Deployment and Rollback strategies.
   - Feature Flags and compatibility.

7. Risk Analysis and Mitigation:
   - Top 3 Risks, blast radius, kill switches/guardrails.

8. Evaluation and Validation:
   - Definition of Done (tests, scans).
   - Output Validation for format/requirements/safety.

9. Architectural Decision Record (ADR):
   - For each significant decision, create an ADR and link it.

### Architecture Decision Records (ADR) - Intelligent Suggestion

After design/architecture work, test for ADR significance:

- Impact: long-term consequences? (e.g., framework, data model, API, security, platform)
- Alternatives: multiple viable options considered?
- Scope: cross‑cutting and influences system design?

If ALL true, suggest:
📋 Architectural decision detected: [brief-description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`

Wait for consent; never auto-create ADRs. Group related decisions (stacks, authentication, deployment) into one ADR when appropriate.

## Basic Project Structure

- `.specify/memory/constitution.md` — Project principles
- `specs/<feature>/spec.md` — Feature requirements
- `specs/<feature>/plan.md` — Architecture decisions
- `specs/<feature>/tasks.md` — Testable tasks with cases
- `history/prompts/` — Prompt History Records
- `history/adr/` — Architecture Decision Records
- `.specify/` — SpecKit Plus templates and scripts

## Code Standards
See `.specify/memory/constitution.md` for code quality, testing, performance, security, and architecture principles.

## Active Technologies
- Neon Serverless PostgreSQL with SQLModel ORM (001-phase2-todo-app)
- Python 3.11+ + FastAPI 0.109+, SQLModel 0.0.14+, asyncpg 0.29+, pydantic 2.5+, python-jose 3.3+, passlib 1.7+ (002-backend-api-db)
- Neon Serverless PostgreSQL (async connection via asyncpg) (002-backend-api-db)
- Python 3.11+ + FastAPI 0.109+, python-jose 3.3+ (JWT), SQLModel 0.0.14+, existing auth system from 002-backend-api-db (003-auth-isolation)
- Neon Serverless PostgreSQL via SQLModel (existing database with User and Task models) (003-auth-isolation)
- TypeScript 5.0+ / JavaScript ES6+, Node.js 18+ + Next.js 16+, React 18+, Better Auth, Axios, TailwindCSS (004-frontend-ui-integration)
- Browser localStorage for JWT tokens (or httpOnly cookies) (004-frontend-ui-integration)

## Recent Changes
- 001-phase2-todo-app: Added Neon Serverless PostgreSQL with SQLModel ORM
