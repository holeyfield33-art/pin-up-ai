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
```bash
cd mcp
pip install -r requirements.txt  # When ready
```

## Running the Project

### Option 1: Backend Only (Development)
```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload
# API available at http://localhost:8000
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

## Project Structure

- **backend/** - FastAPI server with SQLite database
  - `main.py` - Main application entry point
  - `database.py` - Database initialization and connection
  - `models.py` - Pydantic data models
  - `routers/` - API endpoints
    - `snippets.py` - Snippet CRUD and search
    - `tags.py` - Tag management
    - `collections.py` - Collection management

- **frontend/** - Tauri + React desktop app
  - `src/` - React components and styles
  - `src-tauri/` - Rust/Tauri backend
  - `index.html` - HTML entry point
  - `tauri.conf.json` - Tauri configuration
  - `vite.config.js` - Vite configuration

- **mcp/** - MCP server for AI agent integration
  - `server.py` - MCP server
  - `tools/` - MCP tools
    - `search_snippets.py`
    - `get_snippet.py`
    - `list_collections.py`

## Environment Variables

Create a `.env` file in the root directory (or copy from `.env.example`):
```
PINUP_DB=./pinup.db
MCP_PORT=8765
```

## API Documentation

When running the backend:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Endpoints

#### Snippets
- `GET /snippets/` - List snippets
- `POST /snippets/` - Create snippet
- `GET /snippets/{id}` - Get snippet
- `GET /snippets/search/?q=query` - Search snippets

#### Tags
- `GET /tags/` - List tags
- `POST /tags/` - Create tag

#### Collections
- `GET /collections/` - List collections
- `POST /collections/` - Create collection

## Building for Release

### Desktop App
```bash
cd frontend
npm run build
npm run tauri build
```

### Backend
```bash
cd backend
# Package with PyInstaller or use Docker
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

MIT License - See LICENSE file for details
