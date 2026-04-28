import os
import sys
from pathlib import Path

# Load .env before any app imports
from dotenv import load_dotenv

env_file = Path(__file__).parent.parent / ".env"
load_dotenv(env_file)

# Set defaults for test environment if vars are missing
os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/rag_db_test")
os.environ.setdefault("OPENAI_API_KEY", "sk-test-key")
os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11435")
os.environ.setdefault("OLLAMA_EMBEDDING_BASE_URL", "http://localhost:11434")
os.environ.setdefault("OLLAMA_MODEL", "mistral")
os.environ.setdefault("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
os.environ.setdefault("EMBEDDING_PROVIDER", "ollama")
os.environ.setdefault("LLM_PROVIDER", "ollama")
os.environ.setdefault("LOG_LEVEL", "INFO")