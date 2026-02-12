"""Search snippets tool."""
from typing import Any


def search_snippets(payload: dict[str, Any]) -> dict[str, Any]:
    """Search snippets by query string.
    
    Args:
        query (str): Search query
        limit (int): Maximum results (default 50)
    """
    # This is now handled by server.py
    return {"error": "Use server.py for actual implementation"}
