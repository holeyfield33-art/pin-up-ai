# 📌 Pin-Up AI - Enterprise-Grade Snippet Manager

**Local-first desktop companion for saving, organizing, and searching AI conversation highlights with AI agent integration.**

Pin-Up AI brings your favorite AI responses into a secure, private, fully-featured vault. Perfect for developers, researchers, and anyone capturing valuable insights from AI interactions.

## ✨ Core Features

- **⭐ Pin Any Message** - Capture outputs from ChatGPT, Claude, Grok, Perplexity, or any AI service
- **🏷️ Smart Tagging** - Flexible tag system with color coding
- **📁 Collections** - Organize snippets by project or topic
- **🔍 Full-Text Search** - Lightning-fast FTS5-powered search
- **💬 Language Highlighting** - Detect and highlight 100+ programming languages
- **🤖 MCP Integration** - Connect AI agents to your vault programmatically
- **📤 Export** - Export to JSON or Markdown
- **🔒 100% Private** - All data stored locally, zero cloud sync
- **⚡ Fast & Responsive** - ReactTypeScript frontend with Zustand state management
- **🖥️ Native Desktop App** - Tauri-powered cross-platform application

---

## 🏗️ Architecture Overview

### High-Level Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                      CLIENT TIER (React + TypeScript)               │
├─────────────────────────────────────────────────────────────────────┤
│  • SearchBar (Ctrl+P)  • Sidebar (Collections/Tags)                │
│  • SnippetList (filtered)  • SnippetDetail (full view)             │
│  • Toast notifications  • Error boundaries                          │
├─────────────────────────────────────────────────────────────────────┤
│                    API LAYER (Axios HTTP Client)                   │
├─────────────────────────────────────────────────────────────────────┤
│                    FASTAPI BACKEND (Port 8000)                      │
├──────────────────┬────────────────────────┬───────────────────────┤
│  Routers:        │  Services:             │  Middleware:          │
│  • /api/snippets │  • SnippetService      │  • CORS               │
│  • /api/tags     │  • TagService          │  • Rate Limiting      │
│  • /api/collect. │  • CollectionService   │  • Request ID         │
│  • /api/search   │  • MCP Integration     │  • Error Handling     │
│  • /api/mcp      │                        │  • Structured Logging │
├──────────────────┴────────────────────────┴───────────────────────┤
│                     DATABASE TIER (SQLite)                          │
├──────────────────────────────────────────────────────────────────────┤
│  • snippets (id, title, body, language, source, timestamps)        │
│  • tags (id, name, color)                                           │
│  • collections (id, name, description, icon, color)                │
│  • snippet_tags (M2M relationship)                                  │
│  • snippet_collections (M2M relationship)                           │
│  • snippets_fts (FTS5 virtual table for search)                    │
│  • WAL mode enabled for concurrent access                          │
└──────────────────────────────────────────────────────────────────────┘

MCP TOOLS (Agent Integration):
  • search_snippets(query, limit, offset) - Full-text search
  • get_snippet(id) - Retrieve by ID
  • list_snippets(limit, offset) - Paginated list
  • create_snippet(title, body, language, source, tag_ids, collection_ids) - Create new
  • list_collections() - Browse collections
  • list_tags() - Browse tags

DESKTOP WRAPPER:
  • Tauri 1.5 (Rust-based cross-platform framework)
  • Backend auto-launch on app startup
  • File system access for exports
  • System dialogs and notifications
```

---

## 🚀 Quick Start (3 minutes)

### Prerequisites

- **Python 3.11+** (backend)
- **Node.js 16+** (frontend)
- **Rust 1.60+** (Tauri - optional, for desktop app only)

### 1️⃣ Backend Setup

```bash
cd backend

# Create Python virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env from example
cp ../.env.example .env

# Run migrations (auto-initialized on first run)
python -m alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

**Backend runs on:** `http://localhost:8000`
**API Docs:** `http://localhost:8000/api/docs`  
**Health Check:** `http://localhost:8000/api/health`

### 2️⃣ Frontend Setup (Web Dev)

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

**Frontend runs on:** `http://localhost:5173`

