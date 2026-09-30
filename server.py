"""Finora AI Server bootstrap.

Run with: uvicorn server:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

from config.settings import settings
from src.api.app import create_app
from src.api.dependencies.context import RateLimiter, authorize_shop
from src.schemas.legacy import ChatRequest, ChatResponse, HistoryMessage, Source, UploadResponse

app = create_app()

__all__ = [
    "app",
    "create_app",
    "RateLimiter",
    "authorize_shop",
    "ChatRequest",
    "ChatResponse",
    "HistoryMessage",
    "Source",
    "UploadResponse",
]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host=settings.HOST, port=settings.PORT)
