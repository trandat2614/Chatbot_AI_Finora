"""Relational historical trend snapshot repository."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from src.db.models import MarketTrendSnapshot
from src.db.session import Database, get_database


class SQLAlchemyTrendRepository:
    def __init__(self, database: Database | None = None) -> None:
        self.database = database or get_database()

    def upsert_snapshots(self, snapshots: list[dict]) -> int:
        inserted = 0
        with self.database.session() as session:
            for item in snapshots:
                snapshot_id = str(item["snapshot_id"])
                exists = session.scalar(
                    select(MarketTrendSnapshot.id).where(
                        MarketTrendSnapshot.snapshot_id == snapshot_id
                    )
                )
                if exists:
                    continue
                capture_date = item["capture_date"]
                if not isinstance(capture_date, datetime):
                    capture_date = datetime.fromisoformat(str(capture_date)).replace(
                        tzinfo=timezone.utc
                    )
                session.add(
                    MarketTrendSnapshot(
                        id=str(uuid.uuid4()),
                        snapshot_id=snapshot_id,
                        capture_date=capture_date,
                        platform=str(item["platform"]),
                        category=str(item["category"]),
                        period=str(item["period"]),
                        product_id=item.get("product_id"),
                        product_name=str(item["product_name"]),
                        shop_name=item.get("shop_name"),
                        rank=item.get("rank"),
                        price=item.get("price"),
                        sales_growth=item.get("sales_growth"),
                        sales_30d=item.get("sales_30d"),
                        rating=item.get("rating"),
                        source_url=item.get("source_url"),
                    )
                )
                inserted += 1
        return inserted

    def list_snapshots(self, category: str, period: str, limit: int = 100) -> list[dict]:
        with self.database.session() as session:
            items = session.scalars(
                select(MarketTrendSnapshot)
                .where(
                    MarketTrendSnapshot.category == category,
                    MarketTrendSnapshot.period == period,
                )
                .order_by(
                    MarketTrendSnapshot.capture_date.desc(),
                    MarketTrendSnapshot.rank.asc(),
                )
                .limit(max(1, min(limit, 500)))
            ).all()
            return [
                {
                    "snapshot_id": item.snapshot_id,
                    "capture_date": item.capture_date,
                    "platform": item.platform,
                    "category": item.category,
                    "period": item.period,
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "shop_name": item.shop_name,
                    "rank": item.rank,
                    "price": item.price,
                    "sales_growth": item.sales_growth,
                    "sales_30d": item.sales_30d,
                    "rating": item.rating,
                    "source_url": item.source_url,
                }
                for item in items
            ]
