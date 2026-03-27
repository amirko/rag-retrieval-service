import logging

from fastapi import FastAPI

from app.api.routes import router
from app.core.logging import configure_logging

configure_logging()

logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG Retrieval Service",
    description="Document indexing and retrieval using vector similarity search.",
    version="1.0.0",
)

app.include_router(router)


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("RAG Retrieval Service starting up")
    _ensure_pgvector()


def _ensure_pgvector() -> None:
    """Create the pgvector extension if it doesn't already exist."""
    from sqlalchemy import text

    from app.db.session import engine

    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        logger.info("pgvector extension is ready")
    except Exception:
        logger.exception("Could not ensure pgvector extension – is it installed in Postgres?")
