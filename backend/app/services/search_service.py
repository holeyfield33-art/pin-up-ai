"""Search service — FTS5 + DSL parser per search-spec.md."""

import logging
import re
import shlex
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


@dataclass
class ParsedQuery:
    """Result of DSL parsing."""
    fts_terms: str = ""
    tag_names: list[str] = field(default_factory=list)
    collection_names: list[str] = field(default_factory=list)
    source: Optional[str] = None
    language: Optional[str] = None
    pinned: Optional[bool] = None
    archived: Optional[bool] = None


_FILTER_RE = re.compile(
    r"(tag|collection|source|language|pinned|archived):(\S+)", re.IGNORECASE
)


def parse_query(q: str) -> ParsedQuery:
    """Parse a search-spec.md DSL query string.

    Filters:
      tag:<name>  collection:<name>  source:<name>  language:<name>
      pinned:true|false  archived:true|false
    Everything else → FTS MATCH terms.  Quoted phrases preserved.
    """
    result = ParsedQuery()

    # Extract filters first
    remainder = q
    for m in _FILTER_RE.finditer(q):
        key = m.group(1).lower()
        val = m.group(2).strip().strip('"').strip("'")
        if key == "tag":
            result.tag_names.append(val.lower())
        elif key == "collection":
            result.collection_names.append(val)
        elif key == "source":
            result.source = val
        elif key == "language":
            result.language = val.lower()
        elif key == "pinned":
            result.pinned = val.lower() in ("true", "1", "yes")
        elif key == "archived":
            result.archived = val.lower() in ("true", "1", "yes")
        remainder = remainder.replace(m.group(0), "", 1)

    # Remaining text → FTS terms (preserve quoted phrases)
    remainder = remainder.strip()
    if remainder:
        # Clean up multiple spaces
        result.fts_terms = " ".join(remainder.split())

    return result


def search(
    db: Session,
    q: str,
    limit: int = 50,
    offset: int = 0,
    sort: str = "relevance",
) -> tuple[list[dict], int]:
    """Execute a search query and return (results, total)."""
    parsed = parse_query(q)

    # Build SQL dynamically
    params: dict = {}
    joins: list[str] = []
    wheres: list[str] = ["1=1"]

    # FTS match
    if parsed.fts_terms:
        # Use snippets_fts
        joins.append("JOIN snippets_fts fts ON fts.snippet_id = s.id")
        # Sanitize for FTS5 — escape special chars
        safe_q = parsed.fts_terms.replace('"', '""')
        # If it looks like it has a quoted phrase, keep it; else join with *
        if '"' in parsed.fts_terms:
            params["fts_q"] = safe_q
        else:
            # Add implicit prefix matching for better UX
            words = safe_q.split()
            terms = " ".join(w for w in words if w)
            params["fts_q"] = terms
        wheres.append("snippets_fts MATCH :fts_q")

    # Tag filter
    for i, tname in enumerate(parsed.tag_names):
        alias = f"st{i}"
        talias = f"t{i}"
        joins.append(f"JOIN snippet_tags {alias} ON {alias}.snippet_id = s.id")
        joins.append(f"JOIN tags {talias} ON {talias}.id = {alias}.tag_id")
        pkey = f"tname_{i}"
        wheres.append(f"LOWER({talias}.name) = :{pkey}")
        params[pkey] = tname.lower()

    # Collection filter
    for i, cname in enumerate(parsed.collection_names):
        alias = f"sc{i}"
        calias = f"c{i}"
        joins.append(f"JOIN snippet_collections {alias} ON {alias}.snippet_id = s.id")
        joins.append(f"JOIN collections {calias} ON {calias}.id = {alias}.collection_id")
        pkey = f"cname_{i}"
        wheres.append(f"LOWER({calias}.name) = :{pkey}")
        params[pkey] = cname.lower()

    # Source filter
    if parsed.source:
        wheres.append("LOWER(s.source) = :source_f")
        params["source_f"] = parsed.source.lower()

    # Language filter
    if parsed.language:
        wheres.append("LOWER(s.language) = :lang_f")
        params["lang_f"] = parsed.language.lower()

    # Pinned / Archived
    if parsed.pinned is not None:
        wheres.append("s.pinned = :pinned_f")
        params["pinned_f"] = 1 if parsed.pinned else 0

    if parsed.archived is not None:
        wheres.append("s.archived = :archived_f")
        params["archived_f"] = 1 if parsed.archived else 0
    else:
        wheres.append("s.archived = 0")

    join_sql = "\n".join(joins)
    where_sql = " AND ".join(wheres)

    # Sort
    if sort == "newest":
        order_sql = "s.created_at DESC"
    elif sort == "pinned":
        order_sql = "s.pinned DESC, s.updated_at DESC"
    else:  # relevance
        if parsed.fts_terms:
            order_sql = "bm25(snippets_fts), s.created_at DESC"
        else:
            order_sql = "s.created_at DESC"

    # Count
    count_sql = f"SELECT COUNT(DISTINCT s.id) FROM snippets s {join_sql} WHERE {where_sql}"
    total = db.execute(text(count_sql), params).scalar() or 0

    # If zero fts terms and no filters matched, just return empty
    if total == 0:
        return [], 0

    # Fetch
    select_sql = (
        f"SELECT DISTINCT s.id, s.title, s.body, s.language, s.source, "
        f"s.source_url, s.pinned, s.archived, s.created_at, s.updated_at "
        f"FROM snippets s {join_sql} "
        f"WHERE {where_sql} "
        f"ORDER BY {order_sql} "
        f"LIMIT :lim OFFSET :off"
    )
    params["lim"] = limit
    params["off"] = offset

    rows = db.execute(text(select_sql), params).fetchall()

    results = []
    for row in rows:
        sid = row[0]
        # Get tag names
        tag_rows = db.execute(
            text("SELECT t.name FROM snippet_tags st JOIN tags t ON t.id=st.tag_id WHERE st.snippet_id=:sid"),
            {"sid": sid},
        ).fetchall()
        # Get collection names
        col_rows = db.execute(
            text("SELECT c.name FROM snippet_collections sc JOIN collections c ON c.id=sc.collection_id WHERE sc.snippet_id=:sid"),
            {"sid": sid},
        ).fetchall()

        body = row[2] or ""
        preview = body[:200].replace("\n", " ")

        results.append({
            "id": sid,
            "title": row[1],
            "preview": preview,
            "tags": [r[0] for r in tag_rows],
            "collections": [r[0] for r in col_rows],
            "source": row[4],
            "language": row[3],
            "created_at": row[8],
            "updated_at": row[9],
        })

    return results, total
