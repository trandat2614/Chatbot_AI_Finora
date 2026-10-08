"""Deterministic intent routing with an account-data safety classifier."""
from __future__ import annotations

from enum import Enum

from src.services.trend_service import fold_text


class Intent(str, Enum):
    BUSINESS_OVERVIEW = "BUSINESS_OVERVIEW"
    BUSINESS_HEALTH = "BUSINESS_HEALTH"
    REVENUE_LEAKAGE = "REVENUE_LEAKAGE"
    # Backward-compatible enum aliases used by older internal callers.
    FINANCIAL_ANALYSIS = "REVENUE_LEAKAGE"
    PRODUCT_ANALYSIS = "PRODUCT_ANALYSIS"
    ORDER_ANALYSIS = "ORDER_ANALYSIS"
    REFUND_ANALYSIS = "REFUND_ANALYSIS"
    MARKET_TRENDS = "MARKET_TRENDS"
    MARKET_TREND = "MARKET_TRENDS"
    OPPORTUNITIES = "OPPORTUNITIES"
    PRODUCT_OPPORTUNITY = "OPPORTUNITIES"
    ACTION_PLAN = "ACTION_PLAN"
    SALES_PLAN = "SALES_PLAN"
    MARKETING_PLAN = "MARKETING_PLAN"
    POLICY_QUESTION = "POLICY_QUESTION"
    GENERAL_CHAT = "GENERAL_CHAT"

    @property
    def requires_business_data(self) -> bool:
        return self in {
            Intent.BUSINESS_OVERVIEW,
            Intent.BUSINESS_HEALTH,
            Intent.REVENUE_LEAKAGE,
            Intent.PRODUCT_ANALYSIS,
            Intent.ORDER_ANALYSIS,
            Intent.REFUND_ANALYSIS,
            Intent.OPPORTUNITIES,
            Intent.ACTION_PLAN,
            Intent.SALES_PLAN,
            Intent.MARKETING_PLAN,
        }


class IntentRouter:
    """Route by ordered semantic groups and fail safe for account KPI queries.

    The order is intentional: an explicit planning or market request wins over
    metric words that may appear inside the same sentence. Multiple matches
    never fall back to GENERAL_CHAT.
    """

    RULES = (
        (
            Intent.MARKETING_PLAN,
            (
                "ke hoach truyen thong", "communication plan", "content plan",
                "ke hoach marketing", "chien dich marketing",
            ),
        ),
        (
            Intent.SALES_PLAN,
            ("sales plan", "ke hoach ban hang", "ke hoach doanh so"),
        ),
        (
            Intent.ACTION_PLAN,
            ("action plan", "hanh dong uu tien", "nen lam gi", "viec quan trong"),
        ),
        (
            Intent.OPPORTUNITIES,
            ("co hoi san pham", "opportunity", "san pham tiem nang", "nen ban gi"),
        ),
        (
            Intent.MARKET_TRENDS,
            (
                "xu huong", "trend", "thi truong", "bestseller", "gia doi thu",
                "benchmark thi truong",
            ),
        ),
        (
            Intent.POLICY_QUESTION,
            ("chinh sach", "policy", "thue", "quy dinh", "dieu khoan"),
        ),
        (
            Intent.REFUND_ANALYSIS,
            (
                "hoan tien", "refund", "tra hang", "ty le hoan", "ti le hoan",
                "hoan don",
            ),
        ),
        (
            Intent.ORDER_ANALYSIS,
            (
                "don hang", "so don", "bao nhieu don", "huy don",
                "cancellation", "ty le huy", "ti le huy",
            ),
        ),
        (
            Intent.PRODUCT_ANALYSIS,
            (
                "product doctor", "phan tich sku", "san pham nao", "sku",
                "san pham ban tot", "san pham ban chay", "hieu suat san pham",
                "top san pham", "bottom san pham",
            ),
        ),
        (
            Intent.REVENUE_LEAKAGE,
            (
                "revenue leakage", "that thoat", "phi san", "net revenue",
                "doanh thu bi mat", "loi nhuan", "chi phi", "phi dich vu",
                "phi thanh toan",
            ),
        ),
        (
            Intent.BUSINESS_HEALTH,
            (
                "business health", "suc khoe kinh doanh", "bat thuong",
                "canh bao shop", "shop co on khong", "shop toi co on khong",
            ),
        ),
        (
            Intent.BUSINESS_OVERVIEW,
            (
                "tinh hinh kinh doanh", "kinh doanh thang nay", "shop dang the nao",
                "shop toi dang the nao", "kinh doanh cua toi", "doanh thu",
                "doanh so", "gmv", "aov", "tinh hinh ban hang",
                "ban the nao", "ban hang gan day",
            ),
        ),
    )

    _ACCOUNT_MARKERS = (
        "shop toi", "shop cua toi", "cua shop", "tai khoan nay", "cua toi",
        "kinh doanh", "ban hang", "doanh thu", "doanh so", "gmv", "aov",
        "don hang", "so don", "hoan tien", "refund", "huy don", "cancellation",
        "phi san", "loi nhuan", "chi phi", "tang bao nhieu", "giam bao nhieu",
        "ty le", "ti le", "bao nhieu phan tram", "%", "top sku", "bottom sku",
    )

    def route(self, question: str) -> Intent:
        folded = fold_text(question)
        for intent, terms in self.RULES:
            if any(term in folded for term in terms):
                return intent
        # A short category correction should repeat the market query. Longer
        # business questions already match their more specific intent above.
        if len(folded.split()) <= 8 and any(
            term in folded for term in ("thoi trang nu", "thoi trang nam")
        ):
            return Intent.MARKET_TRENDS
        if self.requires_account_data(question):
            # Unknown account-specific KPI wording must query verified shop data.
            return Intent.BUSINESS_OVERVIEW
        return Intent.GENERAL_CHAT

    def requires_account_data(self, question: str) -> bool:
        folded = fold_text(question)
        return any(marker in folded for marker in self._ACCOUNT_MARKERS)
