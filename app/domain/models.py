from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Document:
    id: int
    url: str
    created_at: datetime
    protocol: Optional[str] = None
    doc_type: Optional[str] = None
    embedding: Optional[List[float]] = None


@dataclass
class DocumentSearchResult:
    id: int
    url: str
    score: float
    doc_type: Optional[str] = None
