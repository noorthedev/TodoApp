# Data Model Design

**Feature**: Phase 2 Todo Full-Stack Web Application
**Date**: 2026-02-15
**Status**: Complete

## Overview

This document defines the database schema for the Phase 2 Todo application. The data model consists of two primary entities: User and Task, with a one-to-many relationship enforcing per-user data isolation.

## Entity Relationship Diagram

```
┌─────────────────────┐
│       User          │
├─────────────────────┤
│ id (PK)             │
│ email (UNIQUE)      │
│ hashed_password     │
│ created_at          │
│ updated_at          │
└─────────────────────┘
          │
          │ 1:N
          │
          ▼
┌─────────────────────┐
│       Task          │
├─────────────────────┤
│ id (PK)             │
│ user_id (FK)        │
│ title               │
│ description         │
│ is_completed        │
│ created_at          │
│ updated_at          │
└─────────────────────┘
```

## Entity Definitions

### User Entity

**Purpose**: Represents a registered user account with authentication credentials.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| email | String(255) | UNIQUE, NOT NULL, INDEX | User's email address (used for login) |
| hashed_password | String(255) | NOT NULL | Bcrypt-hashed password (never plaintext) |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| updated_at | DateTime | NOT NULL, DEFAULT NOW(), ON UPDATE NOW() | Last modification timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `email` (for login lookups and duplicate prevention)

**Validation Rules**:
- Email must be valid format (validated by Pydantic before database)
- Email must be unique across all users
- Password must be hashed before storage (handled by Better Auth/backend)
- Minimum password length: 8 characters (enforced at application layer)

**Relationships**:
- One-to-many with Task (one user owns many tasks)

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Security Considerations**:
- Password MUST be hashed using bcrypt or argon2 (never stored plaintext)
- Email is indexed for fast login lookups
- No sensitive data beyond authentication credentials
- User deletion should cascade to tasks (or prevent if tasks exist)

---

### Task Entity

**Purpose**: Represents a todo item belonging to a specific user.

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, AUTO_INCREMENT | Unique task identifier |
| user_id | Integer | FOREIGN KEY (users.id), NOT NULL, INDEX | Owner of this task |
| title | String(255) | NOT NULL | Task title (required) |
| description | Text | NULLABLE | Optional detailed description |
| is_completed | Boolean | NOT NULL, DEFAULT FALSE | Completion status |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Task creation timestamp |
| updated_at | DateTime | NOT NULL, DEFAULT NOW(), ON UPDATE NOW() | Last modification timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id` (critical for per-user queries)
- COMPOSITE INDEX on `(user_id, created_at)` (for sorted task lists)

**Validation Rules**:
- Title is required (NOT NULL, min length 1, max length 255)
- Description is optional (can be NULL or empty string)
- is_completed defaults to FALSE (new tasks are incomplete)
- user_id must reference an existing user

**Relationships**:
- Many-to-one with User (many tasks belong to one user)
- Foreign key constraint ensures referential integrity

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Security Considerations**:
- ALL queries MUST filter by user_id to enforce data isolation
- Foreign key constraint prevents orphaned tasks
- Index on user_id ensures efficient per-user queries
- No direct access to other users' tasks (enforced at application layer)

---

## Data Isolation Strategy

**Critical Requirement**: Users must ONLY access their own data.

**Enforcement Mechanisms**:

1. **Database Level**:
   - Foreign key constraint: `task.user_id → user.id`
   - Index on `user_id` for efficient filtering

2. **Application Level** (Primary Enforcement):
   - JWT token contains user_id
   - All task queries include `WHERE user_id = {authenticated_user_id}`
   - No endpoints expose tasks without user_id filter

3. **Query Pattern**:
```python
# CORRECT: Filter by authenticated user
async def get_user_tasks(user_id: int, session: AsyncSession):
    result = await session.execute(
        select(Task).where(Task.user_id == user_id)
    )
    return result.scalars().all()

# INCORRECT: Returns all tasks (security violation)
async def get_all_tasks(session: AsyncSession):
    result = await session.execute(select(Task))
    return result.scalars().all()  # ❌ NEVER DO THIS
