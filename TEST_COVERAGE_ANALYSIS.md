# Test Coverage Analysis

## Current State

The codebase has **zero test coverage**. There are no test files, no testing frameworks installed, and no test configuration anywhere in the project.

| Component | Source Files | Lines of Code | Test Files | Coverage |
|-----------|-------------|--------------|------------|----------|
| Backend (Python) | 6 | ~620 | 0 | 0% |
| Frontend (React) | 6 | ~253 | 0 | 0% |
| MCP Server (Python) | 4 | ~199 | 0 | 0% |

---

## Recommended Test Infrastructure

### Backend: pytest + httpx

Add to `backend/requirements.txt`:
```
pytest
pytest-asyncio
httpx
```

Use FastAPI's `TestClient` (built on httpx) for API integration tests and plain pytest for unit tests.

### Frontend: Vitest + React Testing Library

Add to `frontend/package.json` devDependencies:
```
vitest
@testing-library/react
@testing-library/jest-dom
jsdom
```

Vitest integrates natively with Vite (already used for the build) and avoids the configuration overhead of Jest.

### MCP Server: pytest + pytest-asyncio + respx

Add `pytest`, `pytest-asyncio`, and `respx` (for mocking httpx) to test the async `BackendClient` and tool dispatch logic.

---

## Priority 1 (High) — Backend API Endpoints

These are the most critical tests because the API is the core of the application and is consumed by both the frontend and the MCP server.

### 1.1 Snippet CRUD (`backend/routers/snippets.py`)

| Test Case | Why It Matters |
|-----------|---------------|
| `POST /snippets/` creates a snippet and returns 201 | Core write path — everything depends on snippets being created correctly |
| `GET /snippets/` returns paginated results | Main read path for the UI |
| `GET /snippets/{id}` returns a specific snippet | Used by detail view and MCP `get_snippet` tool |
| `GET /snippets/{id}` returns 404 for missing ID | Validates error handling for invalid lookups |
| `DELETE /snippets/{id}` removes snippet and returns 204 | Ensures cascade deletes work (tags/collections junction tables) |
| `DELETE /snippets/{id}` returns 404 for missing ID | Validates error handling |
| Creating a snippet with `tags` links them in `snippet_tags` | The tag association logic in `create_snippet` (lines 79-83) is not validated anywhere |
| Creating a snippet with `collection_id` links it in `snippet_collections` | The collection association logic (lines 85-89) is untested |
| `GET /snippets/?collection_id=X` filters correctly | Collection filtering uses a JOIN query that could silently break |

### 1.2 Full-Text Search (`backend/routers/snippets.py:132-149`)

| Test Case | Why It Matters |
|-----------|---------------|
| `GET /snippets/search/query?q=term` returns matching snippets | FTS5 is the flagship feature — if the triggers or virtual table break, search silently returns nothing |
| Search respects `limit` and `offset` parameters | Pagination logic in search queries |
| Search with no matches returns empty list (not an error) | Distinguishes "no results" from "search broken" |
| FTS index stays in sync after insert/delete | The FTS triggers (`snippets_ai`, `snippets_ad`, `snippets_au` in `database.py:96-124`) are the most fragile part of the schema — a broken trigger means search silently stops working |

### 1.3 Tags & Collections CRUD

| Test Case | Why It Matters |
|-----------|---------------|
| `POST /tags/` creates a tag, returns 201 | Basic write path |
| `POST /tags/` with duplicate name returns 409 | The UNIQUE constraint handling in `tags.py:53-54` parses the error string — fragile |
| `GET /tags/` returns tags with correct `count` | The count subquery could drift from reality |
| `DELETE /tags/{id}` cascades and removes `snippet_tags` rows | FK cascade behavior must be verified |
| Same set of tests for `/collections/` | Identical patterns, identical risks |

---

## Priority 2 (Medium) — Data Layer

### 2.1 Database Initialization (`backend/database.py`)

| Test Case | Why It Matters |
|-----------|---------------|
| `init_db()` creates all tables idempotently | The `IF NOT EXISTS` clauses must work on repeated calls |
| `init_db()` creates all three FTS triggers | Triggers are silently skipped if syntax is wrong |
| `get_db()` context manager commits on success | Implicit commit behavior is easy to break during refactoring |
| `get_db()` context manager rolls back on exception | The rollback path (`database.py:27-28`) is never exercised without tests |
| Foreign keys are enforced (PRAGMA foreign_keys = ON) | If this pragma is dropped, cascade deletes silently stop working |

