"""Input sanitization utilities for XSS prevention."""
import html
import re


def sanitize_string(value: str) -> str:
    """Sanitize a string to prevent XSS attacks.
    
    Args:
        value: String to sanitize
        
    Returns:
        Sanitized string with HTML entities escaped
    """
    if not value:
        return value
    
    # Escape HTML entities
    sanitized = html.escape(value.strip())
    
    # Remove any null bytes
    sanitized = sanitized.replace('\x00', '')
    
    return sanitized


def sanitize_email(email: str) -> str:
    """Sanitize and normalize an email address.
    
    Args:
        email: Email address to sanitize
        
    Returns:
        Sanitized and normalized email address (lowercase, trimmed)
    """
    if not email:
        return email
    
    # Convert to lowercase and strip whitespace
    sanitized = email.strip().lower()
    
    # Remove any null bytes
    sanitized = sanitized.replace('\x00', '')
    
    # Basic validation pattern (Pydantic EmailStr will do full validation)
    # This is just for sanitization
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', sanitized):
        # If it doesn't match basic pattern, return as-is and let Pydantic handle validation
        return sanitized
    
    return sanitized
