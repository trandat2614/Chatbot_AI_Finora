"""Strict public /api/v1 request and response contracts."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.commerce import (
    ActionItem,
    AnalysisStatus,
    BusinessAlert,
    MetricResult,
)


class APIModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ResponseMeta(APIModel):
    request_id: str


class ErrorDetail(APIModel):
    code: str
    message: str


class ErrorResponse(APIModel):
    success: Literal[False] = False
    error: ErrorDetail
    meta: ResponseMeta


class ImportData(APIModel):
    import_id: str
    platform: str | None = None
    filename: str
    status: Literal["PENDING", "PROCESSING", "COMPLETED", "FAILED"]
    total_rows: int = 0
    accepted_rows: int = 0
    rejected_rows: int = 0
    orders_created: int = 0
    order_items_created: int = 0
    duplicate: bool = False
    warnings: list[str] = Field(default_factory=list)
    created_at: datetime | None = None
    completed_at: datetime | None = None


class DataImportResponse(APIModel):
    success: Literal[True] = True
    data: ImportData
    meta: ResponseMeta


class ImportStatusResponse(DataImportResponse):
    pass


class BusinessOverviewData(APIModel):
    status: AnalysisStatus
    metrics: MetricResult
    product_count: int


class BusinessOverviewResponse(APIModel):
    success: Literal[True] = True
    data: BusinessOverviewData
    meta: ResponseMeta


class BusinessHealthData(APIModel):
    status: AnalysisStatus
    metrics: MetricResult | None = None
    alerts: list[BusinessAlert] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)


class BusinessHealthResponse(APIModel):
    success: Literal[True] = True
    data: BusinessHealthData
    meta: ResponseMeta


class LeakageComponents(APIModel):
    price_and_seller_discount: float = 0
    seller_discount_reported: float = 0
    platform_discount: float = 0
    refund: float = 0
    platform_fee: float = 0
    transaction_fee: float = 0
    service_fee: float = 0
    shipping_fee: float = 0


class RevenueLeakageData(APIModel):
    status: AnalysisStatus
    gmv: float | None = None
    collected_revenue: float | None = None
    net_revenue: float | None = None
    total_leakage: float | None = None
    leakage_rate: float | None = None
    components: LeakageComponents | None = None
    assumptions: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)


class RevenueLeakageResponse(APIModel):
    success: Literal[True] = True
    data: RevenueLeakageData
    meta: ResponseMeta


class ProductRecord(APIModel):
    sku: str
    product_id: str | None = None
    product_name: str
    margin: float | None = None
    inventory: int | None = None


class ProductListData(APIModel):
    status: AnalysisStatus
    products: list[ProductRecord] = Field(default_factory=list)


class ProductListResponse(APIModel):
    success: Literal[True] = True
    data: ProductListData
    meta: ResponseMeta


class ProductResponse(APIModel):
    success: Literal[True] = True
    data: ProductRecord
    meta: ResponseMeta


class ProductMetrics(APIModel):
    revenue: float
    order_count: int
    units_sold: int
    cancellation_rate: float
    refund_rate: float
    discount_dependency: float


class ProductDiagnosis(APIModel):
    sku: str
    classification: str
    metrics: ProductMetrics
    confidence: float = Field(ge=0, le=1)


class ProductAnalysisData(APIModel):
    status: AnalysisStatus
    products: list[ProductDiagnosis] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)


class ProductAnalysisResponse(APIModel):
    success: Literal[True] = True
    data: ProductAnalysisData
    meta: ResponseMeta


class MarketTrendItem(APIModel):
    capture_date: str
    platform: str
    category: str
    period: str
    rank: int
    product_name: str
    shop: str
    price: float
    sales_growth: float
    sales_30d: int
    rating: float | str | None = None
    url: str
    trend_state: str


class MarketTrendData(APIModel):
    status: AnalysisStatus
    source: str
    category: str
    period: str
    items: list[MarketTrendItem] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class MarketTrendResponse(APIModel):
    success: Literal[True] = True
    data: MarketTrendData
    meta: ResponseMeta


class FashionAttributes(APIModel):
    product_type: str | None = None
    style: str | None = None
    fit: str | None = None
    material: str | None = None
    sleeve: str | None = None
    color: str | None = None
    pattern: str | None = None
    season: str | None = None


class OpportunityEvidence(APIModel):
    name_similarity: float
    market_sales_growth: float | None = None
    shop_order_count: int
    shop_sales_growth: float | None = None
    refund_rate: float
    cancellation_rate: float
    discount_dependency: float
    price_position_percent: float | None = None


class OpportunityItem(APIModel):
    sku: str
    product_name: str
    fashion_attributes: FashionAttributes
    matched_market_product: str
    trend_state: str
    opportunity_score: float
    confidence: float = Field(ge=0, le=1)
    recommendation: str
    missing_metrics: list[str]
    evidence: OpportunityEvidence


class OpportunityData(APIModel):
    status: AnalysisStatus
    opportunities: list[OpportunityItem] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)


class OpportunityResponse(APIModel):
    success: Literal[True] = True
    data: OpportunityData
    meta: ResponseMeta


class ActionPlanData(APIModel):
    status: AnalysisStatus
    actions: list[ActionItem] = Field(default_factory=list)


class ActionPlanResponse(APIModel):
    success: Literal[True] = True
    data: ActionPlanData
    meta: ResponseMeta


class HistoryMessage(APIModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=10_000)


class ChatRequest(APIModel):
    message: str = Field(min_length=1, max_length=10_000)
    history: list[HistoryMessage] = Field(default_factory=list)
    period: Literal["today", "7d", "30d"] | None = None
    category: Literal["nam", "nu"] | None = None
    platform: Literal["shopee", "tiktok_shop", "lazada"] | None = None


class Source(APIModel):
    source: str
    type: Literal["rag", "database", "market"] = "rag"
    name: str | None = None
    period: dict[str, Any] | None = None
    filename: str | None = None
    file_type: str | None = None
    score: float | None = None


class ChatData(APIModel):
    answer: str
    sources: list[Source]
    rag_context_used: bool
    warnings: list[str] = Field(default_factory=list)
    analysis_status: AnalysisStatus
    intent: str
    data_grounded: bool = False
    tool_context_used: bool = False


class ChatResponse(APIModel):
    success: Literal[True] = True
    data: ChatData
    meta: ResponseMeta


class PlannerRequest(APIModel):
    category: Literal["nam", "nu"] = "nam"
    period: Literal["week", "month"] = "week"
    objective: Literal[
        "awareness", "new_customer_acquisition", "conversion", "retention", "clearance"
    ] = "conversion"


class SalesPlanItem(APIModel):
    sku: str
    product_name: str
    objective: str
    period: str
    product_strategy: str
    opportunity_score: float
    actions: list[str]
    numeric_target: float | None = None
    confidence: float
    constraints: list[str]


class SalesPlanData(APIModel):
    status: AnalysisStatus
    period: str | None = None
    objective: str | None = None
    plan: list[SalesPlanItem] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)


class SalesPlanResponse(APIModel):
    success: Literal[True] = True
    data: SalesPlanData
    meta: ResponseMeta


class CommunicationChannel(APIModel):
    objective: str
    product_focus: list[str]
    message_direction: str
    guardrails: list[str]
    content_drafts: list[str]


class CommunicationPlanData(APIModel):
    status: AnalysisStatus
    business_objective: str | None = None
    channels: dict[str, CommunicationChannel] = Field(default_factory=dict)
    missing_fields: list[str] = Field(default_factory=list)


class CommunicationPlanResponse(APIModel):
    success: Literal[True] = True
    data: CommunicationPlanData
    meta: ResponseMeta


class KnowledgeUploadData(APIModel):
    filename: str
    documents: int
    chunks: int
    message: str


class KnowledgeUploadResponse(APIModel):
    success: Literal[True] = True
    data: KnowledgeUploadData
    meta: ResponseMeta
