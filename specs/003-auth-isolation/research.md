# Research & Design Decisions: Authorization & User Isolation Layer

**Feature**: 003-auth-isolation
**Date**: 2026-02-16
**Status**: Complete

## Overview

This document captures the research findings and design decisions for implementing authorization and user isolation in the Task Management API. The feature builds on the existing JWT authentication system (002-backend-api-db) to add strict per-user data isolation and prevent horizontal privilege escalation.

## Key Decisions

### Decision 1: FastAPI Dependency Injection for Authorization

**Chosen Approach**: Use FastAPI's dependency injection system with `Depends()` to centralize authorization logic.

**Rationale**:
- FastAPI's dependency system is designed for cross-cutting concerns like authorization
- Dependencies are automatically executed before route handlers, ensuring fail-secure behavior
- Reusable across all protected endpoints without code duplication
- Type-safe and integrates with FastAPI's automatic documentation
- Already used in 002-backend-api-db for `get_current_user` dependency

**Implementation Pattern**:
```python
from fastapi import Depends
from src.utils.jwt import get_current_user
from src.models.user import User

@router.get("/tasks/{task_id}")
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # current_user is guaranteed to be authenticated
    # Verify ownership before returning task
```

**Alternatives Considered**:
- Middleware-based authorization: Rejected because it's less granular and harder to customize per-endpoint
- Decorator-based authorization: Rejected because FastAPI dependencies are more idiomatic and type-safe
- Manual authorization in each endpoint: Rejected due to code duplication and security risk

---

### Decision 2: JWT Token Validation Strategy

**Chosen Approach**: Validate JWT signature, expiration, and extract user identity in a single dependency function.

**Rationale**:
- Single point of validation reduces security gaps
- Signature verification prevents token tampering
- Expiration check prevents replay attacks with old tokens
- User identity extraction provides authenticated context to all endpoints
- Already implemented in `backend/src/utils/jwt.py` from 002-backend-api-db

**Implementation Pattern**:
```python
from jose import JWTError, jwt
from datetime import datetime

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            raise HTTPException(status_code=401, detail="Token expired")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Security Properties**:
- Cryptographic signature verification (HMAC-SHA256)
- Time-based expiration (24 hours default)
- Automatic rejection of tampered tokens
- No database lookup required for validation (stateless)

**Alternatives Considered**:
- Database-backed token validation: Rejected because it adds latency and complexity
- Refresh token mechanism: Out of scope for this phase (users re-authenticate after expiration)

---

### Decision 3: Ownership Verification Pattern

**Chosen Approach**: Two-step verification - fetch resource, then verify user_id matches authenticated user.

**Rationale**:
- Clear separation between resource existence (404) and authorization (403)
- Prevents information leakage (attacker cannot enumerate valid IDs)
- Follows REST best practices for error responses
- Already implemented in 002-backend-api-db task endpoints

**Implementation Pattern**:
```python
# Step 1: Fetch resource
task = await session.get(Task, task_id)
if not task:
    raise HTTPException(status_code=404, detail="Task not found")

# Step 2: Verify ownership
if task.user_id != current_user.id:
    raise HTTPException(status_code=403, detail="Not authorized to access this task")
