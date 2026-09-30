"""Build and validate LLM context from verified structured tool results only."""
from __future__ import annotations

import json
import math
import re
from decimal import Decimal, InvalidOperation
from typing import Any

from src.agent.intent_router import Intent
from src.security.privacy import sanitize_for_ai

_NUMBER_RE = re.compile(r"(?<![\w])[-+]?\d(?:[\d.,]*\d)?(?:\s*%)?")

# Legacy Web currently sends a compact orderSummary instead of synchronising raw
# orders into the AI database. Only known aggregate fields are accepted so an
# arbitrary object cannot become prompt context.
_SUMMARY_METRIC_ALIASES = {
    "revenue": "revenue",
    "totalrevenue": "revenue",
    "doanhthu": "revenue",
    "gmv": "gmv",
    "netrevenue": "net_revenue",
    "totalorders": "order_count",
    "ordercount": "order_count",
    "orders": "order_count",
    "unitssold": "units_sold",
    "totalunits": "units_sold",
    "aov": "aov",
    "averageordervalue": "aov",
    "refundrate": "refund_rate",
    "cancellationrate": "cancellation_rate",
    "cancelrate": "cancellation_rate",
    "sellerdiscount": "seller_discount",
    "marketplacefee": "marketplace_fee",
    "platformfee": "marketplace_fee",
    "transactionfee": "transaction_fee",
    "servicefee": "service_fee",
    "shippingfee": "shipping_fee",
    "salesgrowth": "sales_growth",
    "revenuegrowth": "sales_growth",
    "growthrate": "sales_growth",
    "salesvelocity": "sales_velocity",
    "refundamount": "refund_amount",
    "totalprofit": "profit",
    "netprofit": "profit",
    "profit": "profit",
    "profitmargin": "profit_margin",
    "conversionrate": "conversion_rate",
}


def _summary_key(value: object) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def _summary_number(value: object) -> int | float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if abs(value) <= 10**18 else None
    if isinstance(value, float):
        return value if math.isfinite(value) and abs(value) <= 10**18 else None
    if isinstance(value, str) and re.fullmatch(r"[-+]?\d+(?:\.\d+)?", value.strip()):
        parsed = float(value)
        return parsed if math.isfinite(parsed) and abs(parsed) <= 10**18 else None
    return None


def build_legacy_summary_result(summary: dict[str, Any]) -> dict[str, Any] | None:
    """Convert an authenticated legacy Web snapshot into guarded metrics.

    This compatibility bridge does not accept instructions, labels, free text or
    unknown fields. The resulting numbers are still post-validated after LLM
    generation, so the model cannot introduce a metric absent from the snapshot.
    """
    metrics: dict[str, int | float] = {}

    def collect(value: object, depth: int = 0) -> None:
        if depth > 4 or not isinstance(value, dict):
            return
        for raw_name, raw_value in value.items():
            canonical = _SUMMARY_METRIC_ALIASES.get(_summary_key(raw_name))
            number = _summary_number(raw_value)
            if canonical and number is not None:
                metrics[canonical] = number
            elif isinstance(raw_value, dict):
                collect(raw_value, depth + 1)

    collect(summary)
    if not metrics:
        return None

    source = {
        "type": "snapshot",
        "service": "web_backend_order_summary",
        "period": {"selection": "legacy_snapshot", "from": None, "to": None},
    }
    return {
        "status": "OK",
        "metrics": metrics,
        "has_verified_metrics": True,
        "verified_metrics": [
            {
                "name": name,
                "value": value,
                "status": "AVAILABLE",
                "source": source,
            }
            for name, value in metrics.items()
        ],
        "provenance": source,
    }


