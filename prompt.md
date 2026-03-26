Create a production-ready Python FastAPI service for document indexing and retrieval using vector similarity.

Requirements:

General:
- Use FastAPI
- Use SQLAlchemy for DB access
- Use PostgreSQL with pgvector
- Read DATABASE_URL from environment
- Use clean architecture (separate services)

Embedding:
- Use OpenAI embeddings (text-embedding-3-small or similar)
- Create a reusable embedding function

Database:
- Table "documents":
  - id (int, primary key)
  - content (text)
  - url (text)
  - embedding (vector(1536))
  - created_at (timestamp)

Endpoints:

1. POST /index
- Input:
  {
    "content": "string",
    "url": "string"
  }
- Steps:
  - Generate embedding for content
  - Store content, url, embedding in DB
- Return:
  {
    "id": int
  }

2. POST /query
- Input:
  {
    "query": "string",
    "top_k": int
  }
- Steps:
  - Generate embedding for query
  - Perform vector similarity search using cosine distance
  - Order by similarity
  - Limit by top_k
- Return:
  [
    {
      "id": int,
      "content": "string",
      "url": "string",
      "score": float
    }
  ]

Implementation details:
- Use pgvector SQL operator for similarity (<->)
- Normalize score to similarity (optional but preferred)
- Add logging
- Add error handling
- Use dependency injection for DB session
- Use Pydantic models for request/response

Structure:
- main app
- embedding service
- repository layer

Keep code clean, modular, and readable.

Also add delete methods for the API. Use an interface for loose coupling for persistence, in the future we might use another datastore.
