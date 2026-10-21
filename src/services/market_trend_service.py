"""Compatibility projection of request-scoped web backend trend JSON."""
from __future__ import annotations

from src.schemas.product_trends import TrendExportData
from src.services.product_trend_service import ProductTrendService


class MarketTrendService:
    def __init__(self, snapshot: TrendExportData | None = None):
        self.snapshot = snapshot

    @staticmethod
    def _state(rank, sales_growth, sales_30d, period):
        if sales_growth is None:
            return "UNKNOWN"
        if sales_growth < 0:
            return "COOLING"
        if rank is not None and 1 <= rank <= 10 and sales_30d and sales_30d > 0:
            return "BESTSELLER"
        if period == "today" and sales_growth > 0:
            return "EMERGING"
        if sales_30d is not None and sales_growth >= max(sales_30d * 0.2, 10):
            return "RISING"
        return "SUSTAINED"

    def get_trends(self, category="nam", period="7d", limit=20, *, historical=False):
        evidence = ProductTrendService().evidence(snapshot=self.snapshot, category=category, period=period, limit=limit)
        items = []
        for item in evidence.get("items", []):
            items.append({
                "capture_date": evidence["date"], "platform": "shopee", "category": item["categoryId"],
                "period": evidence["period"], "rank": item.get("rank"), "product_name": item["title"],
                "shop": item.get("shopName") or item.get("shopId") or "", "price": item.get("price"),
                "sales_growth": item.get("salesIncrease"), "sales_30d": item.get("sold30d"),
                "rating": item.get("rating"), "url": item.get("productUrl") or "",
                "trend_state": self._state(item.get("rank"), item.get("salesIncrease"), item.get("sold30d"), evidence["period"]),
            })
        return {"status": evidence["status"], "source": "web_backend_json", "category": category or "all",
            "period": period, "items": items, "warnings": evidence.get("warnings", [])}
