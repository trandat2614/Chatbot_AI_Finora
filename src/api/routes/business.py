"""Versioned deterministic business analytics endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from src.api.dependencies.context import require_auth_context
from src.api.dependencies.services import commerce_repository
from src.api.routes.common import meta
from src.repositories.commerce_repository import SQLAlchemyCommerceRepository
from src.schemas.api import (
    BusinessHealthData,
    BusinessHealthResponse,
    BusinessOverviewData,
    BusinessOverviewResponse,
    RevenueLeakageData,
    RevenueLeakageResponse,
)
from src.security.audit import audit_event
from src.security.auth import AuthContext
from src.services.business_health_service import BusinessHealthService
from src.services.metric_service import MetricService
from src.services.revenue_leakage_service import RevenueLeakageService

router = APIRouter(prefix="/api/v1/business", tags=["v1-business"])


@router.get("/overview", response_model=BusinessOverviewResponse)
def overview(
    request: Request,
    context: AuthContext = Depends(require_auth_context),
    repository: SQLAlchemyCommerceRepository = Depends(commerce_repository),
) -> BusinessOverviewResponse:
    metrics = MetricService().calculate(
        repository.load_orders(context.tenant_id, context.shop_id)
    )
    products = repository.list_products(context.tenant_id, context.shop_id)
    return BusinessOverviewResponse(
        data=BusinessOverviewData(
            status=metrics.status, metrics=metrics, product_count=len(products)
        ),
        meta=meta(request),
    )


@router.get("/health", response_model=BusinessHealthResponse)
def health(
    request: Request,
    context: AuthContext = Depends(require_auth_context),
    repository: SQLAlchemyCommerceRepository = Depends(commerce_repository),
) -> BusinessHealthResponse:
    metrics = MetricService().calculate(
        repository.load_orders(context.tenant_id, context.shop_id)
    )
    result = BusinessHealthService().analyze(metrics)
    audit_event("business_health", context, resource="analytics", details={"status": result["status"]})
    return BusinessHealthResponse(data=BusinessHealthData(**result), meta=meta(request))


@router.get("/revenue-leakage", response_model=RevenueLeakageResponse)
def revenue_leakage(
    request: Request,
    context: AuthContext = Depends(require_auth_context),
    repository: SQLAlchemyCommerceRepository = Depends(commerce_repository),
) -> RevenueLeakageResponse:
    result = RevenueLeakageService().analyze(
        repository.load_orders(context.tenant_id, context.shop_id)
    )
    audit_event("revenue_leakage", context, resource="analytics", details={"status": result["status"]})
    return RevenueLeakageResponse(data=RevenueLeakageData(**result), meta=meta(request))
