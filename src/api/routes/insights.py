"""Tenant-bound AI Business Insights endpoints."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from services.insights.service import InsightService, InsightStatus, StoredInsight
from src.api.dependencies.context import require_auth_context, require_write_role
from src.api.dependencies.services import insights_service
from src.schemas.insights import (
    GenerateInsightsRequest,
    InsightItem,
    InsightsResponse,
    UpdateInsightRequest,
)
from src.security.audit import audit_event
from src.security.auth import AuthContext

router = APIRouter(prefix="/api/insights", tags=["ai-insights"])


def _response(
    items: list[StoredInsight], empty_reason: str | None = None
) -> InsightsResponse:
    generated_at = max(
        (item.created_at for item in items),
        default=datetime.now(timezone.utc),
    )
    return InsightsResponse(
        items=[InsightItem(**item.model_dump()) for item in items],
        generated_at=generated_at,
        empty_reason=empty_reason,  # type: ignore[arg-type]
    )


@router.get("", response_model=InsightsResponse)
def list_insights(
    request: Request,
    limit: int = Query(default=5, ge=1, le=50),
    status: InsightStatus | None = Query(default="new"),
    context: AuthContext = Depends(require_auth_context),
    service: InsightService = Depends(insights_service),
) -> InsightsResponse:
    items = service.repository.list(
        context.tenant_id, context.shop_id, limit=limit, status=status
    )
    audit_event(
        "insight_list",
        context,
        resource="ai_insights",
        details={"request_id": request.state.request_id, "record_count": len(items)},
    )
    empty_reason = None
    if not items and not service.repository.has_any(context.tenant_id, context.shop_id):
        empty_reason = "not_enough_data"
    return _response(items, empty_reason)


@router.post("/generate", response_model=InsightsResponse)
def generate_insights(
    payload: GenerateInsightsRequest,
    request: Request,
    context: AuthContext = Depends(require_auth_context),
    service: InsightService = Depends(insights_service),
) -> InsightsResponse:
    require_write_role(context)
    items, empty_reason = service.generate(
        context.tenant_id,
        context.shop_id,
        payload.period,
        force=payload.force,
    )
    audit_event(
        "insight_generate",
        context,
        resource="ai_insights",
        details={
            "request_id": request.state.request_id,
            "record_count": len(items),
            "period": payload.period,
            "forced": payload.force,
        },
    )
    return _response(items, empty_reason)


@router.patch("/{insight_id}", response_model=InsightsResponse)
def update_insight(
    insight_id: str,
    payload: UpdateInsightRequest,
    request: Request,
    context: AuthContext = Depends(require_auth_context),
    service: InsightService = Depends(insights_service),
) -> InsightsResponse:
    require_write_role(context)
    item = service.repository.update_status(
        context.tenant_id, context.shop_id, insight_id, payload.status
    )
    if item is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "INSIGHT_NOT_FOUND", "message": "Không tìm thấy insight."},
        )
    audit_event(
        "insight_status_update",
        context,
        resource="ai_insights",
        details={"request_id": request.state.request_id, "status": payload.status},
    )
    return _response([item])
