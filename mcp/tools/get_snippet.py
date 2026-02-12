from typing import Any


def get_snippet(payload: dict[str, Any]) -> dict[str, Any]:
    snippet_id = payload.get("id")
    return {"snippet": None, "id": snippet_id}
