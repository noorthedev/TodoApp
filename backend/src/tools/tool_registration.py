"""Tool registration - registers all MCP tools with the agent."""
from src.tools.registry import register_tool
from src.tools.task_tools import add_task, list_tasks, complete_task, delete_task, update_task


def register_all_tools():
    """Register all MCP tools with their schemas."""

    # Register add_task tool
    register_tool(
        name="add_task",
        func=add_task,
        description="Creates a new task for the authenticated user. Use this when user expresses intent to create, add, or remember something.",
        parameters={
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Task title (1-200 characters)",
                },
                "description": {
                    "type": "string",
                    "description": "Optional task description (max 1000 characters)",
                    "default": "",
                }
            },
            "required": ["title"]
        }
    )

    # Register list_tasks tool
    register_tool(
        name="list_tasks",
        func=list_tasks,
        description="Retrieves all tasks belonging to the authenticated user. Use this when user wants to see, view, or check their tasks.",
        parameters={
            "type": "object",
            "properties": {},
            "required": []
        }
    )

    # Register complete_task tool
    register_tool(
        name="complete_task",
        func=complete_task,
        description="Marks a task as completed for the authenticated user. Use this when user indicates a task is done, finished, or complete.",
        parameters={
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "ID of task to mark as complete",
                }
            },
            "required": ["task_id"]
        }
    )

    # Register delete_task tool
    register_tool(
        name="delete_task",
        func=delete_task,
        description="Permanently removes a task for the authenticated user. Use this when user wants to delete, remove, or discard a task.",
        parameters={
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "ID of task to delete",
                }
            },
            "required": ["task_id"]
        }
    )

    # Register update_task tool
    register_tool(
        name="update_task",
        func=update_task,
        description="Modifies task title or description for the authenticated user. Use this when user wants to change, edit, or update task details.",
        parameters={
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "ID of task to update",
                },
                "title": {
                    "type": "string",
                    "description": "New task title (optional, 1-200 characters)",
                },
                "description": {
                    "type": "string",
                    "description": "New task description (optional, max 1000 characters)",
                }
            },
            "required": ["task_id"]
        }
    )


# Auto-register tools when module is imported
register_all_tools()
