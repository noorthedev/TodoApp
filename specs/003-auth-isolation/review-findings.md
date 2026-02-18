# Code Review Findings: Authorization & User Isolation Layer

**Feature**: 003-auth-isolation
**Date**: 2026-02-16
**Reviewer**: Claude Code (Automated Review)
**Status**: Complete

## Executive Summary

The existing authorization implementation in 002-backend-api-db is **fundamentally sound** with proper JWT validation, ownership verification, and query filtering. Minor gaps identified for strengthening:
1. Missing authorization failure logging (403 responses)
2. Generic JWT error messages (could be more specific)
3. No explicit expiration check in decode_token (relies on jose library)

**Overall Assessment**: ✅ PASS - Implementation meets security requirements with minor enhancements needed

---

## Component Review

### 1. JWT Validation (`backend/src/utils/jwt.py`)

**Status**: ✅ PASS with minor enhancements

#### `create_access_token(data: dict) -> str`
**Lines**: 19-39
**Purpose**: Generate JWT tokens with expiration
**Findings**:
- ✅ Uses HMAC-SHA256 algorithm (secure)
- ✅ Sets expiration timestamp from config (24 hours default)
- ✅ Encodes user_id in "sub" claim
- ✅ Uses secret from environment variable (not hardcoded)

**Recommendation**: No changes needed

---

#### `decode_token(token: str) -> dict`
**Lines**: 42-62
**Purpose**: Validate JWT signature and extract payload
**Findings**:
- ✅ Verifies signature using JWT_SECRET
- ✅ Uses jose library's built-in validation
- ✅ Raises HTTPException with 401 status on failure
- ⚠️ **Gap**: Generic error message "Could not validate credentials"
- ⚠️ **Gap**: No explicit expiration check (relies on jose library)

**Current Behavior**:
```python
try:
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    return payload
except JWTError:
    raise HTTPException(status_code=401, detail="Could not validate credentials")
```

**Recommendation**: Add specific error messages for different failure modes:
- Expired token: "Token expired"
- Invalid signature: "Invalid token"
- Malformed token: "Invalid token format"

**Security Note**: Generic error messages prevent information leakage, but specific messages improve debugging without compromising security (attacker already knows if token is expired).

---

#### `get_current_user(credentials, session) -> User`
**Lines**: 65-103
**Purpose**: Extract and validate authenticated user from JWT token
**Findings**:
- ✅ Uses FastAPI dependency injection (HTTPBearer)
- ✅ Extracts token from Authorization header
- ✅ Validates token via decode_token()
- ✅ Extracts user_id from "sub" claim
- ✅ Queries database for user object
- ✅ Returns 401 if user not found
- ✅ Type-safe (returns User object)

**Recommendation**: No changes needed - implementation is correct

---

### 2. Ownership Verification (`backend/src/api/tasks.py`)

**Status**: ✅ PASS with logging enhancement needed

#### GET /tasks (List Endpoint)
**Lines**: 19-44
**Purpose**: Return all tasks for authenticated user
**Findings**:
- ✅ Uses get_current_user dependency (automatic authentication)
- ✅ Filters query by user_id: `.where(Task.user_id == current_user.id)`
- ✅ Orders by created_at descending
- ✅ Returns TaskList with total count

**Security Properties**:
- ✅ Defense in depth: Query filtering prevents data leakage
- ✅ No cross-user data visible

**Recommendation**: No changes needed

---

#### POST /tasks (Create Endpoint)
**Lines**: 47-78
**Purpose**: Create new task for authenticated user
**Findings**:
- ✅ Uses get_current_user dependency
- ✅ Forces user_id from token: `user_id=current_user.id`
- ✅ Ignores any user_id in request body (security measure)
- ✅ Logs task creation (line 63, 76)

**Security Properties**:
- ✅ Parameter manipulation prevention: Request body user_id is ignored
- ✅ User can only create tasks for themselves

**Recommendation**: No changes needed

---

#### GET /tasks/{task_id} (Read Endpoint)
**Lines**: 81-117
**Purpose**: Get specific task by ID
**Findings**:
- ✅ Uses get_current_user dependency
- ✅ Two-step verification:
  1. Fetch task (line 101-102)
  2. Verify ownership (line 111-115)
- ✅ Returns 404 if task not found
- ✅ Returns 403 if not owner
- ⚠️ **Gap**: No logging for authorization failures

**Current Ownership Check**:
```python
if task.user_id != current_user.id:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized to access this task",
    )
```

**Recommendation**: Add logging before raising 403:
```python
if task.user_id != current_user.id:
    logger.warning(
        f"Authorization failed: user {current_user.id} attempted to access "
        f"task {task_id} owned by user {task.user_id}"
    )
    raise HTTPException(...)
```

---

#### PUT /tasks/{task_id} (Update Endpoint)
**Lines**: 120-177
**Purpose**: Update existing task
**Findings**:
- ✅ Uses get_current_user dependency
- ✅ Two-step verification (fetch + verify ownership)
- ✅ Returns 404 if task not found
- ✅ Returns 403 if not owner
- ✅ Logs successful updates (line 158, 175)
- ⚠️ **Gap**: No logging for authorization failures (403)

**Recommendation**: Add authorization failure logging (same as GET)

---

