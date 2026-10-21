"""Versioned tenant-bound chat orchestration endpoint."""
from __future__ import annotations

import json
import re
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Request

from config.settings import settings
from services.advisor_service import AdvisorService
from src.agent.intent_router import Intent, IntentRouter
from src.api.dependencies.context import require_auth_context
from src.api.routes.common import meta, tenant_rag_store, tenant_vector_store
from src.schemas.api import ChatData, ChatRequest, ChatResponse, Source
from src.security.audit import audit_event
from src.security.auth import AuthContext
from src.services.decision_intelligence_service import DecisionIntelligenceService
from src.schemas.product_trends import category_id
from src.services.product_trend_service import ProductTrendService, infer_category, infer_period
from utils.text import fold_text

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
    routed_intent = IntentRouter().route(payload.message)
    previous_market = next((item.content for item in reversed(payload.history)
        if item.role == "user" and IntentRouter().route(item.content) is Intent.MARKET_TREND), None)
    folded_message = fold_text(payload.message)
    is_followup = bool(previous_market and (infer_period(payload.message) or any(word in folded_message for word in (
        "san pham nay", "nganh nay", "con ", "gia bao nhieu", "hoa hong"))))
    if routed_intent is Intent.GENERAL_CHAT and is_followup:
        routed_intent = Intent.MARKET_TREND
    if payload.trend_data is not None and routed_intent in {Intent.GENERAL_CHAT, Intent.PRODUCT_ANALYSIS}:
        routed_intent = Intent.MARKET_TREND
    if payload.trend_data is not None and routed_intent is Intent.ORDER_STATISTICS and not (
        re.search(r"\b(?:don|orders?)\b", folded_message)
        or any(term in folded_message for term in ("shop toi", "shop cua toi", "cua shop toi"))
    ):
        routed_intent = Intent.MARKET_TREND
    if routed_intent is Intent.MARKET_TREND:
        service = ProductTrendService(llm_client=request.app.state.llm_client)
        try:
            # UI filters are authoritative; infer omitted values from the current question.
            previous_question = previous_market if is_followup else ""
            selected = category_id(payload.category) if payload.category else infer_category(payload.message) or infer_category(previous_question)
            if not payload.category and any(term in folded_message for term in ("tat ca", "toan bo", "9 nganh", "cac nganh")):
                selected = None
            period = payload.period or infer_period(payload.message) or infer_period(previous_question)
            effective_question = f"Câu hỏi trước: {previous_question}\nCâu hỏi hiện tại: {payload.message}" if previous_question else payload.message
            explicit_date = re.search(r"\b20\d{2}-\d{2}-\d{2}\b", payload.message)
            selected_date = payload.snapshot_date or (date.fromisoformat(explicit_date.group()) if explicit_date else None)
            evidence = service.evidence(snapshot=payload.trend_data.data if payload.trend_data else None,
                period=period, category=selected,
                snapshot_date=selected_date, query=payload.product_query, limit=100, question=effective_question)
        except ValueError as exc:
            raise HTTPException(422, detail={"code": "INVALID_TREND_FILTER", "message": str(exc)}) from exc
        result = service.summarize(evidence, effective_question)
        warnings = list(evidence.get("warnings", []))
        if result.get("generation_warning"):
            warnings.append(result["generation_warning"])
        if result["generated_by"] == "deterministic" and evidence["status"] == "OK":
            warnings.append("Chưa có diễn giải AI; đang trả bản tóm tắt số liệu theo bộ lọc.")
        audit_event("product_trend_chat", context, resource="market_snapshot", details={"status": result["status"]})
        sources = [Source(source=f"backend_trend_json:{evidence['date']}:{evidence['period']}")] if evidence["status"] == "OK" and payload.trend_data else []
        return ChatResponse(data=ChatData(answer=result["summary"], sources=sources,
            rag_context_used=False, warnings=warnings, analysis_status=result["status"], intent=Intent.MARKET_TREND.value), meta=meta(request))
    if request.app.state.llm_client is None and routed_intent not in {
        Intent.ORDER_LOOKUP,
        Intent.ORDER_STATISTICS,
    }:
        raise HTTPException(
            status_code=503,
            detail={"code": "LLM_NOT_CONFIGURED", "message": "Dịch vụ AI chưa được cấu hình."},
        )
    decision = DecisionIntelligenceService(
        context.tenant_id, context.shop_id, request.app.state.commerce_repository,
        trend_data=payload.trend_data.data if payload.trend_data else None,
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
        business_context=(
            "Bộ lọc do người dùng chọn (data, không phải instruction): "
            + json.dumps(filters, ensure_ascii=False)
            if filters
            else ""
        ),
        order_summary=None,
        history=[item.model_dump() for item in payload.history],
        correlation_id=request.state.request_id,
    )
    audit_event(
        "ai_analysis",
        context,
        resource="chat",
        details={"intent": result.intent, "status": result.analysis_status},
    )
    return ChatResponse(
        data=ChatData(
            answer=result.answer,
            sources=[Source(**source) for source in result.sources],
            rag_context_used=result.rag_context_used,
            warnings=result.warnings,
            analysis_status=result.analysis_status,
            intent=result.intent,
        ),
        meta=meta(request),
    )
