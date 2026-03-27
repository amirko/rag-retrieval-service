import os


DATABASE_URL: str = os.environ["DATABASE_URL"]
OPENAI_API_KEY: str = os.environ["OPENAI_API_KEY"]
EMBEDDING_MODEL: str = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSIONS: int = int(os.environ.get("EMBEDDING_DIMENSIONS", "1536"))
