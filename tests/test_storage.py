import pytest
from app.services import storage

def test_extract_text_from_bytes_txt():
    text = "hello world"
    result = storage.extract_text_from_bytes(text.encode(), ".txt")
    assert "hello" in result

def test_extract_text_from_bytes_docx(tmp_path):
    pytest.importorskip("docx")
    from docx import Document as DocxDocument
    file = tmp_path / "test.docx"
    doc = DocxDocument()
    doc.add_paragraph("docx content")
    doc.save(file)
    with open(file, "rb") as f:
        data = f.read()
    result = storage.extract_text_from_bytes(data, ".docx")
    assert "docx content" in result

def test_extract_text_from_bytes_pdf(tmp_path):
    pytest.importorskip("fitz")
    import fitz
    file = tmp_path / "test.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "pdf content")
    doc.save(str(file))
    with open(file, "rb") as f:
        data = f.read()
    result = storage.extract_text_from_bytes(data, ".pdf")
    assert "pdf content" in result

def test_get_storage_client_local():
    client = storage.get_storage_client(protocol="local")
    assert hasattr(client, "fetch_text")

def test_get_storage_client_http():
    client = storage.get_storage_client(protocol="http")
    assert hasattr(client, "fetch_text")