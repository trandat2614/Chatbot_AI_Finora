"""Deprecated /api compatibility contracts."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class LegacyModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class HistoryMessage(LegacyModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=10_000)


class ChatRequest(LegacyModel):
    message: str = Field(min_length=1, max_length=10_000)
    orderSummary: dict[str, Any] | None = None
    history: list[HistoryMessage] = Field(default_factory=list)
    shop_id: str = Field(default="default", min_length=1, max_length=200)


class Source(LegacyModel):
    source: str
    filename: str | None = None
    file_type: str | None = None
    score: float | None = None


class ChatResponse(LegacyModel):
    answer: str
    sources: list[Source]
    rag_context_used: bool
    warnings: list[str] = Field(default_factory=list)
    analysis_status: Literal["OK", "INSUFFICIENT_DATA"] = "OK"
    intent: str = "GENERAL_CHAT"


class UploadResponse(LegacyModel):
    filename: str
    documents: int
    chunks: int
    message: str
