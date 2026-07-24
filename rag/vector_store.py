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
    batch_size: int = 25,
    sleep_between_batches: float = 2.0,
) -> Chroma:
    """Create and persist a ChromaDB vector store from documents in batches.

    Args:
        documents: Chunked documents to embed and store.
        db_dir: Persist directory. Defaults to settings.VECTOR_DB_DIR.
        batch_size: Number of documents to embed per API batch call.
        sleep_between_batches: Pause in seconds between batches to avoid API rate limits.

    Returns:
        Chroma vector store instance.
    """
    import time
    import shutil

    path = db_dir or settings.get_vector_db_dir()
    path.mkdir(parents=True, exist_ok=True)

    # Clean existing store files to prevent duplication or stale indexes
    for child in path.glob("*"):
        try:
            if child.is_file():
                child.unlink()
            elif child.is_dir():
                shutil.rmtree(child)
        except Exception as err:
            logger.warning("Could not clean old file %s: %s", child, err)

    embeddings = _get_embeddings()
    logger.info(
        "Creating vector store in %s with %d documents (batch_size=%d).",
        path,
        len(documents),
        batch_size,
    )

    store = None
    total_batches = (len(documents) + batch_size - 1) // batch_size
    for idx, i in enumerate(range(0, len(documents), batch_size), 1):
        batch = documents[i : i + batch_size]
        logger.info("Embedding batch %d/%d (%d docs)...", idx, total_batches, len(batch))
        
        max_retries = 5
        for attempt in range(1, max_retries + 1):
            try:
                if store is None:
                    store = Chroma.from_documents(
                        documents=batch,
                        embedding=embeddings,
                        collection_name=settings.CHROMA_COLLECTION_NAME,
                        persist_directory=str(path),
                    )
                else:
                    store.add_documents(batch)
                break
            except Exception as exc:
                if "429" in str(exc) or "RESOURCE_EXHAUSTED" in str(exc):
                    wait_sec = 15 * attempt
                    logger.warning("Rate limit hit (429). Retrying batch %d/%d in %ds (Attempt %d/%d)...", idx, total_batches, wait_sec, attempt, max_retries)
                    time.sleep(wait_sec)
                else:
                    raise exc

        if i + batch_size < len(documents):
            time.sleep(sleep_between_batches)

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