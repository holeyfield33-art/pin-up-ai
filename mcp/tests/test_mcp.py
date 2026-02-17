"""Tests for MCP server — all 6 tool handlers + protocol envelope."""

import json
import os
import sys
import tempfile
from io import StringIO

import pytest

# Point to a fresh test DB
_test_db = os.path.join(tempfile.mkdtemp(), "mcp_test.db")
os.environ["PINUP_DB"] = _test_db
os.environ["PINUP_LOG_LEVEL"] = "WARNING"

# Ensure backend is importable
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend"))

from app.database import init_db, SessionLocal  # noqa: E402
from mcp.server import MCPStdioServer, _HANDLERS, TOOLS  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    """Initialize DB and seed some data."""
    init_db()
    db = SessionLocal()
    try:
        from app.services import snippet_service, tag_service, collection_service

        # Seed tags and collections
        tag_service.create_tag(db, "python")
        tag_service.create_tag(db, "javascript")
        collection_service.create_collection(db, "tutorials", "Tutorial snippets")

        # Seed snippets
        snippet_service.create_snippet(db, {
            "title": "Hello World Python",
            "body": "```python\nprint('Hello, World!')\n```",
            "language": "python",
            "source": "claude",
            "tags": ["python"],
            "collections": ["tutorials"],
        })
        snippet_service.create_snippet(db, {
            "title": "JS Arrow Function",
            "body": "const greet = (name) => `Hello, ${name}`;",
            "language": "javascript",
            "source": "chatgpt",
            "tags": ["javascript"],
        })
        snippet_service.create_snippet(db, {
            "title": "Sorting Algorithm",
            "body": "def quicksort(arr):\n    if len(arr) <= 1: return arr\n    pivot = arr[0]\n    return quicksort([x for x in arr[1:] if x < pivot]) + [pivot] + quicksort([x for x in arr[1:] if x >= pivot])",
            "language": "python",
            "source": "claude",
            "tags": ["python"],
            "collections": ["tutorials"],
        })
    finally:
        db.close()
    yield


@pytest.fixture()
def server():
    """Fresh MCP server instance."""
    return MCPStdioServer()


@pytest.fixture()
def db():
    """DB session for direct verification."""
    session = SessionLocal()
    yield session
    session.close()


# ── Helpers ──────────────────────────────────────────────────────────────
def capture_response(server: MCPStdioServer, req: dict) -> dict:
    """Call handle_request and capture the JSON response from stdout."""
    old_stdout = sys.stdout
    sys.stdout = buf = StringIO()
    try:
        server.handle_request(req)
    finally:
        sys.stdout = old_stdout
    raw = buf.getvalue().strip()
    if not raw:
        return None  # notification — no response
    return json.loads(raw)


# ── Protocol tests ──────────────────────────────────────────────────────
class TestProtocol:
    def test_initialize(self, server):
        resp = capture_response(server, {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {},
        })
        assert resp["jsonrpc"] == "2.0"
        assert resp["id"] == 1
        result = resp["result"]
        assert result["protocolVersion"] == "2024-11-05"
        assert result["serverInfo"]["name"] == "pinup-ai"
        assert result["serverInfo"]["version"] == "1.0.0"
        assert "tools" in result["capabilities"]

    def test_notifications_initialized(self, server):
        """notifications/initialized should produce no output."""
        resp = capture_response(server, {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        })
        assert resp is None

    def test_tools_list(self, server):
        resp = capture_response(server, {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        })
        tools = resp["result"]["tools"]
        assert len(tools) == 6
        names = {t["name"] for t in tools}
        assert names == {
            "search_snippets", "get_snippet", "list_snippets",
            "create_snippet", "list_tags", "list_collections",
        }
        # All tools must have inputSchema
        for t in tools:
            assert "inputSchema" in t
            assert t["inputSchema"]["type"] == "object"

    def test_unknown_tool(self, server):
        resp = capture_response(server, {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "nonexistent_tool", "arguments": {}},
        })
        assert "error" in resp
        assert resp["error"]["code"] == -32601

    def test_unknown_method(self, server):
        resp = capture_response(server, {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "unknown/method",
        })
        assert "error" in resp
        assert resp["error"]["code"] == -32601


# ── search_snippets ─────────────────────────────────────────────────────
class TestSearchSnippets:
    def test_search_returns_results(self, server):
        resp = capture_response(server, {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {"name": "search_snippets", "arguments": {"query": "python"}},
        })
        content = resp["result"]["content"]
        assert len(content) == 1
        assert content[0]["type"] == "text"
        data = json.loads(content[0]["text"])
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_search_with_limit(self, server):
        resp = capture_response(server, {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {"name": "search_snippets", "arguments": {"query": "python", "limit": 1}},
        })
        data = json.loads(resp["result"]["content"][0]["text"])
        assert len(data) <= 1

    def test_search_no_results(self, server):
        resp = capture_response(server, {
            "jsonrpc": "2.0",
            "id": 12,
            "method": "tools/call",
            "params": {"name": "search_snippets", "arguments": {"query": "xyznonexistent999"}},
        })
        data = json.loads(resp["result"]["content"][0]["text"])
        assert isinstance(data, list)
        assert len(data) == 0


