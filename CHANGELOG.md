# Changelog

All notable changes to Pin-Up AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-02-16

### Added

#### Backend
- FastAPI REST API with 39 endpoints across 10 routers
- SQLite database with FTS5 full-text search and WAL mode
- Full snippet CRUD: create, read, update, delete, pin, unpin, archive, unarchive
- Tags with color support, upsert-on-create behavior
- Collections with descriptions
- Full-text search with BM25 ranking, DSL tag/source filters
- Export to JSON and ZIP bundle formats
- Import from JSON files with conflict handling
- Backup and restore system
- License management (activation, deactivation, status check, trial support)
- Dashboard statistics (totals, top tags, top collections, vault health)
- App settings (dedupe toggle, backup schedule, token rotation)
- Bearer token authentication with SHA-256 hashing
- CORS, rate limiting, request ID tracking, structured logging
- Snippet limit enforcement (100 for free tier, unlimited for Pro)
- Content deduplication check (optional, per settings)
- Pydantic v2 request/response validation
- 40 end-to-end tests (84% coverage)

#### Frontend
- React 18 + TypeScript 5.3 + Tailwind CSS 3
- Five pages: Snippets, Dashboard, Tags, Collections, Settings
- Virtualized snippet list (TanStack Virtual) for performance
- Syntax highlighting with highlight.js (lazy-loaded, code-split)
- Global keyboard shortcuts: `⌘N`, `⌘K`, `⌘S`, `⌘,`, `⌘E`, `⌘?`
- Keyboard shortcut help modal (`⌘?`)
- Dark mode with light/dark/system toggle (persisted)
- Welcome wizard (4-step first-run onboarding)
- Loading skeletons for all views
- Toast notifications (success, error, info, warning)
- Sidebar with navigation, collection/tag quick filters
- Search bar with debounce and `⌘K` focus shortcut
- Snippet detail view with edit/create form
- Tag management with 12 preset colors
- Collection management with card grid
- Settings page: general, license, export/import, backup, security
- Dashboard with stat cards, top tags/collections, vault health
- TanStack Query for data fetching with cache invalidation
- Zustand store for global state management
- API client with auth, request ID, error handling
- 35 frontend tests (Vitest + React Testing Library)

#### Tauri Desktop
- Full sidecar lifecycle management (spawn, health check, restart, shutdown)
- Dynamic port allocation (portpicker)
- 6 IPC commands: bootstrap, port, data dir, restart, open/save dialog
- System tray with Open, New Snippet, Search, Quit actions
- Auto-restart on sidecar crash (3 max attempts)
- Bootstrap flow: WebView receives backend URL + token via IPC

#### MCP Server
- stdio JSON-RPC 2.0 protocol
- 6 tools: search_snippets, get_snippet, list_snippets, create_snippet, list_tags, list_collections
- Reads same SQLite database as backend
- Full tool schema definitions with input validation
- 21 MCP tests

#### Documentation
- README.md with architecture, API reference, test commands
- PRIVACY.md — local-first privacy policy
- CHANGELOG.md
- SETUP.md — development setup guide

### Security
- All SQL queries parameterized (no f-string SQL)
- Bearer token auth on all endpoints except `/health`
- CORS restricted to localhost origins + Tauri webview
- Rate limiting (200 req/min default)
- Request ID middleware for request tracing

[0.1.0]: https://github.com/holeyfield33-art/pin-up-ai/releases/tag/v0.1.0
