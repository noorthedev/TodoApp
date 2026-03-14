"""MCP tools for task management operations."""
import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.task import Task
from src.tools.utils import mcp_tool

logger = logging.getLogger(__name__)


@mcp_tool
async def add_task(
    title: str,
    description: str = "",
    user_context: Dict[str, Any] = None,
    session: AsyncSession = None,
) -> Dict[str, Any]:
    """Create a new task for the authenticated user.

    Args:
        title: Task title (1-200 characters)
        description: Optional task description (max 1000 characters)
        user_context: Authenticated user context (automatically provided)
        session: Database session (automatically provided)

    Returns:
        Structured response with success status and task data or error message
    """
    # Validate user_context
    if not user_context or "user_id" not in user_context:
        return {
            "success": False,
            "error": "User context is missing or invalid"
        }

    # Extract user_id (force it, never trust input)
    user_id = user_context["user_id"]

    # Validate title length
    if not title or len(title) < 1 or len(title) > 200:
        return {
            "success": False,
            "error": "Title must be between 1 and 200 characters"
        }

    # Validate description length
    if description and len(description) > 1000:
        return {
            "success": False,
            "error": "Description must not exceed 1000 characters"
        }

    # Create task with forced user_id
    new_task = Task(
        user_id=user_id,
        title=title,
        description=description if description else None,
        is_completed=False,
    )

    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    # Return structured success response
    return {
        "success": True,
        "data": {
            "task_id": new_task.id,
            "title": new_task.title,
            "description": new_task.description or "",
            "completed": new_task.is_completed,
            "created_at": new_task.created_at.isoformat(),
        }
    }


@mcp_tool
async def list_tasks(
    user_context: Dict[str, Any] = None,
    session: AsyncSession = None,
) -> Dict[str, Any]:
    """Retrieve all tasks belonging to the authenticated user.

    Args:
        user_context: Authenticated user context (automatically provided)
        session: Database session (automatically provided)

    Returns:
        Structured response with success status and tasks array or error message
    """
    # Validate user_context
    if not user_context or "user_id" not in user_context:
        return {
            "success": False,
            "error": "User context is missing or invalid"
        }

    # Extract user_id
    user_id = user_context["user_id"]

    # Query tasks filtered by user_id
    result = await session.execute(
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
    )
    tasks = result.scalars().all()

    # Convert tasks to response format
    tasks_data = [
        {
            "task_id": task.id,
            "title": task.title,
            "description": task.description or "",
            "completed": task.is_completed,
            "created_at": task.created_at.isoformat(),
        }
        for task in tasks
    ]

    # Return structured success response (empty list if no tasks)
    return {
        "success": True,
        "data": {
            "tasks": tasks_data,
            "count": len(tasks_data),
        }
    }

@mcp_tool
async def complete_task(
    task_id: int,
    user_context: Dict[str, Any] = None,
    session: AsyncSession = None,
) -> Dict[str, Any]:
    """Mark a task as completed for the authenticated user.

    Args:
        task_id: ID of task to mark as complete
        user_context: Authenticated user context (automatically provided)
        session: Database session (automatically provided)

    Returns:
        Structured response with success status and task data or error message
    """
    # Validate user_context
    if not user_context or "user_id" not in user_context:
        return {
            "success": False,
            "error": "User context is missing or invalid"
        }

    # Extract user_id
    user_id = user_context["user_id"]

    # Verify task exists
    task = await session.get(Task, task_id)
    if not task:
        return {
            "success": False,
            "error": "Task not found"
        }

    # Verify ownership
    if task.user_id != user_id:
        logger.warning(
            f"Authorization failed: user {user_id} attempted to complete task {task_id} owned by user {task.user_id}"
        )
        return {
            "success": False,
            "error": "Not authorized to access this task"
        }

    # Mark task as completed
    task.is_completed = True
    await session.commit()
    await session.refresh(task)

    # Return structured success response
    return {
        "success": True,
        "data": {
            "task_id": task.id,
            "title": task.title,
            "completed": task.is_completed,
        }
    }


@mcp_tool
async def delete_task(
    task_id: int,
    user_context: Dict[str, Any] = None,
    session: AsyncSession = None,
) -> Dict[str, Any]:
    """Permanently remove a task for the authenticated user.

    Args:
        task_id: ID of task to delete
        user_context: Authenticated user context (automatically provided)
        session: Database session (automatically provided)

    Returns:
        Structured response with success status and deletion confirmation or error message
    """
    # Validate user_context
    if not user_context or "user_id" not in user_context:
        return {
            "success": False,
            "error": "User context is missing or invalid"
        }

    # Extract user_id
    user_id = user_context["user_id"]

    # Verify task exists
    task = await session.get(Task, task_id)
    if not task:
        return {
            "success": False,
            "error": "Task not found"
        }

    # Verify ownership
    if task.user_id != user_id:
        logger.warning(
            f"Authorization failed: user {user_id} attempted to delete task {task_id} owned by user {task.user_id}"
        )
        return {
            "success": False,
            "error": "Not authorized to access this task"
        }

    # Log deletion for audit trail
    logger.info(
        f"Task deletion: user {user_id} deleted task {task_id} (title: '{task.title}')"
    )

    # Delete task
    await session.delete(task)
    await session.commit()

    # Return structured success response
    return {
        "success": True,
        "data": {
            "task_id": task_id,
            "deleted": True,
        }
    }


@mcp_tool
async def update_task(
    task_id: int,
    title: str = None,
    description: str = None,
    user_context: Dict[str, Any] = None,
    session: AsyncSession = None,
) -> Dict[str, Any]:
    """Modify task title or description for the authenticated user.

    Args:
        task_id: ID of task to update
        title: New task title (optional, 1-200 characters)
        description: New task description (optional, max 1000 characters)
        user_context: Authenticated user context (automatically provided)
        session: Database session (automatically provided)

    Returns:
        Structured response with success status and updated task data or error message
    """
    # Validate user_context
    if not user_context or "user_id" not in user_context:
        return {
            "success": False,
            "error": "User context is missing or invalid"
        }

    # Extract user_id
    user_id = user_context["user_id"]

    # Validate at least one field is provided
    if title is None and description is None:
        return {
            "success": False,
            "error": "At least one field (title or description) must be provided"
        }

    # Validate title length if provided
    if title is not None and (len(title) < 1 or len(title) > 200):
        return {
            "success": False,
            "error": "Title must be between 1 and 200 characters"
        }

    # Validate description length if provided
    if description is not None and len(description) > 1000:
        return {
            "success": False,
            "error": "Description must not exceed 1000 characters"
        }

    # Verify task exists
    task = await session.get(Task, task_id)
    if not task:
        return {
            "success": False,
            "error": "Task not found"
        }

    # Verify ownership
    if task.user_id != user_id:
        logger.warning(
            f"Authorization failed: user {user_id} attempted to update task {task_id} owned by user {task.user_id}"
        )
        return {
            "success": False,
            "error": "Not authorized to access this task"
        }

    # Update task fields
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description

    await session.commit()
    await session.refresh(task)

    # Return structured success response
    return {
        "success": True,
        "data": {
            "task_id": task.id,
            "title": task.title,
            "description": task.description or "",
            "completed": task.is_completed,
        }
    }
