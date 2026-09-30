"""Authentication, authorization and request context dependencies."""
from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import Depends, Header, HTTPException, Request, status

from config.settings import settings
from src.security.audit import audit_event
from src.security.auth import (
    AuthContext,
    AuthPrincipal,
    AuthenticationError,
    TenantAuthenticator,
    WebBackendAuthenticator,
)

Identity = AuthContext | AuthPrincipal


class RateLimiter:
    """In-memory limiter for one process; Nginx adds the production outer limit."""

    def __init__(self, limit: int) -> None:
        self.limit = max(limit, 1)
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, identity: str) -> bool:
        now = time.monotonic()
        bucket = self._requests[identity]
        while bucket and now - bucket[0] >= 60:
            bucket.popleft()
        if len(bucket) >= self.limit:
            return False
        bucket.append(now)
        return True


rate_limiter = RateLimiter(settings.RATE_LIMIT_PER_MINUTE)
auth_rate_limiter = RateLimiter(settings.AUTH_RATE_LIMIT_PER_MINUTE)


def _http_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"code": code, "message": message})


def get_identity(
    request: Request,
    authorization: str | None = Header(default=None, alias="Authorization"),
    service_key: str | None = Header(default=None, alias="X-Finora-Service-Key"),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> Identity:
    client_ip = request.client.host if request.client else "unknown"
    if not auth_rate_limiter.allow(client_ip):
        audit_event("authentication", None, outcome="rate_limited")
        raise _http_error(429, "AUTH_RATE_LIMITED", "Quá nhiều lần xác thực.")

    identity: Identity | None = None
    if authorization or service_key:
        try:
            identity = WebBackendAuthenticator().authenticate(authorization, service_key)
        except AuthenticationError as exc:
            audit_event("authentication", None, outcome="denied")
            raise _http_error(status.HTTP_401_UNAUTHORIZED, exc.code, str(exc)) from exc
    elif settings.ENABLE_LEGACY_API_KEY:
        identity = TenantAuthenticator().authenticate(x_api_key)

    if identity is None:
        audit_event("authentication", None, outcome="denied")
        raise _http_error(
            status.HTTP_401_UNAUTHORIZED,
            "INVALID_AUTHENTICATION",
            "Thông tin xác thực không hợp lệ.",
        )

    limiter_identity = f"{identity.audit_tenant}:{client_ip}"
    if not rate_limiter.allow(limiter_identity):
        audit_event("rate_limit", identity, outcome="denied")
        raise _http_error(429, "RATE_LIMITED", "Quá nhiều yêu cầu.")
    audit_event("authentication", identity)
    return identity


def get_auth_context(identity: Identity = None) -> AuthContext:
    # FastAPI injects identity through the explicit wrapper below. Keeping this
    # function pure also makes authorization straightforward to unit test.
    if identity is None:
        raise RuntimeError("Auth identity dependency was not provided.")
    if isinstance(identity, AuthContext):
        return identity
    selected_shop = identity.shop_ids[0] if identity.shop_ids else settings.DEFAULT_SHOP_ID
    return identity.to_context(selected_shop)


def require_auth_context(identity: Identity = Depends(get_identity)) -> AuthContext:
    return get_auth_context(identity)


def authorize_shop(identity: Identity, requested_shop_id: str) -> None:
    if not identity.can_access_shop(requested_shop_id):
        audit_event("shop_authorization", identity, outcome="denied", resource="shop")
        raise _http_error(403, "SHOP_FORBIDDEN", "Không có quyền truy cập shop này.")


def require_write_role(identity: Identity) -> None:
    if identity.role not in {"owner", "admin", "analyst"}:
        audit_event("write_authorization", identity, outcome="denied")
        raise _http_error(403, "WRITE_FORBIDDEN", "Identity chỉ có quyền đọc.")
