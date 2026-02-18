"""Example: Adding a New Protected Endpoint

This file demonstrates how to add a new protected endpoint that follows
the centralized authorization pattern used throughout the Task Management API.

Location: specs/003-auth-isolation/examples/new-endpoint.py
Purpose: Reference implementation for developers adding new protected endpoints
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Field, SQLModel, select
import logging

from src.database import get_session
from src.models.user import User
from src.utils.jwt import get_current_user

# Setup
router = APIRouter(prefix="/notes", tags=["Notes"])
logger = logging.getLogger(__name__)


# ============================================================================
# STEP 1: Define Your Data Model
# ============================================================================

class Note(SQLModel, table=True):
    """Example model: User notes."""
    __tablename__ = "notes"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)  # REQUIRED: user_id FK
    title: str = Field(max_length=200)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# STEP 2: Define Request/Response Schemas
# ============================================================================

class NoteCreate(SQLModel):
    """Schema for creating a note."""
    title: str = Field(max_length=200)
    content: str


class NoteUpdate(SQLModel):
    """Schema for updating a note."""
    title: Optional[str] = Field(default=None, max_length=200)
    content: Optional[str] = None


class NoteResponse(SQLModel):
    """Schema for note response."""
    id: int
    user_id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime


class NoteList(SQLModel):
    """Schema for list of notes."""
    notes: list[NoteResponse]
    total: int


# ============================================================================
# STEP 3: Implement Protected Endpoints
# ============================================================================

@router.get("", response_model=NoteList)
async def get_notes(
    current_user: User = Depends(get_current_user),  # ✓ Authorization dependency
    session: AsyncSession = Depends(get_session),
):
    """Get all notes for the authenticated user.

    PATTERN: List Resources (Filter by User)
    - Always filter by current_user.id
    - Prevents cross-user data leakage
    """
    # Query notes for current user only
    result = await session.execute(
        select(Note)
        .where(Note.user_id == current_user.id)  # ✓ Filter by user_id
        .order_by(Note.created_at.desc())
    )
    notes = result.scalars().all()

    return NoteList(
        notes=[NoteResponse.model_validate(note) for note in notes],
        total=len(notes),
    )


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user),  # ✓ Authorization dependency
    session: AsyncSession = Depends(get_session),
):
    """Create a new note for the authenticated user.

    PATTERN: Create Resource (Force User ID)
    - Always use current_user.id (from token)
    - Ignore any user_id in request body
    - Prevents parameter manipulation attacks
    """
    logger.info(f"Creating note for user {current_user.id}: {note_data.title}")

    # Create new note with authenticated user_id
    new_note = Note(
        user_id=current_user.id,  # ✓ Force authenticated user_id
        title=note_data.title,
        content=note_data.content,
    )

    session.add(new_note)
    await session.commit()
    await session.refresh(new_note)

    logger.info(f"Note created successfully: ID {new_note.id} for user {current_user.id}")

    return NoteResponse.model_validate(new_note)


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    current_user: User = Depends(get_current_user),  # ✓ Authorization dependency
    session: AsyncSession = Depends(get_session),
):
    """Get a specific note by ID.

    PATTERN: Get Specific Resource (Verify Ownership)
    - Fetch resource first
    - Return 404 if not found
    - Verify ownership (user_id match)
    - Return 403 if not owner
    - Log authorization failures
    """
    # Fetch note by ID
    result = await session.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    # Verify ownership
    if note.user_id != current_user.id:  # ✓ Ownership check
        logger.warning(
            f"Authorization failed: user {current_user.id} attempted to access "
            f"note {note_id} owned by user {note.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this note",
        )

    return NoteResponse.model_validate(note)


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note_data: NoteUpdate,
    current_user: User = Depends(get_current_user),  # ✓ Authorization dependency
    session: AsyncSession = Depends(get_session),
):
    """Update a note.

    PATTERN: Update Resource (Verify Ownership)
    - Fetch resource first
    - Return 404 if not found
    - Verify ownership (user_id match)
    - Return 403 if not owner
    - Log authorization failures
    - Update only provided fields
    """
    # Fetch note by ID
    result = await session.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    # Verify ownership
    if note.user_id != current_user.id:  # ✓ Ownership check
        logger.warning(
            f"Authorization failed: user {current_user.id} attempted to update "
            f"note {note_id} owned by user {note.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this note",
        )

    logger.info(f"Updating note {note_id} for user {current_user.id}")

    # Update fields if provided
    if note_data.title is not None:
        note.title = note_data.title
    if note_data.content is not None:
        note.content = note_data.content

    # Update timestamp
    note.updated_at = datetime.utcnow()

    session.add(note)
    await session.commit()
    await session.refresh(note)

    logger.info(f"Note {note_id} updated successfully for user {current_user.id}")

    return NoteResponse.model_validate(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),  # ✓ Authorization dependency
    session: AsyncSession = Depends(get_session),
):
    """Delete a note.

    PATTERN: Delete Resource (Verify Ownership)
    - Fetch resource first
    - Return 404 if not found
    - Verify ownership (user_id match)
    - Return 403 if not owner
    - Log authorization failures
    """
    # Fetch note by ID
    result = await session.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    # Verify ownership
    if note.user_id != current_user.id:  # ✓ Ownership check
        logger.warning(
            f"Authorization failed: user {current_user.id} attempted to delete "
            f"note {note_id} owned by user {note.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this note",
        )

    logger.info(f"Deleting note {note_id} for user {current_user.id}")

    # Delete note
    await session.delete(note)
    await session.commit()

    logger.info(f"Note {note_id} deleted successfully for user {current_user.id}")


# ============================================================================
# STEP 4: Register Router in Main Application
# ============================================================================

# In your main.py or app.py:
# from src.api.notes import router as notes_router
# app.include_router(notes_router)


# ============================================================================
# STEP 5: Write Security Tests
# ============================================================================

"""
Example test structure (in backend/tests/security/test_notes.py):

