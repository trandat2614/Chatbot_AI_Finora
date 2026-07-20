"""
Text splitter configuration for the RAG pipeline.

Uses RecursiveCharacterTextSplitter which respects document structure
(paragraphs, sentences) before resorting to character-level splits.
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config.settings import settings


def create_text_splitter() -> RecursiveCharacterTextSplitter:
    """Create a configured text splitter.

    Returns:
        RecursiveCharacterTextSplitter instance.
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n\n", "\n", ".", " ", ""],
        length_function=len,
    )


def split_documents(documents: list[Document]) -> list[Document]:
    """Split a list of documents into chunks.

    Args:
        documents: Raw documents from the loader.

    Returns:
        Chunked documents with metadata preserved.
    """
    splitter = create_text_splitter()
    chunks = splitter.split_documents(documents)
    return chunks
