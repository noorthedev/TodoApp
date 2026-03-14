# Data Model: MCP Server & Task Tools Integration

**Feature**: 005-mcp-task-tools
**Date**: 2026-02-19
**Status**: Complete

## Overview

This feature introduces two new database models (Conversation and Message) to support stateless conversation persistence. The existing Task and User models are reused without modification.

## Entity Relationship Diagram

```
User (existing)
  ├── 1:N → Task (existing)
  └── 1:N → Conversation (new)
                └── 1:N → Message (new)
```

## Entities

### User (Existing - No Changes)

**Purpose**: Represents authenticated users in the system

**Fields**:
- `id`: Integer, primary key
- `email`: String, unique, indexed
- `hashed_password`: String
- `created_at`: DateTime
- `updated_at`: DateTime

**Relationships**:
- Has many Tasks (existing)
- Has many Conversations (new)

**Location**: `backend/src/models/user.py`

**No changes required** - existing model supports new relationships

---

### Task (Existing - No Changes)

**Purpose**: Represents user's todo items

**Fields**:
- `id`: Integer, primary key
- `user_id`: Integer, foreign key to User, indexed
- `title`: String (max 255 characters)
- `description`: String (max 1000 characters), optional
- `is_completed`: Boolean, default False
- `created_at`: DateTime
- `updated_at`: DateTime

**Relationships**:
- Belongs to User

**Location**: `backend/src/models/task.py`

**No changes required** - MCP tools will use this existing model

---

### Conversation (New)

**Purpose**: Represents a chat conversation between user and AI agent

**Fields**:
- `id`: Integer, primary key, auto-increment
- `user_id`: Integer, foreign key to User, indexed, NOT NULL
- `created_at`: DateTime, default now(), NOT NULL
- `updated_at`: DateTime, default now(), NOT NULL

**Relationships**:
- Belongs to User (many-to-one)
- Has many Messages (one-to-many)

**Indexes**:
- Primary key on `id`
- Index on `user_id` (for fast user conversation lookup)

**Constraints**:
- `user_id` must reference existing User
- `user_id` cannot be null

**Validation Rules**:
- User must exist before creating conversation
- Conversation cannot be orphaned (user_id required)

**State Transitions**:
- Created: When user sends first message
- Updated: When new message added to conversation
- No explicit "closed" state (conversations remain open)

**SQLModel Definition**:
```python
from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, Relationship, SQLModel

class Conversation(SQLModel, table=True):
    """Conversation entity for chat history."""

    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")
```

**Location**: `backend/src/models/conversation.py` (new file)

---

### Message (New)

**Purpose**: Represents individual messages in a conversation (user or assistant)

**Fields**:
- `id`: Integer, primary key, auto-increment
- `conversation_id`: Integer, foreign key to Conversation, indexed, NOT NULL
- `role`: String (max 20 characters), NOT NULL, values: "user" or "assistant"
- `content`: Text, NOT NULL
- `timestamp`: DateTime, default now(), NOT NULL

**Relationships**:
- Belongs to Conversation (many-to-one)

**Indexes**:
- Primary key on `id`
- Index on `conversation_id` (for fast message history lookup)
- Composite index on `(conversation_id, timestamp)` (for ordered history queries)

**Constraints**:
- `conversation_id` must reference existing Conversation
- `role` must be either "user" or "assistant"
- `content` cannot be empty
- `timestamp` cannot be null

**Validation Rules**:
- Role must be "user" or "assistant" (no other values)
- Content must be non-empty string
- Timestamp must be valid datetime

**State Transitions**:
- Created: When message is persisted (before or after agent invocation)
- Immutable: Messages are never updated or deleted (append-only log)

**SQLModel Definition**:
```python
from datetime import datetime
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel

class Message(SQLModel, table=True):
    """Message entity for conversation history."""

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: str = Field(max_length=20)  # "user" or "assistant"
    content: str  # No max length (TEXT column)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
```

**Location**: `backend/src/models/message.py` (new file)

---

## Database Schema (SQL)

```sql
-- Conversations table (new)
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);

-- Messages table (new)
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_conversation_timestamp ON messages(conversation_id, timestamp);
```

---

## Migration Strategy

### Option 1: SQLModel Auto-Create (Development)

For development, SQLModel can auto-create tables on startup:

```python
# In backend/src/database.py
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

This will create Conversation and Message tables automatically when models are imported.

### Option 2: Alembic Migration (Production)

For production, use Alembic migration:

```bash
# Generate migration
alembic revision --autogenerate -m "Add conversation and message tables"

