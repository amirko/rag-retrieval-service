import logging
from typing import List

import openai

from app.core.config import EMBEDDING_DIMENSIONS, EMBEDDING_MODEL, OPENAI_API_KEY

logger = logging.getLogger(__name__)

_client = openai.OpenAI(api_key=OPENAI_API_KEY)


def get_embedding(text: str) -> List[float]:
    """Return the embedding vector for *text* using the configured OpenAI model."""
    logger.debug("Generating embedding for text length=%d", len(text))
    response = _client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL,
        dimensions=EMBEDDING_DIMENSIONS,
    )
    return response.data[0].embedding
