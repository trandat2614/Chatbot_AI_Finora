"""Structured, privacy-safe audit events."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config.settings import settings
from src.security.auth import AuthContext, AuthPrincipal

logger = logging.getLogger("finora.audit")


def audit_event(
    action: str,
    principal: AuthContext | AuthPrincipal | None,
    *,
    outcome: str = "success",
    resource: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    """Write an allow-listed JSON event without request bodies or secrets."""
    safe_details = {
        str(key): value
        for key, value in (details or {}).items()
        if key in {
            "filename_hash", "record_count", "status", "intent", "content_type", "size",
            "tool", "data_status", "grounded", "llm_quantitative_generation_blocked",
        }
        and isinstance(value, (str, int, float, bool, type(None)))
    }
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "outcome": outcome,
        "tenant": principal.audit_tenant if principal else None,
        "user": principal.audit_user if principal else None,
        "shop": principal.audit_shop if principal else None,
        "role": principal.role if principal else None,
        "resource": resource,
        "details": safe_details,
    }
    line = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
    logger.info(line)
    try:
        path = Path(settings.AUDIT_LOG_FILE)
        if not path.is_absolute():
            path = settings.BASE_DIR / path
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    except OSError:
        logger.exception("Could not persist audit event")
    try:
        # Database audit is authoritative for production queries. The file is
        # retained as an append-only operational fallback.
        from src.repositories.audit_repository import SQLAlchemyAuditRepository

        SQLAlchemyAuditRepository().append(
            principal, action, outcome, resource, safe_details  # type: ignore[arg-type]
        )
    except Exception:
        # Authentication must fail closed, but an audit sink outage must not
        # expose secrets or recursively trigger another audit event.
        logger.warning("Database audit sink unavailable", exc_info=True)
