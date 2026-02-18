"""Task management API endpoints."""
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.database import get_session
from src.models.task import Task
from src.models.user import User
from src.schemas.task import TaskCreate, TaskList, TaskResponse, TaskUpdate
from src.utils.jwt import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])
logger = logging.getLogger(__name__)


@router.get("", response_model=TaskList)
async def get_tasks(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Get all tasks for the authenticated user.
    
    Args:
        current_user: Authenticated user from JWT token
        session: Database session
        
    Returns:
        TaskList with all user's tasks ordered by created_at descending
    """
    # Query tasks for current user, ordered by created_at desc
    result = await session.execute(
        select(Task)
        .where(Task.user_id == current_user.id)
        .order_by(Task.created_at.desc())
    )
    tasks = result.scalars().all()
    
    return TaskList(
        tasks=[TaskResponse.model_validate(task) for task in tasks],
        total=len(tasks),
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Create a new task for the authenticated user.

    Args:
        task_data: Task creation data (title and description)
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        Created task with all fields
    """
    logger.info(f"Creating task for user {current_user.id}: {task_data.title}")

    # Create new task with authenticated user_id
    new_task = Task(
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
    )

    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    logger.info(f"Task created successfully: ID {new_task.id} for user {current_user.id}")

    return TaskResponse.model_validate(new_task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Get a specific task by ID.
    
    Args:
        task_id: Task ID to retrieve
        current_user: Authenticated user from JWT token
        session: Database session
        
    Returns:
        Task details
        
    Raises:
        HTTPException: 404 if task not found, 403 if not owner
    """
    # Fetch task by ID
    result = await session.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    # Verify ownership
    if task.user_id != current_user.id:
        logger.warning(
            f"Authorization failed: user {current_user.id} attempted to access "
            f"task {task_id} owned by user {task.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task",
        )
    
    return TaskResponse.model_validate(task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Update a task.
    
    Args:
        task_id: Task ID to update
        task_data: Task update data (title, description, is_completed)
        current_user: Authenticated user from JWT token
        session: Database session
        
    Returns:
        Updated task
        
    Raises:
        HTTPException: 404 if task not found, 403 if not owner
    """
    # Fetch task by ID
    result = await session.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    # Verify ownership
    if task.user_id != current_user.id:
        logger.warning(
            f"Authorization failed: user {current_user.id} attempted to update "
            f"task {task_id} owned by user {task.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task",
        )

    logger.info(f"Updating task {task_id} for user {current_user.id}")

    # Update fields if provided
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.is_completed is not None:
        task.is_completed = task_data.is_completed

    # Update timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    logger.info(f"Task {task_id} updated successfully for user {current_user.id}")

    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Delete a task.
    
    Args:
        task_id: Task ID to delete
        current_user: Authenticated user from JWT token
        session: Database session
        
    Raises:
        HTTPException: 404 if task not found, 403 if not owner
    """
    # Fetch task by ID
    result = await session.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    
    # Verify ownership
    if task.user_id != current_user.id:
        logger.warning(
            f"Authorization failed: user {current_user.id} attempted to delete "
            f"task {task_id} owned by user {task.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task",
        )

    logger.info(f"Deleting task {task_id} for user {current_user.id}")

    # Delete task
    await session.delete(task)
    await session.commit()

    logger.info(f"Task {task_id} deleted successfully for user {current_user.id}")
