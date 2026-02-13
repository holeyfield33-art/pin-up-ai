# Test Coverage Analysis — Pin-Up AI

## Current State

The project has **zero test coverage**. There are no test files, no test frameworks configured, no test scripts in `package.json`, and no testing dependencies in `requirements.txt` or `package.json`.

---

## Proposed Test Improvements by Priority

### Priority 1: Backend API Integration Tests (High Impact)

The FastAPI backend is the core of the application. Testing it with `pytest` + FastAPI's `TestClient` provides the highest value per line of test code.

**What to test:**

#### Snippets Router (`backend/routers/snippets.py`)
- **CRUD lifecycle**: create → read → list → delete a snippet
- **Pagination**: verify `limit` and `offset` query parameters work correctly
- **Collection filtering**: `GET /snippets/?collection_id=X` returns only snippets in that collection
- **Tag association**: creating a snippet with `tags: [1, 2]` correctly populates `snippet_tags`
- **404 handling**: `GET /snippets/999` and `DELETE /snippets/999` return 404
- **FTS search**: `GET /snippets/search/query?q=keyword` returns matching snippets and respects ranking
- **FTS query sanitization** (`_sanitize_fts_query`): special characters like `*`, `(`, `)`, `"`, `-` are escaped properly and don't cause SQL errors
- **Edge case**: creating a snippet with a nonexistent `tag_id` should fail (foreign key constraint)
- **Edge case**: creating a snippet with a nonexistent `collection_id` should fail

#### Tags Router (`backend/routers/tags.py`)
- **CRUD lifecycle**: create → read → list → delete a tag
- **Duplicate name**: creating a tag with an existing name returns 409 Conflict
- **Usage count**: `TagOut.count` reflects the actual number of snippets using the tag
- **Cascade delete**: deleting a tag removes associated `snippet_tags` rows without affecting the snippet itself

#### Collections Router (`backend/routers/collections.py`)
- **CRUD lifecycle**: create → read → list → delete a collection
- **Duplicate name**: creating a collection with an existing name returns 409 Conflict
- **Snippet count**: `CollectionOut.count` reflects the actual number of snippets in the collection
- **Cascade delete**: deleting a collection removes `snippet_collections` rows without deleting the snippets

**Recommended setup:**
```
backend/
├── tests/
│   ├── conftest.py          # pytest fixtures: in-memory SQLite DB, TestClient
│   ├── test_snippets.py
│   ├── test_tags.py
│   ├── test_collections.py
│   └── test_health.py
```

Add to `requirements.txt`:
```
pytest>=8.0
httpx>=0.27        # required by FastAPI TestClient
```

---

### Priority 2: Pydantic Model Validation Tests (Medium Impact)

The models in `backend/models.py` contain validation logic that should be tested in isolation, without needing the database or HTTP layer.

**What to test:**

- `SnippetIn.title` is stripped of whitespace; empty string after strip raises `ValidationError`
- `SnippetIn.body` max length of 50,000 characters is enforced
- `TagIn.name` is lowercased and stripped (`"  Python "` → `"python"`)
- `CollectionIn.name` is stripped; respects max_length of 120
- `SearchQuery.q` requires min_length=1; `limit` is clamped between 1–200
- Fields with `Optional` accept `None` correctly
- Invalid types (e.g., string for `collection_id`) raise `ValidationError`

---

### Priority 3: Database Layer Tests (Medium Impact)

The `backend/database.py` module handles schema initialization and connection management.

**What to test:**

