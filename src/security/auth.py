"""Authentication primitives for trusted Finora web-backend requests."""
from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from typing import Any

import jwt
from jwt import ExpiredSignatureError, InvalidAudienceError, InvalidIssuerError, InvalidTokenError

from config.settings import settings


class AuthenticationError(ValueError):
    """Machine-readable authentication failure without leaking credentials."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class AuthContext:
    """Verified identity asserted by the Finora web backend."""

    user_id: str
    tenant_id: str
    shop_id: str
    role: str
    authorized_shop_ids: tuple[str, ...] = ()
    auth_method: str = "web_token"

    @property
    def shop_ids(self) -> tuple[str, ...]:
        return self.authorized_shop_ids or (self.shop_id,)

    def can_access_shop(self, requested_shop_id: str | None) -> bool:
        if not requested_shop_id:
            return True
        return requested_shop_id == self.shop_id or requested_shop_id in self.shop_ids

    @property
    def audit_tenant(self) -> str:
        return hashlib.sha256(self.tenant_id.encode("utf-8")).hexdigest()[:16]

    @property
    def audit_user(self) -> str:
        return hashlib.sha256(self.user_id.encode("utf-8")).hexdigest()[:16]

    @property
    def audit_shop(self) -> str:
        return hashlib.sha256(self.shop_id.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class AuthPrincipal:
    """Backward-compatible API-key identity used by local/tests during migration."""

    tenant_id: str
    user_id: str
    shop_ids: tuple[str, ...] = ()
    role: str = "analyst"

    @property
    def shop_id(self) -> str:
        return self.shop_ids[0] if self.shop_ids else settings.DEFAULT_SHOP_ID

    def can_access_shop(self, shop_id: str | None) -> bool:
        if not shop_id:
            return True
        return self.role == "admin" or shop_id in self.shop_ids

    @property
    def audit_tenant(self) -> str:
        return hashlib.sha256(self.tenant_id.encode("utf-8")).hexdigest()[:16]

    @property
    def audit_user(self) -> str:
        return hashlib.sha256(self.user_id.encode("utf-8")).hexdigest()[:16]

    @property
    def audit_shop(self) -> str:
        return hashlib.sha256(self.shop_id.encode("utf-8")).hexdigest()[:16]

    def to_context(self, requested_shop_id: str | None = None) -> AuthContext:
        selected = requested_shop_id or (self.shop_ids[0] if self.shop_ids else "default")
        return AuthContext(
            user_id=self.user_id,
            tenant_id=self.tenant_id,
            shop_id=selected,
            role=self.role,
            authorized_shop_ids=self.shop_ids or (selected,),
            auth_method="legacy_api_key",
        )


class WebBackendAuthenticator:
    """Verify both the service credential and the signed short-lived identity token."""

    required_claims = ("user_id", "tenant_id", "shop_id", "role", "iss", "aud", "exp")
    allowed_roles = {"owner", "admin", "analyst", "viewer"}

    @staticmethod
    def _bearer_token(authorization: str | None) -> str:
        if not authorization:
            raise AuthenticationError("MISSING_TOKEN", "Thiếu Bearer token.")
        scheme, separator, token = authorization.partition(" ")
        if not separator or scheme.lower() != "bearer" or not token.strip():
            raise AuthenticationError("INVALID_TOKEN", "Authorization header không hợp lệ.")
        return token.strip()

    @staticmethod
    def _verify_service_key(service_key: str | None) -> None:
        configured = settings.FINORA_SERVICE_KEY
        if not configured or not service_key:
            raise AuthenticationError("INVALID_SERVICE_KEY", "Service credential không hợp lệ.")
        if not secrets.compare_digest(
            hashlib.sha256(service_key.encode()).digest(),
            hashlib.sha256(configured.encode()).digest(),
        ):
            raise AuthenticationError("INVALID_SERVICE_KEY", "Service credential không hợp lệ.")

    def authenticate(
        self,
        authorization: str | None,
        service_key: str | None,
    ) -> AuthContext:
        self._verify_service_key(service_key)
        token = self._bearer_token(authorization)
        if not settings.WEB_TOKEN_SECRET:
            raise AuthenticationError("AUTH_NOT_CONFIGURED", "Web token verification chưa được cấu hình.")
        try:
            payload: dict[str, Any] = jwt.decode(
                token,
                settings.WEB_TOKEN_SECRET,
                algorithms=[settings.WEB_TOKEN_ALGORITHM],
                audience=settings.WEB_TOKEN_AUDIENCE,
                issuer=settings.WEB_TOKEN_ISSUER,
                leeway=settings.WEB_TOKEN_LEEWAY_SECONDS,
                options={"require": list(self.required_claims)},
            )
        except ExpiredSignatureError as exc:
            raise AuthenticationError("TOKEN_EXPIRED", "Bearer token đã hết hạn.") from exc
        except InvalidAudienceError as exc:
            raise AuthenticationError("INVALID_AUDIENCE", "Bearer token sai audience.") from exc
        except InvalidIssuerError as exc:
            raise AuthenticationError("INVALID_ISSUER", "Bearer token sai issuer.") from exc
        except InvalidTokenError as exc:
            raise AuthenticationError("INVALID_TOKEN", "Bearer token không hợp lệ.") from exc

        values = {
            name: str(payload.get(name, "")).strip()
            for name in ("user_id", "tenant_id", "shop_id", "role")
        }
        if not all(values.values()) or values["role"] not in self.allowed_roles:
            raise AuthenticationError("INVALID_CLAIMS", "Bearer token thiếu identity claims hợp lệ.")

        signed_shops = payload.get("shop_ids", [])
        if signed_shops is None:
            signed_shops = []
        if not isinstance(signed_shops, list) or not all(isinstance(item, str) for item in signed_shops):
            raise AuthenticationError("INVALID_CLAIMS", "shop_ids trong token không hợp lệ.")
        authorized = tuple(dict.fromkeys([values["shop_id"], *signed_shops]))
        return AuthContext(
            user_id=values["user_id"],
            tenant_id=values["tenant_id"],
            shop_id=values["shop_id"],
            role=values["role"],
            authorized_shop_ids=authorized,
        )


class TenantAuthenticator:
    """Legacy API-key authenticator retained for local/tests and compatibility routes."""

    def __init__(self) -> None:
        self._credentials: list[tuple[str, AuthPrincipal]] = []
        seen_digests: set[str] = set()
        for item in settings.tenant_credentials():
            if not isinstance(item, dict):
                raise EnvironmentError("Mỗi tenant credential phải là một object.")
            api_key = str(item.get("api_key", ""))
            tenant_id = str(item.get("tenant_id", ""))
            user_id = str(item.get("user_id", ""))
            role = str(item.get("role", "analyst"))
            shop_ids = item.get("shop_ids", [])
            if not api_key or not tenant_id or not user_id or not isinstance(shop_ids, list):
                raise EnvironmentError("Tenant credential thiếu api_key/tenant_id/user_id/shop_ids.")
            if role not in {"admin", "analyst", "viewer"}:
                raise EnvironmentError("Tenant credential có role không hợp lệ.")
            digest = self._digest(api_key)
            if digest in seen_digests:
                raise EnvironmentError("API key tenant bị trùng lặp.")
            seen_digests.add(digest)
            self._credentials.append(
                (digest, AuthPrincipal(tenant_id, user_id, tuple(map(str, shop_ids)), role))
            )

        if settings.AI_SERVER_API_KEY:
            legacy_digest = self._digest(settings.AI_SERVER_API_KEY)
            if legacy_digest in seen_digests:
                raise EnvironmentError("AI_SERVER_API_KEY trùng tenant credential.")
            self._credentials.append(
                (
                    legacy_digest,
                    AuthPrincipal(
                        settings.DEFAULT_TENANT_ID,
                        settings.DEFAULT_USER_ID,
                        role="admin",
                    ),
                )
            )

    @staticmethod
    def _digest(api_key: str) -> str:
        return hashlib.sha256(api_key.encode("utf-8")).hexdigest()

    def authenticate(self, api_key: str | None) -> AuthPrincipal | None:
        if not settings.ENABLE_LEGACY_API_KEY:
            return None
        if not settings.AUTH_REQUIRED and not self._credentials:
            return AuthPrincipal(settings.DEFAULT_TENANT_ID, settings.DEFAULT_USER_ID, role="admin")
        if not api_key:
            return None
        candidate = self._digest(api_key)
        for digest, principal in self._credentials:
            if secrets.compare_digest(candidate, digest):
                return principal
        return None
