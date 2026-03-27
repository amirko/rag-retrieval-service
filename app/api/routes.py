import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.schemas import IndexRequest, IndexResponse, QueryRequest, QueryResultItem
from app.db.session import get_db
from app.repositories.postgres import PostgresDocumentRepository
from app.services.document import DocumentService

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_service(db: Session = Depends(get_db)) -> DocumentService:
    repo = PostgresDocumentRepository(db)
    return DocumentService(repo)


@router.post("/index", response_model=IndexResponse, status_code=status.HTTP_201_CREATED)
def index_document(
    request: IndexRequest,
    service: DocumentService = Depends(_get_service),
) -> IndexResponse:
    """Generate an embedding for *content* and store the document."""
    try:
        doc = service.index(content=request.content, url=request.url)
        return IndexResponse(id=doc.id)
    except Exception as exc:
        logger.exception("Failed to index document")
        raise HTTPException(status_code=500, detail="Failed to index document") from exc


@router.post("/query", response_model=List[QueryResultItem])
def query_documents(
    request: QueryRequest,
    service: DocumentService = Depends(_get_service),
) -> List[QueryResultItem]:
    """Return the most similar documents for the given query."""
    try:
        results = service.query(query=request.query, top_k=request.top_k)
        return [
            QueryResultItem(id=r.id, content=r.content, url=r.url, score=r.score)
            for r in results
        ]
    except Exception as exc:
        logger.exception("Failed to query documents")
        raise HTTPException(status_code=500, detail="Failed to query documents") from exc


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    service: DocumentService = Depends(_get_service),
) -> Response:
    """Delete a document by id."""
    try:
        found = service.delete(document_id)
    except Exception as exc:
        logger.exception("Failed to delete document id=%s", document_id)
        raise HTTPException(status_code=500, detail="Failed to delete document") from exc
    if not found:
        raise HTTPException(status_code=404, detail="Document not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
