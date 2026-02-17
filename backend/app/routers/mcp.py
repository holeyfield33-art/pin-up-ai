"""MCP HTTP router — exposes MCP tool definitions and invocations via REST.

GET  /api/mcp/tools             → list available tools with schemas
POST /api/mcp/tools/{name}/call → invoke a tool by name
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, ConfigDict
from typing import Any

from app.database import get_db
from sqlalchemy.orm import Session
from app.services import snippet_service, tag_service, collection_service, search_service

router = APIRouter(prefix="/mcp", tags=["mcp"])

# ── Tool definitions (mirrors mcp/server.py) ────────────────────────────
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
                "language": {"type": "string", "description": "Programming language"},
                "source": {"type": "string", "description": "Source of snippet"},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Tag names to apply"},
                "collections": {"type": "array", "items": {"type": "string"}, "description": "Collection names"},
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


class ToolCallRequest(BaseModel):
    """Request body for invoking a tool."""
    model_config = ConfigDict(extra="allow")


# ── Serialization helper ─────────────────────────────────────────────────
def _serialize_snippet(s) -> dict:
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
        "collections": [
            {"id": c.id, "name": c.name, "description": c.description, "icon": c.icon, "color": c.color}
            for c in (s.collections or [])
        ],
    }


# ── Tool handlers ────────────────────────────────────────────────────────
def _handle_search_snippets(args: dict, db: Session) -> Any:
    results, total = search_service.search(db, q=args["query"], limit=args.get("limit", 10))
    return results


def _handle_get_snippet(args: dict, db: Session) -> Any:
    s = snippet_service.get_snippet(db, args["snippet_id"])
    if not s:
        raise HTTPException(status_code=404, detail=f"Snippet not found: {args['snippet_id']}")
    return _serialize_snippet(s)


def _handle_list_snippets(args: dict, db: Session) -> Any:
    limit = args.get("limit", 20)
    offset = args.get("offset", 0)
    tag_id = None
    if args.get("tag"):
        tags = tag_service.list_tags(db)
        for t in tags:
            if t["name"].lower() == args["tag"].lower():
                tag_id = t["id"]
                break
    items, total = snippet_service.list_snippets(db, limit=limit, offset=offset, tag_id=tag_id)
    return {"snippets": [_serialize_snippet(s) for s in items], "total": total}


def _handle_create_snippet(args: dict, db: Session) -> Any:
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


def _handle_list_tags(args: dict, db: Session) -> Any:
    return tag_service.list_tags(db)


def _handle_list_collections(args: dict, db: Session) -> Any:
    return collection_service.list_collections(db)


_HANDLERS = {
    "search_snippets": _handle_search_snippets,
    "get_snippet": _handle_get_snippet,
    "list_snippets": _handle_list_snippets,
    "create_snippet": _handle_create_snippet,
    "list_tags": _handle_list_tags,
    "list_collections": _handle_list_collections,
}


# ── Routes ───────────────────────────────────────────────────────────────
@router.get("/tools")
def list_tools():
    """Return all available MCP tool definitions."""
    return {"tools": TOOLS}


@router.post("/tools/{tool_name}/call")
def call_tool(tool_name: str, body: dict = {}, db: Session = Depends(get_db)):
    """Invoke an MCP tool by name with arguments from the request body."""
    handler = _HANDLERS.get(tool_name)
    if not handler:
        raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_name}")
    try:
        result = handler(body, db)
        return {"status": "success", "data": result}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
