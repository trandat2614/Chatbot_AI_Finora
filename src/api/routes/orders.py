"""Tenant-scoped order lookup and statistics endpoints."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from src.api.dependencies.context import require_auth_context
from src.api.dependencies.services import commerce_repository
from src.api.routes.common import meta
from src.repositories.commerce_repository import SQLAlchemyCommerceRepository
from src.schemas.api import (
    OrderData,
    OrderLookupData,
    OrderLookupResponse,
    OrderStatisticsData,
    OrderStatisticsResponse,
)
from src.security.audit import audit_event
from src.security.auth import AuthContext
from src.services.order_analytics_service import OrderAnalyticsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["v1-orders"])
Platform = Literal["shopee", "tiktok_shop", "lazada"]


@router.get("/orders/{order_id}", response_model=OrderLookupResponse)
def get_order(
    order_id: str,
    request: Request,
    platform: Platform | None = None,
    context: AuthContext = Depends(require_auth_context),
    repository: SQLAlchemyCommerceRepository = Depends(commerce_repository),
) -> OrderLookupResponse:
    normalized_id = order_id.strip()
    if not normalized_id or len(normalized_id) > 200:
        raise HTTPException(
            status_code=422,
            detail={"code": "INVALID_ORDER_ID", "message": "Mã đơn hàng không hợp lệ."},
        )
    matches = repository.get_orders_by_external_id(
        context.tenant_id, context.shop_id, normalized_id, platform
    )
    logger.info(
        "order_lookup_api matches=%s request_id=%s",
        len(matches),
        request.state.request_id,
    )
    audit_event(
        "order_lookup",
        context,
        outcome="found" if matches else "not_found",
        resource="orders",
        details={"request_id": request.state.request_id, "match_count": len(matches)},
    )
    if not matches:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "ORDER_NOT_FOUND",
                "message": "Không tìm thấy đơn hàng trong shop hiện tại.",
            },
        )
    if len(matches) > 1:
        platforms = sorted({str(item["platform"]) for item in matches})
        raise HTTPException(
            status_code=409,
            detail={
                "code": "ORDER_PLATFORM_AMBIGUOUS",
                "message": "Mã đơn tồn tại trên nhiều nền tảng; hãy chọn platform: "
                + ", ".join(platforms),
            },
        )
    return OrderLookupResponse(
        data=OrderLookupData(order=OrderData(**matches[0])), meta=meta(request)
    )


@router.get("/analytics/orders/summary", response_model=OrderStatisticsResponse)
def order_statistics(
    request: Request,
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
    platform: Platform | None = None,
    status: str | None = Query(default=None, min_length=1, max_length=200),
    context: AuthContext = Depends(require_auth_context),
    repository: SQLAlchemyCommerceRepository = Depends(commerce_repository),
) -> OrderStatisticsResponse:
    if start_at and end_at and start_at >= end_at:
        raise HTTPException(
            status_code=422,
            detail={"code": "INVALID_DATE_RANGE", "message": "start_at phải trước end_at."},
        )
    result = OrderAnalyticsService().summarize(
        repository.load_orders(context.tenant_id, context.shop_id),
        start_at=start_at,
        end_at=end_at,
        platform=platform,
        status=status,
    )
    audit_event(
        "order_statistics",
        context,
        resource="analytics",
        details={"request_id": request.state.request_id, "record_count": result["total_orders"]},
    )
    return OrderStatisticsResponse(data=OrderStatisticsData(**result), meta=meta(request))
