# Research: MCP Server & Task Tools Integration

**Feature**: 005-mcp-task-tools
**Date**: 2026-02-19
**Status**: Complete

## Research Questions

### Q1: Which MCP SDK should we use?

**Decision**: Official MCP SDK (Python)

**Rationale**:
- Official SDK maintained by Anthropic/OpenAI consortium
- Native Python support (matches FastAPI backend)
- Built-in support for function calling integration with OpenAI Agents SDK
- Pydantic schema validation out of the box
- Active development and community support

**Alternatives Considered**:
- Custom MCP implementation: Rejected (reinventing the wheel, maintenance burden)
- Third-party MCP libraries: Rejected (less mature, uncertain support)

**Implementation Notes**:
- Install via pip: `pip install mcp-sdk`
- SDK provides decorators for tool registration
- Built-in support for async operations (matches FastAPI async patterns)

---

### Q2: How should MCP tools integrate with existing FastAPI backend?

**Decision**: MCP tools as part of FastAPI application (not separate process)

**Rationale**:
- Simpler deployment (single application)
- Shared database connection pool
- Reuse existing authentication and database utilities
- Lower latency (no inter-process communication)
- Easier debugging and testing

**Alternatives Considered**:
- Separate MCP server process: Rejected (added complexity, IPC overhead, deployment complexity)
- Microservices architecture: Rejected (overkill for 5 tools, premature optimization)

**Implementation Notes**:
- Tools in `backend/src/tools/` directory
- Tools import from existing `src/database`, `src/models`, `src/utils`
- Tool registry exposed to agent module
- No separate MCP server process needed

---

### Q3: How should OpenAI Agents SDK be integrated?

**Decision**: Agent module in `backend/src/agent/` with function calling

**Rationale**:
- OpenAI Agents SDK supports function calling natively
- Agent can discover and call MCP tools automatically
- Structured tool responses work seamlessly with function calling
- Agent handles tool selection based on user intent

**Alternatives Considered**:
- Manual tool routing: Rejected (agent is better at intent recognition)
- LangChain integration: Rejected (adds unnecessary abstraction layer)

**Implementation Notes**:
- Install via pip: `pip install openai`
- Agent configuration in `agent/config.py`
- System prompts in `agent/prompts.py`
- Agent invocation in `agent/agent.py`
- Tools registered via MCP SDK tool catalog

---

### Q4: How should conversation state be persisted?

**Decision**: Two new SQLModel models (Conversation, Message)

**Rationale**:
- Consistent with existing database architecture (SQLModel + Neon PostgreSQL)
- Supports stateless architecture (all state in DB)
- Enables conversation history loading
- Allows multiple server instances

