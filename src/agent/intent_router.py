"""Deterministic, safe intent routing with fallback to the existing chatbot."""
from __future__ import annotations

import re
from enum import Enum

from src.services.trend_service import fold_text


class Intent(str, Enum):
    ORDER_LOOKUP = "ORDER_LOOKUP"
    ORDER_STATISTICS = "ORDER_STATISTICS"
    BUSINESS_HEALTH = "BUSINESS_HEALTH"
    PRODUCT_ANALYSIS = "PRODUCT_ANALYSIS"
    FINANCIAL_ANALYSIS = "FINANCIAL_ANALYSIS"
    MARKET_TREND = "MARKET_TREND"
    PRODUCT_OPPORTUNITY = "PRODUCT_OPPORTUNITY"
    ACTION_PLAN = "ACTION_PLAN"
    SALES_PLAN = "SALES_PLAN"
    MARKETING_PLAN = "MARKETING_PLAN"
    POLICY_QUESTION = "POLICY_QUESTION"
    GENERAL_CHAT = "GENERAL_CHAT"


class IntentRouter:
    ORDER_TERMS = (
        "don hang", "ma don", "don nay", "don do", "order", "giao chua", "dang o dau",
    )
    LOOKUP_TERMS = (
        "tim", "kiem tra", "tra cuu", "thong tin", "trang thai", "giao chua",
        "dang o dau", "gia tri bao nhieu", "don nay", "don do",
    )
    STATISTICS_TERMS = (
        "bao nhieu don", "tong so don", "doanh thu", "don bi huy", "don huy",
        "ban chay", "trung binh don", "aov", "theo ngay", "theo thang",
        "nen tang nao", "so don shopee", "so don lazada", "so don tiktok",
    )
    RULES = (
        (Intent.MARKETING_PLAN, ("ke hoach truyen thong", "communication plan", "facebook", "zalo", "content plan")),
        (Intent.SALES_PLAN, ("sales plan", "ke hoach ban hang", "ke hoach doanh so")),
        (Intent.ACTION_PLAN, ("action plan", "hanh dong uu tien", "nen lam gi", "viec quan trong")),
        (Intent.PRODUCT_OPPORTUNITY, ("co hoi san pham", "opportunity", "san pham tiem nang", "nen ban gi")),
        (Intent.BUSINESS_HEALTH, ("business health", "suc khoe kinh doanh", "bat thuong", "canh bao shop")),
        (Intent.PRODUCT_ANALYSIS, ("product doctor", "phan tich sku", "san pham nao", "sku")),
        (Intent.FINANCIAL_ANALYSIS, ("revenue leakage", "that thoat", "gmv", "phi san", "net revenue")),
        (Intent.MARKET_TREND, ("xu huong", "trend", "thi truong", "bestseller")),
        (Intent.POLICY_QUESTION, ("chinh sach", "policy", "thue", "quy dinh", "dieu khoan")),
    )

    def route(self, question: str) -> Intent:
        folded = fold_text(question)
        if self.is_order_lookup(question):
            return Intent.ORDER_LOOKUP
        if any(term in folded for term in self.STATISTICS_TERMS):
            return Intent.ORDER_STATISTICS
        matches = [intent for intent, terms in self.RULES if any(term in folded for term in terms)]
        return matches[0] if len(matches) == 1 else Intent.GENERAL_CHAT

    def is_order_lookup(self, question: str) -> bool:
        folded = fold_text(question)
        mentions_order = any(term in folded for term in self.ORDER_TERMS) or bool(
            re.search(r"\bdon\b", folded)
        )
        lookup_language = any(term in folded for term in self.LOOKUP_TERMS)
        return mentions_order and (lookup_language or self.extract_order_id(question) is not None)

    @staticmethod
    def extract_order_id(question: str) -> str | None:
        """Extract a plausible identifier; repository lookup remains authoritative."""
        labelled = re.search(
            r"(?:m[aã]\s*[đd]ơn(?:\s*h[aà]ng)?|order(?:\s*id)?)\s*[:#-]?\s*([A-Za-z0-9][A-Za-z0-9_-]{4,199})",
            question,
            re.IGNORECASE,
        )
        if labelled:
            return labelled.group(1)
        candidates = re.findall(r"(?<![\w-])([A-Za-z0-9][A-Za-z0-9_-]{5,199})(?![\w-])", question)
        for candidate in candidates:
            if any(char.isdigit() for char in candidate) and not re.fullmatch(
                r"20\d{2}[-_/]\d{1,2}[-_/]\d{1,2}", candidate
            ):
                return candidate
        return None

    def extract_order_id_from_history(self, history: list[dict[str, str]] | None) -> str | None:
        for item in reversed(history or []):
            content = str(item.get("content", ""))
            explicit = re.search(
                r"(?:Mã đơn|Đơn hàng|Order(?: ID)?)\s*[:#]?\s*([A-Za-z0-9][A-Za-z0-9_-]{4,199})",
                content,
                re.IGNORECASE,
            )
            if explicit:
                return explicit.group(1)
            candidate = self.extract_order_id(content)
            if candidate and self.is_order_lookup(content):
                return candidate
        return None
