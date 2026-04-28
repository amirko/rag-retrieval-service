import logging
import os
from typing import Protocol, Optional
from urllib.parse import urlparse
from io import BytesIO

import requests

logger = logging.getLogger(__name__)


class StorageClient(Protocol):
    def fetch_text(self, path: str) -> str:
        """Return text content for the given path/URI."""


class LocalStorageClient:
    def fetch_text(self, path: str) -> str:
        if path.startswith("file://"):
            path = path[len("file://") :]
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()


class HTTPStorageClient:
    def fetch_text(self, path: str) -> str:
        resp = requests.get(path, timeout=30)
        resp.raise_for_status()
        return resp.text


class S3StorageClient:
    def __init__(self, boto3_session=None):
        try:
            import boto3  # lazy import
        except Exception as e:
            logger.error("boto3 is required for S3 access: %s", e)
            raise
        self.boto3 = boto3
        self.session = boto3_session or boto3.Session()

    def fetch_text(self, path: str) -> str:
        parsed = urlparse(path)
        bucket = parsed.netloc
        key = parsed.path.lstrip("/")
        s3 = self.session.client("s3")
        obj = s3.get_object(Bucket=bucket, Key=key)
        body = obj["Body"].read()
        return body.decode("utf-8")


class DropboxStorageClient:
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("DROPBOX_API_TOKEN")
        if not self.token:
            raise RuntimeError("DROPBOX_API_TOKEN not set for DropboxStorageClient")

    def fetch_text(self, path: str) -> str:
        # path can be a dropbox path like /folder/file.txt or a shared link (https://...)
        parsed = urlparse(path)
        headers = {"Authorization": f"Bearer {self.token}"}
        if parsed.scheme in ("http", "https") and "dropbox.com" in parsed.netloc:
            # treat as shared link
            url = "https://content.dropboxapi.com/2/sharing/get_shared_link_file"
            headers.update({"Dropbox-API-Arg": f'{{"url":"{path}"}}'})
            resp = requests.post(url, headers=headers, timeout=60)
            resp.raise_for_status()
            return resp.content.decode("utf-8")
        else:
            # treat as dropbox path
            url = "https://content.dropboxapi.com/2/files/download"
            headers.update({"Dropbox-API-Arg": f'{{"path":"{path}"}}'})
            resp = requests.post(url, headers=headers, timeout=60)
            resp.raise_for_status()
            return resp.content.decode("utf-8")


def get_storage_client(protocol: Optional[str] = None, url: Optional[str] = None) -> StorageClient:
    """
    Factory that returns the appropriate StorageClient.
    Prefer explicit `protocol` (one of: "local", "http", "https", "s3", "dropbox").
    If protocol is None, infer from the URL.
    """
    proto = (protocol or "").strip().lower()

    if not proto:
        if not url:
            proto = "local"
        else:
            parsed = urlparse(url)
            if parsed.scheme in ("http", "https"):
                # explicit http(s)
                if "dropbox.com" in parsed.netloc:
                    proto = "dropbox"
                else:
                    proto = "http"
            elif parsed.scheme == "s3":
                proto = "s3"
            elif parsed.scheme in ("file", ""):
                proto = "local"
            else:
                # unknown scheme: default to http
                proto = "http"

    if proto in ("local", "file"):
        return LocalStorageClient()
    if proto in ("http", "https"):
        return HTTPStorageClient()
    if proto == "s3":
        return S3StorageClient()
    if proto == "dropbox":
        return DropboxStorageClient()
    # fallback
    return HTTPStorageClient()


def extract_text_from_bytes(data: bytes, file_type: str) -> str:
    """
    Extract text from bytes, given the file type (extension, e.g. '.pdf', '.docx', '.txt').
    """
    ext = file_type.lower()
    if ext == ".pdf":
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=data, filetype="pdf")
            return "\n\n".join(page.get_text("text") for page in doc)
        except Exception:
            pass
    if ext == ".docx":
        try:
            from docx import Document as DocxDocument
            doc = DocxDocument(BytesIO(data))
            return "\n\n".join(p.text for p in doc.paragraphs)
        except Exception:
            pass
    # fallback: try decode as utf-8
    try:
        return data.decode("utf-8")
    except Exception:
        return ""


def fetch_text_from_storage(path: str, protocol: str = None):
    """
    Fetch file bytes and file type from storage, then extract text using extract_text_from_bytes.
    Returns the extracted text.
    """
    client = get_storage_client(protocol=protocol, url=path)
    # Get file extension/type
    _, ext = os.path.splitext(path)
    # Fetch bytes from storage
    data = client.fetch_bytes(path) if hasattr(client, "fetch_bytes") else client.fetch_text(path).encode("utf-8")
    # Extract text from bytes
    return extract_text_from_bytes(data, ext)