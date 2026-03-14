"""Agent invocation logic for OpenAI function calling."""
import json
import logging
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from src.agent.config import client, AGENT_CONFIG
from src.agent.prompts import SYSTEM_PROMPT
from src.tools.registry import get_tool_catalog, get_tool

# Import tools module to trigger registration
import src.tools  # noqa: F401

logger = logging.getLogger(__name__)


async def invoke_agent(
    user_message: str,
    conversation_history: List[Dict[str, str]],
    user_context: Dict[str, Any],
    session: AsyncSession,
) -> str:
    """Invoke OpenAI agent with tool calling support.

    Args:
        user_message: User's current message
        conversation_history: Previous messages in conversation
        user_context: Authenticated user context (user_id, email)
        session: Database session for tool operations

    Returns:
        Agent's response as string
    """
    # Build messages with history
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *conversation_history,
        {"role": "user", "content": user_message},
    ]

    # Get tool catalog
    tools = get_tool_catalog()

    try:
        # Call agent with function calling
        response = client.chat.completions.create(
            model=AGENT_CONFIG["model"],
            messages=messages,
            tools=tools if tools else None,
            tool_choice="auto" if tools else None,
            temperature=AGENT_CONFIG["temperature"],
            max_tokens=AGENT_CONFIG["max_tokens"],
            timeout=AGENT_CONFIG["timeout"],
        )

        # Handle tool calls
        if response.choices[0].message.tool_calls:
            # Add assistant message with tool calls to history
            assistant_message = response.choices[0].message
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })

            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                logger.info(f"Executing tool: {tool_name} with args: {tool_args}")

                # Inject user_context and session
                tool_args["user_context"] = user_context
                tool_args["session"] = session

                # Execute tool
                tool_func = get_tool(tool_name)
                tool_result = await tool_func(**tool_args)

                logger.info(f"Tool {tool_name} result: {tool_result}")

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result),
                })

            # Get final response after tool execution
            final_response = client.chat.completions.create(
                model=AGENT_CONFIG["model"],
                messages=messages,
                temperature=AGENT_CONFIG["temperature"],
                max_tokens=AGENT_CONFIG["max_tokens"],
                timeout=AGENT_CONFIG["timeout"],
            )

            return final_response.choices[0].message.content

        # No tool calls - return direct response
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Agent invocation error: {str(e)}", exc_info=True)
        return "I'm sorry, I encountered an error processing your request. Please try again."
