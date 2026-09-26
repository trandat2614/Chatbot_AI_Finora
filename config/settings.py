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
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini").lower()
    FPT_API_KEY: str = os.getenv("FPT_API_KEY", "")
    FPT_BASE_URL: str = os.getenv("FPT_BASE_URL", "https://mkp-api.fptcloud.com/v1")
    FPT_CHAT_MODEL: str = os.getenv("FPT_CHAT_MODEL", "DeepSeek-V4-Flash")
    FPT_EMBEDDING_MODEL: str = os.getenv("FPT_EMBEDDING_MODEL", "Vietnamese_Embedding")

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
    # Stay below the low free-tier Gemini embedding quota by default. Increase
    # this only after confirming the quota for the configured API project.
    EMBEDDING_BATCH_SIZE: int = int(os.getenv("EMBEDDING_BATCH_SIZE", "20"))
    EMBEDDING_REQUEST_INTERVAL_SECONDS: float = float(
        os.getenv("EMBEDDING_REQUEST_INTERVAL_SECONDS", "15")
    )

    # ------------------------------------------------------------------ #
    # LLM generation
    # ------------------------------------------------------------------ #
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2048"))
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "60"))

    # API server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    ALLOWED_ORIGINS: list[str] = [
        value.strip()
        for value in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
        if value.strip()
    ]
    AI_SERVER_API_KEY: str = os.getenv("AI_SERVER_API_KEY", "")
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
    MAX_HISTORY_MESSAGES: int = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
    MAX_REQUEST_BYTES: int = int(os.getenv("MAX_REQUEST_BYTES", "1048576"))

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
        api_key = cls.FPT_API_KEY if cls.AI_PROVIDER == "fpt" else cls.GEMINI_API_KEY
        if not api_key or api_key in (
            "",
            "your_gemini_api_key",
        ):
            raise EnvironmentError(
                "GEMINI_API_KEY chưa được cấu hình.\n"
                "Vui lòng:\n"
                "  1. Sao chép file .env.example thành .env\n"
                "  2. Điền GEMINI_API_KEY vào file .env\n"
                "  3. Khi deploy, đặt GEMINI_API_KEY trong biến môi trường của server."
            )

    @classmethod
    def is_api_key_configured(cls) -> bool:
        """Return True when the API key looks valid (non-empty, non-placeholder)."""
        api_key = cls.FPT_API_KEY if cls.AI_PROVIDER == "fpt" else cls.GEMINI_API_KEY
        return bool(api_key and api_key not in ("", "your_gemini_api_key"))

    @classmethod
    def active_api_key(cls) -> str:
        return cls.FPT_API_KEY if cls.AI_PROVIDER == "fpt" else cls.GEMINI_API_KEY

    @classmethod
    def active_llm_model(cls) -> str:
        return cls.FPT_CHAT_MODEL if cls.AI_PROVIDER == "fpt" else cls.GEMINI_MODEL

    @classmethod
    def active_embedding_model(cls) -> str:
        return cls.FPT_EMBEDDING_MODEL if cls.AI_PROVIDER == "fpt" else cls.EMBEDDING_MODEL


settings = Settings()
