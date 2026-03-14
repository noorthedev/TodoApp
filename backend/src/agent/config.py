"""Agent configuration for OpenAI integration."""
from openai import OpenAI
from src.config import settings

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Agent configuration
AGENT_CONFIG = {
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 500,
    "timeout": 10,  # seconds
}
