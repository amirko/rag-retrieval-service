import logging
import os
from abc import ABC, abstractmethod

import requests

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def generate(self, doc_type: str, prompt: str, context: str) -> str:
        """Generate content based on doc type, prompt, and context."""
        pass

    @abstractmethod
    def generate_simple(self, prompt: str, context: str = "") -> str:
        """Generate content based on prompt and optional context."""
        pass


class OllamaClient(LLMClient):
    """Client for Ollama models."""

    def __init__(self, base_url: str = "http://localhost:11435", model: str = "mistral"):
        self.base_url = base_url
        self.model = model

    def generate(self, doc_type: str, prompt: str, context: str) -> str:
        """Generate document using Ollama."""
        system_prompt = f"You are a document generator. Generate a {doc_type} based on the provided context and prompt."
        full_prompt = f"{system_prompt}\n\nContext:\n{context}\n\nPrompt:\n{prompt}"

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": full_prompt, "stream": False},
                timeout=300,
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            logger.error("Ollama generation failed: %s", e)
            raise

    def generate_simple(self, prompt: str, context: str = "") -> str:
        """Generate content using Ollama with just prompt and optional context."""
        if context:
            full_prompt = f"Context:\n{context}\n\nPrompt:\n{prompt}"
        else:
            full_prompt = prompt

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": full_prompt, "stream": False},
                timeout=300,
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            logger.error("Ollama generation failed: %s", e)
            raise


class OpenAIClient(LLMClient):
    """Client for OpenAI models."""

    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

    def generate(self, doc_type: str, prompt: str, context: str) -> str:
        """Generate document using OpenAI."""
        import openai

        openai.api_key = self.api_key
        system_prompt = f"You are a document generator. Generate a {doc_type} based on the provided context and prompt."
        full_prompt = f"Context:\n{context}\n\nPrompt:\n{prompt}"

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt},
                ],
                temperature=0.1,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("OpenAI generation failed: %s", e)
            raise

    def generate_simple(self, prompt: str, context: str = "") -> str:
        """Generate content using OpenAI with just prompt and optional context."""
        import openai

        openai.api_key = self.api_key
        if context:
            full_prompt = f"Context:\n{context}\n\nPrompt:\n{prompt}"
        else:
            full_prompt = prompt

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": full_prompt},
                ],
                temperature=0.1,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("OpenAI generation failed: %s", e)
            raise


def get_llm_client() -> LLMClient:
    """Factory function to return the appropriate LLM client based on configuration."""
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "openai":
        logger.info("Using OpenAI LLM client")
        return OpenAIClient()
    else:
        # Default to Ollama
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "llama2")
        logger.info("Using Ollama LLM client base_url=%s model=%s", base_url, model)
        return OllamaClient(base_url=base_url, model=model)