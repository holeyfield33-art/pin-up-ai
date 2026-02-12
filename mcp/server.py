"""
MCP Server for Pin-Up AI
Provides AI agents with tools to search, manage, and save snippets
"""
import asyncio
import httpx
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
TIMEOUT = 30


class MCPServerError(Exception):
    """Base MCP server exception."""
    pass


class BackendClient:
    """HTTP client for FastAPI backend."""
    
    def __init__(self, base_url: str = BACKEND_URL, timeout: int = TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout
    
    async def search_snippets(self, query: str, limit: int = 50) -> list[dict]:
        """Search snippets using full-text search."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/snippets/search/query",
                    params={"q": query, "limit": limit},
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise MCPServerError(f"Failed to search snippets: {str(e)}")
    
    async def get_snippet(self, snippet_id: int) -> dict:
        """Get a specific snippet by ID."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/snippets/{snippet_id}")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Get snippet failed: {e}")
            raise MCPServerError(f"Failed to get snippet: {str(e)}")
    
    async def list_snippets(self, limit: int = 50) -> list[dict]:
        """List snippets."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/snippets/",
                    params={"limit": limit},
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"List snippets failed: {e}")
            raise MCPServerError(f"Failed to list snippets: {str(e)}")
    
    async def create_snippet(self, title: str, body: str, language: str | None = None, source: str | None = None) -> dict:
        """Create a new snippet."""
        try:
            payload = {"title": title, "body": body, "language": language, "source": source, "tags": [], "collection_id": None}
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/snippets/", json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Create snippet failed: {e}")
            raise MCPServerError(f"Failed to create snippet: {str(e)}")
    
    async def list_collections(self, limit: int = 100) -> list[dict]:
        """List all collections."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/collections/",
                    params={"limit": limit},
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"List collections failed: {e}")
            raise MCPServerError(f"Failed to list collections: {str(e)}")
    
    async def list_tags(self, limit: int = 100) -> list[dict]:
        """List all tags."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/tags/",
                    params={"limit": limit},
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"List tags failed: {e}")
            raise MCPServerError(f"Failed to list tags: {str(e)}")


backend_client = BackendClient()


# Tool definitions
TOOLS = {
    "search_snippets": {"description": "Search snippets by query", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "default": 50}}, "required": ["query"]}},
    "get_snippet": {"description": "Get a specific snippet", "inputSchema": {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]}},
    "list_snippets": {"description": "List all snippets", "inputSchema": {"type": "object", "properties": {"limit": {"type": "integer", "default": 50}}}},
    "create_snippet": {"description": "Create a new snippet", "inputSchema": {"type": "object", "properties": {"title": {"type": "string"}, "body": {"type": "string"}, "language": {"type": "string"}, "source": {"type": "string"}}, "required": ["title", "body"]}},
    "list_collections": {"description": "List all collections", "inputSchema": {"type": "object", "properties": {"limit": {"type": "integer", "default": 100}}}},
    "list_tags": {"description": "List all tags", "inputSchema": {"type": "object", "properties": {"limit": {"type": "integer", "default": 100}}}},
}


async def handle_tool_call(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Handle MCP tool calls and return results."""
    try:
        if tool_name == "search_snippets":
            result = await backend_client.search_snippets(
                query=arguments.get("query"),
                limit=arguments.get("limit", 50),
            )
            return {"status": "success", "data": result}
        elif tool_name == "get_snippet":
            result = await backend_client.get_snippet(snippet_id=arguments.get("id"))
            return {"status": "success", "data": result}
        elif tool_name == "list_snippets":
            result = await backend_client.list_snippets(limit=arguments.get("limit", 50))
            return {"status": "success", "data": result}
        elif tool_name == "create_snippet":
            result = await backend_client.create_snippet(
                title=arguments.get("title"),
                body=arguments.get("body"),
                language=arguments.get("language"),
                source=arguments.get("source"),
            )
            return {"status": "success", "data": result}
        elif tool_name == "list_collections":
            result = await backend_client.list_collections(limit=arguments.get("limit", 100))
            return {"status": "success", "data": result}
        elif tool_name == "list_tags":
            result = await backend_client.list_tags(limit=arguments.get("limit", 100))
            return {"status": "success", "data": result}
        else:
            return {"status": "error", "message": f"Unknown tool: {tool_name}"}
    except MCPServerError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        logger.error(f"Tool error: {e}", exc_info=True)
        return {"status": "error", "message": "Internal server error"}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Pin-Up AI MCP Server")
    print(f"Backend: {BACKEND_URL}")
    print(f"Available tools: {list(TOOLS.keys())}")
