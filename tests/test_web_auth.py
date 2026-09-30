"""Signed web-backend authentication regression tests."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from config.settings import settings
from src.security.auth import AuthenticationError, WebBackendAuthenticator


@pytest.fixture
def web_auth(monkeypatch):
    monkeypatch.setattr(settings, "WEB_TOKEN_SECRET", "t" * 48)
    monkeypatch.setattr(settings, "FINORA_SERVICE_KEY", "s" * 48)
    monkeypatch.setattr(settings, "WEB_TOKEN_ISSUER", "finora-web")
    monkeypatch.setattr(settings, "WEB_TOKEN_AUDIENCE", "finora-ai")
    monkeypatch.setattr(settings, "WEB_TOKEN_ALGORITHM", "HS256")
    monkeypatch.setattr(settings, "WEB_TOKEN_LEEWAY_SECONDS", 0)
    return WebBackendAuthenticator()


def token(**overrides) -> str:
    payload = {
        "user_id": "usr-a",
        "tenant_id": "tenant-a",
        "shop_id": "shop-a",
        "role": "owner",
        "iss": "finora-web",
        "aud": "finora-ai",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=2),
    }
    payload.update(overrides)
    return jwt.encode(payload, settings.WEB_TOKEN_SECRET, algorithm="HS256")


def test_valid_web_backend_token(web_auth) -> None:
    context = web_auth.authenticate(f"Bearer {token()}", "s" * 48)
    assert context.tenant_id == "tenant-a"
    assert context.shop_id == "shop-a"
    assert context.can_access_shop("shop-a")
    assert not context.can_access_shop("shop-b")


def test_invalid_signature_is_rejected(web_auth) -> None:
    invalid = jwt.encode(
        {
            "user_id": "u", "tenant_id": "t", "shop_id": "s", "role": "owner",
            "iss": "finora-web", "aud": "finora-ai",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=1),
        },
        "w" * 48,
        algorithm="HS256",
    )
    with pytest.raises(AuthenticationError, match="không hợp lệ"):
        web_auth.authenticate(f"Bearer {invalid}", "s" * 48)


def test_expired_token_is_rejected(web_auth) -> None:
    with pytest.raises(AuthenticationError) as exc_info:
        web_auth.authenticate(
            f"Bearer {token(exp=datetime.now(timezone.utc) - timedelta(seconds=1))}",
            "s" * 48,
        )
    assert exc_info.value.code == "TOKEN_EXPIRED"


def test_invalid_audience_is_rejected(web_auth) -> None:
    with pytest.raises(AuthenticationError) as exc_info:
        web_auth.authenticate(f"Bearer {token(aud='other-service')}", "s" * 48)
    assert exc_info.value.code == "INVALID_AUDIENCE"


def test_invalid_service_key_is_rejected_before_token(web_auth) -> None:
    with pytest.raises(AuthenticationError) as exc_info:
        web_auth.authenticate(f"Bearer {token()}", "wrong")
    assert exc_info.value.code == "INVALID_SERVICE_KEY"
