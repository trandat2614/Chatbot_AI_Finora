"""
Document retriever for the RAG pipeline.

Wraps ChromaDB similarity search with metadata enrichment.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from langchain_chroma import Chroma
else:
    Chroma = Any

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
    tenant_scope: str = "public"


def retrieve_documents(
    query: str,
    vector_store: Chroma,
    top_k: Optional[int] = None,
    expected_tenant_scope: str | None = "public",
    metadata_filter: dict[str, Any] | None = None,
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
        selected_filter = metadata_filter
        if selected_filter is None and expected_tenant_scope is not None:
            selected_filter = {"tenant_scope": expected_tenant_scope}
        results_with_scores = vector_store.similarity_search_with_relevance_scores(
            query, k=k, filter=selected_filter
        )
    except Exception as exc:
        logger.warning("Similarity search failed: %s. Falling back to plain search.", exc)
        selected_filter = metadata_filter
        if selected_filter is None and expected_tenant_scope is not None:
            selected_filter = {"tenant_scope": expected_tenant_scope}
        docs = vector_store.similarity_search(query, k=k, filter=selected_filter)
        results_with_scores = [(doc, None) for doc in docs]

    chunks = []
    for doc, score in results_with_scores:
        meta = doc.metadata
        scope = str(meta.get("tenant_scope", "public"))
        if expected_tenant_scope is not None and scope != expected_tenant_scope:
            logger.error("Blocked cross-tenant RAG chunk")
            continue
        chunks.append(
            RetrievedChunk(
                content=doc.page_content,
                source=meta.get("source", "unknown"),
                filename=meta.get("filename", "unknown"),
                file_type=meta.get("file_type", "unknown"),
                relevance_score=float(score) if score is not None else None,
                tenant_scope=scope,
            )
        )

    logger.debug("Retrieved %d chunks for query: %s", len(chunks), query[:50])
    return chunks
