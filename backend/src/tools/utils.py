"""Utility functions and decorators for MCP tools."""
import logging
from functools import wraps
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)


def mcp_tool(func: Callable) -> Callable:
    """Decorator for MCP tools with consistent error handling.

    Wraps tool functions to:
    - Catch all exceptions
    - Log errors for debugging
    - Return structured error responses

    Args:
        func: Async tool function to wrap

    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Dict[str, Any]:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Tool error in {func.__name__}: {str(e)}",
                exc_info=True,
                extra={
                    "tool_name": func.__name__,
                    "args": args,
                    "kwargs": {k: v for k, v in kwargs.items() if k != "session"}
                }
            )
            return {
                "success": False,
                "error": "Internal error occurred"
            }
    return wrapper
