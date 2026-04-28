import pytest
from unittest.mock import MagicMock, patch
from app.services.document import DocumentService

@pytest.fixture
def repo():
    return MagicMock()

@pytest.fixture
def service(repo):
    return DocumentService(repo)

def test_infer_doc_type(service):
    with patch("app.services.document.get_llm_client") as mock_llm:
        mock_llm.return_value.generate.return_value = "contract"
        doc_type = service._infer_doc_type("This is a contract.")
        assert doc_type == "contract"

def test_index_fetches_and_embeds(service):
    with patch("app.services.document.fetch_text_from_storage") as fetch, \
         patch("app.services.document.get_embedding") as embed, \
         patch.object(service, "_infer_doc_type") as infer:
        fetch.return_value = "hello"
        embed.return_value = [0.1, 0.2]
        infer.return_value = "summary"
        service._repo.add.return_value = MagicMock(id=1)
        doc = service.index(url="file.txt")
        assert doc.id == 1
        fetch.assert_called_once()
        embed.assert_called_once_with("hello")

def test_generate_document_fetches_text(service):
    with patch("app.services.document.get_embedding") as embed, \
         patch("app.services.document.get_llm_client") as llm, \
         patch("app.services.document.fetch_text_from_storage") as fetch:
        embed.return_value = [0.1, 0.2]
        service._repo.search.return_value = [MagicMock(url="file.txt", protocol="local")]
        fetch.return_value = "doc text"
        llm.return_value.generate.return_value = "generated"
        result = service.generate_document(doc_type="report", prompt="make a report")
        assert "generated" in result