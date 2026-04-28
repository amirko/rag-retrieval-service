import logging
from typing import List, Optional

from app.domain.models import Document, DocumentSearchResult
from app.repositories.interface import DocumentRepository
from app.services.embedding import get_embedding
from app.services.llm import get_llm_client
from app.services.storage import fetch_text_from_storage
import json
import re

logger = logging.getLogger(__name__)


class DocumentService:
    """Orchestrates embedding generation and persistence."""

    def __init__(self, repository: DocumentRepository) -> None:
        self._repo = repository

    def _infer_doc_type(self, content: str) -> str:
        """Infer document type from content using LLM."""
        logger.info("Inferring document type from content")
        prompt = f"""Analyze the following document and classify it into ONE of these types:
- report
- contract
- NDA
- arrest
- summary
- faq
- manual
- other
- law suite
- legal brief
- memorandum
- affidavit
- will
- power of attorney
- trust

Document excerpt (first 500 chars):
{content[:500]}

Respond with only the document type, nothing else."""

        llm_client = get_llm_client()
        doc_type = llm_client.generate(
            doc_type="classification",
            prompt=prompt,
            context=""
        ).strip().lower()
        
        logger.info("Inferred doc_type=%s", doc_type)
        return doc_type

    def index(self, url: str, protocol: Optional[str] = None, doc_type: Optional[str] = None) -> Document:
        """
        Index a document by fetching its content from storage (local/http/s3/dropbox)
        then generating embeddings and persisting metadata + embedding.

        - url: storage path or URL (e.g. s3://bucket/key, https://..., /path/to/file)
        - protocol: optional explicit protocol hint ("s3", "http", "local", "dropbox")
        - doc_type: optional; if None, will be inferred from the fetched content
        """
        # fetch content from storage
        logger.info("Fetching content for url=%s protocol=%s", url, protocol)
        content = fetch_text_from_storage(url, protocol=protocol)

        # infer doc_type if not provided
        if not doc_type:
            doc_type = self._infer_doc_type(content)

        logger.info("Indexing document url=%s doc_type=%s", url, doc_type)
        embedding = get_embedding(content)

        # persist: repository may accept content and protocol; adapt if your repo signature differs
        return self._repo.add(url=url, embedding=embedding, doc_type=doc_type, protocol=protocol)

    def query(self, query: str, top_k: int, doc_type: Optional[str] = None) -> List[DocumentSearchResult]:
        logger.info("Querying top_k=%d query_len=%d doc_type=%s", top_k, len(query), doc_type)
        embedding = get_embedding(query)
        return self._repo.search(query_embedding=embedding, top_k=top_k, doc_type=doc_type)


    def delete(self, document_id: int) -> bool:
        logger.info("Deleting document id=%d", document_id)
        return self._repo.delete(document_id)
    

    def generate_document(self, doc_type: str, prompt: str, top_k: int = 5, use_structure: bool = False) -> str:
        """Generate a document of a specific type based on ingested documents and a user prompt.

        Notes:
        - Repository.search() may return metadata only (ids/urls). We fetch text for each hit
          (use stored content if present on the result, otherwise fetch from storage using the url/protocol).
        - Fetching is done in parallel to reduce latency.
        """
        logger.info("Generating document doc_type=%s top_k=%d", doc_type, top_k)

        # Retrieve relevant documents using the prompt as query, filtered by doc_type
        embedding = get_embedding(prompt)
        results = self._repo.search(query_embedding=embedding, top_k=top_k, doc_type=doc_type)
        mode = "template_based"

        # Fallback: if no documents found with doc_type, search without type filter
        if not results:
            logger.warning("No documents found for doc_type=%s, searching without type filter", doc_type)
            results = self._repo.search(query_embedding=embedding, top_k=top_k)
            mode = "style_based"

        if not results:
            logger.warning("No documents found for generation")
            return ""

        # Fetch text for each result (use result.content if present, otherwise fetch via storage)
        from concurrent.futures import ThreadPoolExecutor

        def _fetch_text_for_result(r):
            text = getattr(r, "content", None)
            if text:
                return text
            storage_path = getattr(r, "url", None)
            protocol = getattr(r, "protocol", None)
            if not storage_path:
                return ""
            try:
                return fetch_text_from_storage(storage_path, protocol=protocol)
            except Exception:
                logger.exception("Failed to fetch document content for %s", storage_path)
                return ""

        max_workers = min(8, max(1, len(results)))
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            texts = list(ex.map(_fetch_text_for_result, results))

        # Assemble context from retrieved documents (skip empty fetches)
        context_parts = []
        for i, text in enumerate(texts):
            if text:
                context_parts.append(f"[Document {i+1}]\n{text}")
        context = "\n\n".join(context_parts)

        # Use LLM to generate document
        llm_client = get_llm_client()
        generated_content = llm_client.generate(
            doc_type=doc_type, prompt=prompt, context=context
        )

        logger.info("Document generated successfully doc_type=%s mode=%s", doc_type, mode)
        return generated_content



def extract_structure(self, text: str):
    prompt = f"""
    Extract the structure of the following legal document.

    Return ONLY valid JSON in this format:  
    {{
    "sections": ["Section 1", "Section 2", ...]  
    }}

    Rules:
    - Keep order
    - Use concise titles
    - No explanations

    Document:
    {text}
    """
    llm_client = get_llm_client()
    response = llm_client.generate(prompt)  
    return self.parse_structure(response)

def parse_structure(self, response: str):
    """
    Parse LLM response into a list of section titles.
    Handles imperfect JSON outputs.
    """

    # 1. Try direct JSON parsing
    try:
        data = json.loads(response)
        if "sections" in data and isinstance(data["sections"], list):
            return data["sections"]
    except json.JSONDecodeError:
        pass

    # 2. Try to extract JSON substring (common LLM issue)
    try:
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            if "sections" in data:
                return data["sections"]
    except Exception:
        pass

    # 3. Fallback: parse as bullet/line list
    lines = response.split("\n")
    sections = []

    for line in lines:
        line = line.strip()

        # remove bullets / numbering
        line = re.sub(r"^[-*\d\.\)\s]+", "", line)

        if len(line) > 3:
            sections.append(line)

    # 4. Deduplicate + clean
    seen = set()
    clean_sections = []

    for s in sections:
        if s.lower() not in seen:
            seen.add(s.lower())
            clean_sections.append(s)

    return clean_sections if clean_sections else None

def build_prompt(self, query, documents, structure, mode):
    docs_text = "\n\n".join([d.content for d in documents])

    base = f"""
    You are a legal assistant.

    User request:
    {query}

    Context documents:
    {docs_text}
    """

    if mode == "template_based":
        instructions = """
        Use the documents as templates.
        Follow their structure and style.
        Reuse similar clauses where possible.
        """
    else:
        instructions = """
        No exact templates available.
        Use the general style and tone of the documents.
        Create a logical structure.
        """

    if structure:
        instructions += f"\nFollow this structure:\n{structure}"

    return base + instructions
