# RAG Retrieval Service – Full Specification

This file tracks the original requirements and subsequent additions that shaped
this repository.

---

## Core requirements

Build a production-ready Python FastAPI service for document indexing and
retrieval using vector similarity, with clean architecture and an abstraction
layer so storage/vector operations are not strongly coupled to Postgres.

- FastAPI app with clean architecture separation (API layer, services,
  repositories/adapters, domain models).
- SQLAlchemy for DB access.
- PostgreSQL with pgvector.
- Read `DATABASE_URL` from environment.
- Add logging and robust error handling.
- Dependency injection for DB session.
- Pydantic models for request/response.

---

## Data model

Table: `documents`

| Column       | Type             | Notes             |
|--------------|------------------|-------------------|
| `id`         | int              | primary key       |
| `content`    | text             |                   |
| `url`        | text             |                   |
| `embedding`  | vector(1536)     | pgvector column   |
| `created_at` | timestamp        | auto-set by DB    |

---

## Embedding

- Use OpenAI embeddings (`text-embedding-3-small` or similar).
- Implement a reusable embedding function/service.
- Read OpenAI API key from environment (`OPENAI_API_KEY`).

---

## Endpoints

### 1. `POST /index`

**Request JSON**
```json
{ "content": "string", "url": "string" }
```

**Steps**
1. Generate embedding for `content`.
2. Store `content`, `url`, `embedding` in DB.

**Response JSON**
```json
{ "id": 1 }
```

---

### 2. `POST /query`

**Request JSON**
```json
{ "query": "string", "top_k": 5 }
```

**Steps**
1. Generate embedding for `query`.
2. Perform vector similarity search using cosine distance.
3. Order by similarity, limit to `top_k`.

**Response JSON**
```json
[
  { "id": 1, "content": "string", "url": "string", "score": 0.95 }
]
```

- Use pgvector SQL operator `<->` for similarity.
- Normalize score to similarity (preferred): `score = 1 - distance / 2`

---

### 3. `DELETE /documents/{id}`

- Delete a document by id.
- Return **204 No Content** on success.
- Return **404** if not found.

---

## Abstraction / interface requirement

Introduce an interface/protocol for data/vector operations (CRUD + vector
search) so the core service is **not** strongly coupled to Postgres.

- Implement a Postgres+pgvector adapter that fulfils this interface.
- Organise code so swapping the backend (e.g. another vector DB) requires
  changing only adapter wiring.

---

## Operational / project updates

- Environment config (`.env.example`) for `DATABASE_URL` and `OPENAI_API_KEY`.
- Startup checks (ensure pgvector extension exists).
- Alembic migrations for schema setup.
- Dockerfile + docker-compose for running the API and a Postgres+pgvector
  database locally.
- README with run instructions and API examples.
- This file (`PROMPT.md`) containing the full specification.
