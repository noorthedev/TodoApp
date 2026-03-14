"""MCP tool registry for agent function calling."""
from typing import Dict, List, Any, Callable

# Tool catalog - maps tool names to their implementations
_tool_catalog: Dict[str, Callable] = {}

# Tool schemas for OpenAI function calling
_tool_schemas: List[Dict[str, Any]] = []


def register_tool(
    name: str,
    func: Callable,
    description: str,
    parameters: Dict[str, Any]
) -> None:
    """Register a tool in the catalog.

    Args:
        name: Tool name
        func: Tool function
        description: Tool description for agent
        parameters: JSON schema for tool parameters
    """
    _tool_catalog[name] = func

    # Create OpenAI function schema
    schema = {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters
        }
    }
    _tool_schemas.append(schema)


def get_tool(name: str) -> Callable:
    """Get a tool by name.

    Args:
        name: Tool name

    Returns:
        Tool function

    Raises:
        KeyError: If tool not found
    """
    return _tool_catalog[name]


def get_tool_catalog() -> List[Dict[str, Any]]:
    """Get all tool schemas for OpenAI function calling.

    Returns:
        List of tool schemas in OpenAI format
    """
    return _tool_schemas


def list_tools() -> List[str]:
    """List all registered tool names.

    Returns:
        List of tool names
    """
    return list(_tool_catalog.keys())
