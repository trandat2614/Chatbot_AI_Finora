"""Offline tests for API schemas and server helpers."""
import pytest
from pydantic import ValidationError

from server import ChatRequest, RateLimiter


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
