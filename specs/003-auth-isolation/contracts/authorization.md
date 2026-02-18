# API Authorization Contracts

**Feature**: 003-auth-isolation
**Date**: 2026-02-16
**Status**: Complete

## Overview

This document defines the authorization requirements for all API endpoints. The base API contracts are defined in `specs/002-backend-api-db/contracts/`. This document adds authorization-specific requirements.

## Authorization Headers

All protected endpoints require the following HTTP header:

```
Authorization: Bearer <jwt_token>
```

**Token Format**: JWT token obtained from POST /auth/login or POST /auth/register

**Token Contents**:
- `sub` (subject): User ID (integer)
- `exp` (expiration): Unix timestamp
- `iat` (issued at): Unix timestamp

**Token Validation**:
- Signature must be valid (HMAC-SHA256 with JWT_SECRET)
- Token must not be expired
- User ID must exist in database

## Authorization Error Responses

### 401 Unauthorized

**When**: Authentication is missing, invalid, or expired

**Response Format**:
```json
{
  "error": {
    "type": "http_error",
    "status_code": 401,
    "message": "Authentication required"
  }
}
```

**Scenarios**:
- No Authorization header provided
- Token signature is invalid
- Token is expired
- Token format is malformed

### 403 Forbidden

**When**: User is authenticated but not authorized to access the resource

**Response Format**:
```json
{
  "error": {
    "type": "http_error",
    "status_code": 403,
    "message": "Not authorized to access this task"
  }
}
```

**Scenarios**:
- User attempts to access another user's task
- User attempts to modify another user's task
- User attempts to delete another user's task

## Endpoint Authorization Requirements

### Authentication Endpoints (No Authorization Required)

#### POST /auth/register
- **Authorization**: None (public endpoint)
- **Purpose**: Create new user account
- **Returns**: JWT token for newly created user

#### POST /auth/login
- **Authorization**: None (public endpoint)
- **Purpose**: Authenticate existing user
- **Returns**: JWT token for authenticated user

#### POST /auth/logout
- **Authorization**: None (informational endpoint)
- **Purpose**: Client-side token removal
- **Returns**: Success message

---

### Task Endpoints (Authorization Required)

#### GET /tasks

**Authorization**: Required (valid JWT token)

**Access Control**:
- Returns only tasks where `task.user_id == authenticated_user.id`
- Other users' tasks are never visible

**Authorization Logic**:
```python
# Extract user from token
current_user = get_current_user(token)

# Filter query by user_id
tasks = session.execute(
    select(Task).where(Task.user_id == current_user.id)
)
```

**Success Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": 123,
      "title": "My task",
      "description": "Task description",
      "is_completed": false,
      "created_at": "2026-02-16T10:00:00Z",
      "updated_at": "2026-02-16T10:00:00Z"
    }
  ],
  "total": 1
}
```

**Error Responses**:
- 401 Unauthorized: Invalid/missing token

---

#### POST /tasks

**Authorization**: Required (valid JWT token)

**Access Control**:
- New task is automatically assigned to authenticated user
- `user_id` from request body is ignored (security measure)
- Only authenticated user can create tasks for themselves

**Authorization Logic**:
```python
# Extract user from token
current_user = get_current_user(token)

# Force user_id to authenticated user (ignore request body)
new_task = Task(
    user_id=current_user.id,  # Always use token user_id
    title=task_data.title,
    description=task_data.description
)
```

**Request Body**:
```json
{
  "title": "New task",
  "description": "Optional description"
}
```

**Success Response** (201 Created):
```json
{
  "id": 2,
  "user_id": 123,
  "title": "New task",
  "description": "Optional description",
  "is_completed": false,
  "created_at": "2026-02-16T10:05:00Z",
  "updated_at": "2026-02-16T10:05:00Z"
}
```

**Error Responses**:
- 401 Unauthorized: Invalid/missing token
- 422 Unprocessable Entity: Validation error (title missing, too long, etc.)

---

#### GET /tasks/{task_id}

**Authorization**: Required (valid JWT token)

**Access Control**:
- User can only access tasks where `task.user_id == authenticated_user.id`
- Attempting to access another user's task returns 403 Forbidden
- Attempting to access non-existent task returns 404 Not Found

**Authorization Logic**:
```python
# Extract user from token
current_user = get_current_user(token)

# Fetch task
task = session.get(Task, task_id)
if not task:
    raise HTTPException(404, "Task not found")

# Verify ownership
if task.user_id != current_user.id:
    raise HTTPException(403, "Not authorized to access this task")
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 123,
  "title": "My task",
  "description": "Task description",
  "is_completed": false,
  "created_at": "2026-02-16T10:00:00Z",
  "updated_at": "2026-02-16T10:00:00Z"
}
```

**Error Responses**:
- 401 Unauthorized: Invalid/missing token
- 403 Forbidden: Task belongs to another user
- 404 Not Found: Task does not exist

---

#### PUT /tasks/{task_id}

**Authorization**: Required (valid JWT token)

**Access Control**:
- User can only update tasks where `task.user_id == authenticated_user.id`
- Attempting to update another user's task returns 403 Forbidden
- `user_id` cannot be changed (immutable after creation)

**Authorization Logic**:
```python
# Extract user from token
current_user = get_current_user(token)