```

**Testing Requirements**:
- Create multiple test users
- Verify User A cannot see User B's tasks
- Verify User A cannot update/delete User B's tasks
- Test authorization failures return 403 Forbidden

---

## Database Constraints Summary

### User Table Constraints
- `PRIMARY KEY (id)`
- `UNIQUE (email)`
- `NOT NULL (email, hashed_password, created_at, updated_at)`
- `INDEX (email)` for login lookups

### Task Table Constraints
- `PRIMARY KEY (id)`
- `FOREIGN KEY (user_id) REFERENCES users(id)`
- `NOT NULL (user_id, title, is_completed, created_at, updated_at)`
- `INDEX (user_id)` for per-user queries
- `INDEX (user_id, created_at)` for sorted lists

---

## Migration Strategy

### Development Environment
Use SQLModel's `create_all()` method for rapid iteration:

```python
from sqlmodel import SQLModel, create_engine

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

### Production Environment
Manual migration script for explicit control:

```sql
-- Migration: 001_initial_schema.sql

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- Create tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at);

-- Trigger for updated_at (PostgreSQL)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## Performance Considerations

### Query Optimization
- Index on `user_id` ensures O(log n) lookup for user's tasks
- Composite index on `(user_id, created_at)` supports sorted queries
- Email index enables fast login lookups

### Expected Query Patterns
1. **Login**: `SELECT * FROM users WHERE email = ?` (indexed)
2. **Get User Tasks**: `SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC` (indexed)
3. **Create Task**: `INSERT INTO tasks (user_id, title, ...) VALUES (?, ?, ...)`
4. **Update Task**: `UPDATE tasks SET ... WHERE id = ? AND user_id = ?` (ensures ownership)
5. **Delete Task**: `DELETE FROM tasks WHERE id = ? AND user_id = ?` (ensures ownership)

### Scalability Notes
- Current design supports 100+ concurrent users
- For 10,000+ users, consider:
  - Connection pooling (Neon provides this)
  - Read replicas for task queries
  - Caching layer for frequently accessed data

---

## Data Validation

### Application Layer (Pydantic Schemas)
```python
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=10000)

class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    is_completed: bool | None = None
```

### Database Layer (Constraints)
- NOT NULL constraints prevent missing required fields
- UNIQUE constraint prevents duplicate emails
- FOREIGN KEY constraint ensures referential integrity
- CHECK constraints (if needed): `CHECK (LENGTH(title) > 0)`

---

## Edge Cases & Handling

### User Deletion
**Question**: What happens to tasks when a user is deleted?

**Decision**: CASCADE DELETE (tasks are deleted with user)

**Rationale**:
- Tasks have no meaning without their owner
- Prevents orphaned data
- Simpler than soft deletes for Phase 2

**Implementation**: `ON DELETE CASCADE` in foreign key constraint

### Concurrent Updates
**Question**: What if two requests update the same task simultaneously?

**Decision**: Last-write-wins with updated_at timestamp

**Rationale**:
- Optimistic locking adds complexity
- Unlikely scenario for single-user tasks
- updated_at provides audit trail

### Long Descriptions
**Question**: Should description have a length limit?

**Decision**: TEXT type (no hard limit), validate at 10,000 characters in application

**Rationale**:
- Flexible for user needs
- Application validation prevents abuse
- Database TEXT type handles variable length efficiently

---

## Testing Checklist

- [ ] User creation with valid email and password
- [ ] User creation with duplicate email (should fail)
- [ ] Task creation with valid user_id
- [ ] Task creation with invalid user_id (should fail)
- [ ] Task query filtered by user_id (returns only user's tasks)
- [ ] Task update with correct user_id (should succeed)
- [ ] Task update with wrong user_id (should fail/return 0 rows)
- [ ] Task deletion with correct user_id (should succeed)
- [ ] Task deletion with wrong user_id (should fail/return 0 rows)
- [ ] User deletion cascades to tasks

---

**Status**: ✅ Data model design complete and ready for implementation
