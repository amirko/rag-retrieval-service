from typing import List, Protocol, runtime_checkable

from app.domain.models import Document, DocumentSearchResult


@runtime_checkable
class DocumentRepository(Protocol):
    """Abstract interface for document persistence and vector search.

    Implement this protocol to swap out the storage backend (e.g. Postgres,
    Pinecone, Weaviate) without changing any service-layer code.
    """

    def add(self, content: str, url: str, embedding: List[float]) -> Document:
        """Persist a new document and return the created domain object."""
        ...

    def search(
        self, query_embedding: List[float], top_k: int
    ) -> List[DocumentSearchResult]:
        """Return the *top_k* most similar documents for the given embedding."""
        ...

    def delete(self, document_id: int) -> bool:
        """Delete a document by id.  Return True if found, False otherwise."""
        ...
