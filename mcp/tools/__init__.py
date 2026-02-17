"""MCP tool wrappers for direct invocation outside the MCP protocol."""

from mcp.tools.search_snippets import search_snippets
from mcp.tools.get_snippet import get_snippet
from mcp.tools.list_snippets import list_snippets
from mcp.tools.create_snippet import create_snippet
from mcp.tools.list_tags import list_tags
from mcp.tools.list_collections import list_collections

__all__ = [
    "search_snippets",
    "get_snippet",
    "list_snippets",
    "create_snippet",
    "list_tags",
    "list_collections",
]