# ── get_snippet ──────────────────────────────────────────────────────────
class TestGetSnippet:
    def test_get_existing(self, server, db):
        from app.services import snippet_service
        items, _ = snippet_service.list_snippets(db, limit=1)
        sid = items[0].id

        resp = capture_response(server, {
            "jsonrpc": "2.0",
            "id": 20,
            "method": "tools/call",
            "params": {"name": "get_snippet", "arguments": {"snippet_id": sid}},
        })
        data = json.loads(resp["result"]["content"][0]["text"])
        assert data["id"] == sid
        assert "title" in data
        assert "body" in data
        assert "tags" in data
        assert "collections" in data

    def test_get_not_found(self, server):
        resp = capture_response(server, {
            "jsonrpc": "2.0",
            "id": 21,
            "method": "tools/call",
            "params": {"name": "get_snippet", "arguments": {"snippet_id": "does-not-exist"}},
        })
        data = json.loads(resp["result"]["content"][0]["text"])
        assert "error" in data


# ── list_snippets ────────────────────────────────────────────────────────
class TestListSnippets:
    def test_list_all(self, server):
        resp = capture_response(server, {
            "jsonrpc": "2.0",
            "id": 30,
            "method": "tools/call",
            "params": {"name": "list_snippets", "arguments": {}},
        })
        data = json.loads(resp["result"]["content"][0]["text"])
        assert "snippets" in data
        assert "total" in data
        assert data["total"] >= 3

    def test_list_with_pagination(self, server):
        resp = capture_response(server, {
            "jsonrpc": "2.0",
            "id": 31,
            "method": "tools/call",
            "params": {"name": "list_snippets", "arguments": {"limit": 1, "offset": 0}},
        })
        data = json.loads(resp["result"]["content"][0]["text"])
        assert len(data["snippets"]) == 1
        assert data["total"] >= 3

    def test_list_filter_by_tag(self, server):
        resp = capture_response(server, {
            "jsonrpc": "2.0",
            "id": 32,
            "method": "tools/call",
            "params": {"name": "list_snippets", "arguments": {"tag": "javascript"}},
        })
        data = json.loads(resp["result"]["content"][0]["text"])
        assert data["total"] >= 1
        for s in data["snippets"]:
            tag_names = [t["name"] for t in s["tags"]]
            assert "javascript" in tag_names


# ── create_snippet ───────────────────────────────────────────────────────
class TestCreateSnippet:
    def test_create_minimal(self, server):
        resp = capture_response(server, {
            "jsonrpc": "2.0",
            "id": 40,
            "method": "tools/call",
            "params": {
                "name": "create_snippet",
                "arguments": {"body": "Created via MCP test"},
            },
        })
        data = json.loads(resp["result"]["content"][0]["text"])
        assert "id" in data
        assert data["created_at"] > 0

    def test_create_full(self, server):
        resp = capture_response(server, {
            "jsonrpc": "2.0",
            "id": 41,
            "method": "tools/call",
            "params": {
                "name": "create_snippet",
                "arguments": {
                    "title": "MCP Full Snippet",
                    "body": "Full snippet body with all fields",
                    "language": "markdown",
                    "source": "mcp-test",
                    "tags": ["mcp-test-tag"],
                    "collections": ["mcp-test-col"],
                },
            },
        })
        data = json.loads(resp["result"]["content"][0]["text"])
        assert "id" in data
        assert data["title"] == "MCP Full Snippet"

    def test_create_and_verify(self, server, db):
        """Create via MCP then verify via DB."""
        resp = capture_response(server, {
            "jsonrpc": "2.0",
            "id": 42,
            "method": "tools/call",
            "params": {
                "name": "create_snippet",
                "arguments": {"body": "verify_mcp_create_12345", "source": "mcp"},
            },
        })
        data = json.loads(resp["result"]["content"][0]["text"])
        sid = data["id"]

        from app.services import snippet_service
        s = snippet_service.get_snippet(db, sid)
        assert s is not None
        assert s.body == "verify_mcp_create_12345"
        assert s.source == "mcp"


# ── list_tags ────────────────────────────────────────────────────────────
class TestListTags:
    def test_list_tags(self, server):
        resp = capture_response(server, {
            "jsonrpc": "2.0",
            "id": 50,
            "method": "tools/call",
            "params": {"name": "list_tags", "arguments": {}},
        })
        data = json.loads(resp["result"]["content"][0]["text"])
        assert isinstance(data, list)
        assert len(data) >= 2
        # Each tag should have name
        names = {t["name"] for t in data}
        assert "python" in names
        assert "javascript" in names


# ── list_collections ─────────────────────────────────────────────────────
class TestListCollections:
    def test_list_collections(self, server):
        resp = capture_response(server, {
            "jsonrpc": "2.0",
            "id": 60,
            "method": "tools/call",
            "params": {"name": "list_collections", "arguments": {}},
        })
        data = json.loads(resp["result"]["content"][0]["text"])
        assert isinstance(data, list)
        assert len(data) >= 1
        names = {c["name"] for c in data}
        assert "tutorials" in names


# ── Tool registry validation ────────────────────────────────────────────
class TestToolRegistry:
    def test_all_tools_have_handlers(self):
        """Every registered tool must have a handler."""
        for tool in TOOLS:
            assert tool["name"] in _HANDLERS, f"Missing handler for {tool['name']}"

    def test_all_handlers_have_tools(self):
        """Every handler must be in the tool registry."""
        tool_names = {t["name"] for t in TOOLS}
        for handler_name in _HANDLERS:
            assert handler_name in tool_names, f"Handler {handler_name} not in TOOLS"

    def test_tool_schemas_valid(self):
        """All tool schemas have required fields."""
        for tool in TOOLS:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            schema = tool["inputSchema"]
            assert schema["type"] == "object"
            assert "properties" in schema
            assert "required" in schema
