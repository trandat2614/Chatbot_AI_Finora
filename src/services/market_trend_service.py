"""Historical market-trend analysis built on the existing trend loader."""
from __future__ import annotations

import hashlib
from typing import Any

from src.repositories.interfaces import TrendRepository
from src.services.trend_service import TrendDataLoader, normalise_gender, normalise_timeframe


class MarketTrendService:
    def __init__(
        self,
        loader: TrendDataLoader | None = None,
        repository: TrendRepository | None = None,
    ) -> None:
        self.loader = loader or TrendDataLoader()
        self.repository = repository

    @staticmethod
    def _state(rank: int, sales_growth: int, sales_30d: int, period: str) -> str:
        if sales_growth < 0:
            return "COOLING"
        if rank <= 10 and sales_30d > 0:
            return "BESTSELLER"
        if period == "today" and sales_growth > 0:
            return "EMERGING"
        if sales_growth >= max(sales_30d * 0.2, 10):
            return "RISING"
        return "SUSTAINED"

    def get_trends(
        self, category: str, period: str = "7d", limit: int = 20, *, historical: bool = False
    ) -> dict[str, Any]:
        gender = normalise_gender(category)
        timeframe = normalise_timeframe(period)
        if historical and self.repository is not None:
            stored = self.repository.list_snapshots(gender, timeframe, limit)
            if stored:
                return {
                    "status": "OK",
                    "source": "relational_marketplace_snapshots",
                    "category": gender,
                    "period": timeframe,
                    "items": [
                        {
                            "capture_date": item["capture_date"].date().isoformat(),
                            "platform": item["platform"],
                            "category": item["category"],
                            "period": item["period"],
                            "rank": int(item["rank"] or 0),
                            "product_name": item["product_name"],
                            "shop": item["shop_name"] or "",
                            "price": float(item["price"] or 0),
                            "sales_growth": float(item["sales_growth"] or 0),
                            "sales_30d": int(item["sales_30d"] or 0),
                            "rating": item["rating"],
                            "url": item["source_url"] or "",
                            "trend_state": self._state(
                                int(item["rank"] or 0),
                                int(item["sales_growth"] or 0),
                                int(item["sales_30d"] or 0),
                                timeframe,
                            ),
                        }
                        for item in stored
                    ],
                    "warnings": self.loader.warnings,
                }
        source = self.loader.select_history(gender, timeframe) if historical else self.loader.select(gender, timeframe)
        frame = source.head(max(1, min(limit, 100)))
        items = []
        for _, row in frame.iterrows():
            rank = int(row.get("Hạng", 0) or 0)
            growth = int(row.get("Lượt bán tăng", 0) or 0)
            sales = int(row.get("Đã bán 30 ngày", 0) or 0)
            items.append({
                "capture_date": str(row.get("capture_date", "unknown")),
                "platform": "shopee",
                "category": gender,
                "period": timeframe,
                "rank": rank,
                "product_name": str(row.get("Sản phẩm", "")),
                "shop": str(row.get("Shop", "")),
                "price": int(row.get("Giá", 0) or 0),
                "sales_growth": growth,
                "sales_30d": sales,
                "rating": row.get("Đánh giá"),
                "url": str(row.get("Link", "")),
                "trend_state": self._state(rank, growth, sales, timeframe),
            })
        if self.repository is not None and items:
            snapshots = []
            for item in items:
                identity = (
                    f"{item['capture_date']}:{item['platform']}:{item['category']}:"
                    f"{item['period']}:{item['rank']}:{item['product_name']}:{item['shop']}"
                )
                snapshots.append(
                    {
                        "snapshot_id": hashlib.sha256(identity.encode()).hexdigest(),
                        "capture_date": item["capture_date"],
                        "platform": item["platform"],
                        "category": item["category"],
                        "period": item["period"],
                        "product_name": item["product_name"],
                        "shop_name": item["shop"],
                        "rank": item["rank"],
                        "price": item["price"],
                        "sales_growth": item["sales_growth"],
                        "sales_30d": item["sales_30d"],
                        "rating": item["rating"],
                        "source_url": item["url"],
                    }
                )
            self.repository.upsert_snapshots(snapshots)
        return {
            "status": "OK" if items else "INSUFFICIENT_DATA",
            "source": "public_marketplace_snapshot",
            "category": gender,
            "period": timeframe,
            "items": items,
            "warnings": self.loader.warnings,
        }
