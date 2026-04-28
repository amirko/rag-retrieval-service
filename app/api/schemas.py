from typing import List, Optional

from pydantic import BaseModel, Field


class IndexRequest(BaseModel):
    url: str = Field(..., description="Storage URL or path for the document (s3://..., https://..., /local/path)")
    protocol: Optional[str] = Field(None, description="Optional storage protocol hint: s3, http, local, dropbox")
    doc_type: Optional[str] = Field(None, description="Optional document type for filtering / indexing")


class IndexResponse(BaseModel):
    id: int


class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query")
    top_k: int = Field(5, ge=1, le=100, description="Number of results to return")
    doc_type: Optional[str] = Field(None, description="Optional document type to filter by")


class QueryResultItem(BaseModel):
    id: int
    content: str
    url: str
    score: float


QueryResponse = List[QueryResultItem]


class GenerateDocumentRequest(BaseModel):
    doc_type: str = Field(..., description="Type of document to generate")
    prompt: str = Field(..., description="User input/instructions for generation")
    top_k: int = Field(5, ge=1, le=100, description="Number of documents to use as context")


class GenerateDocumentResponse(BaseModel):
    content: str   # the generated document