# Fetch task
task = session.get(Task, task_id)
if not task:
    raise HTTPException(404, "Task not found")

# Verify ownership
if task.user_id != current_user.id:
    raise HTTPException(403, "Not authorized to update this task")

# Update allowed fields only
if task_data.title is not None:
    task.title = task_data.title
if task_data.description is not None:
    task.description = task_data.description
if task_data.is_completed is not None:
    task.is_completed = task_data.is_completed
```

**Request Body** (all fields optional):
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "is_completed": true
}
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 123,
  "title": "Updated title",
  "description": "Updated description",
  "is_completed": true,
  "created_at": "2026-02-16T10:00:00Z",
  "updated_at": "2026-02-16T10:10:00Z"
}
```

**Error Responses**:
- 401 Unauthorized: Invalid/missing token
- 403 Forbidden: Task belongs to another user
- 404 Not Found: Task does not exist
- 422 Unprocessable Entity: Validation error

---

#### DELETE /tasks/{task_id}

**Authorization**: Required (valid JWT token)

**Access Control**:
- User can only delete tasks where `task.user_id == authenticated_user.id`
- Attempting to delete another user's task returns 403 Forbidden

**Authorization Logic**:
```python
# Extract user from token
current_user = get_current_user(token)

# Fetch task
task = session.get(Task, task_id)
if not task:
    raise HTTPException(404, "Task not found")

# Verify ownership
if task.user_id != current_user.id:
    raise HTTPException(403, "Not authorized to delete this task")

# Delete task
session.delete(task)
session.commit()
```

**Success Response** (204 No Content):
- Empty response body

**Error Responses**:
- 401 Unauthorized: Invalid/missing token
- 403 Forbidden: Task belongs to another user
- 404 Not Found: Task does not exist

---

## Security Testing Scenarios

### Scenario 1: Cross-User Access (Horizontal Privilege Escalation)

**Setup**:
1. Create User A and User B
2. User A creates Task 1
3. User B attempts to access Task 1

**Expected Results**:
- GET /tasks/{task_1_id} with User B's token → 403 Forbidden
- PUT /tasks/{task_1_id} with User B's token → 403 Forbidden
- DELETE /tasks/{task_1_id} with User B's token → 403 Forbidden
- GET /tasks with User B's token → Empty list (Task 1 not visible)

**Test Commands**:
```bash
# User A creates task
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"title": "Alice task"}'

# User B tries to access (should fail)
curl -X GET http://localhost:8000/tasks/1 \
  -H "Authorization: Bearer $TOKEN_B"
# Expected: 403 Forbidden
```

---

### Scenario 2: Token Tampering

**Setup**:
1. User A obtains valid token
2. Attacker modifies token payload (changes user_id)
3. Attacker attempts to use modified token

**Expected Results**:
- All requests with tampered token → 401 Unauthorized
- Signature verification fails

**Test Commands**:
```bash
# Get valid token
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "password123"}' \
  | jq -r '.access_token')

# Manually modify token payload (will break signature)
# Attempt to use modified token
curl -X GET http://localhost:8000/tasks \
  -H "Authorization: Bearer $MODIFIED_TOKEN"
# Expected: 401 Unauthorized
```

---

### Scenario 3: Expired Token

**Setup**:
1. User obtains valid token
2. Wait for token to expire (24 hours)
3. Attempt to use expired token

**Expected Results**:
- All requests with expired token → 401 Unauthorized
- Error message: "Token expired"

**Test Commands**:
```bash
# Use expired token
curl -X GET http://localhost:8000/tasks \
  -H "Authorization: Bearer $EXPIRED_TOKEN"
# Expected: 401 Unauthorized with "Token expired" message
```

---

### Scenario 4: Missing Authorization

**Setup**:
1. Attempt to access protected endpoint without token

**Expected Results**:
- All protected endpoints → 401 Unauthorized
- Error message: "Authentication required"

**Test Commands**:
```bash
# No Authorization header
curl -X GET http://localhost:8000/tasks
# Expected: 401 Unauthorized
```

---

### Scenario 5: Parameter Manipulation

**Setup**:
1. User A obtains valid token
2. User A attempts to create task with different user_id in request body

**Expected Results**:
- Task is created with User A's ID (from token)
- Request body user_id is ignored

**Test Commands**:
```bash
# Attempt to create task for user_id=999
curl -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"title": "Task", "user_id": 999}'

# Verify task belongs to User A (not 999)
curl -X GET http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN_A"
# Expected: Task has user_id matching User A's ID
```

---

## Authorization Flow Summary

```
Request → Extract Token → Validate Signature → Check Expiration → Extract User ID →
Query User → Verify Resource Ownership → Execute Operation → Return Response
```

**Failure Points**:
- No token → 401 Unauthorized
- Invalid signature → 401 Unauthorized
- Expired token → 401 Unauthorized
- User not found → 401 Unauthorized
- Resource not found → 404 Not Found
- Ownership mismatch → 403 Forbidden

**Success Path**:
- Valid token + Authorized access → 200/201/204 with response data