def has_verified_metrics(result: dict[str, Any]) -> bool:
    if result.get("status") != "OK" or not result.get("has_verified_metrics"):
        return False
    metrics = result.get("verified_metrics")
    return bool(
        isinstance(metrics, list)
        and all(
            isinstance(item, dict)
            and item.get("status") == "AVAILABLE"
            and item.get("value") is not None
            and isinstance(item.get("source"), dict)
            and item["source"].get("type")
            and item["source"].get("service")
            for item in metrics
        )
    )


def build_verified_context(result: dict[str, Any]) -> str:
    """Return a strongly labelled block after enforcing metric provenance."""
    if not has_verified_metrics(result):
        return "VERIFIED SHOP METRICS:\nNONE"
    safe_result = sanitize_for_ai(result, block_prompt_injection=True)
    source_type = str(result.get("provenance", {}).get("type", ""))
    heading = (
        "AUTHENTICATED WEB METRIC SNAPSHOT (legacy compatibility data)"
        if source_type == "snapshot"
        else "VERIFIED SHOP METRICS (authoritative structured data)"
    )
    return (
        heading + "\n"
        + json.dumps(safe_result, ensure_ascii=False, indent=2)
        + "\nOnly values in verified_metrics may be stated as shop facts; "
        "never infer a missing value."
    )


def public_metric_sources(result: dict[str, Any]) -> list[dict[str, Any]]:
    """Expose provenance without leaking raw tenant/shop identifiers."""
    seen: set[tuple[str, str, str]] = set()
    sources: list[dict[str, Any]] = []
    for metric in result.get("verified_metrics", []):
        source = metric.get("source", {}) if isinstance(metric, dict) else {}
        period = source.get("period") if isinstance(source.get("period"), dict) else {}
        key = (
            str(source.get("type", "")),
            str(source.get("service", "")),
            json.dumps(period, sort_keys=True),
        )
        if not key[0] or not key[1] or key in seen:
            continue
        seen.add(key)
        sources.append(
            {
                "source": key[1],
                "type": "database" if key[0] == "postgresql" else key[0],
                "name": key[1],
                "period": period or None,
            }
        )
    return sources


def insufficient_data_answer(intent: Intent) -> str:
    labels = {
        Intent.BUSINESS_OVERVIEW: "tình hình kinh doanh",
        Intent.BUSINESS_HEALTH: "sức khỏe kinh doanh",
        Intent.REVENUE_LEAKAGE: "doanh thu và chi phí",
        Intent.ORDER_ANALYSIS: "đơn hàng",
        Intent.REFUND_ANALYSIS: "hoàn tiền",
        Intent.PRODUCT_ANALYSIS: "hiệu suất sản phẩm",
        Intent.OPPORTUNITIES: "cơ hội sản phẩm",
        Intent.ACTION_PLAN: "kế hoạch hành động",
        Intent.SALES_PLAN: "kế hoạch bán hàng",
        Intent.MARKETING_PLAN: "kế hoạch truyền thông",
    }
    subject = labels.get(intent, "chỉ số được yêu cầu")
    return (
        f"Hiện Finora chưa có đủ dữ liệu bán hàng đã xác thực của shop để phân tích {subject}. "
        "Hãy nhập dữ liệu CSV hoặc XLSX qua mục nhập dữ liệu trước."
    )


