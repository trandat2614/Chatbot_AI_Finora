"""Versioned tenant-bound chat orchestration endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from config.settings import settings
from services.advisor_service import AdvisorService
from src.api.dependencies.context import require_auth_context
from src.api.routes.common import meta, tenant_rag_store, tenant_vector_store
from src.schemas.api import ChatData, ChatRequest, ChatResponse, Source
from src.security.audit import audit_event
from src.security.auth import AuthContext
from src.services.decision_intelligence_service import DecisionIntelligenceService

router = APIRouter(prefix="/api/v1", tags=["v1-chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    request: Request,
    context: AuthContext = Depends(require_auth_context),
) -> ChatResponse:
    if len(payload.history) > settings.MAX_HISTORY_MESSAGES:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "HISTORY_TOO_LARGE",
                "message": f"history tối đa {settings.MAX_HISTORY_MESSAGES} tin nhắn.",
            },
        )
    if request.app.state.llm_client is None:
        raise HTTPException(
            status_code=503,
            detail={"code": "LLM_NOT_CONFIGURED", "message": "Dịch vụ AI chưa được cấu hình."},
        )
    decision = DecisionIntelligenceService(
        context.tenant_id, context.shop_id, request.app.state.commerce_repository
    )
    filters = {
        key: value
        for key, value in {
            "period": payload.period,
            "category": payload.category,
            "platform": payload.platform,
        }.items()
        if value is not None
    }
    advisor = AdvisorService(
        llm_client=request.app.state.llm_client,
        vector_store=request.app.state.vector_store,
        tenant_vector_store=tenant_vector_store(context),
        tenant_scope=tenant_rag_store.scope_token(context.tenant_id, context.shop_id),
        tenant_id=context.tenant_id,
        shop_id=context.shop_id,
        decision_service=decision,
    )
    result = advisor.answer(
        question=payload.message,
        order_summary=None,
        history=[item.model_dump() for item in payload.history],
        filters=filters,
    )
    audit_event(
        "ai_analysis",
        context,
        resource="chat",
        details={
            "intent": result.intent,
            "status": result.analysis_status,
            "tool": "decision_intelligence" if result.tool_context_used else None,
            "data_status": result.analysis_status,
            "grounded": result.data_grounded,
            "llm_quantitative_generation_blocked": result.quantitative_generation_blocked,
        },
    )
    return ChatResponse(
        data=ChatData(
            answer=result.answer,
            sources=[Source(**source) for source in result.sources],
            rag_context_used=result.rag_context_used,
            warnings=result.warnings,
            analysis_status=result.analysis_status,
            intent=result.intent,
            data_grounded=result.data_grounded,
            tool_context_used=result.tool_context_used,
        ),
        meta=meta(request),
    )
