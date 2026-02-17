"""Comprehensive backend tests: CRUD, search, export/import, auth, license."""

import hashlib
import json
import os
import tempfile

import pytest
from fastapi.testclient import TestClient

# Set test DB before importing app
_test_db = os.path.join(tempfile.mkdtemp(), "test.db")
os.environ["PINUP_DB"] = _test_db
os.environ["PINUP_LOG_LEVEL"] = "WARNING"

from app.main import app  # noqa: E402

TOKEN = ""


@pytest.fixture(scope="module", autouse=True)
def setup():
    """Trigger app lifespan and extract token."""
    global TOKEN
    import sqlite3
    # Create a known token
    token = "test-token-abc123"
    h = hashlib.sha256(token.encode()).hexdigest()

    with TestClient(app) as client:
        # The lifespan creates the DB and token; override with our known one
        import sqlite3 as s3
        conn = s3.connect(_test_db)
        conn.execute("UPDATE settings SET value=? WHERE key='install_token_hash'", (h,))
        conn.commit()
        conn.close()

        TOKEN = token
        yield client


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def auth(token=None):
    return {"Authorization": f"Bearer {token or TOKEN}"}


# ──────────────────────────────────────────────────────────────────────
# Health
# ──────────────────────────────────────────────────────────────────────
class TestHealth:
    def test_health_no_auth(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["version"] == "0.1.0"
        assert "db_path" in data
        assert "uptime_ms" in data

    def test_health_ready(self, client):
        r = client.get("/api/health/ready")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ready"
        assert data["database"] == "connected"

    def test_health_live(self, client):
        r = client.get("/api/health/live")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "alive"
        assert "uptime_ms" in data


# ──────────────────────────────────────────────────────────────────────
# Auth
# ──────────────────────────────────────────────────────────────────────
class TestAuth:
    def test_no_token_rejected(self, client):
        r = client.get("/api/snippets")
        assert r.status_code == 401

    def test_bad_token_rejected(self, client):
        r = client.get("/api/snippets", headers={"Authorization": "Bearer wrong"})
        assert r.status_code == 401

    def test_valid_token_accepted(self, client):
        r = client.get("/api/snippets", headers=auth())
        assert r.status_code == 200


# ──────────────────────────────────────────────────────────────────────
# Snippet CRUD
# ──────────────────────────────────────────────────────────────────────
class TestSnippets:
    def test_create_snippet(self, client):
        r = client.post("/api/snippets", json={
            "body": "console.log('Hello');",
            "tags": ["javascript", "test"],
            "collections": ["Demo"],
        }, headers=auth())
        assert r.status_code == 201
        data = r.json()
        assert data["id"]
        assert data["title"]  # auto-inferred
        assert data["body"] == "console.log('Hello');"
        assert len(data["tags"]) == 2
        assert len(data["collections"]) == 1
        assert data["pinned"] == 0
        assert data["archived"] == 0
        assert data["created_at"] > 0

    def test_create_snippet_with_title(self, client):
        r = client.post("/api/snippets", json={
            "title": "My Python Snippet",
            "body": "```python\nprint('hi')\n```",
            "language": "python",
            "tags": ["python"],
        }, headers=auth())
        assert r.status_code == 201
        data = r.json()
        assert data["title"] == "My Python Snippet"
        assert data["language"] == "python"

    def test_list_snippets(self, client):
        r = client.get("/api/snippets", headers=auth())
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 2

    def test_get_snippet(self, client):
        # Create one first
        r = client.post("/api/snippets", json={"body": "test body xyz"}, headers=auth())
        sid = r.json()["id"]

        r = client.get(f"/api/snippets/{sid}", headers=auth())
        assert r.status_code == 200
        assert r.json()["id"] == sid

    def test_get_snippet_not_found(self, client):
        r = client.get("/api/snippets/nonexistent-id", headers=auth())
        assert r.status_code == 404

    def test_patch_snippet(self, client):
        r = client.post("/api/snippets", json={"body": "original body"}, headers=auth())
        sid = r.json()["id"]

        r = client.patch(f"/api/snippets/{sid}", json={
            "title": "Updated Title",
            "body": "updated body",
            "tags": ["updated-tag"],
        }, headers=auth())
        assert r.status_code == 200
        assert r.json()["title"] == "Updated Title"
        assert r.json()["body"] == "updated body"
        assert len(r.json()["tags"]) == 1
        assert r.json()["tags"][0]["name"] == "updated-tag"

    def test_delete_snippet(self, client):
        r = client.post("/api/snippets", json={"body": "to delete"}, headers=auth())
        sid = r.json()["id"]

        r = client.delete(f"/api/snippets/{sid}", headers=auth())
        assert r.status_code == 200
        assert r.json()["ok"] is True

        # Verify gone
        r = client.get(f"/api/snippets/{sid}", headers=auth())
        assert r.status_code == 404

    def test_pin_unpin(self, client):
        r = client.post("/api/snippets", json={"body": "pin me"}, headers=auth())
        sid = r.json()["id"]

        r = client.post(f"/api/snippets/{sid}/pin", headers=auth())
        assert r.status_code == 200
        assert r.json()["pinned"] == 1

        r = client.post(f"/api/snippets/{sid}/unpin", headers=auth())
        assert r.status_code == 200
        assert r.json()["pinned"] == 0

    def test_archive_unarchive(self, client):
        r = client.post("/api/snippets", json={"body": "archive me"}, headers=auth())
        sid = r.json()["id"]

        r = client.post(f"/api/snippets/{sid}/archive", headers=auth())
        assert r.status_code == 200
        assert r.json()["archived"] == 1

        # Archived snippets not in default list
        r = client.get("/api/snippets", headers=auth())
        ids = [s["id"] for s in r.json()["items"]]
        assert sid not in ids

        r = client.post(f"/api/snippets/{sid}/unarchive", headers=auth())
        assert r.status_code == 200
        assert r.json()["archived"] == 0

    def test_list_filter_by_tag(self, client):
        # Create snippet with a unique tag
        r = client.post("/api/snippets", json={
            "body": "filter test", "tags": ["filter-tag-unique"]
        }, headers=auth())
        assert r.status_code == 201
        tag_id = r.json()["tags"][0]["id"]

        r = client.get(f"/api/snippets?tag_id={tag_id}", headers=auth())
        assert r.status_code == 200
        assert r.json()["total"] >= 1

    def test_list_filter_by_collection(self, client):
        r = client.post("/api/snippets", json={
            "body": "collection filter", "collections": ["UniqueCol"]
        }, headers=auth())
        col_id = r.json()["collections"][0]["id"]

        r = client.get(f"/api/snippets?collection_id={col_id}", headers=auth())
        assert r.status_code == 200
        assert r.json()["total"] >= 1


# ──────────────────────────────────────────────────────────────────────
# Tags
# ──────────────────────────────────────────────────────────────────────
class TestTags:
    def test_list_tags(self, client):
        r = client.get("/api/tags", headers=auth())
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert "total" in data

    def test_create_tag(self, client):
        r = client.post("/api/tags", json={"name": "rust", "color": "#FF5733"}, headers=auth())
        assert r.status_code == 201
        assert r.json()["name"] == "rust"
        assert r.json()["color"] == "#FF5733"

    def test_upsert_tag(self, client):
        """Creating same tag name again should return existing one."""
        r1 = client.post("/api/tags", json={"name": "upsert-tag"}, headers=auth())
        r2 = client.post("/api/tags", json={"name": "upsert-tag"}, headers=auth())
        assert r1.json()["id"] == r2.json()["id"]

    def test_patch_tag(self, client):
        r = client.post("/api/tags", json={"name": "to-rename"}, headers=auth())
        tid = r.json()["id"]

        r = client.patch(f"/api/tags/{tid}", json={"name": "renamed"}, headers=auth())
        assert r.status_code == 200
        assert r.json()["name"] == "renamed"

    def test_delete_tag(self, client):
        r = client.post("/api/tags", json={"name": "to-delete"}, headers=auth())
        tid = r.json()["id"]

        r = client.delete(f"/api/tags/{tid}", headers=auth())
        assert r.status_code == 200
        assert r.json()["ok"] is True


# ──────────────────────────────────────────────────────────────────────
# Collections
# ──────────────────────────────────────────────────────────────────────
class TestCollections:
    def test_list_collections(self, client):
        r = client.get("/api/collections", headers=auth())
        assert r.status_code == 200

    def test_create_collection(self, client):
        r = client.post("/api/collections", json={
            "name": "Work", "description": "Work snippets"
        }, headers=auth())
        assert r.status_code == 201
        assert r.json()["name"] == "Work"

    def test_patch_collection(self, client):
        r = client.post("/api/collections", json={"name": "ToRename"}, headers=auth())
        cid = r.json()["id"]

        r = client.patch(f"/api/collections/{cid}", json={"description": "Updated"}, headers=auth())
        assert r.status_code == 200
        assert r.json()["description"] == "Updated"

    def test_delete_collection(self, client):
        r = client.post("/api/collections", json={"name": "ToDelete"}, headers=auth())
        cid = r.json()["id"]

        r = client.delete(f"/api/collections/{cid}", headers=auth())
        assert r.status_code == 200
        assert r.json()["ok"] is True


# ──────────────────────────────────────────────────────────────────────
# Search
# ──────────────────────────────────────────────────────────────────────
class TestSearch:
    def test_basic_search(self, client):
        # Create a snippet to search for
        client.post("/api/snippets", json={
            "body": "unique_search_term_xyz123",
            "tags": ["searchable"],
        }, headers=auth())

        r = client.get("/api/search?q=unique_search_term_xyz123", headers=auth())
        assert r.status_code == 200
        data = r.json()
        assert data["total"] >= 1
        assert "results" in data
        assert data["results"][0]["preview"]

    def test_search_dsl_tag_filter(self, client):
        client.post("/api/snippets", json={
            "body": "DSL tag search body", "tags": ["dsl-test-tag"]
        }, headers=auth())

        r = client.get("/api/search?q=tag:dsl-test-tag DSL", headers=auth())
        assert r.status_code == 200
        assert r.json()["total"] >= 1

    def test_search_empty_query(self, client):
        r = client.get("/api/search?q=nonexistent_xyzabc999", headers=auth())
        assert r.status_code == 200
        assert r.json()["total"] == 0


# ──────────────────────────────────────────────────────────────────────
# Export / Import
# ──────────────────────────────────────────────────────────────────────
class TestExportImport:
    def test_export_json(self, client):
        r = client.post("/api/export", json={"format": "json"}, headers=auth())
        assert r.status_code == 200
        data = r.json()
        assert data["version"] == "1"
        assert len(data["snippets"]) > 0
        assert "tags" in data
        assert "collections" in data

    def test_export_bundle_zip(self, client):
        r = client.post("/api/export", json={"format": "bundle"}, headers=auth())
        assert r.status_code == 200
        assert "application/zip" in r.headers.get("content-type", "")

    def test_import_json(self, client):
        # Export first
        r = client.post("/api/export", json={"format": "json"}, headers=auth())
        export_data = r.json()

        # Modify to avoid ID conflicts
        for s in export_data["snippets"]:
            s["id"] = "import-" + s["id"][:28]
        for st in export_data["snippet_tags"]:
            st["snippet_id"] = "import-" + st["snippet_id"][:28]
        for sc in export_data["snippet_collections"]:
            sc["snippet_id"] = "import-" + sc["snippet_id"][:28]

        # Import
        import io
        content = json.dumps(export_data).encode()
        r = client.post(
            "/api/import",
            files={"file": ("export.json", io.BytesIO(content), "application/json")},
            headers=auth(),
        )
        assert r.status_code == 200
        data = r.json()
        assert data["ok"] is True
        assert data["imported"]["snippets"] > 0


# ──────────────────────────────────────────────────────────────────────
# License
# ──────────────────────────────────────────────────────────────────────
class TestLicense:
    def test_license_status(self, client):
        r = client.get("/api/license/status", headers=auth())
        assert r.status_code == 200
        data = r.json()
        assert data["status"] in ("trial_active", "trial_expired", "licensed_active", "grace_period")
        assert "days_left" in data
        assert "plan" in data

    def test_activate_license(self, client):
        r = client.post("/api/license/activate", json={
            "license_key": "VALID-KEY-12345678"
        }, headers=auth())
        assert r.status_code == 200
        assert r.json()["status"] == "licensed_active"

    def test_deactivate_license(self, client):
        r = client.post("/api/license/deactivate", headers=auth())
        assert r.status_code == 200
        assert r.json()["ok"] is True

    def test_invalid_license_key(self, client):
        r = client.post("/api/license/activate", json={
            "license_key": "short"
        }, headers=auth())
        assert r.status_code == 400


# ──────────────────────────────────────────────────────────────────────
# Stats
# ──────────────────────────────────────────────────────────────────────
class TestStats:
    def test_stats(self, client):
        r = client.get("/api/stats", headers=auth())
        assert r.status_code == 200
        data = r.json()
        assert "totals" in data
        assert data["totals"]["snippets"] > 0
        assert "top_tags" in data
        assert "top_collections" in data
        assert "created_counts" in data
        assert "recent_activity" in data
        assert "vault" in data


# ──────────────────────────────────────────────────────────────────────
# Backup
# ──────────────────────────────────────────────────────────────────────
class TestBackup:
    def test_run_backup(self, client):
        r = client.post("/api/backup/run", headers=auth())
        assert r.status_code == 200
        data = r.json()
        assert "name" in data
        assert data["db_size_bytes"] > 0

    def test_list_backups(self, client):
        # Run one first
        client.post("/api/backup/run", headers=auth())

        r = client.get("/api/backup/list", headers=auth())
        assert r.status_code == 200
        assert len(r.json()["items"]) > 0


# ──────────────────────────────────────────────────────────────────────
# Settings (last because rotate_token invalidates current token)
# ──────────────────────────────────────────────────────────────────────
class TestSettings:
    def test_get_settings(self, client):
        r = client.get("/api/settings", headers=auth())
        assert r.status_code == 200
        data = r.json()
        assert "dedupe_enabled" in data
        assert "backup_schedule" in data

    def test_patch_settings(self, client):
        r = client.patch("/api/settings", json={
            "dedupe_enabled": True, "backup_schedule": "daily"
        }, headers=auth())
        assert r.status_code == 200
        assert r.json()["dedupe_enabled"] is True
        assert r.json()["backup_schedule"] == "daily"

    def test_rotate_token(self, client):
        global TOKEN
        r = client.post("/api/settings/rotate-token", headers=auth())
        assert r.status_code == 200
        new_token = r.json()["token"]
        assert new_token
        TOKEN = new_token

        # Verify old token no longer works (by checking new one does)
        r = client.get("/api/snippets", headers=auth(new_token))
        assert r.status_code == 200


# ──────────────────────────────────────────────────────────────────────
# MCP HTTP
# ──────────────────────────────────────────────────────────────────────
class TestMCPHTTP:
    def test_list_tools(self, client):
        r = client.get("/api/mcp/tools", headers=auth())
        assert r.status_code == 200
        data = r.json()
        assert "tools" in data
        names = [t["name"] for t in data["tools"]]
        assert "search_snippets" in names
        assert "get_snippet" in names
        assert "list_snippets" in names
        assert "create_snippet" in names
        assert "list_tags" in names
        assert "list_collections" in names

    def test_call_list_tags(self, client):
        r = client.post("/api/mcp/tools/list_tags/call", json={}, headers=auth())
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert isinstance(data["data"], list)

    def test_call_list_collections(self, client):
        r = client.post("/api/mcp/tools/list_collections/call", json={}, headers=auth())
        assert r.status_code == 200
        assert r.json()["status"] == "success"

    def test_call_unknown_tool(self, client):
        r = client.post("/api/mcp/tools/nonexistent/call", json={}, headers=auth())
        assert r.status_code == 404

    def test_call_list_snippets(self, client):
        r = client.post("/api/mcp/tools/list_snippets/call", json={"limit": 5}, headers=auth())
        assert r.status_code == 200
        data = r.json()["data"]
        assert "snippets" in data
        assert "total" in data
