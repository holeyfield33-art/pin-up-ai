"""Export service — JSON, Markdown, Bundle per export-import-spec.md."""

import io
import json
import logging
import os
import tempfile
import time
import zipfile
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import Snippet, Tag, Collection
from app.config import settings

logger = logging.getLogger(__name__)


def _snippet_to_export(s: Snippet) -> dict:
    return {
        "id": s.id,
        "title": s.title,
        "body": s.body,
        "language": s.language,
        "source": s.source,
        "source_url": s.source_url,
        "pinned": s.pinned,
        "archived": s.archived,
        "content_hash": s.content_hash,
        "created_at": s.created_at,
        "updated_at": s.updated_at,
    }


def export_json(db: Session, scope: str = "all", ids: Optional[list[str]] = None) -> dict:
    """Build the v1 JSON export structure."""
    snippets_q = db.query(Snippet)
    if scope == "snippet" and ids:
        snippets_q = snippets_q.filter(Snippet.id.in_(ids))
    elif scope == "collection" and ids:
        snippets_q = snippets_q.filter(Snippet.collections.any(Collection.id.in_(ids)))

    snippets = snippets_q.all()
    snippet_ids = {s.id for s in snippets}

    # Tags
    tags = db.query(Tag).all()
    tag_list = [{"id": t.id, "name": t.name, "color": t.color, "created_at": t.created_at} for t in tags]

    # Collections
    collections = db.query(Collection).all()
    col_list = [{"id": c.id, "name": c.name, "description": c.description, "created_at": c.created_at} for c in collections]

    # Joins
    st_rows = db.execute(text("SELECT snippet_id, tag_id FROM snippet_tags")).fetchall()
    sc_rows = db.execute(text("SELECT snippet_id, collection_id FROM snippet_collections")).fetchall()

    snippet_tags_list = [{"snippet_id": r[0], "tag_id": r[1]} for r in st_rows if r[0] in snippet_ids]
    snippet_cols_list = [{"snippet_id": r[0], "collection_id": r[1]} for r in sc_rows if r[0] in snippet_ids]

    return {
        "version": "1",
        "exported_at": int(time.time() * 1000),
        "snippets": [_snippet_to_export(s) for s in snippets],
        "tags": tag_list,
        "collections": col_list,
        "snippet_tags": snippet_tags_list,
        "snippet_collections": snippet_cols_list,
    }


def _snippet_to_markdown(s: Snippet, tag_names: list[str], col_names: list[str]) -> str:
    """Convert snippet to markdown with YAML frontmatter."""
    lines = [
        "---",
        f"id: {s.id}",
        f"title: \"{s.title}\"",
        f"created_at: {s.created_at}",
        f"updated_at: {s.updated_at}",
    ]
    if s.source:
        lines.append(f"source: {s.source}")
    if s.source_url:
        lines.append(f"source_url: {s.source_url}")
    if s.language:
        lines.append(f"language: {s.language}")
    if tag_names:
        lines.append(f"tags: [{', '.join(tag_names)}]")
    if col_names:
        lines.append(f"collections: [{', '.join(col_names)}]")
    lines.append("---")
    lines.append("")
    lines.append(s.body)
    return "\n".join(lines)


def export_bundle(db: Session, scope: str = "all", ids: Optional[list[str]] = None) -> str:
    """Create a .zip bundle and return the file path."""
    json_data = export_json(db, scope, ids)

    # Build tag/collection name lookups
    tag_map = {t["id"]: t["name"] for t in json_data["tags"]}
    col_map = {c["id"]: c["name"] for c in json_data["collections"]}
    snippet_tag_map: dict[str, list[str]] = {}
    snippet_col_map: dict[str, list[str]] = {}
    for st in json_data["snippet_tags"]:
        snippet_tag_map.setdefault(st["snippet_id"], []).append(tag_map.get(st["tag_id"], ""))
    for sc in json_data["snippet_collections"]:
        snippet_col_map.setdefault(sc["snippet_id"], []).append(col_map.get(sc["collection_id"], ""))

    # Write zip
    tmp = tempfile.mktemp(suffix=".zip", prefix="pinup_export_")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
        # manifest
        manifest = {
            "version": "1",
            "exported_at": json_data["exported_at"],
            "counts": {
                "snippets": len(json_data["snippets"]),
                "tags": len(json_data["tags"]),
                "collections": len(json_data["collections"]),
            },
        }
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))
        zf.writestr("data.json", json.dumps(json_data, indent=2))

        # Markdown files
        for s_dict in json_data["snippets"]:
            sid = s_dict["id"]
            tag_names = snippet_tag_map.get(sid, [])
            col_names = snippet_col_map.get(sid, [])
            # Simple Snippet-like object for markdown rendering
            class _S:
                pass
            s = _S()
            for k, v in s_dict.items():
                setattr(s, k, v)
            md = _snippet_to_markdown(s, tag_names, col_names)
            zf.writestr(f"markdown/snippets/{sid}.md", md)

            # Also put into collection folders
            for cn in col_names:
                safe_name = cn.replace("/", "_").replace("\\", "_")
                zf.writestr(f"markdown/collections/{safe_name}/{sid}.md", md)

    return tmp


def export_markdown_zip(db: Session, scope: str = "all", ids: Optional[list[str]] = None) -> str:
    """Export as markdown zip."""
    json_data = export_json(db, scope, ids)
    tag_map = {t["id"]: t["name"] for t in json_data["tags"]}
    col_map = {c["id"]: c["name"] for c in json_data["collections"]}
    snippet_tag_map: dict[str, list[str]] = {}
    snippet_col_map: dict[str, list[str]] = {}
    for st in json_data["snippet_tags"]:
        snippet_tag_map.setdefault(st["snippet_id"], []).append(tag_map.get(st["tag_id"], ""))
    for sc in json_data["snippet_collections"]:
        snippet_col_map.setdefault(sc["snippet_id"], []).append(col_map.get(sc["collection_id"], ""))

    tmp = tempfile.mktemp(suffix=".zip", prefix="pinup_md_export_")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
        for s_dict in json_data["snippets"]:
            sid = s_dict["id"]
            class _S:
                pass
            s = _S()
            for k, v in s_dict.items():
                setattr(s, k, v)
            md = _snippet_to_markdown(s, snippet_tag_map.get(sid, []), snippet_col_map.get(sid, []))
            zf.writestr(f"{sid}.md", md)
    return tmp
