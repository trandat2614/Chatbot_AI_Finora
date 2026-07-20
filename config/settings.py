"""
Application settings for FINORA AI Business Advisor.
Loads configuration from environment variables via python-dotenv.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if it exists (local development)
load_dotenv()


class Settings:
    """Centralised configuration for the application.

    All values are read from environment variables so that the application
    can be deployed without changing source code.
    """

    # ------------------------------------------------------------------ #
    # Gemini / Google GenAI
    # ------------------------------------------------------------------ #
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")

    # ------------------------------------------------------------------ #
    # RAG / ChromaDB
    # ------------------------------------------------------------------ #
    KNOWLEDGE_DIR: str = os.getenv("KNOWLEDGE_DIR", "knowledge")
    VECTOR_DB_DIR: str = os.getenv("VECTOR_DB_DIR", "vector_db")
    CHROMA_COLLECTION_NAME: str = os.getenv(
        "CHROMA_COLLECTION_NAME", "finora_knowledge"
    )
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "700"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    RETRIEVAL_TOP_K: int = int(os.getenv("RETRIEVAL_TOP_K", "4"))

    # ------------------------------------------------------------------ #
    # LLM generation
    # ------------------------------------------------------------------ #
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2048"))
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "60"))

    # ------------------------------------------------------------------ #
    # Paths (resolved relative to this file's parent's parent)
    # ------------------------------------------------------------------ #
    BASE_DIR: Path = Path(__file__).parent.parent

    @classmethod
    def get_knowledge_dir(cls) -> Path:
        """Return absolute path to the knowledge directory."""
        return cls.BASE_DIR / cls.KNOWLEDGE_DIR

    @classmethod
    def get_vector_db_dir(cls) -> Path:
        """Return absolute path to the vector database directory."""
        return cls.BASE_DIR / cls.VECTOR_DB_DIR

    @classmethod
    def validate_api_key(cls) -> None:
        """Raise a clear error if GEMINI_API_KEY is not configured.

        Raises:
            EnvironmentError: When the API key is missing or is still the
                placeholder value from .env.example.
        """
        if not cls.GEMINI_API_KEY or cls.GEMINI_API_KEY in (
            "",
            "your_gemini_api_key",
        ):
            raise EnvironmentError(
                "GEMINI_API_KEY chưa được cấu hình.\n"
                "Vui lòng:\n"
                "  1. Sao chép file .env.example thành .env\n"
                "  2. Điền GEMINI_API_KEY vào file .env\n"
                "  Hoặc khi deploy Streamlit Cloud:\n"
                "  3. Thêm GEMINI_API_KEY vào Secrets của ứng dụng."
            )

    @classmethod
    def is_api_key_configured(cls) -> bool:
        """Return True when the API key looks valid (non-empty, non-placeholder)."""
        return bool(
            cls.GEMINI_API_KEY
            and cls.GEMINI_API_KEY not in ("", "your_gemini_api_key")
        )


settings = Settings()
