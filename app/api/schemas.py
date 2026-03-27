from typing import List

from pydantic import BaseModel, Field


class IndexRequest(BaseModel):
    content: str = Field(..., description="The text content to index")
    url: str = Field(..., description="Source URL for the document")


class IndexResponse(BaseModel):
    id: int


class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query")
    top_k: int = Field(5, ge=1, le=100, description="Number of results to return")


class QueryResultItem(BaseModel):
    id: int
    content: str
    url: str
    score: float


QueryResponse = List[QueryResultItem]
