import logging
from typing import List

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.models import DocumentModel
from app.domain.models import Document, DocumentSearchResult

logger = logging.getLogger(__name__)


class PostgresDocumentRepository:
    """Postgres + pgvector implementation of :class:`DocumentRepository`."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, content: str, url: str, embedding: List[float]) -> Document:
        doc = DocumentModel(content=content, url=url, embedding=embedding)
        self._db.add(doc)
        self._db.commit()
        self._db.refresh(doc)
        logger.info("Stored document id=%s url=%s", doc.id, doc.url)
        return Document(id=doc.id, content=doc.content, url=doc.url, created_at=doc.created_at)

    def search(self, query_embedding: List[float], top_k: int) -> List[DocumentSearchResult]:
        # Use pgvector cosine distance operator <->
        results = (
            self._db.query(
                DocumentModel,
                DocumentModel.embedding.cosine_distance(query_embedding).label("distance"),
            )
            .order_by("distance")
            .limit(top_k)
            .all()
        )
        search_results = []
        for doc, distance in results:
            # Normalise cosine distance [0, 2] → similarity score [0, 1]
            score = 1.0 - distance / 2.0
            search_results.append(
                DocumentSearchResult(id=doc.id, content=doc.content, url=doc.url, score=score)
            )
        logger.info("Vector search returned %d results", len(search_results))
        return search_results

    def delete(self, document_id: int) -> bool:
        doc = self._db.get(DocumentModel, document_id)
        if doc is None:
            return False
        self._db.delete(doc)
        self._db.commit()
        logger.info("Deleted document id=%s", document_id)
        return True
