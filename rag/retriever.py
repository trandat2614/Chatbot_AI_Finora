"""
Document retriever for the RAG pipeline.

Wraps ChromaDB similarity search with metadata enrichment.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from langchain_chroma import Chroma

from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    """A retrieved document chunk with its metadata."""

    content: str
    source: str
    filename: str
    file_type: str
    relevance_score: Optional[float] = None


def retrieve_documents(
    query: str,
    vector_store: Chroma,
    top_k: Optional[int] = None,
) -> list[RetrievedChunk]:
    """Retrieve the most relevant document chunks for a query.

    Args:
        query: The user's question or search query.
        vector_store: Loaded Chroma vector store.
        top_k: Number of results to return. Defaults to settings.RETRIEVAL_TOP_K.

    Returns:
        List of RetrievedChunk objects sorted by relevance.
    """
    k = top_k or settings.RETRIEVAL_TOP_K

    try:
        results_with_scores = vector_store.similarity_search_with_relevance_scores(
            query, k=k
        )
    except Exception as exc:
        logger.warning("Similarity search failed: %s. Falling back to plain search.", exc)
        docs = vector_store.similarity_search(query, k=k)
        results_with_scores = [(doc, None) for doc in docs]

    chunks = []
    for doc, score in results_with_scores:
        meta = doc.metadata
        chunks.append(
            RetrievedChunk(
                content=doc.page_content,
                source=meta.get("source", "unknown"),
                filename=meta.get("filename", "unknown"),
                file_type=meta.get("file_type", "unknown"),
                relevance_score=float(score) if score is not None else None,
            )
        )

    logger.debug("Retrieved %d chunks for query: %s", len(chunks), query[:50])
    return chunks
