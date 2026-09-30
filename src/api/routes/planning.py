"""Versioned recommendation-only planning endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from src.api.dependencies.context import require_auth_context
from src.api.routes.common import meta
from src.repositories.recommendation_repository import SQLAlchemyRecommendationRepository
from src.schemas.api import (
    CommunicationPlanData,
    CommunicationPlanResponse,
    PlannerRequest,
    SalesPlanData,
    SalesPlanResponse,
)
from src.security.audit import audit_event
from src.security.auth import AuthContext
from src.services.decision_intelligence_service import DecisionIntelligenceService

router = APIRouter(prefix="/api/v1", tags=["v1-planning"])


def _service(request: Request, context: AuthContext) -> DecisionIntelligenceService:
    return DecisionIntelligenceService(
        context.tenant_id, context.shop_id, request.app.state.commerce_repository
    )


@router.post("/sales-plan", response_model=SalesPlanResponse)
def sales_plan(
    payload: PlannerRequest,
    request: Request,
    context: AuthContext = Depends(require_auth_context),
) -> SalesPlanResponse:
    result = _service(request, context).generate_sales_plan(
        payload.category, payload.period, payload.objective
    )
    SQLAlchemyRecommendationRepository(request.app.state.database).save(
        context, "sales_plan", payload.model_dump(mode="json"), result
    )
    audit_event("sales_plan", context, resource="recommendation", details={"status": result["status"]})
    return SalesPlanResponse(data=SalesPlanData(**result), meta=meta(request))


@router.post("/communication-plan", response_model=CommunicationPlanResponse)
def communication_plan(
    payload: PlannerRequest,
    request: Request,
    context: AuthContext = Depends(require_auth_context),
) -> CommunicationPlanResponse:
    result = _service(request, context).generate_communication_plan(
        payload.category, payload.period, payload.objective
    )
    SQLAlchemyRecommendationRepository(request.app.state.database).save(
        context, "communication_plan", payload.model_dump(mode="json"), result
    )
    audit_event(
        "communication_plan",
        context,
        resource="recommendation",
        details={"status": result["status"]},
    )
    return CommunicationPlanResponse(
        data=CommunicationPlanData(**result), meta=meta(request)
    )
