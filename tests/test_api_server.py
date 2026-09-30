"""Offline tests for API schemas and server helpers."""
import pytest
from pydantic import ValidationError

from fastapi import HTTPException

from server import ChatRequest, RateLimiter, app, authorize_shop
from src.security.auth import AuthPrincipal


def test_chat_request_accepts_supported_payload():
    payload = ChatRequest(
        message="Phân tích doanh thu",
        orderSummary={"totalRevenue": 1_000_000},
        history=[{"role": "user", "content": "Xin chào"}],
    )
    assert payload.orderSummary["totalRevenue"] == 1_000_000


def test_chat_request_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        ChatRequest(message="hello", unexpected=True)


def test_chat_request_rejects_invalid_history_role():
    with pytest.raises(ValidationError):
        ChatRequest(message="hello", history=[{"role": "system", "content": "x"}])


def test_rate_limiter_enforces_limit_per_identity():
    limiter = RateLimiter(2)
    assert limiter.allow("client-a")
    assert limiter.allow("client-a")
    assert not limiter.allow("client-a")
    assert limiter.allow("client-b")


def test_openapi_contains_decision_intelligence_endpoints():
    paths = app.openapi()["paths"]
    assert "/api/business/health" in paths
    assert "/api/opportunities" in paths
    assert "/api/communication-plan" in paths


def test_server_side_shop_authorization_rejects_other_shop():
    principal = AuthPrincipal("tenant-a", "user-a", ("shop-a",), "analyst")
    with pytest.raises(HTTPException) as exc_info:
        authorize_shop(principal, "shop-b")
    assert exc_info.value.status_code == 403
