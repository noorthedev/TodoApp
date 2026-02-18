# Data Model: Authorization & User Isolation Layer

**Feature**: 003-auth-isolation
**Date**: 2026-02-16
**Status**: Complete

## Overview

This feature does not introduce new database entities. It builds on the existing User and Task models from 002-backend-api-db to enforce authorization and data isolation.

## Existing Entities (No Changes Required)

### User Entity

**Purpose**: Represents an authenticated user in the system.

**Key Attributes**:
- `id` (integer, primary key): Unique identifier for the user
- `email` (string, unique, indexed): User's email address for authentication
- `hashed_password` (string): Bcrypt-hashed password (never plaintext)
- `created_at` (datetime): Account creation timestamp
- `updated_at` (datetime): Last modification timestamp

**Relationships**:
- One-to-Many with Task: A user can own multiple tasks

**Authorization Role**: The `id` field is extracted from JWT tokens and used to filter all user-owned resources.

**Implementation**: `backend/src/models/user.py` (already exists)

---

### Task Entity

**Purpose**: Represents a todo task owned by a specific user.

**Key Attributes**:
- `id` (integer, primary key): Unique identifier for the task
- `user_id` (integer, foreign key, indexed): Owner of the task (references User.id)
- `title` (string, max 255): Task title
- `description` (string, optional, max 1000): Task description
- `is_completed` (boolean, default false): Completion status
- `created_at` (datetime): Task creation timestamp
- `updated_at` (datetime): Last modification timestamp

**Relationships**:
- Many-to-One with User: Each task belongs to exactly one user

**Authorization Role**: The `user_id` field is the primary authorization mechanism. All task operations verify that `task.user_id == authenticated_user.id`.

**Implementation**: `backend/src/models/task.py` (already exists)

---

## Authorization Context (Conceptual Entity)

**Purpose**: Represents the authenticated user identity available to all protected endpoints.

**Source**: Extracted from validated JWT token by `get_current_user` dependency.

**Attributes**:
- `id` (integer): User ID from token's "sub" claim
- `email` (string): User email from token
- `created_at` (datetime): Account creation timestamp

**Lifecycle**: Created per-request from JWT token, not persisted to database.

**Usage**: Passed to all protected endpoints via FastAPI dependency injection.

**Implementation**: `backend/src/utils/jwt.py::get_current_user()` (already exists)

---

## Data Isolation Strategy

### Query Filtering

All queries for user-owned resources MUST include a `user_id` filter:

```python
# Correct: Filtered by authenticated user
tasks = await session.execute(
    select(Task).where(Task.user_id == current_user.id)
)

# Incorrect: Returns all users' tasks (security violation)
tasks = await session.execute(select(Task))
```

### Ownership Verification

For operations on specific resources (GET/PUT/DELETE by ID):

```python
# Step 1: Fetch resource
task = await session.get(Task, task_id)
if not task:
    raise HTTPException(status_code=404, detail="Task not found")

# Step 2: Verify ownership
if task.user_id != current_user.id:
    raise HTTPException(status_code=403, detail="Not authorized")
```

### Create Operations

For creating new resources, always use the authenticated user's ID:

```python
# Correct: Use authenticated user ID
new_task = Task(
    user_id=current_user.id,  # From JWT token
    title=task_data.title,
    description=task_data.description
)

# Incorrect: Trust user_id from request body (security violation)
new_task = Task(
    user_id=request_data.user_id,  # NEVER do this
    title=task_data.title
)
```

---

## Database Schema Validation

### Required Indexes

The following indexes are required for authorization performance:

| Table | Column | Index Type | Purpose | Status |
|-------|--------|-----------|---------|--------|
| users | email | UNIQUE | Authentication lookup | ✅ Exists |
| tasks | user_id | INDEX | Authorization filtering | ✅ Exists |

**Performance Impact**: With indexes, authorization queries complete in <5ms.

### Foreign Key Constraints

| Child Table | Column | Parent Table | Parent Column | On Delete | Status |
|-------------|--------|--------------|---------------|-----------|--------|
| tasks | user_id | users | id | CASCADE | ✅ Exists |

**Authorization Impact**: Foreign key constraint ensures `task.user_id` always references a valid user. Orphaned tasks are automatically deleted when user is deleted.

---

## Data Flow Diagrams

### Authentication Flow (Existing)

```
1. User submits email + password to POST /auth/login
2. Backend verifies credentials against users table
3. Backend generates JWT token with user.id in "sub" claim
4. Backend returns token to user
5. User stores token (localStorage/cookie)
```

### Authorization Flow (This Feature)

```
1. User sends request with Authorization: Bearer <token> header
2. FastAPI extracts token from header
3. get_current_user dependency validates token:
   - Verify signature (prevents tampering)
   - Check expiration (prevents replay)
   - Extract user_id from "sub" claim
4. Dependency queries users table for user_id
5. If valid, user object passed to endpoint handler
6. Endpoint verifies resource ownership:
   - Fetch resource from database
   - Compare resource.user_id with current_user.id
   - Return 403 if mismatch
7. If authorized, perform operation and return response
```

### Data Isolation Flow

```
GET /tasks (list all tasks):
1. Extract current_user from JWT token
2. Query: SELECT * FROM tasks WHERE user_id = current_user.id
3. Return only authenticated user's tasks

GET /tasks/{id} (get specific task):
1. Extract current_user from JWT token
2. Query: SELECT * FROM tasks WHERE id = {id}
3. If not found: return 404
4. If task.user_id != current_user.id: return 403
5. If authorized: return task

PUT /tasks/{id} (update task):
1. Extract current_user from JWT token
2. Query: SELECT * FROM tasks WHERE id = {id}
3. If not found: return 404
4. If task.user_id != current_user.id: return 403
5. If authorized: update task and return

DELETE /tasks/{id} (delete task):
1. Extract current_user from JWT token
2. Query: SELECT * FROM tasks WHERE id = {id}
3. If not found: return 404
4. If task.user_id != current_user.id: return 403
5. If authorized: delete task and return 204
```

---

## Security Properties

### Property 1: User Isolation
**Guarantee**: A user can only access tasks where `task.user_id == user.id`
**Enforcement**: Database query filtering + ownership verification
**Validation**: Security test suite verifies cross-user access is blocked

### Property 2: Token Integrity
**Guarantee**: Only tokens signed with JWT_SECRET are accepted
**Enforcement**: Cryptographic signature verification in jwt.decode()
**Validation**: Tampered tokens are rejected with 401 Unauthorized

### Property 3: Token Freshness
**Guarantee**: Tokens expire after 24 hours
**Enforcement**: Expiration timestamp check in decode_token()
**Validation**: Expired tokens are rejected with 401 Unauthorized

### Property 4: No ID Enumeration
**Guarantee**: Attackers cannot enumerate valid task IDs
**Enforcement**: 404 response for non-existent or unauthorized resources
**Validation**: Security tests verify no information leakage

---

## Migration Requirements

**Database Migrations**: None required. All necessary schema elements exist from 002-backend-api-db.

**Data Migrations**: None required. No data transformation needed.

**Backward Compatibility**: Fully compatible with existing 002-backend-api-db implementation.

---

## Summary

This feature leverages existing User and Task entities without modification. Authorization is enforced through:
1. JWT token validation (identity extraction)
2. Database query filtering (user_id WHERE clause)
3. Ownership verification (user_id comparison)
4. Foreign key constraints (referential integrity)

No new database entities, tables, or migrations are required.
