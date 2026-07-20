"""
Document loader for RAG pipeline.

Supports Markdown (.md), plain text (.txt) and PDF (.pdf) files.
Each document preserves metadata: source, filename, file_type.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_core.documents import Document

from utils.file_helpers import list_files

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = [".md", ".txt", ".pdf"]


def load_document(file_path: Path) -> list[Document]:
    """Load a single document and attach metadata.

    Args:
        file_path: Absolute path to the document.

    Returns:
        List of LangChain Document objects (PDF may return multiple pages).
    """
    ext = file_path.suffix.lower()

    if ext in (".md", ".txt"):
        loader = TextLoader(str(file_path), encoding="utf-8")
        docs = loader.load()
    elif ext == ".pdf":
        loader = PyPDFLoader(str(file_path))
        docs = loader.load()
    else:
        logger.warning("Unsupported file type: %s", file_path)
        return []

    # Attach structured metadata
    for doc in docs:
        doc.metadata.update({
            "source": str(file_path),
            "filename": file_path.name,
            "file_type": ext.lstrip("."),
        })

    return docs


def load_all_documents(directory: Path | str) -> list[Document]:
    """Load all supported documents from a directory.

    Args:
        directory: Path to the knowledge base directory.

    Returns:
        All loaded Document objects.
    """
    d = Path(directory)
    if not d.is_dir():
        logger.error("Knowledge directory not found: %s", d)
        return []

    files = list_files(d, extensions=SUPPORTED_EXTENSIONS)
    logger.info("Found %d documents in %s", len(files), d)

    all_docs: list[Document] = []
    for file_path in files:
        try:
            docs = load_document(file_path)
            all_docs.extend(docs)
            logger.debug("Loaded %d page(s) from %s", len(docs), file_path.name)
        except Exception as exc:
            logger.warning("Failed to load %s: %s", file_path.name, exc)

    logger.info("Total documents loaded: %d", len(all_docs))
    return all_docs
