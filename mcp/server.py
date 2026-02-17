"""MCP (Model Context Protocol) Server for Pin-Up AI.

Exposes the user's snippet library to AI agents via stdio JSON-RPC.
Uses the same SQLite database as the backend.  Pro-tier feature.

Protocol: JSON-RPC 2.0 over stdin/stdout (MCP transport=stdio).
"""

import json
import logging
import os
import sys
from typing import Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.services import snippet_service, tag_service, collection_service, search_service

logger = logging.getLogger(__name__)

# ── Tool registry ────────────────────────────────────────────────────────
TOOLS = [
    {
        "name": "search_snippets",
        "description": "Search the user's snippet library using full-text search.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query (FTS5 syntax supported)", "minLength": 1},
                "limit": {"type": "integer", "description": "Max results (default 10)", "default": 10, "minimum": 1, "maximum": 100},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_snippet",
        "description": "Get a single snippet by ID with full content.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "snippet_id": {"type": "string", "description": "The snippet UUID"},
            },
            "required": ["snippet_id"],
        },
    },
    {
        "name": "list_snippets",
        "description": "List snippets with optional filtering.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 20, "minimum": 1, "maximum": 100},
                "offset": {"type": "integer", "default": 0, "minimum": 0},
                "tag": {"type": "string", "description": "Filter by tag name"},
                "source": {"type": "string", "description": "Filter by source"},
            },
            "required": [],
        },
    },
    {
        "name": "create_snippet",
        "description": "Create a new snippet in the user's library.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Snippet title", "maxLength": 255},
                "body": {"type": "string", "description": "Snippet content", "minLength": 1},
                "language": {"type": "string", "description": "Programming language", "default": "plaintext"},
                "source": {"type": "string", "description": "Source of snippet (e.g. 'claude', 'chatgpt')"},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Tag names to apply"},
                "collections": {"type": "array", "items": {"type": "string"}, "description": "Collection names to add to"},
            },
            "required": ["body"],
        },
    },
    {
        "name": "list_tags",
        "description": "List all tags with snippet counts.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "list_collections",
        "description": "List all collections with snippet counts.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
]


# ── Serialization helpers ────────────────────────────────────────────────
def _serialize_snippet(s) -> dict:
    """Convert ORM Snippet to JSON-safe dict."""
    return {
        "id": s.id,
        "title": s.title,
        "body": s.body,
        "language": s.language,
        "source": s.source,
        "source_url": s.source_url,
        "pinned": bool(s.pinned),
        "archived": bool(s.archived),
        "created_at": s.created_at,
        "updated_at": s.updated_at,
        "tags": [{"id": t.id, "name": t.name, "color": t.color} for t in (s.tags or [])],
        "collections": [{"id": c.id, "name": c.name, "description": c.description} for c in (s.collections or [])],
    }


# ── Tool handlers ────────────────────────────────────────────────────────
def _handle_search_snippets(args: dict) -> list[dict]:
    query = args["query"]
    limit = args.get("limit", 10)
    db: Session = SessionLocal()
    try:
        results, total = search_service.search(db, q=query, limit=limit)
        return results
    finally:
        db.close()


def _handle_get_snippet(args: dict) -> dict:
    snippet_id = args["snippet_id"]
    db: Session = SessionLocal()
    try:
        s = snippet_service.get_snippet(db, snippet_id)
        if not s:
            return {"error": f"Snippet not found: {snippet_id}"}
        return _serialize_snippet(s)
    finally:
        db.close()


def _handle_list_snippets(args: dict) -> dict:
    limit = args.get("limit", 20)
    offset = args.get("offset", 0)
    db: Session = SessionLocal()
    try:
        # If tag filter supplied, resolve tag_id
        tag_id = None
        if args.get("tag"):
            tags = tag_service.list_tags(db)
            for t in tags:
                if t["name"].lower() == args["tag"].lower():
                    tag_id = t["id"]
                    break

        items, total = snippet_service.list_snippets(
            db, limit=limit, offset=offset, tag_id=tag_id,
        )
        return {"snippets": [_serialize_snippet(s) for s in items], "total": total}
    finally:
        db.close()


