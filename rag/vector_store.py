"""
Vector store management using ChromaDB + Google Generative AI Embeddings.

Provides persistent storage that survives API server restarts.
Vector store is created once via ingest.py, then loaded at runtime.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings

from config.settings import settings
from core.exceptions import VectorStoreNotFoundError, ConfigurationError
logger = logging.getLogger(__name__)


def _get_embeddings() -> GoogleGenerativeAIEmbeddings | OpenAIEmbeddings:
    """Create a Google Generative AI embeddings instance."""
    if not settings.is_api_key_configured():
        raise ConfigurationError(
            "GEMINI_API_KEY chưa được cấu hình. Không thể tạo embeddings."
        )
    if settings.AI_PROVIDER == "fpt":
        return OpenAIEmbeddings(
            model=settings.active_embedding_model(),
            api_key=settings.active_api_key(),
            base_url=settings.FPT_BASE_URL,
            # FPT accepts strings/string arrays, not the token-id arrays that
            # LangChain's OpenAI adapter normally sends after tokenization.
            check_embedding_ctx_length=False,
        )
    return GoogleGenerativeAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        # ``api_key`` is the current langchain-google-genai 4.x argument.
        api_key=settings.GEMINI_API_KEY,
        # Do not inherit GOOGLE_GENAI_USE_VERTEXAI or other global Google
        # configuration from the shell. This application uses a Gemini
        # Developer API key, not Vertex AI OAuth credentials.
        vertexai=False,
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
    batch_size: Optional[int] = None,
    sleep_between_batches: Optional[float] = None,
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

    batch_size = max(batch_size or settings.EMBEDDING_BATCH_SIZE, 1)
    sleep_between_batches = max(
        sleep_between_batches
        if sleep_between_batches is not None
        else settings.EMBEDDING_REQUEST_INTERVAL_SECONDS,
        0.0,
    )

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
        last_rate_limit_error: Exception | None = None
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
                    last_rate_limit_error = exc
                    # Gemini often includes an exact retry delay in the error
                    # message. Prefer it over a fixed wait so free-tier runs
                    # resume as soon as the quota window allows.
                    import re
                    retry_match = re.search(r"retry in ([0-9.]+)s", str(exc), re.IGNORECASE)
                    suggested_wait = float(retry_match.group(1)) + 2 if retry_match else 60.0
                    wait_sec = max(suggested_wait, sleep_between_batches) * attempt
                    logger.warning(
                        "Rate limit hit (429). Retrying batch %d/%d in %.0fs "
                        "(Attempt %d/%d). API detail: %s",
                        idx, total_batches, wait_sec, attempt, max_retries, str(exc)[:600],
                    )
                    time.sleep(wait_sec)
                else:
                    raise exc
        else:
            raise RuntimeError(
                f"Gemini embedding quota vẫn bị giới hạn sau {max_retries} lần thử. "
                "Kiểm tra quota/billing của API key hoặc thử lại sau."
            ) from last_rate_limit_error

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
