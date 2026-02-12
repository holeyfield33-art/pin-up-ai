import os
from typing import Any

from tools.get_snippet import get_snippet
from tools.list_collections import list_collections
from tools.search_snippets import search_snippets


def handle_request(request: dict[str, Any]) -> dict[str, Any]:
    name = request.get("tool")
    payload = request.get("input", {})

    if name == "search_snippets":
        return search_snippets(payload)
    if name == "get_snippet":
        return get_snippet(payload)
    if name == "list_collections":
        return list_collections(payload)

    return {"error": f"Unknown tool: {name}"}


if __name__ == "__main__":
    print("MCP server placeholder")
    print(f"PORT={os.getenv('MCP_PORT', 'not-set')}")