def _handle_create_snippet(args: dict) -> dict:
    db: Session = SessionLocal()
    try:
        data = {
            "body": args["body"],
            "title": args.get("title"),
            "language": args.get("language"),
            "source": args.get("source", "mcp"),
            "tags": args.get("tags", []),
            "collections": args.get("collections", []),
        }
        s = snippet_service.create_snippet(db, data)
        return {"id": s.id, "title": s.title, "created_at": s.created_at}
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


def _handle_list_tags(args: dict) -> list[dict]:
    db: Session = SessionLocal()
    try:
        return tag_service.list_tags(db)
    finally:
        db.close()


def _handle_list_collections(args: dict) -> list[dict]:
    db: Session = SessionLocal()
    try:
        return collection_service.list_collections(db)
    finally:
        db.close()


_HANDLERS = {
    "search_snippets": _handle_search_snippets,
    "get_snippet": _handle_get_snippet,
    "list_snippets": _handle_list_snippets,
    "create_snippet": _handle_create_snippet,
    "list_tags": _handle_list_tags,
    "list_collections": _handle_list_collections,
}


# ── MCP Stdio Server ────────────────────────────────────────────────────
class MCPStdioServer:
    """Minimal MCP server using stdio JSON-RPC 2.0 transport."""

    def __init__(self):
        self.server_info = {
            "name": "pinup-ai",
            "version": "1.0.0",
        }
        self.capabilities = {
            "tools": {},
        }

    def _respond(self, id: Any, result: Any) -> None:
        """Write a JSON-RPC success response to stdout."""
        msg = {"jsonrpc": "2.0", "id": id, "result": result}
        out = json.dumps(msg)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()

    def _error(self, id: Any, code: int, message: str) -> None:
        """Write a JSON-RPC error response to stdout."""
        msg = {"jsonrpc": "2.0", "id": id, "error": {"code": code, "message": message}}
        out = json.dumps(msg)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()

    def handle_request(self, req: dict) -> None:
        """Process a single JSON-RPC request."""
        method = req.get("method", "")
        id_ = req.get("id")
        params = req.get("params", {})

        if method == "initialize":
            self._respond(id_, {
                "protocolVersion": "2024-11-05",
                "serverInfo": self.server_info,
                "capabilities": self.capabilities,
            })
        elif method == "notifications/initialized":
            pass  # no response needed
        elif method == "tools/list":
            self._respond(id_, {"tools": TOOLS})
        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            handler = _HANDLERS.get(tool_name)
            if not handler:
                self._error(id_, -32601, f"Unknown tool: {tool_name}")
                return
            try:
                result = handler(arguments)
                self._respond(id_, {
                    "content": [{"type": "text", "text": json.dumps(result, default=str)}],
                })
            except Exception as e:
                logger.error("Tool %s error: %s", tool_name, e, exc_info=True)
                self._respond(id_, {
                    "content": [{"type": "text", "text": json.dumps({"error": str(e)})}],
                    "isError": True,
                })
        else:
            if id_ is not None:
                self._error(id_, -32601, f"Method not found: {method}")

    def run(self) -> None:
        """Main loop: read JSON-RPC from stdin, respond on stdout."""
        init_db()
        logger.info("Pin-Up AI MCP server started (stdio)")
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                self.handle_request(req)
            except json.JSONDecodeError:
                self._error(None, -32700, "Parse error")
            except Exception as e:
                logger.error("Unhandled error: %s", e, exc_info=True)
                self._error(None, -32603, "Internal error")


# ── Entry point ──────────────────────────────────────────────────────────
def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(message)s",
        stream=sys.stderr,  # Logs go to stderr, protocol goes to stdout
    )
    server = MCPStdioServer()
    server.run()


if __name__ == "__main__":
    main()