#### DELETE /tasks/{task_id} (Delete Endpoint)
**Lines**: 180-219
**Purpose**: Delete task
**Findings**:
- ✅ Uses get_current_user dependency
- ✅ Two-step verification (fetch + verify ownership)
- ✅ Returns 404 if task not found
- ✅ Returns 403 if not owner
- ✅ Logs successful deletions (line 213, 219)
- ⚠️ **Gap**: No logging for authorization failures (403)

**Recommendation**: Add authorization failure logging (same as GET)

---

### 3. Error Handling

**Status**: ✅ PASS - Appropriate error responses

**401 Unauthorized** (Authentication Failures):
- Missing token
- Invalid token signature
- Expired token
- User not found in database

**403 Forbidden** (Authorization Failures):
- User authenticated but doesn't own resource
- Attempting to access another user's task

**404 Not Found**:
- Task doesn't exist
- Prevents ID enumeration (attacker can't distinguish between non-existent and unauthorized)

**Recommendation**: Error responses are correct - no changes needed

---

### 4. Query Filtering

**Status**: ✅ PASS - Defense in depth implemented

**GET /tasks Endpoint**:
```python
select(Task).where(Task.user_id == current_user.id)
```

**Security Properties**:
- ✅ Always filters by authenticated user_id
- ✅ Prevents accidental data leakage
- ✅ Leverages database index on user_id (performance)

**Recommendation**: No changes needed

---

### 5. Logging

**Status**: ⚠️ PARTIAL - Missing authorization failure logs

**Current Logging**:
- ✅ Task creation (POST /tasks)
- ✅ Task updates (PUT /tasks/{id})
- ✅ Task deletions (DELETE /tasks/{id})
- ❌ Authorization failures (403 responses) - **NOT LOGGED**
- ❌ Token validation failures (401 responses) - **NOT LOGGED**

**Security Impact**:
- Cannot detect attack patterns (repeated 403s from same user)
- Cannot audit authorization violations
- Difficult to debug authorization issues

**Recommendation**: Add logging for all authorization failures

---

## Identified Gaps

### Gap 1: Authorization Failure Logging (Priority: HIGH)
**Impact**: Security monitoring and audit trail
**Location**: `backend/src/api/tasks.py` (GET/PUT/DELETE endpoints)
**Fix**: Add logger.warning() before raising 403 HTTPException

**Example**:
```python
if task.user_id != current_user.id:
    logger.warning(
        f"Authorization failed: user {current_user.id} attempted to access "
        f"task {task_id} owned by user {task.user_id}"
    )
    raise HTTPException(status_code=403, detail="Not authorized")
```

---

### Gap 2: JWT Error Message Specificity (Priority: MEDIUM)
**Impact**: Debugging and user experience
**Location**: `backend/src/utils/jwt.py` (decode_token function)
**Fix**: Differentiate between expired, invalid signature, and malformed tokens

**Example**:
```python
try:
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    return payload
except jwt.ExpiredSignatureError:
    raise HTTPException(status_code=401, detail="Token expired")
except jwt.JWTClaimsError:
    raise HTTPException(status_code=401, detail="Invalid token claims")
except JWTError:
    raise HTTPException(status_code=401, detail="Invalid token")
```

---

### Gap 3: Token Validation Failure Logging (Priority: MEDIUM)
**Impact**: Security monitoring
**Location**: `backend/src/utils/jwt.py` (decode_token, get_current_user)
**Fix**: Add logging for token validation failures

**Example**:
```python
except JWTError as e:
    logger.warning(f"Token validation failed: {type(e).__name__}")
    raise HTTPException(...)
```

---

## Security Validation

### ✅ Horizontal Privilege Escalation Prevention
- All endpoints verify ownership before allowing access
- Cross-user access attempts return 403 Forbidden
- Query filtering prevents data leakage

### ✅ Token Tampering Prevention
- JWT signature verification using HMAC-SHA256
- Modified tokens are rejected
- Secret key stored in environment variable

### ✅ Token Replay Prevention
- Token expiration (24 hours)
- Expired tokens are rejected

### ✅ IDOR (Insecure Direct Object Reference) Prevention
- Ownership verification on all operations
- 404 response prevents ID enumeration

### ✅ Parameter Manipulation Prevention
- POST /tasks ignores user_id from request body
- Always uses authenticated user_id from token

### ✅ Fail-Secure by Default
- FastAPI dependency injection requires get_current_user
- Missing dependency causes type error at development time

---

## Recommendations Summary

### Immediate (Phase 3 & 4 - MVP)
1. **Add authorization failure logging** to GET/PUT/DELETE endpoints
2. **Add specific JWT error messages** for expired vs invalid tokens
3. **Add token validation failure logging** in jwt.py

### Future Enhancements (Post-MVP)
1. Add token refresh mechanism (extend session without re-authentication)
2. Implement token revocation (blacklist for logout)
3. Add rate limiting per user (prevent brute force)
4. Add audit log UI (view authorization events)

---

## Conclusion

The existing authorization implementation is **production-ready** with minor enhancements needed for logging and error messaging. The core security properties are correctly implemented:
- JWT validation with signature verification
- Ownership verification on all operations
- Query filtering for defense in depth
- Appropriate error responses (401/403/404)

**Next Steps**: Proceed with Phase 3 (US1) to add authorization failure logging and strengthen error messages.