class TestNoteOwnership:
    def test_cross_user_access_blocked(self, client, alice_user, bob_user):
        # Alice creates a note
        alice_headers = {"Authorization": f"Bearer {alice_user['token']}"}
        note_response = client.post(
            "/notes",
            json={"title": "Alice's note", "content": "Secret"},
            headers=alice_headers
        )
        note_id = note_response.json()["id"]

        # Bob attempts to access Alice's note
        bob_headers = {"Authorization": f"Bearer {bob_user['token']}"}
        response = client.get(f"/notes/{note_id}", headers=bob_headers)

        # Should return 403 Forbidden
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]

    def test_note_list_isolation(self, client, alice_user, bob_user):
        # Alice creates a note
        alice_headers = {"Authorization": f"Bearer {alice_user['token']}"}
        alice_note = client.post(
            "/notes",
            json={"title": "Alice's note", "content": "Secret"},
            headers=alice_headers
        ).json()

        # Bob creates a note
        bob_headers = {"Authorization": f"Bearer {bob_user['token']}"}
        bob_note = client.post(
            "/notes",
            json={"title": "Bob's note", "content": "Secret"},
            headers=bob_headers
        ).json()

        # Alice should see only her note
        alice_list = client.get("/notes", headers=alice_headers).json()
        alice_note_ids = [note["id"] for note in alice_list["notes"]]
        assert alice_note["id"] in alice_note_ids
        assert bob_note["id"] not in alice_note_ids

        # Bob should see only his note
        bob_list = client.get("/notes", headers=bob_headers).json()
        bob_note_ids = [note["id"] for note in bob_list["notes"]]
        assert bob_note["id"] in bob_note_ids
        assert alice_note["id"] not in bob_note_ids
"""


# ============================================================================
# SECURITY CHECKLIST
# ============================================================================

"""
Before deploying your new endpoint, verify:

✓ Model has user_id foreign key with index
✓ All endpoints use current_user: User = Depends(get_current_user)
✓ List operations filter by current_user.id
✓ Create operations force user_id=current_user.id
✓ Read/Update/Delete operations verify ownership
✓ Authorization failures are logged
✓ 403 Forbidden returned for ownership violations
✓ 404 Not Found returned for non-existent resources
✓ Tests cover: valid token, missing token, expired token, cross-user access
✓ No authorization logic duplication
✓ Error messages don't leak sensitive information
"""