- `init_db()` creates all 6 tables and the FTS virtual table
- `init_db()` is idempotent (calling it twice doesn't error)
- `get_db()` context manager commits on success and rolls back on exception
- Foreign key enforcement is active (`PRAGMA foreign_keys = ON`)
- FTS triggers: inserting/updating/deleting a snippet updates `snippets_fts`
- WAL mode is enabled

---

### Priority 4: Middleware Tests (Medium Impact)

The custom middleware in `backend/main.py` has logic that is easy to get wrong and hard to test manually.

**What to test:**

#### RateLimitMiddleware
- Requests below the limit pass through normally
- The (N+1)th request within the window returns 429 with `Retry-After` header
- Requests from different IPs are tracked independently
- Old entries are pruned after the window expires

#### BodySizeLimitMiddleware
- Requests with `Content-Length` exceeding the limit return 413
- Requests without `Content-Length` header pass through
- Requests within the limit pass through

---

### Priority 5: MCP Server Unit Tests (Medium Impact)

The MCP server (`mcp/server.py`) is a thin HTTP client wrapper, but it still has testable logic.

**What to test:**

- `handle_tool_call` dispatches to the correct `BackendClient` method for each tool name
- Unknown tool names return `{"status": "error", "message": "Unknown tool: ..."}`
- `MCPServerError` exceptions are caught and returned as error responses
- Generic exceptions are caught and return a generic error message (no leaking internals)
- `BackendClient` methods construct the correct URL and query parameters

**Recommended approach:** Use `pytest` with `respx` or `pytest-httpx` to mock the outbound HTTP calls without needing the real backend running.

---

### Priority 6: Frontend Component Tests (Lower Impact, Still Valuable)

The React frontend has 4 components plus the `App` shell and an API client module.

**What to test:**

#### `api.js`
- Successful responses are parsed as JSON
- 204 responses return `null`
- Non-OK responses throw an `Error` with the `detail` from the response body
- URL construction for each method (especially `snippetsAPI.list` with optional `collectionId`)

#### `App.jsx`
- Initial load fetches snippets, tags, and collections
- Search with empty string reloads the full snippet list
- Collection filter passes `collection_id` to the API
- Delete removes the snippet from state and clears selection if it was selected
- Error state is displayed when API calls fail
- Loading indicator shows during fetches

#### Components (`SearchBar`, `Sidebar`, `SnippetList`, `SnippetDetail`)
- Render without crashing with valid props
- Callbacks fire with correct arguments on user interaction

**Recommended setup:**
```
frontend/
├── src/
│   ├── __tests__/
│   │   ├── api.test.js
│   │   ├── App.test.jsx
│   │   ├── SearchBar.test.jsx
│   │   ├── Sidebar.test.jsx
│   │   ├── SnippetList.test.jsx
│   │   └── SnippetDetail.test.jsx
```

Add to `package.json` devDependencies:
```json
{
  "vitest": "^2.0",
  "@testing-library/react": "^16.0",
  "@testing-library/jest-dom": "^6.0",
  "jsdom": "^24.0"
}
```

---

## Summary Table

| Area | Priority | Test Type | Estimated Tests | Key Risk Mitigated |
|------|----------|-----------|----------------|--------------------|
| Snippets API | P1 | Integration | ~15 | Data loss, search bugs, FK violations |
| Tags API | P1 | Integration | ~8 | Duplicate handling, cascade behavior |
| Collections API | P1 | Integration | ~8 | Duplicate handling, cascade behavior |
| Pydantic Models | P2 | Unit | ~10 | Malformed input accepted silently |
| Database Layer | P3 | Unit | ~8 | Schema drift, broken migrations |
| Middleware | P4 | Integration | ~8 | Rate limit bypass, DoS via large body |
| MCP Server | P5 | Unit | ~10 | Tool dispatch errors, leaked internals |
| Frontend API | P6 | Unit | ~8 | Broken fetch calls, wrong URL params |
| Frontend Components | P6 | Component | ~12 | UI regressions, broken interactions |

**Total: ~87 tests** to reach reasonable coverage across the stack.

---

## Recommended First Steps

1. Add `pytest` and `httpx` to `backend/requirements.txt`
2. Create `backend/tests/conftest.py` with an in-memory SQLite fixture and FastAPI `TestClient`
3. Write the snippets CRUD integration tests first — they cover the most critical path
4. Add a `test` script to `package.json` and set up Vitest for frontend tests
5. Consider adding a CI pipeline (GitHub Actions) to run tests on every push
