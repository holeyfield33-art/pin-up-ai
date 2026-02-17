# 📌 Pin-Up AI

**Never lose a great AI answer again.**

Pin-Up AI is a local-first desktop app for saving, organizing, and searching your best AI conversation highlights — from ChatGPT, Claude, Grok, Perplexity, or any AI chat.

Everything stays on your machine. No cloud, no accounts, no tracking.

---

## Features

| Feature | Description |
|---------|-------------|
| **Pin Messages** | Save valuable AI outputs with one click |
| **Full-Text Search** | Blazing-fast FTS5 search across all snippets |
| **Tags & Collections** | Organize by topic, project, or language |
| **Syntax Highlighting** | Auto-detect and highlight 100+ languages |
| **Dark Mode** | Full light/dark/system theme support |
| **Keyboard Shortcuts** | `⌘N` new, `⌘K` search, `⌘S` save, `⌘?` help |
| **MCP Integration** | Give AI agents access to your snippet vault |
| **Import/Export** | JSON export, file import, backup & restore |
| **Freemium Model** | Free (100 snippets) · Pro (unlimited) |

## Architecture

```
Tauri Desktop Shell (Rust)
├── React 18 Frontend (TypeScript + Tailwind CSS)
│   ├── Zustand state management
│   ├── TanStack Query (data fetching)
│   └── TanStack Virtual (virtualized lists)
├── FastAPI Backend (Python sidecar)
│   ├── SQLite + FTS5 full-text search
│   ├── Pydantic v2 validation
│   └── Bearer token auth
└── MCP Server (stdio JSON-RPC 2.0)
    └── 6 tools: search, get, list, create, list_tags, list_collections
```

All data is stored locally:
- **macOS:** `~/Library/Application Support/com.pinup-ai.app/`
- **Windows:** `%APPDATA%/com.pinup-ai.app/`
- **Linux:** `~/.config/com.pinup-ai.app/`

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Rust 1.60+ (for Tauri desktop builds)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/api/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

### Desktop (Tauri)

```bash
cd frontend
npm run tauri dev
```

### MCP Server

```bash
cd mcp
python server.py
```

The MCP server uses stdio JSON-RPC 2.0. Configure your AI agent with:

```json
{
  "mcpServers": {
    "pinup-ai": {
      "command": "python",
      "args": ["mcp/server.py"],
      "transport": "stdio"
    }
  }
}
```

## API Reference

Base URL: `http://localhost:8000/api`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check (no auth) |
| `GET` | `/snippets` | List snippets (paginated, filterable) |
| `POST` | `/snippets` | Create snippet |
| `GET` | `/snippets/{id}` | Get snippet by ID |
| `PATCH` | `/snippets/{id}` | Update snippet |
| `DELETE` | `/snippets/{id}` | Delete snippet |
| `POST` | `/snippets/{id}/pin` | Pin snippet |
| `POST` | `/snippets/{id}/unpin` | Unpin snippet |
| `POST` | `/snippets/{id}/archive` | Archive snippet |
| `POST` | `/snippets/{id}/unarchive` | Unarchive snippet |
| `GET` | `/search?q=…` | Full-text search |
| `GET` | `/tags` | List tags with counts |
| `POST` | `/tags` | Create/upsert tag |
| `PATCH` | `/tags/{id}` | Update tag |
| `DELETE` | `/tags/{id}` | Delete tag |
| `GET` | `/collections` | List collections with counts |
| `POST` | `/collections` | Create collection |
| `PATCH` | `/collections/{id}` | Update collection |
| `DELETE` | `/collections/{id}` | Delete collection |
| `GET` | `/stats` | Dashboard statistics |
| `GET` | `/settings` | Get app settings |
| `PATCH` | `/settings` | Update settings |
| `POST` | `/settings/rotate-token` | Rotate API token |
| `GET` | `/license/status` | License status |
| `POST` | `/license/activate` | Activate license key |
| `POST` | `/license/deactivate` | Deactivate license |
| `POST` | `/export` | Export data (JSON or ZIP bundle) |
| `POST` | `/import` | Import data file |
| `POST` | `/backup/run` | Create backup |
| `GET` | `/backup/list` | List backups |
| `POST` | `/backup/restore` | Restore from backup |

All endpoints (except `/health`) require `Authorization: Bearer <token>`.

## Testing

### Backend (40 tests, 84% coverage)

```bash
cd backend
python -m pytest tests/ -x -q --tb=short
python -m pytest tests/ --cov=app --cov-report=term-missing  # coverage
```

### Frontend (35 tests)

```bash
cd frontend
npm test              # single run
npm run test:watch    # watch mode
```

### MCP (21 tests)

```bash
python -m pytest mcp/tests/test_mcp.py -x -q
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `⌘K` / `Ctrl+K` | Focus search |
| `⌘N` / `Ctrl+N` | New snippet |
| `⌘S` / `Ctrl+S` | Save snippet |
| `⌘,` / `Ctrl+,` | Settings |
| `⌘E` / `Ctrl+E` | Export |
| `⌘?` / `Ctrl+/` | Shortcut help |
| `Esc` | Cancel / close |

## Project Structure

```
pin-up-ai/
├── backend/
│   ├── app/
│   │   ├── routers/        # API endpoints (10 routers)
│   │   ├── services/       # Business logic (8 services)
│   │   ├── security/       # CORS, rate limiting, logging, request ID
│   │   ├── config.py       # Pydantic settings
│   │   ├── database.py     # SQLite + FTS5 setup
│   │   ├── models.py       # SQLAlchemy ORM models
│   │   └── schemas.py      # Pydantic request/response schemas
│   ├── tests/              # pytest E2E tests (40 tests)
│   ├── alembic/            # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # SearchBar, Sidebar, SnippetList, SnippetDetail,
│   │   │                   # Toast, WelcomeWizard, ShortcutHelp, Skeleton
│   │   ├── pages/          # Snippets, Dashboard, Tags, Collections, Settings
│   │   ├── hooks/          # useApi (TanStack Query), useToast
│   │   ├── stores/         # Zustand app store (theme, nav, filters)
│   │   ├── api/            # API client with auth
│   │   ├── types/          # TypeScript interfaces
│   │   └── utils/          # formatDate, debounce, cn
│   ├── src-tauri/          # Rust: sidecar, IPC, system tray
│   └── package.json
└── mcp/
    ├── server.py           # stdio JSON-RPC 2.0 MCP server
    └── tools/              # 6 tool handlers
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Desktop | Tauri 1.5 (Rust) |
| Frontend | React 18, TypeScript 5.3, Tailwind 3, Vite 5 |
| State | Zustand 4, TanStack Query 5 |
| Backend | FastAPI, SQLAlchemy, Pydantic v2 |
| Database | SQLite + FTS5, WAL mode |
| MCP | Custom stdio JSON-RPC 2.0 |
| Testing | pytest (backend), Vitest + RTL (frontend) |

## Security

- All data stored locally — no cloud sync
- Bearer token authentication (SHA-256 hashed)
- Parameterized SQL queries (no f-string SQL)
- CORS restricted to localhost + Tauri webview
- Rate limiting on all API endpoints
- Request ID tracking for debugging

## License

MIT License — see [LICENSE](LICENSE)

---

Built with care by **AshuraStudio**
