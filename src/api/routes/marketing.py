"""Internal marketing API. BE attests product ownership using JWT + service key."""
import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from config.settings import settings
from src.api.dependencies.context import require_auth_context, require_write_role
from src.schemas.marketing import (AdaptRequest, CalendarRequest, GenerationRequest, MarketingResponse, MarketingValidationError,
    RewriteRequest, StrategyRequest, VALID_TARGETS, LEGACY_TARGETS)
from src.security.auth import AuthContext
from src.services.marketing.idempotency import IdempotencyStore
from src.services.marketing.knowledge import MarketingKnowledge
from src.services.marketing.prompts import PROMPT_VERSION
from src.services.marketing.service import MarketingService
from src.schemas.api import ErrorResponse

router = APIRouter(prefix="/api/v1/marketing", tags=["v1-marketing"], responses={
    409: {"model": ErrorResponse}, 422: {"model": MarketingValidationError},
    502: {"model": MarketingResponse}, 503: {"model": MarketingResponse}, 504: {"model": MarketingResponse}})
IdempotencyKey = Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=120, pattern=r"^[A-Za-z0-9._:-]+$")]


def marketing_context(context: AuthContext = Depends(require_auth_context)):
    # This new internal contract intentionally never opts into legacy auth.
    if context.auth_method != "web_token":
        raise HTTPException(401, detail={"code": "WEB_AUTH_REQUIRED", "message": "Marketing cần JWT và service key từ BE."})
    return context


def marketing_service(request):
    # A dependency seam for offline tests and future authenticated tool callers.
    return MarketingService(getattr(request.app.state, "llm_client", None),
        MarketingKnowledge(getattr(request.app.state, "marketing_vector_store", None)))


@router.get("/capabilities")
def capabilities(context: AuthContext = Depends(marketing_context)):
    return {"targets": [dict(zip(("channel", "placement", "content_type"), t)) for t in VALID_TARGETS],
        "legacy_channels": {k: dict(zip(("channel", "placement", "content_type"), v)) for k, v in LEGACY_TARGETS.items()},
        "objectives": ["introduce_product", "drive_sales", "promote_offer", "answer_questions"],
        "duration_seconds": [15, 30, 60], "production_modes": ["on_camera", "hands_only", "voiceover", "text_only"],
        "video_styles": ["product_demo", "tutorial", "unboxing", "faq", "objection_handling", "scenario", "presenter", "ugc_style"],
        "variants": {"min": 1, "max": 3, "default": 3}, "emoji_limit": {"min": 0, "max": 2, "default": 0},
        "max_workload": settings.MARKETING_MAX_WORKLOAD, "timeout_seconds": settings.MARKETING_TIMEOUT_SECONDS,
        "call_timeout_seconds": settings.MARKETING_CALL_TIMEOUT_SECONDS,
        "max_repairs": max(0, min(settings.MARKETING_MAX_REPAIRS, 2)),
        "calendar_days": 7, "default_timezone": "Asia/Ho_Chi_Minh",
        "idempotency": {"required": True, "storage": "database", "ttl_seconds": max(settings.MARKETING_IDEMPOTENCY_TTL_SECONDS, int(settings.MARKETING_TIMEOUT_SECONDS) + 60),
                        "scope": "authenticated backend issuer + user + tenant + shop + endpoint + key"},
        "editorial_limits": {"facebook_standard_units": settings.MARKETING_FACEBOOK_STANDARD_UNITS,
                             "facebook_short_units": settings.MARKETING_FACEBOOK_SHORT_UNITS,
                             "shopee_title_chars": settings.MARKETING_SHOPEE_TITLE_CHARS,
                             "kind": "Finora editorial configuration, not platform maxima"},
        "prompt_version": PROMPT_VERSION, "requires_human_review": True}


async def execute(payload, request, context, key, operation):
    require_write_role(context)
    store = IdempotencyStore(request.app.state.database)
    scope_key, operation_id, saved, status = await asyncio.to_thread(
        store.claim, context, request.url.path, key, payload.model_dump(mode="json"))
    if saved is not None:
        result = MarketingResponse.model_validate(saved)
        result.metadata.idempotency_replayed = True
        return JSONResponse(status_code=status, content=result.model_dump(mode="json"))
    service = marketing_service(request)
    if operation == "calendar":
        result = await service.calendar(payload, context, request.state.request_id, operation_id=operation_id)
    elif operation == "strategy":
        result = await service.strategy(payload, context, request.state.request_id)
    else:
        result = await service.generate(payload, context, request.state.request_id, operation=operation, operation_id=operation_id)
    status = 200
    if result.status == "failed":
        codes = {e.code for e in result.errors}
        status = 503 if "LLM_NOT_CONFIGURED" in codes else 504 if codes == {"TIMEOUT"} else 502
    await asyncio.to_thread(store.complete, scope_key, operation_id, result.model_dump(mode="json"), status)
    return JSONResponse(status_code=status, content=result.model_dump(mode="json"))


@router.post("/generate", response_model=MarketingResponse, responses={504: {"model": MarketingResponse}})
async def generate(payload: GenerationRequest, request: Request, idempotency_key: IdempotencyKey,
                   context: AuthContext = Depends(marketing_context)):
    return await execute(payload, request, context, idempotency_key, "generate")


@router.post("/video-scripts/generate", response_model=MarketingResponse)
async def video_generate(payload: GenerationRequest, request: Request, idempotency_key: IdempotencyKey,
                         context: AuthContext = Depends(marketing_context)):
    if any(t.content_type != "video_script" for t in payload.selected_targets()):
        raise HTTPException(422, detail={"code": "VIDEO_TARGET_REQUIRED", "message": "Route này chỉ nhận target video."})
    return await execute(payload, request, context, idempotency_key, "generate")


@router.post("/rewrite", response_model=MarketingResponse)
async def rewrite(payload: RewriteRequest, request: Request, idempotency_key: IdempotencyKey,
                  context: AuthContext = Depends(marketing_context)):
    return await execute(payload, request, context, idempotency_key, "rewrite")


@router.post("/video-scripts/adapt", response_model=MarketingResponse)
async def adapt(payload: AdaptRequest, request: Request, idempotency_key: IdempotencyKey,
                context: AuthContext = Depends(marketing_context)):
    return await execute(payload, request, context, idempotency_key, "adapt")


@router.post("/calendar", response_model=MarketingResponse)
async def calendar(payload: CalendarRequest, request: Request, idempotency_key: IdempotencyKey,
                   context: AuthContext = Depends(marketing_context)):
    return await execute(payload, request, context, idempotency_key, "calendar")


@router.post("/strategy", response_model=MarketingResponse)
async def strategy(payload: StrategyRequest, request: Request, idempotency_key: IdempotencyKey,
                   context: AuthContext = Depends(marketing_context)):
    return await execute(payload, request, context, idempotency_key, "strategy")