### 3️⃣ Desktop App (Tauri)

```bash
cd frontend

# Install JS dependencies (if not already done)
npm install

# Launch in dev mode
npm run tauri:dev

# Build production binary
npm run tauri:build
```

---

## 📚 API Reference

### Base URL
```
http://127.0.0.1:8000/api
```

### Snippets Endpoints

#### List Snippets
```http
GET /api/snippets?limit=50&offset=0&collection_id=<id>
```

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "title": "Python async/await",
      "body": "async def main():\n  await fetch(...)",
      "language": "python",
      "source": "Claude",
      "created_at": "2024-02-12T03:00:00Z",
      "updated_at": "2024-02-12T03:00:00Z",
      "is_archived": false,
      "tags": [{"id": "...", "name": "async", "color": "#6366F1"}],
      "collections": [{"id": "...", "name": "Web Dev","snippet_count": 23}]
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

#### Create Snippet
```http
POST /api/snippets
Content-Type: application/json

{
  "title": "React Hook Pattern",
  "body": "const [count, setCount] = useState(0);",
  "language": "javascript",
  "source": "ChatGPT",
  "tag_ids": ["tag-uuid-1"],
  "collection_ids": ["collection-uuid-1"]
}
```

**Status: 201 Created**

#### Get Snippet
```http
GET /api/snippets/{snippet_id}
```

#### Update Snippet
```http
PUT /api/snippets/{snippet_id}

{
  "title": "Updated Title",
  "tag_ids": ["new-tag-id"]
}
```

#### Delete Snippet
```http
DELETE /api/snippets/{snippet_id}
```

**Status: 204 No Content**

#### Search Snippets
```http
GET /api/snippets/search/query?q=async&limit=50&offset=0
```

#### Export Snippets
```http
GET /api/snippets/export/{format}
```

**Formats:** `json`, `markdown`

### Tags Endpoints

#### List Tags
```http
GET /api/tags?limit=100
```

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "typescript",
      "color": "#3B82F6",
      "created_at": "2024-02-12T00:00:00Z",
      "snippet_count": 12
    }
  ],
  "total": 45,
  "limit": 100,
  "offset": 0
}
```

#### Create Tag
```http
POST /api/tags

{
  "name": "api-design",
  "color": "#10B981"
}
```

**Status: 201 Created**  
**Status: 409 Conflict** (tag already exists)

### Collections Endpoints

#### List Collections
```http
GET /api/collections?limit=100
```

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Web Development",
      "description": "Frontend and backend web patterns",
      "icon": "code",
      "color": "#0EA5E9",
      "created_at": "2024-02-12T00:00:00Z",
      "updated_at": "2024-02-12T00:00:00Z",
      "snippet_count": 45
    }
  ],
  "total": 8,
  "limit": 100,
  "offset": 0
}
```

#### Create Collection
```http
POST /api/collections

{
  "name": "Machine Learning",
  "description": "ML/AI algorithms and patterns",
  "icon": "brain",
  "color": "#F59E0B"
}
```

### Health Endpoints

#### Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "healthy"
}
```

#### Readiness Check
```http
GET /api/health/ready
```

#### Liveness Check
```http
GET /api/health/live
```

---

## 🤖 MCP Tools

### Get Available Tools
```http
GET /api/mcp/tools
```

### Call a Tool
```http
POST /api/mcp/tools/{tool_name}/call

