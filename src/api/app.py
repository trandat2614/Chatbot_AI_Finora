"""FastAPI application factory and cross-cutting production middleware."""
from __future__ import annotations

import logging
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from config.settings import settings
from core.exceptions import FinoraBaseError
from core.llm_client import LLMClient
from rag.vector_store import load_vector_store, vector_store_exists
from src.db.session import get_database
from src.repositories.commerce_repository import SQLAlchemyCommerceRepository
from src.schemas.api import ErrorDetail, ErrorResponse, ResponseMeta
from src.services.raw_upload_service import RawUploadService
from utils.logger import setup_logging

setup_logging(level=logging.INFO)
logger = logging.getLogger(__name__)


def _error(request: Request, status_code: int, code: str, message: str) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    payload = ErrorResponse(
        error=ErrorDetail(code=code, message=message),
        meta=ResponseMeta(request_id=request_id),
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump(mode="json"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate_security()
    database = get_database()
    if settings.AUTO_CREATE_SCHEMA:
        database.create_schema()
    app.state.database = database
    app.state.commerce_repository = SQLAlchemyCommerceRepository(database)
    RawUploadService().cleanup_expired()
    app.state.llm_client = LLMClient() if settings.is_api_key_configured() else None
    app.state.vector_store = None
    if vector_store_exists():
        try:
            app.state.vector_store = load_vector_store()
        except Exception:
            logger.exception("Could not load public vector store")
    else:
        logger.warning("Public vector store is missing; RAG will be unavailable.")
    yield
    database.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Finora AI Server",
        version="4.0.0",
        docs_url="/docs" if settings.ENABLE_API_DOCS else None,
        redoc_url="/redoc" if settings.ENABLE_API_DOCS else None,
        lifespan=lifespan,
        responses={
            401: {"model": ErrorResponse},
            403: {"model": ErrorResponse},
            404: {"model": ErrorResponse},
            413: {"model": ErrorResponse},
            415: {"model": ErrorResponse},
            422: {"model": ErrorResponse},
            429: {"model": ErrorResponse},
            500: {"model": ErrorResponse},
            502: {"model": ErrorResponse},
            503: {"model": ErrorResponse},
        },
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-Finora-Service-Key",
            "X-API-Key",
        ],
    )

    @app.middleware("http")
    async def security_and_request_id(request: Request, call_next):
        started = time.perf_counter()
        request.state.request_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex}"
        content_length = request.headers.get("content-length")
        is_upload = request.url.path.endswith("/data/import") or request.url.path.endswith(
            "/knowledge/upload"
        )
        max_bytes = settings.MAX_UPLOAD_BYTES + 64 * 1024 if is_upload else settings.MAX_REQUEST_BYTES
        if content_length and content_length.isdigit() and int(content_length) > max_bytes:
            return _error(request, 413, "REQUEST_TOO_LARGE", "Request vượt quá kích thước cho phép.")
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        if request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        logger.info(
            "%s %s status=%s duration_ms=%.1f request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            (time.perf_counter() - started) * 1000,
            request.state.request_id,
        )
        return response

    @app.exception_handler(HTTPException)
    async def http_error_handler(request: Request, exc: HTTPException):
        detail = exc.detail
        if isinstance(detail, dict):
            code = str(detail.get("code", "HTTP_ERROR"))
            message = str(detail.get("message", "Yêu cầu không hợp lệ."))
        else:
            code, message = "HTTP_ERROR", str(detail)
        return _error(request, exc.status_code, code, message)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, _exc: RequestValidationError):
        return _error(request, 422, "VALIDATION_ERROR", "Request không đúng schema.")

    @app.exception_handler(FinoraBaseError)
    async def finora_error_handler(request: Request, exc: FinoraBaseError):
        logger.warning("Finora error: %s", type(exc).__name__)
        return _error(request, 502, "AI_UPSTREAM_ERROR", "Dịch vụ AI tạm thời không khả dụng.")

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, _exc: Exception):
        logger.exception("Unhandled server error")
        return _error(request, 500, "INTERNAL_ERROR", "Lỗi máy chủ nội bộ.")

    @app.get("/health", tags=["operations"])
    def health(request: Request) -> dict:
        return {
            "status": "ok",
            "service": "finora-ai-server",
            "model": settings.active_llm_model(),
            "rag_ready": getattr(request.app.state, "vector_store", None) is not None,
        }

    @app.get("/", include_in_schema=False)
    def root():
        if settings.ENABLE_DEMO:
            return RedirectResponse(url="/demo/")
        return {"service": "finora-ai-server", "status": "ok"}

    if settings.ENABLE_DEMO:
        app.mount(
            "/demo",
            StaticFiles(directory=str(settings.BASE_DIR / "web"), html=True),
            name="demo",
        )

    from src.api.routes import legacy, v1

    app.include_router(v1.router)
    app.include_router(legacy.router)
    return app
