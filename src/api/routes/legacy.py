"""Deprecated /api compatibility wrappers.

These routes preserve existing clients during migration. New Finora web integration
must use /api/v1 and signed web-backend authentication.
"""
from __future__ import annotations

import json
from dataclasses import replace
from typing import Literal

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile

from config.settings import settings
from services.advisor_service import AdvisorService
from src.api.dependencies.context import (
    Identity,
    authorize_shop,
    get_identity,
)
from src.api.routes.common import tenant_rag_store, tenant_vector_store
from src.api.routes.data import import_data as v1_import_data
from src.api.routes.knowledge import upload_knowledge as v1_upload_knowledge
from src.schemas.commerce import CommunicationPlanRequest, PlannerRequest
from src.schemas.legacy import ChatRequest, ChatResponse, Source, UploadResponse
from src.security.audit import audit_event
from src.security.auth import AuthContext
from src.services.decision_intelligence_service import DecisionIntelligenceService

router = APIRouter(prefix="/api", tags=["deprecated"], deprecated=True)


def _context(identity: Identity, shop_id: str) -> AuthContext:
    authorize_shop(identity, shop_id)
    if isinstance(identity, AuthContext):
        return replace(identity, shop_id=shop_id)
    return identity.to_context(shop_id)


@router.post("/chat", response_model=ChatResponse, deprecated=True)
def chat(
    payload: ChatRequest,
    request: Request,
    identity: Identity = Depends(get_identity),
) -> ChatResponse:
    context = _context(identity, payload.shop_id)
    if len(payload.history) > settings.MAX_HISTORY_MESSAGES:
        raise HTTPException(status_code=422, detail="history vượt quá giới hạn.")
    if request.app.state.llm_client is None:
        raise HTTPException(status_code=503, detail="Dịch vụ AI chưa được cấu hình.")
    advisor = AdvisorService(
        llm_client=request.app.state.llm_client,
        vector_store=request.app.state.vector_store,
        tenant_vector_store=tenant_vector_store(context),
        tenant_scope=tenant_rag_store.scope_token(context.tenant_id, context.shop_id),
        tenant_id=context.tenant_id,
        shop_id=context.shop_id,
        decision_service=DecisionIntelligenceService(
            context.tenant_id, context.shop_id, request.app.state.commerce_repository
        ),
    )
    result = advisor.answer(
        question=payload.message,
        order_summary=payload.orderSummary,
        history=[item.model_dump() for item in payload.history],
        # Compatibility bridge for the existing Finora Web. The advisor only
        # accepts allowlisted numeric metrics and post-validates LLM numbers.
        allow_legacy_summary=True,
    )
    audit_event("ai_analysis", context, resource="chat", details={"intent": result.intent, "status": result.analysis_status})
    return ChatResponse(
        answer=result.answer,
        sources=[Source(**item) for item in result.sources],
        rag_context_used=result.rag_context_used,
        warnings=result.warnings,
        analysis_status=result.analysis_status,
        intent=result.intent,
        data_grounded=result.data_grounded,
        tool_context_used=result.tool_context_used,
    )


@router.post("/data/import", deprecated=True)
async def import_data(
    request: Request,
    shop_id: str = Query(min_length=1, max_length=200),
    file: UploadFile = File(...),
    identity: Identity = Depends(get_identity),
) -> dict:
    context = _context(identity, shop_id)
    response = await v1_import_data(
        request, file, context, request.app.state.commerce_repository
    )
    item = response.data
    return {
        "status": "OK" if item.status == "COMPLETED" else item.status,
        "import_id": item.import_id,
        "platform": item.platform,
        "record_count": item.accepted_rows,
        "rejected_rows": item.rejected_rows,
        "warnings": item.warnings,
    }


@router.post("/knowledge/upload", response_model=UploadResponse, deprecated=True)
async def upload_knowledge(
    request: Request,
    shop_id: str = Query(min_length=1, max_length=200),
    file: UploadFile = File(...),
    identity: Identity = Depends(get_identity),
) -> UploadResponse:
    response = await v1_upload_knowledge(request, file, _context(identity, shop_id))
    return UploadResponse(**response.data.model_dump())


def _service(request: Request, identity: Identity, shop_id: str) -> DecisionIntelligenceService:
    context = _context(identity, shop_id)
    return DecisionIntelligenceService(
        context.tenant_id, context.shop_id, request.app.state.commerce_repository
    )


@router.get("/business/health", deprecated=True)
def business_health(
    request: Request,
    shop_id: str,
    identity: Identity = Depends(get_identity),
) -> dict:
    return _service(request, identity, shop_id).get_business_health()


@router.get("/products/{sku}/analysis", deprecated=True)
def product_analysis(
    sku: str,
    request: Request,
    shop_id: str,
    identity: Identity = Depends(get_identity),
) -> dict:
    return _service(request, identity, shop_id).analyze_product(sku)


@router.get("/revenue/leakage", deprecated=True)
def revenue_leakage(
    request: Request,
    shop_id: str,
    identity: Identity = Depends(get_identity),
) -> dict:
    return _service(request, identity, shop_id).analyze_revenue_leakage()


@router.get("/market/trends", deprecated=True)
def market_trends(
    request: Request,
    shop_id: str,
    category: Literal["nam", "nu"] = "nam",
    period: Literal["today", "7d", "30d"] = "7d",
    historical: bool = False,
    identity: Identity = Depends(get_identity),
) -> dict:
    service = _service(request, identity, shop_id)
    return service.market_service.get_trends(category, period, historical=historical)


@router.get("/opportunities", deprecated=True)
def opportunities(
    request: Request,
    shop_id: str,
    category: Literal["nam", "nu"] = "nam",
    period: Literal["today", "7d", "30d"] = "7d",
    identity: Identity = Depends(get_identity),
) -> dict:
    return _service(request, identity, shop_id).find_product_opportunities(category, period)


@router.get("/action-plan", deprecated=True)
def action_plan(
    request: Request,
    shop_id: str,
    category: Literal["nam", "nu"] = "nam",
    period: Literal["today", "7d", "30d"] = "7d",
    identity: Identity = Depends(get_identity),
) -> dict:
    return _service(request, identity, shop_id).generate_action_plan(category, period)


@router.post("/sales-plan", deprecated=True)
def sales_plan(
    payload: PlannerRequest,
    request: Request,
    identity: Identity = Depends(get_identity),
) -> dict:
    return _service(request, identity, payload.shop_id).generate_sales_plan(
        payload.category, payload.period, payload.objective
    )


@router.post("/communication-plan", deprecated=True)
def communication_plan(
    payload: CommunicationPlanRequest,
    request: Request,
    identity: Identity = Depends(get_identity),
) -> dict:
    return _service(request, identity, payload.shop_id).generate_communication_plan(
        payload.category, payload.period, payload.objective
    )
