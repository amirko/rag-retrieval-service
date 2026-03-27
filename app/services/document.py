import logging
from typing import List

from app.domain.models import Document, DocumentSearchResult
from app.repositories.interface import DocumentRepository
from app.services.embedding import get_embedding

logger = logging.getLogger(__name__)


class DocumentService:
    """Orchestrates embedding generation and persistence."""

    def __init__(self, repository: DocumentRepository) -> None:
        self._repo = repository

    def index(self, content: str, url: str) -> Document:
        logger.info("Indexing document url=%s", url)
        embedding = get_embedding(content)
        return self._repo.add(content=content, url=url, embedding=embedding)

    def query(self, query: str, top_k: int) -> List[DocumentSearchResult]:
        logger.info("Querying top_k=%d query_len=%d", top_k, len(query))
        embedding = get_embedding(query)
        return self._repo.search(query_embedding=embedding, top_k=top_k)

    def delete(self, document_id: int) -> bool:
        logger.info("Deleting document id=%d", document_id)
        return self._repo.delete(document_id)
