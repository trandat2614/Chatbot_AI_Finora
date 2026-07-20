"""
Vector store management using ChromaDB + Google Generative AI Embeddings.

Provides persistent storage that survives Streamlit reruns.
Vector store is created once via ingest.py, then loaded at runtime.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config.settings import settings
from core.exceptions import VectorStoreNotFoundError, ConfigurationError
logger = logging.getLogger(__name__)


def _get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Create a Google Generative AI embeddings instance."""
    if not settings.is_api_key_configured():
        raise ConfigurationError(
            "GEMINI_API_KEY chưa được cấu hình. Không thể tạo embeddings."
        )
    return GoogleGenerativeAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
    )


def vector_store_exists(db_dir: Optional[Path] = None) -> bool:
    """Check whether a ChromaDB vector store exists on disk.

    Args:
        db_dir: Directory to check. Defaults to settings.VECTOR_DB_DIR.

    Returns:
        True if the store exists and contains data.
    """
    path = db_dir or settings.get_vector_db_dir()
    chroma_sqlite = path / "chroma.sqlite3"
    return chroma_sqlite.exists()


def create_vector_store(
    documents: list[Document],
    db_dir: Optional[Path] = None,
) -> Chroma:
    """Create and persist a ChromaDB vector store from documents.

    Args:
        documents: Chunked documents to embed and store.
        db_dir: Persist directory. Defaults to settings.VECTOR_DB_DIR.

    Returns:
        Chroma vector store instance.
    """
    path = db_dir or settings.get_vector_db_dir()
    path.mkdir(parents=True, exist_ok=True)

    embeddings = _get_embeddings()
    logger.info(
        "Creating vector store in %s with %d documents.",
        path,
        len(documents),
    )

    store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=settings.CHROMA_COLLECTION_NAME,
        persist_directory=str(path),
    )
    logger.info("Vector store created successfully.")
    return store


def load_vector_store(db_dir: Optional[Path] = None) -> Chroma:
    """Load an existing ChromaDB vector store from disk.

    Args:
        db_dir: Persist directory. Defaults to settings.VECTOR_DB_DIR.

    Returns:
        Chroma vector store instance.

    Raises:
        VectorStoreNotFoundError: If the store does not exist.
    """
    path = db_dir or settings.get_vector_db_dir()

    if not vector_store_exists(path):
        raise VectorStoreNotFoundError()

    embeddings = _get_embeddings()
    logger.info("Loading vector store from %s.", path)

    store = Chroma(
        collection_name=settings.CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(path),
    )
    return store


def add_documents(
    store: Chroma,
    documents: list[Document],
) -> None:
    """Add additional documents to an existing vector store.

    Args:
        store: Existing Chroma instance.
        documents: New document chunks to add.
    """
    store.add_documents(documents)
    logger.info("Added %d documents to the vector store.", len(documents))