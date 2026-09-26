"""Production-facing FastAPI server for Finora AI Business Advisor."""
from __future__ import annotations

import logging
import secrets
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Literal

from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from config.settings import settings
from core.exceptions import FinoraBaseError
from core.llm_client import LLMClient
from rag.vector_store import load_vector_store, vector_store_exists
from services.advisor_service import AdvisorService
from utils.logger import setup_logging

setup_logging(level=logging.INFO)
logger = logging.getLogger(__name__)


class HistoryMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=10_000)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: str = Field(min_length=1, max_length=10_000)
    orderSummary: dict[str, Any] | None = None
    history: list[HistoryMessage] = Field(default_factory=list)


class Source(BaseModel):
    source: str
    filename: str | None = None
    file_type: str | None = None
    score: float | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    rag_context_used: bool
    warnings: list[str] = Field(default_factory=list)


class UploadResponse(BaseModel):
    filename: str
    documents: int
    chunks: int
    message: str


class RateLimiter:
    """In-memory limiter for a single server process."""

    def __init__(self, limit: int) -> None:
        self.limit = max(limit, 1)
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, identity: str) -> bool:
        now = time.monotonic()
        bucket = self._requests[identity]
        while bucket and now - bucket[0] >= 60:
            bucket.popleft()
        if len(bucket) >= self.limit:
            return False
        bucket.append(now)
        return True


rate_limiter = RateLimiter(settings.RATE_LIMIT_PER_MINUTE)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate_api_key()
    app.state.llm_client = LLMClient()
    app.state.vector_store = None
    if vector_store_exists():
        try:
            app.state.vector_store = load_vector_store()
        except Exception:
            logger.exception("Could not load vector store; chat will run without RAG")
    else:
        logger.warning("Vector store is missing. Run `python ingest.py` to enable RAG.")
    yield


app = FastAPI(
    title="Finora AI Server",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
)
app.mount("/demo", StaticFiles(directory=str(Path(__file__).parent / "web"), html=True), name="demo")


@app.middleware("http")
async def request_logging(request: Request, call_next):
    started = time.perf_counter()
    content_length = request.headers.get("content-length")
    max_bytes = 10 * 1024 * 1024 if request.url.path == "/api/knowledge/upload" else settings.MAX_REQUEST_BYTES
    if content_length and content_length.isdigit() and int(content_length) > max_bytes:
        return JSONResponse(status_code=413, content={"detail": "Request quá lớn."})
    response = await call_next(request)
    logger.info(
        "%s %s status=%s duration_ms=%.1f",
        request.method,
        request.url.path,
        response.status_code,
        (time.perf_counter() - started) * 1000,
    )
    return response


@app.get("/", include_in_schema=False)
def demo_home() -> RedirectResponse:
    """Open the browser demo when visiting the server root."""
    return RedirectResponse(url="/demo/")


def authorize_and_limit(request: Request, x_api_key: str | None = Header(None)) -> None:
    if settings.AI_SERVER_API_KEY and not secrets.compare_digest(
        x_api_key or "", settings.AI_SERVER_API_KEY
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key không hợp lệ.")
    identity = request.client.host if request.client else "unknown"
    if not rate_limiter.allow(identity):
        raise HTTPException(status_code=429, detail="Quá nhiều yêu cầu. Vui lòng thử lại sau.")


@app.get("/health")
def health(request: Request) -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "finora-ai-server",
        "model": settings.active_llm_model(),
        "rag_ready": getattr(request.app.state, "vector_store", None) is not None,
    }


@app.post("/api/chat", response_model=ChatResponse, dependencies=[Depends(authorize_and_limit)])
def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    if len(payload.history) > settings.MAX_HISTORY_MESSAGES:
        raise HTTPException(
            status_code=422,
            detail=f"history chỉ được chứa tối đa {settings.MAX_HISTORY_MESSAGES} tin nhắn.",
        )
    advisor = AdvisorService(
        llm_client=request.app.state.llm_client,
        vector_store=request.app.state.vector_store,
    )
    result = advisor.answer(
        question=payload.message,
        order_summary=payload.orderSummary,
        history=[item.model_dump() for item in payload.history],
    )
    if "Dịch vụ Gemini tạm thời không khả dụng." in result.warnings:
        raise HTTPException(status_code=502, detail="Dịch vụ AI tạm thời không khả dụng.")
    return ChatResponse(
        answer=result.answer,
        sources=[Source(**source) for source in result.sources],
        rag_context_used=result.rag_context_used,
        warnings=result.warnings,
    )


@app.post(
    "/api/knowledge/upload",
    response_model=UploadResponse,
    dependencies=[Depends(authorize_and_limit)],
)
async def upload_knowledge(request: Request, file: UploadFile = File(...)) -> UploadResponse:
    """Add one supported document and rebuild the local RAG index."""
    from rag.document_loader import SUPPORTED_EXTENSIONS, load_all_documents
    from rag.text_splitter import split_documents
    from rag.vector_store import create_vector_store

    original_name = file.filename or ""
    filename = Path(original_name).name
    if not filename or filename != original_name or Path(filename).suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Chỉ hỗ trợ file .md, .txt, .pdf, .xlsx, .xls hoặc .csv.")

    contents = await file.read()
    await file.close()
    if not contents:
        raise HTTPException(status_code=422, detail="File đang rỗng.")
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File tối đa 10 MB.")

    knowledge_dir = settings.get_knowledge_dir()
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    destination = knowledge_dir / filename
    destination.write_bytes(contents)

    try:
        documents = load_all_documents(knowledge_dir)
        chunks = split_documents(documents)
        if not chunks:
            raise HTTPException(status_code=422, detail="Không thể đọc nội dung từ file đã upload.")
        request.app.state.vector_store = create_vector_store(chunks, settings.get_vector_db_dir())
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Knowledge upload/indexing failed for %s", filename)
        raise HTTPException(status_code=502, detail="Không thể tạo embeddings. Kiểm tra GEMINI_API_KEY.") from exc

    return UploadResponse(
        filename=filename,
        documents=len(documents),
        chunks=len(chunks),
        message="Đã upload và nạp lại kho kiến thức.",
    )


@app.exception_handler(FinoraBaseError)
async def finora_error_handler(_request: Request, exc: FinoraBaseError):
    logger.warning("Finora error: %s", type(exc).__name__)
    return JSONResponse(status_code=502, content={"detail": "Dịch vụ AI tạm thời không khả dụng."})


@app.exception_handler(Exception)
async def unexpected_error_handler(_request: Request, exc: Exception):
    logger.exception("Unhandled server error")
    return JSONResponse(status_code=500, content={"detail": "Lỗi máy chủ nội bộ."})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host=settings.HOST, port=settings.PORT)
