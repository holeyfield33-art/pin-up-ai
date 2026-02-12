"""MCP (Model Context Protocol) Server - Provides tools for AI agents."""

import json
import logging
import sys
import os
from typing import Any, Callable, Dict, List
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services import SnippetService, TagService, CollectionService
from app.schemas import SnippetCreate

logger = logging.getLogger(__name__)


class MCPTool:
    """Represents an MCP tool definition and handler."""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable,
    ):
        """Initialize MCP tool."""
        self.name = name
        self.description = description
        self.parameters = parameters
        self.handler = handler

    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary format."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": self.parameters.get("properties", {}),
                "required": self.parameters.get("required", []),
            },
        }


class MCPServer:
    """MCP Server providing AI agent tools."""

    def __init__(self):
        """Initialize MCP server."""
        self.tools: Dict[str, MCPTool] = {}
        self._register_tools()
        logger.info("MCP Server initialized with tools")

    def _register_tools(self) -> None:
        """Register all available tools."""
        # Search snippets
        self.register_tool(
            MCPTool(
                name="search_snippets",
                description="Search snippets by query",
                parameters={
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query",
                            "minLength": 1,
                            "maxLength": 500,
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results",
                            "default": 20,
                            "minimum": 1,
                            "maximum": 100,
                        },
                    },
                    "required": ["query"],
                },
                handler=self._search_snippets,
            )
        )

        # Get single snippet
        self.register_tool(
            MCPTool(
                name="get_snippet",
                description="Get snippet by ID",
                parameters={
                    "properties": {
                        "snippet_id": {
                            "type": "string",
                            "description": "Snippet ID",
                        },
                    },
                    "required": ["snippet_id"],
                },
                handler=self._get_snippet,
            )
        )

        # List snippets
        self.register_tool(
            MCPTool(
                name="list_snippets",
                description="List all snippets",
                parameters={
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Max results",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 100,
                        },
                        "offset": {
                            "type": "integer",
                            "description": "Offset for pagination",
                            "default": 0,
                            "minimum": 0,
                        },
                    },
                    "required": [],
                },
                handler=self._list_snippets,
            )
        )

        # Create snippet
        self.register_tool(
            MCPTool(
                name="create_snippet",
                description="Create a new snippet",
                parameters={
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Snippet title",
                            "minLength": 1,
                            "maxLength": 255,
                        },
                        "body": {
                            "type": "string",
                            "description": "Snippet content",
                            "minLength": 1,
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language",
                            "default": "plaintext",
                        },
                        "source": {
                            "type": "string",
                            "description": "Source of snippet",
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tag names",
                            "default": [],
                        },
                    },
                    "required": ["title", "body"],
                },
                handler=self._create_snippet,
            )
        )

        # List collections
        self.register_tool(
            MCPTool(
                name="list_collections",
                description="List all collections",
                parameters={
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Max results",
                            "default": 100,
                            "minimum": 1,
                            "maximum": 1000,
                        },
                    },
                    "required": [],
                },
                handler=self._list_collections,
            )
        )

        # List tags
        self.register_tool(
            MCPTool(
                name="list_tags",
                description="List all tags with counts",
                parameters={
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Max results",
                            "default": 100,
                            "minimum": 1,
                            "maximum": 1000,
                        },
                    },
                    "required": [],
                },
                handler=self._list_tags,
            )
        )

    def register_tool(self, tool: MCPTool) -> None:
        """Register a tool."""
        self.tools[tool.name] = tool
        logger.info(f"Registered MCP tool: {tool.name}")

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get all tools as dictionaries."""
        return [tool.to_dict() for tool in self.tools.values()]

    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Call a tool by name."""
        if tool_name not in self.tools:
            return {
                "status": "error",
                "error": f"Unknown tool: {tool_name}",
            }

        tool = self.tools[tool_name]
        try:
            result = await tool.handler(**kwargs)
            return {
                "status": "success",
                "data": result,
            }
        except ValueError as e:
            logger.warning(f"Tool {tool_name} validation error: {e}")
            return {
                "status": "error",
                "error": str(e),
            }
        except Exception as e:
            logger.error(f"Tool {tool_name} error: {e}", exc_info=True)
            return {
                "status": "error",
                "error": "Internal server error",
            }

    async def _search_snippets(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search snippets."""
        db = SessionLocal()
        try:
            snippets, _ = SnippetService.search_snippets(db, query=query, limit=limit)
            return [
                {
                    "id": s.id,
                    "title": s.title,
                    "body": s.body[:200],  # Preview
                    "language": s.language,
                    "created_at": s.created_at.isoformat(),
                }
                for s in snippets
            ]
        finally:
            db.close()

    async def _get_snippet(self, snippet_id: str) -> Dict[str, Any]:
        """Get snippet by ID."""
        db = SessionLocal()
        try:
            snippet = SnippetService.get_snippet(db, snippet_id)
            if not snippet:
                raise ValueError(f"Snippet not found: {snippet_id}")

            return {
                "id": snippet.id,
                "title": snippet.title,
                "body": snippet.body,
                "language": snippet.language,
                "source": snippet.source,
                "tags": [{"id": t.id, "name": t.name} for t in snippet.tags],
                "collections": [{"id": c.id, "name": c.name} for c in snippet.collections],
                "created_at": snippet.created_at.isoformat(),
            }
        finally:
            db.close()

    async def _list_snippets(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """List snippets."""
        db = SessionLocal()
        try:
            snippets, total = SnippetService.list_snippets(db, limit=limit, offset=offset)
            return [
                {
                    "id": s.id,
                    "title": s.title,
                    "body": s.body[:100],  # Preview
                    "language": s.language,
                    "created_at": s.created_at.isoformat(),
                }
                for s in snippets
            ]
        finally:
            db.close()

    async def _create_snippet(
        self,
        title: str,
        body: str,
        language: str = "plaintext",
        source: str = None,
        tags: List[str] = None,
    ) -> Dict[str, Any]:
        """Create snippet."""
        db = SessionLocal()
        try:
            # Create snippet
            snippet_create = SnippetCreate(
                title=title,
                body=body,
                language=language,
                source=source,
            )
            snippet = SnippetService.create_snippet(db, snippet_create)

            # Add tags if provided
            if tags:
                for tag_name in tags:
                    try:
                        TagService.create_tag(db, name=tag_name)
                    except ValueError:
                        pass  # Tag already exists

            return {
                "id": snippet.id,
                "title": snippet.title,
                "language": snippet.language,
                "created_at": snippet.created_at.isoformat(),
            }
        finally:
            db.close()

    async def _list_collections(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List collections."""
        db = SessionLocal()
        try:
            collections, _ = CollectionService.list_collections(db, limit=limit)
            return collections
        finally:
            db.close()

    async def _list_tags(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List tags."""
        db = SessionLocal()
        try:
            tags, _ = TagService.list_tags(db, limit=limit)
            return tags
        finally:
            db.close()


# Global MCP server instance
mcp_server = MCPServer()
