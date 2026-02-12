# 📌 Pin-Up AI

**Local-first desktop companion for saving, organizing, and searching AI conversation highlights.**

Pin-Up AI brings your favorite AI responses into a personal vault—fast, private, and fully local. Perfect for developers, researchers, and anyone who captures valuable insights from their AI chats.

## ✨ Features

- **⭐ Pin Any Message** - Capture outputs from ChatGPT, Claude, Grok, Perplexity, or any AI chat
- **🏷️ Smart Tagging** - Organize snippets with flexible tag system
- **📁 Collections** - Group related snippets into project-based collections
- **🔍 Full-Text Search** - Blazing-fast FTS5-powered search across all content
- **💬 Language Detection** - Auto-detect and syntax-highlight code snippets
- **🤖 MCP Integration** - Connect AI agents to your snippet vault
- **🔒 100% Private** - All data stored locally, no cloud sync
- **📊 Usage Analytics** - Track tags and collections with snippet counts

## 🏗️ Architecture

```
Pin-Up AI/
├── frontend/          # Tauri + React + Tailwind desktop app
│   ├── src-tauri/     # Rust backend for Tauri
│   ├── src/           # React components & UI
│   └── package.json   # Frontend dependencies
├── backend/           # FastAPI REST API
│   ├── main.py        # FastAPI app with CORS, logging
│   ├── database.py    # SQLite + FTS5 setup
│   ├── models.py      # Pydantic validation
│   └── routers/       # API endpoints
├── mcp/               # MCP server for AI agents
│   ├── server.py      # Tool handlers
│   └── tools/         # AI-callable tools
└── requirements.txt   # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 16+  
- Rust 1.60+ (for Tauri desktop app)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --port 8000
```

Backend: `http://localhost:8000`  
Docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server (Vite)
npm run dev
```

Frontend: `http://localhost:5173`

### Desktop App (Tauri)

```bash
cd frontend
npm install
npm run tauri dev  # Requires Rust
```

### MCP Server

```bash
cd mcp
python server.py
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Snippets API

#### List Snippets
```
GET /snippets/?limit=50&offset=0&collection_id=1
```

#### Create Snippet
```
POST /snippets/
{
  "title": "Title",
  "body": "Content",
  "language": "python",
  "source": "ChatGPT",
  "tags": [1, 2],
  "collection_id": 1
}
```

#### Get Snippet
```
GET /snippets/{id}
```

#### Delete Snippet
```
DELETE /snippets/{id}
```

#### Search Snippets
```
GET /snippets/search/query?q=machine+learning&limit=50
```

### Tags API

#### List Tags
```
GET /tags/?limit=100
```

#### Create Tag
```
POST /tags/
{"name": "typescript"}
```

### Collections API

#### List Collections
```
GET /collections/?limit=100
```

#### Create Collection
```
POST /collections/
{
  "name": "Web Dev",
  "description": "Web development tips"
}
```

### Health Check
```
GET /health
```

## 🤖 MCP Server Tools

Available tools for AI agents:
- `search_snippets` - Full-text search
- `get_snippet` - Get specific snippet
- `list_snippets` - List all snippets
- `create_snippet` - Add new snippet
- `list_collections` - Get collections
- `list_tags` - Get tags

## 🗄️ Database

SQLite with FTS5 full-text search:
- **snippets** - Main snippet data
- **tags** - Tag names
- **collections** - Collection names
- **snippet_tags** - Many-to-many relationships
- **snippet_collections** - Collection membership
- **snippets_fts** - Full-text search index

All tables have cascade delete enabled.

## 🔒 Security

- **CORS enabled** for localhost (5173, 3000, 8000)
- **Parameterized queries** prevent SQL injection
- **Input validation** with Pydantic models
- **Transaction-based** database operations
- **Foreign keys** enforced

## 📦 Environment Variables

```env
PINUP_DB=./pinup.db
MCP_PORT=8765
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
```

## 🛠️ Development

### Run All Services

**Terminal 1 - Backend:**
```bash
cd backend && source .venv/bin/activate && uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend && npm run dev
```

**Terminal 3 - MCP (optional):**
```bash
cd mcp && python server.py
```

Access at: `http://localhost:5173`

## 📦 Production Build

### Desktop
```bash
cd frontend
npm run build
npm run tauri build
```

### Backend
```bash
gunicorn main:app --port 8000 --workers 4
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend .
CMD ["gunicorn", "main:app"]
```

## ⚡ Performance

- FTS5 search: ~50ms for 100k snippets
- React virtual scrolling for large lists
- Native Tauri performance
- Async/await throughout backend

## 🐛 Troubleshooting

### Backend connection fails
```bash
curl http://localhost:8000/health
```

### Reset database
```bash
rm pinup.db
# Restart backend
```

### CORS errors
Check frontend URL is in allowlist in `main.py`

## 🎯 Roadmap

- v0.2: Advanced search filters
- v0.3: Browser extension
- v0.4: Mobile app
- v0.5: Collaborative mode
- v1.0: Plugin marketplace

## 📝 License

MIT License

---

**Questions?** APIs at `/docs` when backend is running.
