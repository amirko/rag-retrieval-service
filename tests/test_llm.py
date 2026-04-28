from app.services.llm import get_llm_client

def test_get_llm_client_ollama(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    client = get_llm_client()
    assert hasattr(client, "generate")

def test_get_llm_client_openai(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    client = get_llm_client()
    assert hasattr(client, "generate")