def deterministic_grounded_answer(intent: Intent, result: dict[str, Any]) -> str:
    """Safe fallback if model output contains a number absent from tool data."""
    metrics = result.get("metrics", {})
    if intent in {
        Intent.BUSINESS_OVERVIEW,
        Intent.BUSINESS_HEALTH,
        Intent.ORDER_ANALYSIS,
        Intent.REFUND_ANALYSIS,
    }:
        labels = (
            ("revenue", "Doanh thu", "VND"),
            ("net_revenue", "Doanh thu thuần", "VND"),
            ("order_count", "Số đơn", ""),
            ("units_sold", "Sản phẩm bán ra", ""),
            ("aov", "Giá trị đơn trung bình", "VND"),
            ("refund_rate", "Tỷ lệ hoàn tiền", "%"),
            ("cancellation_rate", "Tỷ lệ hủy đơn", "%"),
            ("marketplace_fee", "Phí sàn", "VND"),
            ("sales_growth", "Tăng trưởng doanh thu", "%"),
        )
        lines = []
        for key, label, unit in labels:
            value = metrics.get(key)
            if value is None:
                continue
            rendered = f"{value:,.2f}".rstrip("0").rstrip(".")
            lines.append(f"- {label}: {rendered} {unit}".rstrip())
        if lines:
            return "Số liệu đã xác thực từ dữ liệu của shop:\n" + "\n".join(lines)

    if intent == Intent.REVENUE_LEAKAGE:
        labels = (
            ("gmv", "GMV", "VND"),
            ("collected_revenue", "Doanh thu đã thu", "VND"),
            ("net_revenue", "Doanh thu thuần", "VND"),
            ("total_leakage", "Tổng thất thoát", "VND"),
            ("leakage_rate", "Tỷ lệ thất thoát", "%"),
        )
        lines = []
        for key, label, unit in labels:
            value = result.get(key)
            if value is not None:
                rendered = f"{value:,.2f}".rstrip("0").rstrip(".")
                lines.append(f"- {label}: {rendered} {unit}".rstrip())
        if lines:
            return "Số liệu tài chính đã xác thực từ dữ liệu của shop:\n" + "\n".join(lines)

    if intent == Intent.PRODUCT_ANALYSIS and result.get("products"):
        lines = []
        for product in result["products"][:5]:
            product_metrics = product.get("metrics", {})
            lines.append(
                f"- SKU {product.get('sku')}: {product.get('classification')}; "
                f"doanh thu {product_metrics.get('revenue', 0):,.2f} VND; "
                f"số đơn {product_metrics.get('order_count', 0)}."
            )
        return "Phân tích sản phẩm từ dữ liệu đã xác thực:\n" + "\n".join(lines)

    return (
        "Finora đã truy vấn dữ liệu đã xác thực, nhưng chưa thể tạo phần diễn giải "
        "mà không đưa thêm số liệu ngoài nguồn."
    )


def _decimal(value: object) -> Decimal | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        try:
            return Decimal(str(value)).normalize()
        except InvalidOperation:
            return None
    return None


def _number_from_text(token: str) -> Decimal | None:
    raw = token.strip().rstrip("%").strip()
    if not raw:
        return None
    sign = ""
    if raw[0] in "+-":
        sign, raw = raw[0], raw[1:]
    if "," in raw and "." in raw:
        last_separator = max(raw.rfind(","), raw.rfind("."))
        integer = re.sub(r"[.,]", "", raw[:last_separator])
        raw = integer + "." + raw[last_separator + 1 :]
    elif "," in raw:
        parts = raw.split(",")
        raw = "".join(parts) if len(parts) > 2 or all(len(p) == 3 for p in parts[1:]) else ".".join(parts)
    elif "." in raw:
        parts = raw.split(".")
        if len(parts) > 2 or (len(parts) == 2 and len(parts[1]) == 3):
            raw = "".join(parts)
    try:
        return Decimal(sign + raw).normalize()
    except InvalidOperation:
        return None


def _collect_numbers(value: Any) -> set[Decimal]:
    values: set[Decimal] = set()
    if isinstance(value, dict):
        for item in value.values():
            values.update(_collect_numbers(item))
    elif isinstance(value, (list, tuple)):
        for item in value:
            values.update(_collect_numbers(item))
    else:
        number = _decimal(value)
        if number is not None:
            values.add(number)
    return values


def numeric_claims_are_grounded(answer: str, result: dict[str, Any]) -> bool:
    """Reject model output containing numeric claims absent from verified data."""
    allowed = _collect_numbers(result)
    for token in _NUMBER_RE.findall(answer):
        number = _number_from_text(token)
        if number is not None and number not in allowed:
            return False
    return True
