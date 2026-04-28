from app.services.embedding import get_embedding_client

def test_get_embedding_client_ollama(monkeypatch):
    monkeypatch.setenv("EMBEDDING_PROVIDER", "ollama")
    client = get_embedding_client()
    assert hasattr(client, "embed")

def test_get_embedding_client_openai(monkeypatch):
    monkeypatch.setenv("EMBEDDING_PROVIDER", "openai")
    client = get_embedding_client()
    assert hasattr(client, "embed")