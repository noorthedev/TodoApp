# ADR-0001: Stateless Server Architecture for AI Chatbot

**Status**: Accepted
**Date**: 2026-02-19
**Deciders**: Architecture Team
**Related**: Constitution v2.0.0, Phase-III Architecture

## Context

Phase-III transforms the todo application from a traditional CRUD web app into an AI-powered chatbot. This introduces new challenges around conversation state management, scalability, and reliability. We need to decide how to manage conversation state across multiple requests and potentially multiple server instances.

### Problem Statement

AI chatbot applications typically require maintaining conversation context across multiple user interactions. Traditional approaches include:
- In-memory session storage
- Sticky sessions with load balancers
- Distributed caching (Redis, Memcached)
- Database-backed sessions

Each approach has different implications for scalability, reliability, and operational complexity.

### Requirements

1. **Scalability**: Support horizontal scaling without session affinity
2. **Reliability**: Survive server restarts without losing conversation state
3. **Consistency**: Ensure all server instances see the same conversation state
4. **Simplicity**: Minimize operational complexity and dependencies
5. **Auditability**: Enable debugging and conversation history review

## Decision

We will implement a **fully stateless server architecture** where:

1. **No in-memory conversation state**: Server maintains zero conversation state in memory
2. **Database as single source of truth**: All conversations and messages persisted to Neon PostgreSQL immediately
3. **Fresh context per request**: Each request loads conversation history from database
4. **Stateless agent invocation**: OpenAI Agent receives fresh context every time, no memory between calls
5. **Immediate persistence**: User messages persisted BEFORE agent processing, agent responses persisted AFTER generation

### Architecture Pattern

```
Request arrives → Load conversation from DB → Invoke agent with history → Persist response → Return to user
                                                      ↓
                                            Agent is stateless
                                            (no memory between calls)
```

## Consequences

### Positive

1. **Horizontal Scaling**: Any server instance can handle any request without session affinity
2. **Restart Safe**: Server restarts do not lose conversation state
3. **Simple Operations**: No need for Redis, sticky sessions, or distributed caching
4. **Audit Trail**: Complete conversation history in database for debugging
5. **Consistency**: All instances see same state immediately (database is source of truth)
6. **Cost Effective**: Neon PostgreSQL already required; no additional infrastructure

### Negative

1. **Database Load**: Every request requires database reads (conversation history) and writes (new messages)
2. **Latency**: Database round-trips add ~50-100ms per request
3. **Context Window Management**: Must implement truncation strategy for long conversations
4. **Token Costs**: Agent receives full history each time (no incremental context)

### Mitigations

1. **Database Optimization**:
   - Index on `conversation.user_id` and `message.conversation_id`
   - Limit conversation history queries (e.g., last 50 messages)
   - Use async database connections for performance

2. **Context Window Management**:
   - Implement smart truncation (keep system prompt + recent messages)
   - Archive old conversations to reduce active dataset

3. **Caching (Optional Future)**:
   - Can add read-through cache for conversation history if needed
   - Does not change stateless architecture (cache is optimization, not requirement)

## Alternatives Considered

### Alternative 1: In-Memory Session Storage

**Approach**: Store conversation state in server memory (Python dict, global state)

**Pros**:
- Fastest access (no database round-trip)
- Lowest latency

**Cons**:
- ❌ Requires sticky sessions (breaks horizontal scaling)
- ❌ Lost on server restart
- ❌ No audit trail
- ❌ Cannot scale horizontally
- ❌ Violates Phase-III principles

**Rejected**: Fundamentally incompatible with scalability and reliability requirements.

### Alternative 2: Redis-Backed Sessions

**Approach**: Store conversation state in Redis, load on each request

**Pros**:
- Fast access (~1-5ms)
- Supports horizontal scaling
- Survives server restarts

**Cons**:
- ❌ Additional infrastructure dependency (Redis cluster)
- ❌ Additional operational complexity (Redis monitoring, backups)
- ❌ Additional cost
- ❌ Still requires database for persistence (Redis is cache, not source of truth)
- ❌ Adds complexity without significant benefit (Neon PostgreSQL already fast enough)

**Rejected**: Adds operational complexity and cost without sufficient benefit. Neon PostgreSQL performance is adequate for our scale.

### Alternative 3: Hybrid (Redis + Database)

**Approach**: Use Redis for hot conversations, database for cold storage

**Pros**:
- Optimizes for active conversations
- Reduces database load

**Cons**:
- ❌ Most complex solution
- ❌ Cache invalidation challenges
- ❌ Two sources of truth (consistency issues)
- ❌ Premature optimization (no evidence of performance problems)

**Rejected**: Over-engineered for current requirements. Can revisit if performance becomes an issue.

## Implementation Notes

### Database Schema

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_user_id (user_id)
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_conversation_id (conversation_id)
);
```

### Request Flow

```python
@router.post("/api/chat")
async def chat_endpoint(
    message: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # 1. Get or create conversation
    conversation = await get_or_create_conversation(session, current_user.id)

    # 2. Persist user message IMMEDIATELY
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=message,
        timestamp=datetime.utcnow(),
    )
    session.add(user_message)
    await session.commit()

    # 3. Load conversation history from database
    history = await load_conversation_history(session, conversation.id, limit=50)

    # 4. Invoke agent (stateless, receives fresh context)
    user_context = {"user_id": current_user.id, "email": current_user.email}
    response = await invoke_agent(history, user_context)

    # 5. Persist agent response IMMEDIATELY
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response,
        timestamp=datetime.utcnow(),
    )
    session.add(assistant_message)
    await session.commit()

    return {"response": response}
```

## Performance Benchmarks

Expected latency breakdown:
- JWT validation: <5ms
- Database read (conversation history): 20-50ms
- Agent processing (OpenAI API): 1000-5000ms (dominates)
- Database write (response): 10-20ms
- **Total**: ~1-5 seconds (dominated by OpenAI API)

Database operations are <5% of total latency, making optimization unnecessary at current scale.

## Success Metrics

1. **Scalability**: Can deploy multiple server instances without configuration changes
2. **Reliability**: Zero conversation data loss on server restart
3. **Performance**: <100ms database overhead per request
4. **Consistency**: All instances see same conversation state within 1 second

## References

- Constitution v2.0.0: Principle I (Stateless Server Architecture)
- CLAUDE.md: Stateless Architecture Patterns
- Plan Template: Stateless Architecture Considerations section
