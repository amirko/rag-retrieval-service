import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_index_route(monkeypatch):
    monkeypatch.setattr("app.services.document.DocumentService.index", lambda self, **kwargs: type("Obj", (), {"id": 1})())
    resp = client.post("/index", json={"url": "file.txt"})
    assert resp.status_code == 201
    assert resp.json()["id"] == 1

def test_query_route(monkeypatch):
    monkeypatch.setattr("app.services.document.DocumentService.query", lambda self, **kwargs: [])
    resp = client.post("/query", json={"query": "test", "top_k": 1})
    assert resp.status_code == 200