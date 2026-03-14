---
id: 0001
title: Update CLAUDE.md for Phase III Architecture
stage: general
date: 2026-02-19
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: system
command: update CLAUDE.md
labels: ["claude-md", "phase-3", "documentation", "architecture", "mcp", "stateless", "ai-agent", "tools"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - CLAUDE.md
tests:
  - none
---

## Prompt

```text
update CLAUDE.md
```

## Response snapshot

Updated CLAUDE.md to align with Phase-III constitution (v2.0.0). Major changes include:

**Project Overview Updated:**
- Changed from "Phase II Todo Full-Stack Web Application" to "Phase III Todo AI Chatbot"
- Updated description to reflect AI-powered natural language task management

**Technology Stack Updated:**
- Frontend: Next.js 16+ → OpenAI ChatKit
- Added: AI Agent (OpenAI Agents SDK)
- Added: MCP Tools (Official MCP SDK)
- Retained: FastAPI, SQLModel, Neon PostgreSQL, Better Auth

**Specialized Agent Usage Updated:**
- Updated frontend agent guidance for ChatKit integration
- Added MCP Tool Development guidance (using fastapi-backend-expert)
- Added AI Agent Integration guidance (using fastapi-backend-expert)
- Removed API Client Integration (no longer needed for Phase-III)

**Architecture Overview Added:**
- New section explaining stateless, tool-driven architecture
- Visual flow diagram: User → ChatKit → Backend → Agent → MCP Tools → Database
- Key principles: stateless server, tool-driven, agent-database separation

**Authentication Flow Updated:**
- Extended 5-step flow to 10-step flow including agent and MCP tools
- Added conversation persistence steps
- Added agent invocation and tool authorization steps

**Stateless Architecture Patterns Added:**
- Pattern 1: Conversation Persistence (immediate database persistence)
- Pattern 2: Agent Invocation (stateless agent with fresh context)
- Pattern 3: MCP Tool Authorization (user context enforcement)

**MCP Tool Standards Added:**
- Tool definition requirements
- Authorization requirements with code examples
- Error handling requirements
- Tool best practices (DO/DON'T lists)

**Authorization Patterns Updated:**
- Replaced traditional endpoint patterns with MCP tool patterns
- Updated from HTTPException to structured error responses
- Changed from endpoint-level to tool-level authorization
- Added user_context parameter pattern for tools

**Project Requirements Updated:**
- Changed from CRUD web app to AI chatbot requirements
- Added natural language interaction requirements
- Added agent integration requirements
- Added conversation persistence requirements

**Active Technologies Updated:**
- Removed Phase-II specific technologies (Next.js, Axios, TailwindCSS)
- Added Phase-III technologies (ChatKit, OpenAI Agents SDK, MCP SDK)
- Updated feature references from phase-2 to phase-3-ai-chatbot

**Recent Changes Updated:**
- Replaced Phase-II changes with Phase-III architectural changes
- Listed key Phase-III additions (agent, MCP tools, stateless architecture)

## Outcome

- ✅ Impact: CLAUDE.md fully aligned with Phase-III constitution; provides comprehensive guidance for AI agent-driven development
- 🧪 Tests: N/A (documentation update)
- 📁 Files: 1 file updated (CLAUDE.md)
- 🔁 Next prompts: Update template files (spec-template.md, plan-template.md, tasks-template.md), create ADRs for architectural decisions
- 🧠 Reflection: Successfully transformed project guidance from traditional web app patterns to AI agent-driven patterns with MCP tools, maintaining security-first approach throughout

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual review - PASS (all Phase-II references updated, new Phase-III patterns documented, code examples provided)
- Prompt variant (if applicable): Standard documentation update workflow
- Next experiment (smallest change to try): Apply updated CLAUDE.md guidance to first Phase-III feature specification
