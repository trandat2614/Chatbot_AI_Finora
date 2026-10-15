"""Strict request/response contracts for AI Business Insights."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class InsightAPIModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class GenerateInsightsRequest(InsightAPIModel):
    period: Literal["7d", "30d", "90d"] = "30d"
    force: bool = False


class UpdateInsightRequest(InsightAPIModel):
    status: Literal["new", "read", "dismissed"]


class InsightItem(InsightAPIModel):
    id: str
    type: str
    severity: Literal["info", "warning", "critical", "positive"]
    title: str = Field(max_length=60)
    summary: str
    recommendation: str
    evidence: dict
    created_at: datetime


class InsightsResponse(InsightAPIModel):
    items: list[InsightItem]
    generated_at: datetime
    empty_reason: Literal["not_enough_data"] | None = None
