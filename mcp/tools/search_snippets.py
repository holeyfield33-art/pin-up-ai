from typing import Any


def search_snippets(payload: dict[str, Any]) -> dict[str, Any]:
    query = payload.get("query", "")
    return {"results": [], "query": query}