**Alternatives Considered**:
- Redis for conversation cache: Rejected (adds dependency, not source of truth)
- In-memory state: Rejected (violates stateless principle)
- File-based storage: Rejected (doesn't scale, no transactions)

**Implementation Notes**:
- Conversation model: id, user_id, created_at, updated_at
- Message model: id, conversation_id, role (user/assistant), content, timestamp
- Foreign key relationships: Conversation → User, Message → Conversation
- Indexes on user_id and conversation_id for fast queries

---

### Q5: How should user context be passed to MCP tools?

**Decision**: user_context dict parameter automatically injected by chat endpoint

**Rationale**:
- Explicit user context passing (no hidden state)
- Tools can validate user_id before operations
- Consistent with authorization pattern from Phase-II
- Easy to test (mock user_context in tests)

**Alternatives Considered**:
- Thread-local storage: Rejected (not async-safe, hidden state)
- Global context manager: Rejected (not stateless, testing complexity)
- Middleware injection: Rejected (tools should be explicit about dependencies)

**Implementation Notes**:
- Chat endpoint extracts user from JWT token
- Creates user_context dict: {"user_id": user.id, "email": user.email}
- Passes user_context to agent invocation
- Agent passes user_context to all tool calls
- Tools validate user_context before operations

---

### Q6: What error handling strategy should tools use?

**Decision**: Structured responses with success/error fields (no exceptions to agent)

**Rationale**:
- Agent can handle errors gracefully without crashing
- Consistent response format across all tools
- Enables agent to provide user-friendly error messages
- Prevents exception propagation to agent

**Alternatives Considered**:
- Raise exceptions: Rejected (agent crashes, poor UX)
- HTTP status codes: Rejected (tools are not HTTP endpoints)
- Error codes: Rejected (less descriptive than error messages)

**Implementation Notes**:
- Success response: {"success": True, "data": {...}}
- Error response: {"success": False, "error": "User-friendly message"}
- Tool decorator catches all exceptions and returns structured error
- Logging for debugging (but not exposed to agent/user)

---

### Q7: How should the chat endpoint be structured?

**Decision**: POST /api/chat endpoint with JWT authentication

**Rationale**:
- Consistent with existing API patterns (JWT auth, async handlers)
- Single endpoint for all chat interactions
- Stateless (loads history from DB per request)
- Returns agent response directly to frontend

**Alternatives Considered**:
- WebSocket connection: Rejected (adds complexity, not needed for MVP)
- Server-Sent Events: Rejected (streaming not required for MVP)
- Separate endpoints per intent: Rejected (agent handles intent routing)

**Implementation Notes**:
- Endpoint: POST /api/chat
- Request body: {"message": "user message"}
- Authentication: JWT token in Authorization header
- Response: {"response": "agent response"}
- Conversation persistence: before and after agent invocation

---

## Technology Stack Summary

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| MCP SDK | Official MCP SDK | Latest | Tool implementation and registration |
| AI Agent | OpenAI Agents SDK | Latest | Natural language understanding and tool calling |
| Backend | FastAPI | 0.109+ | API server and tool hosting |
| Database | Neon PostgreSQL | Latest | State persistence (tasks, conversations, messages) |
| ORM | SQLModel | 0.0.14+ | Database models and queries |
| Auth | Better Auth + JWT | Existing | User authentication (reuse from Phase-II) |
| Testing | pytest + pytest-asyncio | Latest | Unit and integration tests |

---

## Best Practices

### MCP Tool Development

1. **One tool per operation**: Separate tools for add, list, complete, delete, update
2. **Pydantic schemas**: Strict input validation at schema level
3. **Structured responses**: Always return {"success": bool, "data/error": ...}
4. **Authorization first**: Validate user_context before any operation
5. **Database transactions**: Use async session with proper commit/rollback
6. **Error logging**: Log errors for debugging but don't expose to agent
7. **Idempotency**: Make tools idempotent where possible (e.g., complete already completed task)

### Agent Integration

1. **Clear system prompts**: Define agent behavior and capabilities explicitly
2. **Tool descriptions**: Provide clear descriptions for agent tool selection
3. **Error handling**: Agent should handle tool errors gracefully
4. **Context management**: Load conversation history from DB per request
5. **Token limits**: Truncate history to fit within context window
6. **Stateless design**: Agent has no memory between requests

### Conversation Persistence

1. **Immediate persistence**: Save messages before and after agent invocation
2. **Database transactions**: Ensure consistency with proper commit/rollback
3. **Indexed queries**: Use indexes on user_id and conversation_id
4. **History limits**: Load only recent messages (last 50) for performance
5. **Cleanup strategy**: Archive or delete old conversations (future enhancement)

---

## Security Considerations

1. **JWT validation**: Reuse existing get_current_user dependency
2. **User isolation**: All tools filter/verify by user_id from user_context
3. **Input validation**: Pydantic schemas validate all tool inputs
4. **Authorization logging**: Log all authorization failures for security monitoring
5. **No secrets in code**: OpenAI API key in .env file
6. **SQL injection prevention**: SQLModel ORM prevents SQL injection
7. **XSS prevention**: Frontend sanitizes user input (existing)

---

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Tool execution | <100ms | Time from tool call to response |
| Authorization check | <10ms | Time to validate user_context |
| Message persistence | <10ms | Time to save message to DB |
| History loading | <50ms | Time to load 50 messages from DB |
| Agent processing | 1-5s | Time for OpenAI API response (external) |
| Total request | <5s | End-to-end chat request (dominated by OpenAI) |
| Concurrent users | 100+ | Number of simultaneous users supported |

---

## Risks and Mitigations

### Risk 1: OpenAI API latency or failures

**Impact**: High (blocks all chat interactions)

**Mitigation**:
- Implement timeout on OpenAI API calls (10 seconds)
- Return user-friendly error message on timeout
- Log failures for monitoring
- Consider retry logic with exponential backoff (future)

### Risk 2: Agent selects wrong tool

**Impact**: Medium (poor user experience)

**Mitigation**:
- Clear tool descriptions for agent
- Comprehensive system prompts
- Tool returns error if wrong parameters
- Agent can retry with different tool
- Monitor tool selection accuracy

### Risk 3: Database connection failures

**Impact**: High (blocks all operations)

**Mitigation**:
- Connection pooling with retry logic (existing)
- Graceful error handling in tools
- Health check endpoint monitors DB connection
- Neon PostgreSQL has built-in redundancy

### Risk 4: Token limit exceeded

**Impact**: Medium (conversation context lost)

**Mitigation**:
- Truncate conversation history to fit token limit
- Keep system prompt + recent messages
- Implement smart truncation (keep important context)
- Monitor token usage per request

---

## Open Questions

None - all research questions resolved.

---

## References

- Constitution v2.0.0: Stateless architecture, tool-driven execution, agent-database separation
- ADR-0001: Stateless Server Architecture
- ADR-0002: MCP Tool Integration
- Feature Spec: specs/005-mcp-task-tools/spec.md
- Existing codebase: backend/src/api/tasks.py (Phase-II CRUD endpoints)
