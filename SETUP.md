# Pin-Up AI Development Setup

## Prerequisites

### Backend (FastAPI)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend (Tauri + React)
```bash
cd frontend
npm install
```

### MCP Server
The MCP server shares the backend's Python environment — no separate install needed.

## Running the Project

### Option 1: Backend Only (Development)
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
# API available at http://localhost:8000/api
# Docs at http://localhost:8000/docs
```

### Option 2: Frontend Only (Web Development)
```bash
cd frontend
npm run dev
# App available at http://localhost:5173
```

### Option 3: Full Tauri App (Desktop)
```bash
cd frontend
npm run tauri dev
# Requires Rust and system dependencies (see Tauri prerequisites)
```

### Option 4: Docker
```bash
docker build -t pin-up-ai .
docker run -p 8000:8000 -v ./data:/app/data pin-up-ai
```

## Project Structure

- **backend/** — FastAPI server with SQLite database
  - `app/main.py` — Application factory (`create_app()`)
  - `app/config.py` — Settings with PINUP_ env var prefix
  - `app/database.py` — SQLAlchemy engine, FTS5 setup, WAL mode
  - `app/models.py` — Snippet, Tag, Collection ORM models + M2M join tables
  - `app/schemas.py` — Pydantic v2 request/response models
  - `app/auth.py` — Bearer token auth middleware
  - `app/routers/` — 11 router files, 42+ total routes
    - `health.py` — /api/health, /api/health/ready, /api/health/live
    - `snippets.py` — CRUD + pin/unpin/archive/unarchive
    - `tags.py` — CRUD with color
    - `collections.py` — CRUD with icon/color/updated_at
    - `search.py` — FTS5 search with DSL
    - `mcp.py` — MCP tool definitions + invocation via HTTP
    - `export_import.py` — JSON/bundle export, file import
    - `backup.py` — WAL checkpoint backup, list, restore
    - `license.py` — Gumroad license validation
    - `settings.py` — App settings + token rotation
    - `stats.py` — Dashboard statistics
  - `app/services/` — 8 service modules
  - `app/security/` — CORS, logging, rate limiting, request ID
  - `tests/test_e2e.py` — 40 backend tests
  - `alembic/` — Database migrations

- **frontend/** — Tauri + React desktop app
  - `src/types/index.ts` — TypeScript interfaces matching backend
  - `src/api/client.ts` — Fetch-based API client with bearer token
  - `src/stores/appStore.ts` — Zustand global state
  - `src/hooks/useApi.ts` — TanStack Query hooks
  - `src/components/` — SearchBar, Sidebar, SnippetList, SnippetDetail, Toast, ErrorBoundary
  - `src/pages/` — Snippets, Dashboard, Tags, Collections, Settings
  - `src-tauri/` — Rust/Tauri sidecar management, system tray

- **mcp/** — MCP server for AI agent integration (stdio JSON-RPC 2.0)
  - `server.py` — Protocol handler with 6 tools
  - `tools/` — search_snippets, get_snippet, list_snippets, create_snippet, list_tags, list_collections

## Environment Variables

Copy `.env.example` to `.env` in the root directory:
```bash
cp .env.example .env
```

Key variables:
- `DATABASE_URL` — SQLite path (default: `sqlite:///./pinup.db`)
- `DEBUG` — Enable debug logging (default: `false`)
- `RATE_LIMIT_ENABLED` — Enable rate limiting (default: `true`)
- `LOG_LEVEL` — Logging level (default: `INFO`)

## Running Tests

```bash
# Backend (40 tests)
cd backend && python -m pytest tests/ -q

# Frontend (35 tests)
cd frontend && npx vitest run

# MCP (21 tests)
cd mcp && python -m pytest tests/ -q
```

## Database Management

```bash
# Run migrations
cd backend && alembic upgrade head

# Reset database (delete and restart backend)
rm backend/pinup.db

# View database
sqlite3 backend/pinup.db ".schema"
```

## API Documentation

When running the backend:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/api/health

## Building for Release

### Desktop App
```bash
cd frontend
npm run build
npm run tauri build
```

### Docker
```bash
docker build -t pin-up-ai:1.0.0 .
docker run -p 8000:8000 pin-up-ai:1.0.0
```

## Troubleshooting

### Tauri Prerequisites Missing
On Linux:
```bash
sudo apt-get install libwebkit2gtk-4.1-dev rsvg2-dev
```

Install Rust:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### Database Issues
Delete `pinup.db` to reset the database on next startup.

### Node Issues
```bash
rm -rf node_modules package-lock.json
npm install
```

## License

MIT License — See LICENSE file for details
