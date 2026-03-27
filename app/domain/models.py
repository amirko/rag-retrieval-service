from dataclasses import dataclass
from datetime import datetime


@dataclass
class Document:
    id: int
    content: str
    url: str
    created_at: datetime


@dataclass
class DocumentSearchResult:
    id: int
    content: str
    url: str
    score: float
