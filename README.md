# rag-retrieval-service

A production-ready Python FastAPI service for document indexing and retrieval
using vector similarity search (OpenAI embeddings + PostgreSQL/pgvector).

---

## Features

- **POST /index** – store a document with its OpenAI embedding
- **POST /query** – semantic search; returns top-k most similar documents
- **DELETE /documents/{id}** – remove a document by id
- Clean architecture: API → Service → Repository interface → Postgres adapter
- Alembic migrations, dependency injection, structured logging

---

## Quick start (Docker Compose)

```bash
# 1. Copy and fill in your env vars
cp .env.example .env
# Edit .env and set OPENAI_API_KEY

# 2. Start the stack (Postgres + app)
docker compose up --build
```

The API will be available at <http://localhost:8000>.

Interactive docs: <http://localhost:8000/docs>

---

## Local development (without Docker)

```bash
# Create and activate a virtual environment
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (or create a .env file)
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/rag_db"
export OPENAI_API_KEY="sk-..."

# Apply migrations (Postgres must be running with pgvector installed)
alembic upgrade head

# Run the server
uvicorn app.main:app --reload
```

---

## API examples

### Index a document

```bash
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{"content": "FastAPI is a modern web framework for Python.", "url": "https://fastapi.tiangolo.com"}'
# {"id": 1}
```

### Query documents

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Python web frameworks", "top_k": 3}'
# [{"id":1,"content":"FastAPI is a modern web framework for Python.","url":"...","score":0.95}]
```

### Delete a document

```bash
curl -X DELETE http://localhost:8000/documents/1
# HTTP 204 No Content
```

---

## Project structure

```
app/
  main.py               # FastAPI app, startup hooks
  core/
    config.py           # Environment config
    logging.py          # Logging setup
  db/
    session.py          # SQLAlchemy engine + get_db dependency
    models.py           # ORM model (DocumentModel)
  domain/
    models.py           # Domain dataclasses (Document, DocumentSearchResult)
  repositories/
    interface.py        # DocumentRepository Protocol (storage abstraction)
    postgres.py         # Postgres + pgvector adapter
  services/
    embedding.py        # OpenAI embedding helper
    document.py         # DocumentService (orchestration)
  api/
    schemas.py          # Pydantic request/response models
    routes.py           # FastAPI route handlers
alembic/                # Database migrations
```

---

## Environment variables

| Variable              | Required | Default                     | Description                         |
|-----------------------|----------|-----------------------------|-------------------------------------|
| `DATABASE_URL`        | Yes      | –                           | PostgreSQL connection string        |
| `OPENAI_API_KEY`      | Yes      | –                           | OpenAI API key                      |
| `EMBEDDING_MODEL`     | No       | `text-embedding-3-small`    | OpenAI embedding model              |
| `EMBEDDING_DIMENSIONS`| No       | `1536`                      | Embedding vector dimensions         |

See `.env.example` for a template.
