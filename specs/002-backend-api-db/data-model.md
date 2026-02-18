# Data Model: Backend API & Database Layer

**Feature**: Backend API & Database Layer
**Date**: 2026-02-16
**Database**: Neon Serverless PostgreSQL
**ORM**: SQLModel

## Overview

This document defines the database schema for the backend API. The data model consists of two primary entities: User and Task, with a one-to-many relationship (one user can have many tasks).

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
│ user_id (FK)        │◄─── Foreign Key to User.id
│ title               │
│ description         │
│ is_completed        │
│ created_at          │
│ updated_at          │
└─────────────────────┘
```

## Entities

### User

Represents a registered user account in the system.

**Table Name**: `users`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique identifier for the user |
| email | VARCHAR(255) | NOT NULL, UNIQUE, INDEX | User's email address (used for login) |
| hashed_password | VARCHAR(255) | NOT NULL | Bcrypt-hashed password (never plaintext) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the user account was created |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the user account was last updated |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `email` (for fast login lookups and uniqueness enforcement)

**Validation Rules**:
- Email must be valid email format (validated by Pydantic EmailStr)
- Password must be at least 8 characters before hashing
- Email is case-insensitive (stored lowercase)

**Relationships**:
- One user can have many tasks (1:N relationship with Task)

**Security Notes**:
- Password is NEVER stored in plaintext
- Password is hashed with bcrypt before insertion
- Email is used as the unique identifier for login
- No sensitive data stored beyond authentication credentials

---

### Task

Represents a todo item belonging to a specific user.

**Table Name**: `tasks`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique identifier for the task |
| user_id | INTEGER | NOT NULL, FOREIGN KEY (users.id), INDEX | Owner of the task |
| title | VARCHAR(255) | NOT NULL | Task title/summary |
| description | TEXT | NULLABLE | Optional detailed description |
| is_completed | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the task was created |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When the task was last modified |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id` (for fast filtering of user's tasks)

**Validation Rules**:
- Title must be 1-255 characters (enforced by Pydantic)
- Description can be up to 10,000 characters (enforced by Pydantic)
- user_id must reference a valid user (enforced by foreign key)
- is_completed defaults to false for new tasks

**Relationships**:
- Each task belongs to exactly one user (N:1 relationship with User)
- Foreign key constraint ensures referential integrity

**Business Rules**:
- Users can only access their own tasks (enforced in API layer)
- Deleting a user should cascade delete their tasks (or prevent deletion if tasks exist)
- Tasks cannot exist without a user (NOT NULL constraint on user_id)

---

## SQLModel Implementation

### User Model

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

### Task Model

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

---

## Database Migrations

### Initial Schema Creation

SQLModel can automatically create tables on application startup:

```python
from sqlmodel import SQLModel, create_engine

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

### Migration Strategy

For this hackathon project, we use automatic table creation on startup. For production, consider:
- **Alembic**: SQLAlchemy migration tool (recommended for production)
- **Manual migrations**: SQL scripts for schema changes
- **Version control**: Track schema versions in database

---

## Data Integrity

### Constraints

1. **Primary Keys**: Ensure unique identification of records
2. **Foreign Keys**: Maintain referential integrity between users and tasks
3. **Unique Constraints**: Prevent duplicate emails
4. **NOT NULL**: Ensure required fields are always present
5. **Default Values**: Provide sensible defaults (is_completed=false, timestamps)

### Cascade Behavior

**On User Deletion**:
- Option 1: CASCADE DELETE (delete all user's tasks)
- Option 2: RESTRICT (prevent deletion if user has tasks)
- **Recommended**: CASCADE DELETE for this application

**On Task Deletion**:
- No cascade needed (tasks don't reference other entities)

---

## Query Patterns

### Common Queries

**Get all tasks for a user**:
```python
result = await session.execute(
    select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
)
tasks = result.scalars().all()
```

**Get specific task with ownership check**:
```python
result = await session.execute(
    select(Task).where(Task.id == task_id, Task.user_id == user_id)
)
task = result.scalar_one_or_none()
```

**Find user by email**:
```python
result = await session.execute(
    select(User).where(User.email == email)
)
user = result.scalar_one_or_none()
```

**Create new task**:
```python
new_task = Task(user_id=user_id, title=title, description=description)
session.add(new_task)
await session.commit()
await session.refresh(new_task)
```

---

## Performance Considerations

### Indexes

- `users.email`: UNIQUE INDEX for fast login lookups
- `tasks.user_id`: INDEX for filtering user's tasks

### Query Optimization

- Always filter tasks by user_id (uses index)
- Use pagination for large result sets
- Avoid SELECT * (specify needed columns)
- Use async operations to prevent blocking

### Connection Pooling

- Configure appropriate pool size (5-10 connections)
- Use async session management
- Close sessions properly (use context managers)

---

## Security Considerations

### Data Isolation

- **Critical**: All task queries MUST filter by user_id
- Never trust client-provided user_id (get from JWT token)
- Verify ownership before update/delete operations
- Return 403 Forbidden for unauthorized access attempts

### Sensitive Data

- Passwords are hashed with bcrypt (never plaintext)
- JWT tokens contain user_id and email (no sensitive data)
- No PII beyond email address
- Sanitize user input to prevent XSS

### SQL Injection Prevention

- Use parameterized queries (SQLModel handles this)
- Never concatenate user input into SQL
- Validate all input types with Pydantic

---

## Testing Strategy

### Model Tests

- Test model creation and validation
- Test field constraints (max_length, NOT NULL)
- Test relationships (foreign keys)
- Test default values

### Query Tests

- Test CRUD operations
- Test filtering and ordering
- Test ownership checks
- Test error cases (not found, unauthorized)

### Integration Tests

- Test with real database (test database)
- Test transaction rollback on errors
- Test concurrent operations
- Test data integrity constraints

---

## Future Enhancements

Potential schema extensions (out of scope for current phase):

- **Task Categories**: Add category_id foreign key
- **Task Priority**: Add priority field (low/medium/high)
- **Task Due Dates**: Add due_date timestamp
- **Task Tags**: Many-to-many relationship with tags table
- **Task Sharing**: Many-to-many relationship for shared tasks
- **User Profiles**: Additional user metadata (name, avatar, preferences)
- **Audit Log**: Track all changes to tasks

---

## Conclusion

The data model is simple, focused, and sufficient for the MVP requirements. It provides:
- Clear entity relationships (User 1:N Task)
- Proper constraints and indexes
- Security through data isolation
- Performance through strategic indexing
- Extensibility for future features

**Next Steps**: Generate API contracts based on this data model.
