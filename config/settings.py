"""
Application settings for FINORA AI Business Advisor.
Loads configuration from environment variables via python-dotenv.
"""
import os
import json
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
    TREND_IMPORT_DATE: str = os.getenv("TREND_IMPORT_DATE", "")

    # ------------------------------------------------------------------ #
    # LLM generation
    # ------------------------------------------------------------------ #
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    ADAPTIVE_RESPONSE_TEMPERATURE: float = min(
        0.7,
        max(0.5, float(os.getenv("ADAPTIVE_RESPONSE_TEMPERATURE", "0.6"))),
    )
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
    AUTH_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("AUTH_RATE_LIMIT_PER_MINUTE", "10"))
    MAX_HISTORY_MESSAGES: int = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
    MAX_REQUEST_BYTES: int = int(os.getenv("MAX_REQUEST_BYTES", "1048576"))
    MAX_UPLOAD_BYTES: int = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
    RAW_UPLOAD_RETENTION_HOURS: int = int(os.getenv("RAW_UPLOAD_RETENTION_HOURS", "24"))
    RAW_UPLOAD_DIR: str = os.getenv("RAW_UPLOAD_DIR", "data/uploads")

    # Primary production authentication: signed short-lived web token plus a
    # separate server-to-server credential. Legacy API keys are migration-only.
    AUTH_REQUIRED: bool = os.getenv("AUTH_REQUIRED", "true").lower() in ("1", "true", "yes")
    WEB_TOKEN_SECRET: str = os.getenv("WEB_TOKEN_SECRET", "")
    WEB_TOKEN_ISSUER: str = os.getenv("WEB_TOKEN_ISSUER", "finora-web")
    WEB_TOKEN_AUDIENCE: str = os.getenv("WEB_TOKEN_AUDIENCE", "finora-ai")
    WEB_TOKEN_ALGORITHM: str = os.getenv("WEB_TOKEN_ALGORITHM", "HS256")
    WEB_TOKEN_LEEWAY_SECONDS: int = int(os.getenv("WEB_TOKEN_LEEWAY_SECONDS", "15"))
    FINORA_SERVICE_KEY: str = os.getenv("FINORA_SERVICE_KEY", "")
    ENABLE_LEGACY_API_KEY: bool = os.getenv(
        "ENABLE_LEGACY_API_KEY",
        "false" if os.getenv("ENVIRONMENT", "development").lower() == "production" else "true",
    ).lower() in ("1", "true", "yes")
    TENANT_API_KEYS_JSON: str = os.getenv("TENANT_API_KEYS_JSON", "")
    DEFAULT_TENANT_ID: str = os.getenv("DEFAULT_TENANT_ID", "default")
    DEFAULT_USER_ID: str = os.getenv("DEFAULT_USER_ID", "api-user")
    DEFAULT_SHOP_ID: str = os.getenv("DEFAULT_SHOP_ID", "default")
    PII_HASH_SECRET: str = os.getenv("PII_HASH_SECRET", "")
    TENANT_DATA_DIR: str = os.getenv("TENANT_DATA_DIR", "data/tenants")
    AUDIT_LOG_FILE: str = os.getenv("AUDIT_LOG_FILE", "logs/audit.log")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()
    ENABLE_DEMO: bool = os.getenv(
        "ENABLE_DEMO", "false" if os.getenv("ENVIRONMENT", "development").lower() == "production" else "true"
    ).lower() in ("1", "true", "yes")
    ENABLE_API_DOCS: bool = os.getenv(
        "ENABLE_API_DOCS", "false" if os.getenv("ENVIRONMENT", "development").lower() == "production" else "true"
    ).lower() in ("1", "true", "yes")

    # Relational persistence. SQLite is suitable for local development/tests;
    # staging and production must use PostgreSQL.
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/finora.db")
    AUTO_CREATE_SCHEMA: bool = os.getenv(
        "AUTO_CREATE_SCHEMA",
        "false" if os.getenv("ENVIRONMENT", "development").lower() == "production" else "true",
    ).lower() in ("1", "true", "yes")

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
    def get_tenant_data_dir(cls) -> Path:
        return cls.BASE_DIR / cls.TENANT_DATA_DIR

    @classmethod
    def get_raw_upload_dir(cls) -> Path:
        path = Path(cls.RAW_UPLOAD_DIR)
        return path if path.is_absolute() else cls.BASE_DIR / path

    @classmethod
    def tenant_credentials(cls) -> list[dict]:
        """Parse server-managed tenant credentials without logging secrets."""
        if not cls.TENANT_API_KEYS_JSON.strip():
            return []
        try:
            value = json.loads(cls.TENANT_API_KEYS_JSON)
        except json.JSONDecodeError as exc:
            raise EnvironmentError("TENANT_API_KEYS_JSON không phải JSON hợp lệ.") from exc
        if not isinstance(value, list):
            raise EnvironmentError("TENANT_API_KEYS_JSON phải là một JSON array.")
        return value

    @classmethod
    def validate_security(cls) -> None:
        if cls.ENVIRONMENT == "production":
            if not cls.AUTH_REQUIRED:
                raise EnvironmentError("AUTH_REQUIRED phải bật trong production.")
            if "*" in cls.ALLOWED_ORIGINS:
                raise EnvironmentError("Không được dùng wildcard CORS trong production.")
            if not cls.PII_HASH_SECRET or len(cls.PII_HASH_SECRET) < 32:
                raise EnvironmentError("PII_HASH_SECRET production phải có ít nhất 32 ký tự.")
            if not cls.WEB_TOKEN_SECRET or len(cls.WEB_TOKEN_SECRET) < 32:
                raise EnvironmentError("WEB_TOKEN_SECRET production phải có ít nhất 32 ký tự.")
            if not cls.FINORA_SERVICE_KEY or len(cls.FINORA_SERVICE_KEY) < 32:
                raise EnvironmentError("FINORA_SERVICE_KEY production phải có ít nhất 32 ký tự.")
            if cls.WEB_TOKEN_ALGORITHM != "HS256":
                raise EnvironmentError("WEB_TOKEN_ALGORITHM hiện chỉ hỗ trợ HS256.")
            if cls.DATABASE_URL.startswith("sqlite"):
                raise EnvironmentError("Production phải dùng PostgreSQL qua DATABASE_URL.")
            if cls.AI_SERVER_API_KEY and len(cls.AI_SERVER_API_KEY) < 32:
                raise EnvironmentError("AI_SERVER_API_KEY production phải có ít nhất 32 ký tự.")
            for credential in cls.tenant_credentials():
                if len(str(credential.get("api_key", ""))) < 32:
                    raise EnvironmentError("Mỗi tenant API key production phải có ít nhất 32 ký tự.")
        has_web_auth = bool(cls.WEB_TOKEN_SECRET and cls.FINORA_SERVICE_KEY)
        has_legacy_auth = cls.ENABLE_LEGACY_API_KEY and bool(
            cls.AI_SERVER_API_KEY or cls.tenant_credentials()
        )
        if cls.AUTH_REQUIRED and not has_web_auth and not has_legacy_auth:
            raise EnvironmentError(
                "Authentication đang bật nhưng chưa cấu hình WEB_TOKEN_SECRET + "
                "FINORA_SERVICE_KEY hoặc legacy API key được cho phép."
            )

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