{
  "query": "async patterns",
  "limit": 20
}
```

**Response:**
```json
{
  "status": "success",
  "data": [...]
}
```

### Tool Definitions

#### search_snippets
- **Description:** Full-text search snippets
- **Parameters:**
  - `query` (string, required): Search query (1-500 chars)
  - `limit` (integer, optional, default: 20): Max results (1-100)
- **Returns:** Array of snippets with preview

#### get_snippet
- **Description:** Get specific snippet by ID
- **Parameters:**
  - `snippet_id` (string, required): UUID
- **Returns:** Complete snippet with all relations

#### list_snippets
- **Description:** Paginated snippet list
- **Parameters:**
  - `limit` (integer, optional, default: 10): Max results
  - `offset` (integer, optional, default: 0): Pagination offset
- **Returns:** Array of snippets

#### create_snippet
- **Description:** Create new snippet
- **Parameters:**
  - `title` (string, required): Title (1-255 chars)
  - `body` (string, required): Content
  - `language` (string, optional): Programming language
  - `source` (string, optional): Source URL/name
  - `tag_ids` (array[string], optional): Tag IDs to attach
  - `collection_ids` (array[string], optional): Collection IDs to attach
- **Returns:** Created snippet

#### list_collections
- **Description:** List all collections
- **Parameters:**
  - `limit` (integer, optional, default: 100): Max results
- **Returns:** Array of collections with counts

#### list_tags
- **Description:** List all tags with usage counts
- **Parameters:**
  - `limit` (integer, optional, default: 100): Max results
- **Returns:** Array of tags with snippet counts

---

## 🗄️ Database Schema

### Snippets Table
```sql
CREATE TABLE snippets (
  id VARCHAR(36) PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  body TEXT NOT NULL,
  language VARCHAR(50),
  source VARCHAR(255),
  created_at DATETIME,
  updated_at DATETIME,
  is_archived BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_snippets_title ON snippets(title);
CREATE INDEX idx_snippets_created ON snippets(created_at DESC);
```

### Tags Table
```sql
CREATE TABLE tags (
  id VARCHAR(36) PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL,
  color VARCHAR(7),
  created_at DATETIME
);
```

### Collections Table
```sql
CREATE TABLE collections (
  id VARCHAR(36) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  icon VARCHAR(50),
  color VARCHAR(7),
  created_at DATETIME,
  updated_at DATETIME
);
```

### Many-to-Many Relationships
```sql
CREATE TABLE snippet_tags (
  snippet_id VARCHAR(36),
  tag_id VARCHAR(36),
  PRIMARY KEY (snippet_id, tag_id),
  FOREIGN KEY (snippet_id) REFERENCES snippets(id) ON DELETE CASCADE,
  FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE TABLE snippet_collections (
  snippet_id VARCHAR(36),
  collection_id VARCHAR(36),
  PRIMARY KEY (snippet_id, collection_id),
  FOREIGN KEY (snippet_id) REFERENCES snippets(id) ON DELETE CASCADE,
  FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
);
```

### Full-Text Search (FTS5)
```sql
CREATE VIRTUAL TABLE snippets_fts USING fts5(
  snippet_id UNINDEXED,
  title,
  body,
  language,
  source
);

-- Triggers to keep FTS index in sync
CREATE TRIGGER snippets_fts_insert
AFTER INSERT ON snippets
BEGIN
  INSERT INTO snippets_fts(snippet_id, title, body, language, source)
  VALUES (NEW.id, NEW.title, NEW.body, NEW.language, NEW.source);
END;

CREATE TRIGGER snippets_fts_update
AFTER UPDATE ON snippets
BEGIN
  DELETE FROM snippets_fts WHERE snippet_id = OLD.id;
  INSERT INTO snippets_fts(snippet_id, title, body, language, source)
  VALUES (NEW.id, NEW.title, NEW.body, NEW.language, NEW.source);
END;

CREATE TRIGGER snippets_fts_delete
AFTER DELETE ON snippets
BEGIN
  DELETE FROM snippets_fts WHERE snippet_id = OLD.id;
END;
```

---

## 🔒 Security Features

### Input Validation
- Pydantic v2 strict schema validation
- HTML escaping for all user input
- Min/max length constraints
- Regex pattern matching for colors, URIs, etc.

### Database Security
- Foreign key constraints enabled
- Parameterized queries (SQLAlchemy ORM)
- Transaction-based ACID operations with rollback
- Cascade delete rules to prevent orphans

### API Security
- **CORS:** Locked to `localhost:5173`, `localhost:3000`, `127.0.0.1:8000`
- **Rate Limiting:** 100 requests per 60 seconds per IP
- **Request ID Injection:** Track requests through logs
- **Error Handling:** No sensitive data in responses
- **Structured Logging:** JSON logs with request context

### Network Security
- HTTPS-ready (configure in production)
- X-Request-ID header for audit trails
- No credentials stored on client
- SQLite only accessible locally

---

## ⚙️ Configuration

### .env File
```bash
# App
APP_NAME=Pin-Up AI
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=production

# Database
DATABASE_URL=sqlite:///./pinup.db
DB_CHECK_SAME_THREAD=false

# API
API_PREFIX=/api
API_TITLE=Pin-Up AI API
API_DOCS_URL=/docs
API_REDOC_URL=/redoc

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://127.0.0.1:3000","http://127.0.0.1:5173"]
CORS_CREDENTIALS=true

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Export
MAX_EXPORT_SIZE=10000000
```

---

## 🛠️ Development Workflow

### Run All Services Locally

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Visit `http://localhost:5173` to see your changes instantly.

### Database Management

#### View Database
```bash
sqlite3 pinup.db
sqlite> .schema
sqlite> SELECT COUNT(*) FROM snippets;
sqlite> .quit
```

#### Reset Database
```bash
rm pinup.db
# Restart backend - database will be re-initialized
```

#### Run Migrations
```bash
cd backend
alembic upgrade head
```

### Type Checking

```bash
cd frontend
npm run type-check
```

---

## 📦 Production Deployment

### Docker Deployment

**Create Dockerfile (root):**
```dockerfile
FROM python:3.11-slim
WORKDIR /app

# Backend
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend app/

# Frontend (optional, for serving static files)
COPY frontend/dist dist/

EXPOSE 8000
CMD ["gunicorn", "app.main:app", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

**Deploy:**
```bash
docker build -t pin-up-ai:1.0.0 .
docker run -p 8000:8000 -v ./data:/app/data pin-up-ai:1.0.0
```

### Gunicorn (Production ASGI Server)

```bash
cd backend
source .venv/bin/activate
gunicorn app.main:app \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --timeout 300 \
  --access-logfile - \
  --error-logfile -
```

### Nginx Reverse Proxy

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name pin-up.example.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name pin-up.example.com;

    ssl_certificate /etc/letsencrypt/live/pin-up.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/pin-up.example.com/privkey.pem;

    # Frontend SPA
    location / {
        root /var/www/pin-up/dist;
        try_files $uri /index.html;
    }

    # API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Request-ID $request_id;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### Environment-Specific Config

```bash
# Production
export ENVIRONMENT=production
export DEBUG=false
export LOG_FORMAT=json
export LOG_LEVEL=WARNING
export RATE_LIMIT_REQUESTS=50
export RATE_LIMIT_PERIOD=60
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Check port 8000 is free
lsof -i :8000

# Check dependencies
pip install -r requirements.txt --force-reinstall

# Check database permissions
chmod 644 pinup.db
chmod 755 .
```

### Frontend can't reach backend
```bash
# Verify backend is running
curl http://127.0.0.1:8000/api/health

# Check CORS settings in backend/.env
# Check frontend/.env has correct API_URL
export VITE_API_URL=http://127.0.0.1:8000/api
```

### Database locked
```bash
# SQLite WAL mode requires cleanup
# Close all open connections and restart backend
rm pinup.db-shm pinup.db-wal
```

### Tauri build fails
```bash
# Ensure Rust is installed
rustup --version

# Update Rust
rustup update

# Clear Tauri cache
cargo clean
```

---

## 📖 Development Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React TypeScript Guide](https://react.dev/learn/typescript)
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/)
- [Tauri 1.x Guide](https://tauri.app/)
- [Zustand State Management](https://zustand-demo.vercel.app/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)

---

## 📝 License

MIT License - see LICENSE file

---

## 🚀 Next Steps

- [ ] Add user authentication for multi-user deployments
- [ ] Implement cloud backup with encryption
- [ ] Add browser extension for one-click capture
- [ ] Build mobile companion app (React Native)
- [ ] Add collaborative sharing via secure links
- [ ] Implement plugin marketplace
- [ ] Add advanced analytics dashboard
- [ ] Integrate with popular note-taking apps

---

**Built with ❤️ for capturing and organizing AI wisdom.**