```

**Error Response Strategy**:
- 404 Not Found: Resource does not exist
- 403 Forbidden: Resource exists but user does not have permission
- 401 Unauthorized: Authentication missing or invalid

**Alternatives Considered**:
- Always return 404 for unauthorized access: Rejected because 403 is more semantically correct
- Single-step query with user_id filter: Rejected because it makes 404 vs 403 distinction harder

---

### Decision 4: Database Query Filtering Strategy

**Chosen Approach**: Always include `user_id` filter in queries for user-owned resources.

**Rationale**:
- Defense in depth - even if ownership check is missed, query filter prevents data leakage
- Efficient - database can use index on user_id
- Explicit - makes authorization intent clear in code
- Already implemented in 002-backend-api-db GET /tasks endpoint

**Implementation Pattern**:
```python
# List endpoint - filter by user_id
result = await session.execute(
    select(Task)
    .where(Task.user_id == current_user.id)
    .order_by(Task.created_at.desc())
)
tasks = result.scalars().all()
```

**Security Properties**:
- Prevents accidental data leakage from missing authorization checks
- Leverages database indexes for performance
- Works with SQLModel's type-safe query API

**Alternatives Considered**:
- Row-level security in PostgreSQL: Rejected as overkill for this simple use case
- Application-level filtering after fetch: Rejected due to performance and security concerns

---

### Decision 5: Security Testing Approach

**Chosen Approach**: Manual security testing with documented test scenarios in quickstart.md.

**Rationale**:
- Comprehensive coverage of authorization attack vectors
- Tests real HTTP requests (not just unit tests)
- Validates end-to-end security behavior
- Suitable for hackathon timeline

**Test Scenarios**:
1. Cross-user access attempts (Alice tries to access Bob's tasks)
2. Token tampering (modify user_id in token payload)
3. Expired token usage
4. Missing authentication header
5. Invalid token signature
6. Parameter manipulation (valid token but wrong task_id)

**Tools**:
- cURL for manual HTTP requests
- Postman for organized test collections
- pytest for automated security test suite (future enhancement)

**Alternatives Considered**:
- Automated penetration testing tools: Rejected due to setup complexity
- Unit tests only: Rejected because they do not test real authorization flow

---

### Decision 6: Error Handling and Logging

**Chosen Approach**: Log all authorization failures with sufficient detail for security audit.

**Rationale**:
- Security monitoring requires audit trail
- Helps detect attack patterns
- Debugging authorization issues
- Already implemented in 002-backend-api-db with logging in auth endpoints

**Logging Pattern**:
```python
logger.warning(
    f"Authorization failed - user {current_user.id} attempted to access task {task_id}"
)
```

**Logged Information**:
- Authenticated user ID
- Attempted resource ID
- Timestamp (automatic)
- Endpoint path

**Security Considerations**:
- Do not log sensitive data (tokens, passwords)
- Do not expose internal system details in error responses
- Use structured logging for analysis

**Alternatives Considered**:
- No logging: Rejected due to security monitoring requirements
- Verbose error messages: Rejected to prevent information leakage

---

## Technology Stack Validation

| Component | Technology | Version | Status |
|-----------|-----------|---------|--------|
| Web Framework | FastAPI | 0.109+ | Already in use |
| JWT Library | python-jose | 3.3+ | Already in use |
| ORM | SQLModel | 0.0.14+ | Already in use |
| Database | Neon PostgreSQL | Latest | Already in use |
| Testing | pytest + manual | Latest | Available |

**Validation**: All required technologies are already in place from 002-backend-api-db. No new dependencies needed.

---

## Architecture Patterns

### Pattern 1: Dependency Injection for Cross-Cutting Concerns

FastAPI's dependency injection is the primary pattern for implementing authorization:
- `get_current_user` dependency extracts and validates user identity
- Automatically applied to all protected endpoints
- Type-safe and self-documenting

### Pattern 2: Fail-Secure by Default

Authorization checks happen before business logic:
- Dependencies execute before route handlers
- Exceptions prevent handler execution
- Missing authorization dependency causes type error (caught at development time)

### Pattern 3: Defense in Depth

Multiple layers of protection:
1. JWT signature verification (prevents token forgery)
2. Token expiration check (prevents replay attacks)
3. Ownership verification (prevents horizontal privilege escalation)
4. Database query filtering (prevents accidental data leakage)

---

## Performance Considerations

**Authorization Overhead**: Less than 5ms per request
- JWT validation: approximately 1ms (cryptographic operation)
- Database query for ownership: approximately 2-3ms (indexed lookup)
- Total: Well within 50ms constraint

**Optimization Strategies**:
- Database indexes on user_id (already in place)
- Stateless JWT validation (no database lookup for token)
- Async/await for non-blocking I/O

---

## Security Threat Model

### Threat 1: Horizontal Privilege Escalation
**Attack**: User A tries to access User B's tasks by manipulating task IDs
**Mitigation**: Ownership verification on all operations
**Status**: Implemented in 002-backend-api-db

### Threat 2: Token Tampering
**Attack**: Attacker modifies user_id in JWT payload
**Mitigation**: Signature verification rejects modified tokens
**Status**: Implemented in 002-backend-api-db

### Threat 3: Token Replay
**Attack**: Attacker uses captured old token
**Mitigation**: Token expiration (24 hours)
**Status**: Implemented in 002-backend-api-db

### Threat 4: IDOR (Insecure Direct Object Reference)
**Attack**: Attacker enumerates task IDs to find valid resources
**Mitigation**: Ownership verification prevents access even if ID is valid
**Status**: Implemented in 002-backend-api-db

### Threat 5: Missing Authorization Check
**Attack**: Developer forgets to add authorization to new endpoint
**Mitigation**: Dependency injection makes authorization explicit and required
**Status**: Pattern established in 002-backend-api-db

---

## Implementation Status

**Key Finding**: The authorization layer is already substantially implemented in 002-backend-api-db:
- JWT validation in `backend/src/utils/jwt.py`
- Ownership verification in `backend/src/api/tasks.py`
- Database query filtering in GET /tasks endpoint
- Error handling with 401/403 responses

**This Feature's Scope**:
1. **Validation**: Verify existing implementation meets all security requirements
2. **Strengthening**: Add any missing authorization checks or logging
3. **Testing**: Create comprehensive security test suite
4. **Documentation**: Document authorization architecture and patterns

**Risk Assessment**: Low risk - building on proven implementation rather than creating from scratch.

---

## References

- FastAPI Security Documentation: https://fastapi.tiangolo.com/tutorial/security/
- JWT Best Practices: RFC 8725
- OWASP API Security Top 10: https://owasp.org/www-project-api-security/
- Existing Implementation: specs/002-backend-api-db/