### 2.2 Pydantic Model Validation (`backend/models.py`)

| Test Case | Why It Matters |
|-----------|---------------|
| `SnippetIn` rejects empty title/body | `min_length=1` after `.strip()` — does `"   "` pass or fail? (It should fail, and currently does, but this is undocumented) |
| `SnippetIn` rejects title > 200 chars | Boundary validation |
| `SnippetIn` rejects body > 50,000 chars | Prevents oversized payloads |
| `TagIn.validate_name` lowercases and strips | `" Python "` should become `"python"` — this normalization affects uniqueness |
| `SearchQuery` enforces `limit` bounds (1–200) | Prevents unbounded queries |

---

## Priority 3 (Medium) — Frontend

### 3.1 API Client (`frontend/src/api.js`)

| Test Case | Why It Matters |
|-----------|---------------|
| `api()` throws with error detail on non-2xx response | The error extraction logic (line 9) falls back to `res.statusText` — both paths need coverage |
| `snippetsAPI.search()` encodes query parameter | `encodeURIComponent` on line 20 — a missing encode would break searches with special characters |
| `snippetsAPI.list()` omits `collection_id` when null | The ternary on line 17 controls query string construction |

### 3.2 App Component (`frontend/src/App.jsx`)

| Test Case | Why It Matters |
|-----------|---------------|
| Initial load fetches snippets, tags, and collections | The `useEffect` on mount (lines 19-43) is the entry point for all data |
| `handleSearch("")` reloads full snippet list | Empty-query branch (line 47-51) resets to unfiltered view |
| `handleDeleteSnippet` removes snippet from local state | Optimistic UI update (line 82) could desync from backend |
| Error state renders error banner | The error banner (line 99) should appear on API failure |
| Backend status indicator reflects connection state | `backendStatus` transitions: "checking" → "connected" or "error" |

---

## Priority 4 (Lower) — MCP Server

### 4.1 BackendClient (`mcp/server.py`)

| Test Case | Why It Matters |
|-----------|---------------|
| Each method (`search_snippets`, `get_snippet`, etc.) calls the correct backend URL | A typo in a URL string means silent failure |
| Methods raise `MCPServerError` on HTTP errors | The exception wrapping (e.g., line 42) is the only error feedback path for AI agents |
| `handle_tool_call` dispatches to correct method | The if/elif chain (lines 127-153) maps tool names to methods — a typo means "Unknown tool" |
| `handle_tool_call` returns error dict for unknown tools | Line 154 — the fallback case |
| `handle_tool_call` catches `MCPServerError` and returns error status | Lines 155-156 — the error response path |

---

## Summary of Gaps by Risk

| Risk Level | Area | Gap |
|-----------|------|-----|
| **Critical** | FTS5 triggers | No test verifies the search index stays in sync with CRUD operations |
| **Critical** | Snippet CRUD | No test verifies the core create/read/delete cycle |
| **High** | Tag/collection associations | Junction table writes in `create_snippet` are untested |
| **High** | Cascade deletes | FK cascade behavior (deleting a snippet removes tag/collection links) is assumed but unverified |
| **High** | Unique constraint handling | Error-string parsing for duplicate tags/collections (`"UNIQUE" in str(e)`) is fragile |
| **Medium** | Pydantic validators | Strip + min_length interaction could silently change behavior |
| **Medium** | Frontend API client | Error handling and URL construction paths |
| **Medium** | MCP tool dispatch | Tool routing correctness |
| **Lower** | Frontend components | UI rendering and state transitions |

---

## Suggested File Structure

```
backend/
  tests/
    conftest.py          # pytest fixtures: in-memory SQLite DB, FastAPI TestClient
    test_snippets.py     # Snippet CRUD + search integration tests
    test_tags.py         # Tag CRUD tests
    test_collections.py  # Collection CRUD tests
    test_database.py     # Database init, context manager, FK enforcement
    test_models.py       # Pydantic validation unit tests

frontend/
  src/
    __tests__/
      api.test.js        # API client unit tests (mock fetch)
      App.test.jsx       # App component integration tests

mcp/
  tests/
    test_server.py       # BackendClient + handle_tool_call tests (mock httpx)
```
