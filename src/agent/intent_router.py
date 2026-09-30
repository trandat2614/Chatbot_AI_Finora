"""Deterministic, safe intent routing with fallback to the existing chatbot."""
from __future__ import annotations

from enum import Enum

from src.services.trend_service import fold_text


class Intent(str, Enum):
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
        matches = [intent for intent, terms in self.RULES if any(term in folded for term in terms)]
        return matches[0] if len(matches) == 1 else Intent.GENERAL_CHAT
