# ONE UI - Backend

FastAPI backend for the ONE UI application.

## Features

- 🚀 FastAPI with async support
- 📦 JSON-based storage (easy migration to DB later)
- 🔍 Smart search with filtering
- 🏷️ Tag management
- 📝 Full CRUD operations
- 🔄 CORS enabled for frontend

## Setup

### Install dependencies with uv

```bash
cd backend
uv sync
```

### Run the server

```bash
uv run python main.py
```

Or with uvicorn directly:

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Tools
- `GET /api/tools` - Get all tools
- `GET /api/tools/{id}` - Get tool by ID
- `POST /api/tools` - Create new tool
- `PUT /api/tools/{id}` - Update tool
- `DELETE /api/tools/{id}` - Delete tool

### Search
- `GET /api/search?q=query&tags=tag1,tag2` - Search tools
- `GET /api/search/suggest?q=query` - Get suggestions

### Tags
- `GET /api/tags` - Get all tags
- `GET /api/tags/stats` - Get tag statistics

## Data Storage

Data is stored in `data/tools.json`. Sample data is created automatically on first run.

## Configuration

Edit `app/core/config.py` or create `.env` file:

```env
HOST=0.0.0.0
PORT=8000
DEBUG=True
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

## Future Enhancements

- [ ] Database integration (PostgreSQL/SQLite)
- [ ] AI-powered semantic search
- [ ] User authentication
- [ ] Tool analytics
- [ ] Image upload for icons
