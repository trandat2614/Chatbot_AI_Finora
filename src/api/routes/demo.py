"""Landing page endpoints: service credential only, no user/tenant dependency."""
from __future__ import annotations

import ipaddress
import json
import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import ValidationError
from starlette.concurrency import run_in_threadpool

from config.settings import settings
from core.exceptions import LLMClientError
from src.demo.schemas import (
    MAX_DEMO_BODY_BYTES, DemoChatRequest, DemoChatResponse, DemoConfigResponse, DemoErrorResponse,
)
from src.security.auth import AuthenticationError, WebBackendAuthenticator

logger = logging.getLogger(__name__)


def require_demo_service_key(
    service_key: str | None = Header(default=None, alias="X-Finora-Service-Key"),
) -> None:
    if not settings.DEMO_ENABLED:
        raise HTTPException(404, detail="Không tìm thấy tính năng này.")
    try:
        # Only verify the BE credential. No JWT, AuthContext or DB-backed audit.
        WebBackendAuthenticator._verify_service_key(service_key)
    except AuthenticationError:
        raise HTTPException(401, detail="Thông tin xác thực dịch vụ không hợp lệ.") from None


router = APIRouter(
    prefix="/api/chatbot/demo", tags=["demo-chat"],
    dependencies=[Depends(require_demo_service_key)],
    responses={code: {"model": DemoErrorResponse} for code in (400, 401, 404, 429, 500, 503)},
)


def client_ip(request: Request) -> str:
    # Called only after authenticating BE; BE must overwrite browser-supplied headers.
    for value in (
        request.headers.get("x-client-ip", ""),
        request.headers.get("x-forwarded-for", "").split(",", 1)[0],
    ):
        try:
            return str(ipaddress.ip_address(value.strip()))
        except ValueError:
            continue
    return request.client.host if request.client else "unknown"


@router.get("/config", response_model=DemoConfigResponse)
def config() -> DemoConfigResponse:
    return DemoConfigResponse(
        botName=f"Trợ lý {settings.BRAND_NAME}",
        welcome=f"Chào bạn! Mình là trợ lý {settings.BRAND_NAME}. Hãy trải nghiệm phân tích bán hàng với dữ liệu mẫu của Demo Store.",
        suggestions=[
            "Doanh thu hôm qua bao nhiêu?",
            "Sản phẩm nào bán chạy nhất tháng này?",
            "Kênh quảng cáo nào đang hiệu quả nhất?",
            "Tại sao lợi nhuận ròng chỉ 6,4%?",
            "Làm sao giảm tỷ lệ bỏ giỏ hàng?",
            f"{settings.BRAND_NAME} làm được gì?",
        ],
        loginUrl=settings.LOGIN_URL,
        signupUrl=settings.SIGNUP_URL,
    )


@router.post("/chat", response_model=DemoChatResponse, openapi_extra={
    "requestBody": {"required": True, "content": {"application/json": {"schema": {
        "type": "object", "required": ["messages"], "additionalProperties": False,
        "properties": {"messages": {"type": "array", "minItems": 1, "items": {
            "type": "object", "required": ["role", "content"], "additionalProperties": False,
            "properties": {"role": {"type": "string", "enum": ["user", "assistant"]},
                           "content": {"type": "string", "minLength": 1}},
        }}},
    }}}},
})
async def chat(request: Request) -> DemoChatResponse:
    if not request.app.state.demo_rate_limiter.allow(client_ip(request)):
        raise HTTPException(429, detail="Bạn gửi tin nhắn hơi nhanh. Vui lòng thử lại sau một phút.",
                            headers={"Retry-After": "60"})
    if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
        raise HTTPException(400, detail="Vui lòng gửi nội dung theo định dạng JSON.")
    raw = bytearray()
    async for chunk in request.stream():
        if len(raw) + len(chunk) > MAX_DEMO_BODY_BYTES:
            raise HTTPException(400, detail="Nội dung hội thoại vượt quá giới hạn 20 KB.")
        raw.extend(chunk)
    try:
        payload = DemoChatRequest.model_validate(json.loads(raw.decode("utf-8")))
    except (ValueError, UnicodeError, ValidationError, RecursionError):
        raise HTTPException(
            400, detail="Hội thoại không hợp lệ. Chỉ gửi tin user/assistant; tin đầu và cuối phải là user, mỗi tin user tối đa 500 ký tự.",
        ) from None
    service = getattr(request.app.state, "demo_service", None)
    if service is None:
        raise HTTPException(503, detail="Trợ lý demo tạm thời chưa sẵn sàng. Bạn vui lòng thử lại sau.")
    try:
        reply = await run_in_threadpool(service.reply, payload.messages)
    except LLMClientError:
        raise HTTPException(503, detail="Trợ lý demo đang bận. Bạn vui lòng thử lại sau.") from None
    except Exception as exc:
        logger.error("Demo chat failed type=%s", type(exc).__name__)
        raise HTTPException(500, detail="Có lỗi khi xử lý tin nhắn. Bạn vui lòng thử lại sau.") from None
    return DemoChatResponse(reply=reply)
