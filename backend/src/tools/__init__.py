"""Tools module - exports MCP tools and ensures registration."""
from src.tools.task_tools import add_task, list_tasks, complete_task, delete_task, update_task

# Import tool_registration to trigger auto-registration
from src.tools import tool_registration  # noqa: F401

__all__ = ["add_task", "list_tasks", "complete_task", "delete_task", "update_task"]
