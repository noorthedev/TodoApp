---
id: 0002
title: Phase III AI Agent Architecture Constitution
stage: constitution
date: 2026-02-19
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: system
command: /sp.constitution
labels: ["constitution", "phase-3", "architecture", "mcp", "ai-agent", "stateless", "tool-driven"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

```text
Project: Phase-III – Todo AI Chatbot (Agent + MCP)

Core principles:
- Stateless server architecture
- Tool-driven execution via MCP
- Clear separation of Agent, Tools, API, and Database
- Secure multi-user isolation
- Database as single source of truth

Key standards:
- All task operations must run through MCP tools
- Agent must not directly access database
- Chat endpoint must persist conversation state in DB
- All endpoints require JWT authentication
- Tool inputs/outputs must follow strict schemas
- Ownership enforced on every operation

Architecture constraints:
- Frontend: OpenAI ChatKit
- Backend: FastAPI
- AI: OpenAI Agents SDK
- MCP: Official MCP SDK
- ORM: SQLModel
- Database: Neon PostgreSQL
- Auth: Better Auth (JWT)

Data rules:
- Tasks, Conversations, and Messages linked to user_id
- No cross-user access allowed
- Server holds no in-memory chat state

Security:
- JWT validation required
- Protect against IDOR
- Structured error handling

Success criteria:
- AI manages tasks via natural language
```

## Response snapshot

Updated project constitution from Phase-II (v1.0.1) to Phase-III (v2.0.0) with major architectural changes:

**Version Change**: 1.0.1 → 2.0.0 (MAJOR)
- Backward-incompatible architectural shift from traditional CRUD web app to AI agent-driven system

**Core Principles Redefined**:
1. Functional Correctness → **Stateless Server Architecture**
2. Security-First Design → **Security-First Design** (retained, enhanced for MCP)
3. Clear Separation of Concerns → **Tool-Driven Execution Pattern**
4. Spec-Driven Development → **Agent-Database Separation**
5. Production-Oriented Development → **Database as Single Source of Truth**

**New Technology Stack**:
- Frontend: Next.js → OpenAI ChatKit
- AI Layer: None → OpenAI Agents SDK
- MCP Layer: None → Official MCP SDK
- Backend: FastAPI (retained)
- Database: Neon PostgreSQL (retained)
- Auth: Better Auth JWT (retained)

**New Standards Added**:
- MCP Tool Standards (schemas, authorization, error handling)
- Agent Integration Standards (OpenAI SDK, tool calling, context management)
- Conversation State Management (persistence, retrieval, isolation)

**Architecture Diagram**: Added visual representation of layered architecture showing Frontend → Backend → Agent → MCP Tools → Database flow.

**Sync Impact Report**: Documented required updates to templates (spec, plan, tasks) and CLAUDE.md to align with Phase-III architecture.

## Outcome

- ✅ Impact: Major architectural transformation documented; establishes foundation for Phase-III AI agent implementation
- 🧪 Tests: N/A (constitution is governance document)
- 📁 Files: 1 file updated (.specify/memory/constitution.md)
- 🔁 Next prompts: Update templates (spec, plan, tasks), update CLAUDE.md, create ADRs for stateless architecture and MCP integration
- 🧠 Reflection: Constitution successfully captures the paradigm shift from traditional web app to AI agent-driven system with clear separation of concerns and security boundaries

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual review - PASS (all placeholders filled, principles clear, standards comprehensive)
- Prompt variant (if applicable): Standard constitution update workflow
- Next experiment (smallest change to try): Apply constitution principles to first Phase-III feature specification
