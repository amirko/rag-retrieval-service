import logging
import os
from typing import List

import requests

from app.core.config import EMBEDDING_DIMENSIONS, EMBEDDING_MODEL, OPENAI_API_KEY

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """Abstract base class for embedding clients."""

    def embed(self, text: str) -> List[float]:
        """Return embedding vector for the given text."""
        raise NotImplementedError


class OpenAIEmbeddingClient(EmbeddingClient):
    """OpenAI embedding client."""

    def __init__(self, api_key: str = OPENAI_API_KEY, model: str = EMBEDDING_MODEL):
        import openai

        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def embed(self, text: str) -> List[float]:
        """Return embedding vector using OpenAI."""
        logger.debug("Generating embedding for text length=%d model=%s", len(text), self.model)
        response = self.client.embeddings.create(
            input=text,
            model=self.model,
            dimensions=EMBEDDING_DIMENSIONS,
        )
        return response.data[0].embedding


class OllamaEmbeddingClient(EmbeddingClient):
    """Ollama embedding client."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "nomic-embed-text"):
        self.base_url = base_url
        self.model = model

    def embed(self, text: str) -> List[float]:
        """Return embedding vector using Ollama."""
        logger.debug("Generating embedding for text length=%d model=%s", len(text), self.model)
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text},
                timeout=60,
            )
            response.raise_for_status()
            return response.json().get("embedding", [])
        except Exception as e:
            logger.error("Ollama embedding failed: %s", e)
            raise


def get_embedding_client() -> EmbeddingClient:
    """Factory function to return the appropriate embedding client based on configuration."""
    provider = os.getenv("EMBEDDING_PROVIDER", "ollama").lower()

    if provider == "openai":
        logger.info("Using OpenAI embedding client")
        return OpenAIEmbeddingClient()
    else:
        # Default to Ollama
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
        logger.info("Using Ollama embedding client base_url=%s model=%s", base_url, model)
        return OllamaEmbeddingClient(base_url=base_url, model=model)


def get_embedding(text: str) -> List[float]:
    """Return the embedding vector for *text* using the configured embedding provider."""
    client = get_embedding_client()
    return client.embed(text)
