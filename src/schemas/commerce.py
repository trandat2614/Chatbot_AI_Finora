"""Unified commerce and decision-intelligence response schemas."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AnalysisStatus(str, Enum):
    OK = "OK"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class UnifiedOrderItem(StrictModel):
    platform: Literal["shopee", "tiktok_shop", "lazada"]
    order_id: str = Field(min_length=1, max_length=200)
    order_item_id: str = Field(min_length=1, max_length=200)
    created_at: datetime
    product_id: str | None = Field(default=None, max_length=200)
    seller_sku: str | None = Field(default=None, max_length=200)
    product_name: str = Field(min_length=1, max_length=1000)
    variation: str | None = Field(default=None, max_length=500)
    quantity: int = Field(ge=0, le=1_000_000)
    original_price: float | None = Field(default=None, ge=0)
    selling_price: float = Field(ge=0)
    seller_discount: float = Field(default=0, ge=0)
    platform_discount: float = Field(default=0, ge=0)
    shipping_fee: float = Field(default=0, ge=0)
    platform_fee: float = Field(default=0, ge=0)
    transaction_fee: float = Field(default=0, ge=0)
    service_fee: float = Field(default=0, ge=0)
    refund_amount: float = Field(default=0, ge=0)
    order_status: str = Field(min_length=1, max_length=200)
    cancel_reason: str | None = Field(default=None, max_length=1000)


class MetricResult(StrictModel):
    status: AnalysisStatus
    revenue: float | None = None
    order_count: int | None = None
    units_sold: int | None = None
    aov: float | None = None
    cancellation_rate: float | None = None
    refund_rate: float | None = None
    seller_discount: float | None = None
    marketplace_fee: float | None = None
    net_revenue: float | None = None
    sales_growth: float | None = None
    sales_velocity: float | None = None
    missing_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class BusinessAlert(StrictModel):
    code: str
    severity: Literal["info", "warning", "critical"]
    metric: str
    current_value: float
    baseline: float | None = None
    difference: float | None = None
    entity: str
    explanation: str


class ActionItem(StrictModel):
    priority: int = Field(ge=1, le=5)
    title: str
    problem: str
    evidence: list[str]
    recommendation: str
    expected_impact: str | None = None
    confidence: float = Field(ge=0, le=1)


class PlannerRequest(StrictModel):
    shop_id: str = Field(min_length=1, max_length=200)
    category: Literal["nam", "nu"] = "nam"
    period: Literal["week", "month"] = "week"
    objective: Literal[
        "awareness", "new_customer_acquisition", "conversion", "retention", "clearance"
    ] = "conversion"


class CommunicationPlanRequest(PlannerRequest):
    """The server derives the sales plan; clients cannot inject one."""