# Apply migration
alembic upgrade head
```

**Migration file** (auto-generated):
```python
def upgrade():
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])

    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("role IN ('user', 'assistant')")
    )
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_conversation_timestamp', 'messages', ['conversation_id', 'timestamp'])

def downgrade():
    op.drop_table('messages')
    op.drop_table('conversations')
```

---

## Data Access Patterns

### Pattern 1: Get or Create Conversation

```python
async def get_or_create_conversation(
    session: AsyncSession,
    user_id: int
) -> Conversation:
    """Get active conversation for user or create new one."""
    # Try to get most recent conversation
    result = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(1)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        # Create new conversation
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)

    return conversation
```

### Pattern 2: Load Conversation History

```python
async def load_conversation_history(
    session: AsyncSession,
    conversation_id: int,
    limit: int = 50
) -> List[Message]:
    """Load recent messages from conversation."""
    result = await session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.timestamp.desc())
        .limit(limit)
    )
    messages = result.scalars().all()

    # Reverse to get chronological order
    return list(reversed(messages))
```

### Pattern 3: Persist Message

```python
async def persist_message(
    session: AsyncSession,
    conversation_id: int,
    role: str,
    content: str
) -> Message:
    """Persist a message to the conversation."""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)

    # Update conversation timestamp
    conversation = await session.get(Conversation, conversation_id)
    conversation.updated_at = datetime.utcnow()
    await session.commit()

    return message
```

---

## Performance Considerations

### Query Optimization

1. **Index on user_id**: Fast lookup of user's conversations
2. **Index on conversation_id**: Fast lookup of conversation messages
3. **Composite index on (conversation_id, timestamp)**: Fast ordered history queries
4. **Limit queries**: Always use LIMIT to prevent loading entire history

### Expected Query Performance

| Query | Expected Time | Optimization |
|-------|---------------|--------------|
| Get user's conversations | <10ms | Index on user_id |
| Load 50 messages | <50ms | Index on conversation_id + LIMIT |
| Persist message | <10ms | Single INSERT with index update |
| Update conversation timestamp | <5ms | Primary key lookup |

### Scaling Considerations

- **Conversation growth**: One conversation per user (or per session)
- **Message growth**: ~100 messages per conversation average
- **Storage**: ~1KB per message average
- **Total storage**: 10,000 users × 100 messages × 1KB = ~1GB (manageable)

### Cleanup Strategy (Future)

- Archive conversations older than 90 days
- Delete messages from archived conversations
- Keep conversation metadata for analytics

---

## Data Integrity

### Foreign Key Constraints

- `Conversation.user_id` → `User.id` (CASCADE DELETE)
- `Message.conversation_id` → `Conversation.id` (CASCADE DELETE)

**Behavior**:
- Deleting user deletes all their conversations and messages
- Deleting conversation deletes all its messages
- Orphaned records prevented by database constraints

### Validation

- Role validation: CHECK constraint ensures role is "user" or "assistant"
- Content validation: NOT NULL constraint ensures content exists
- Timestamp validation: Default value ensures timestamp always set

---

## Testing Strategy

### Unit Tests

```python
# Test conversation creation
async def test_create_conversation():
    conversation = Conversation(user_id=1)
    assert conversation.user_id == 1
    assert conversation.created_at is not None

# Test message creation
async def test_create_message():
    message = Message(
        conversation_id=1,
        role="user",
        content="Hello"
    )
    assert message.role == "user"
    assert message.content == "Hello"
```

### Integration Tests

```python
# Test get or create conversation
async def test_get_or_create_conversation(session, user):
    conv1 = await get_or_create_conversation(session, user.id)
    conv2 = await get_or_create_conversation(session, user.id)
    assert conv1.id == conv2.id  # Same conversation returned

# Test load conversation history
async def test_load_conversation_history(session, conversation):
    # Create 3 messages
    for i in range(3):
        await persist_message(session, conversation.id, "user", f"Message {i}")

    # Load history
    messages = await load_conversation_history(session, conversation.id)
    assert len(messages) == 3
    assert messages[0].content == "Message 0"  # Chronological order
```

---

## Summary

**New Models**: 2 (Conversation, Message)
**Existing Models**: 2 (User, Task) - no changes
**New Tables**: 2 (conversations, messages)
**New Indexes**: 3 (user_id, conversation_id, conversation_id+timestamp)
**Foreign Keys**: 2 (Conversation→User, Message→Conversation)
**Migration**: Auto-create (dev) or Alembic (prod)
