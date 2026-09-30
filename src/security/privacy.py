"""PII redaction and prompt-injection hardening before AI boundaries."""
from __future__ import annotations

import hashlib
import hmac
import re
from typing import Any

from config.settings import settings

PII_FIELD_MARKERS = (
    "customer", "buyer", "recipient", "customer name", "full name", "phone", "mobile", "email",
    "address", "street", "ward", "district", "province", "người mua",
    "người nhận", "điện thoại", "địa chỉ", "tên khách",
)

_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_PHONE_RE = re.compile(r"(?<!\d)(?:\+?84|0)[\s.\-]?(?:\d[\s.\-]?){8,10}(?!\d)")
_ADDRESS_RE = re.compile(
    r"(?i)\b(?:địa chỉ|address)\s*[:=-]\s*[^\n,;]{5,}(?:[,;][^\n]{2,})?"
)
_NAME_RE = re.compile(
    r"(?i)\b(?:tên khách hàng|customer name|buyer name|người nhận|recipient)"
    r"\s*[:=-]\s*[^\n,;]{2,80}"
)
_INJECTION_RE = re.compile(
    r"(ignore|disregard|override|bỏ qua|quên).{0,40}"
    r"(instruction|system|prompt|chỉ dẫn|hướng dẫn)|"
    r"(system prompt|developer message|reveal secrets?|execute code|gọi tool|call tool)",
    re.IGNORECASE,
)


def hash_pii(value: str) -> str:
    secret = settings.PII_HASH_SECRET or settings.AI_SERVER_API_KEY
    normalized = value.strip().lower().encode()
    digest = (
        hmac.new(secret.encode(), normalized, hashlib.sha256).hexdigest()
        if secret else hashlib.sha256(normalized).hexdigest()
    )
    return f"pii_{digest[:16]}"


def sanitize_text(value: str, *, block_prompt_injection: bool = False) -> str:
    text = _EMAIL_RE.sub("[REDACTED_EMAIL]", str(value))
    text = _PHONE_RE.sub("[REDACTED_PHONE]", text)
    text = _ADDRESS_RE.sub("[REDACTED_ADDRESS]", text)
    text = _NAME_RE.sub("[REDACTED_NAME]", text)
    if block_prompt_injection:
        safe_lines = []
        for line in text.splitlines():
            safe_lines.append("[BLOCKED_UNTRUSTED_INSTRUCTION]" if _INJECTION_RE.search(line) else line)
        text = "\n".join(safe_lines)
    return text


def sanitize_for_ai(value: Any, *, block_prompt_injection: bool = False) -> Any:
    """Recursively remove PII fields and redact PII patterns."""
    if isinstance(value, dict):
        clean: dict[str, Any] = {}
        for key, item in value.items():
            folded = str(key).casefold().replace("_", " ")
            is_business_name = folded in {"product name", "shop name", "company name"}
            if not is_business_name and any(marker in folded for marker in PII_FIELD_MARKERS):
                clean[str(key)] = "[REDACTED_PII]"
            else:
                clean[str(key)] = sanitize_for_ai(item, block_prompt_injection=block_prompt_injection)
        return clean
    if isinstance(value, list):
        return [sanitize_for_ai(item, block_prompt_injection=block_prompt_injection) for item in value]
    if isinstance(value, tuple):
        return tuple(sanitize_for_ai(item, block_prompt_injection=block_prompt_injection) for item in value)
    if isinstance(value, str):
        return sanitize_text(value, block_prompt_injection=block_prompt_injection)
    return value


def contains_pii(value: str) -> bool:
    return bool(
        _EMAIL_RE.search(value) or _PHONE_RE.search(value)
        or _ADDRESS_RE.search(value) or _NAME_RE.search(value)
    )
