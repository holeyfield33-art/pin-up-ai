"""Get snippet tool."""
from typing import Any


def get_snippet(payload: dict[str, Any]) -> dict[str, Any]:
    """Get a specific snippet by ID.
    
    Args:
        id (int): Snippet ID
    """
    # This is now handled by server.py
    return {"error": "Use server.py for actual implementation"}
