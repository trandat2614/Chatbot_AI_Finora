"""Versioned market, opportunity and action-plan endpoints."""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Request

from src.api.dependencies.context import require_auth_context
from src.api.dependencies.services import commerce_repository
from src.api.routes.common import meta
from src.repositories.commerce_repository import SQLAlchemyCommerceRepository
from src.repositories.trend_repository import SQLAlchemyTrendRepository
from src.schemas.api import (
    ActionPlanData,
    ActionPlanResponse,
    MarketTrendData,
    MarketTrendResponse,
    OpportunityData,
    OpportunityResponse,
)
from src.security.audit import audit_event
from src.security.auth import AuthContext
from src.services.action_plan_service import ActionPlanService
from src.services.business_health_service import BusinessHealthService
from src.services.market_trend_service import MarketTrendService
from src.services.metric_service import MetricService
from src.services.opportunity_matching_service import OpportunityMatchingService
from src.services.product_doctor_service import ProductDoctorService
from src.services.revenue_leakage_service import RevenueLeakageService
from src.tools.trend_tools import get_trend_loader

router = APIRouter(prefix="/api/v1", tags=["v1-market"])


def _market(request: Request, category: str, period: str, historical: bool = False) -> dict:
    return MarketTrendService(
        get_trend_loader(), SQLAlchemyTrendRepository(request.app.state.database)
    ).get_trends(
        category, period, historical=historical
    )


@router.get("/market/trends", response_model=MarketTrendResponse)
def market_trends(
    request: Request,
    category: Literal["nam", "nu"] = "nam",
    period: Literal["today", "7d", "30d"] = "7d",
    historical: bool = False,
    context: AuthContext = Depends(require_auth_context),
) -> MarketTrendResponse:
    result = _market(request, category, period, historical)
    audit_event("market_trend", context, resource="public_market_data", details={"status": result["status"]})
    return MarketTrendResponse(data=MarketTrendData(**result), meta=meta(request))


@router.get("/opportunities", response_model=OpportunityResponse)
def opportunities(
    request: Request,
    category: Literal["nam", "nu"] = "nam",
    period: Literal["today", "7d", "30d"] = "7d",
    context: AuthContext = Depends(require_auth_context),
    repository: SQLAlchemyCommerceRepository = Depends(commerce_repository),
) -> OpportunityResponse:
    frame = repository.load_orders(context.tenant_id, context.shop_id)
    result = OpportunityMatchingService().match(
        frame, _market(request, category, period)
    )
    audit_event("product_opportunity", context, resource="analytics", details={"status": result["status"]})
    return OpportunityResponse(data=OpportunityData(**result), meta=meta(request))


@router.get("/action-plan", response_model=ActionPlanResponse)
def action_plan(
    request: Request,
    category: Literal["nam", "nu"] = "nam",
    period: Literal["today", "7d", "30d"] = "7d",
    context: AuthContext = Depends(require_auth_context),
    repository: SQLAlchemyCommerceRepository = Depends(commerce_repository),
) -> ActionPlanResponse:
    frame = repository.load_orders(context.tenant_id, context.shop_id)
    metrics = MetricService().calculate(frame)
    health = BusinessHealthService().analyze(metrics)
    leakage = RevenueLeakageService().analyze(frame)
    products = ProductDoctorService().analyze(frame)
    opportunities_result = OpportunityMatchingService().match(
        frame, _market(request, category, period)
    )
    result = ActionPlanService().generate(
        health, leakage, products, opportunities_result
    )
    audit_event("action_plan", context, resource="recommendation", details={"status": result["status"]})
    return ActionPlanResponse(data=ActionPlanData(**result), meta=meta(request))
