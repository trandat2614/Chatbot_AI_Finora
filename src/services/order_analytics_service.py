"""Deterministic, tenant-scoped order statistics for APIs and AI tools."""
from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pandas as pd

from config.settings import settings
from src.services.metric_service import cancelled_mask


def _iso(value: object) -> str | None:
    if value is None or pd.isna(value):
        return None
    return pd.Timestamp(value).isoformat()


class OrderAnalyticsService:
    """Calculate aggregates without sending order rows to the LLM."""

    def summarize(
        self,
        frame: pd.DataFrame,
        *,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
        platform: str | None = None,
        status: str | None = None,
    ) -> dict:
        timezone_name = settings.BUSINESS_TIMEZONE
        if frame.empty:
            return self._empty(timezone_name, start_at, end_at, platform, status)

        data = frame.copy()
        data["created_at"] = pd.to_datetime(data.get("created_at"), errors="coerce", utc=True)
        data = data.dropna(subset=["created_at", "order_id", "platform"])
        if start_at is not None:
            data = data.loc[data["created_at"] >= self._utc(start_at)]
        if end_at is not None:
            data = data.loc[data["created_at"] < self._utc(end_at)]
        if platform:
            data = data.loc[data["platform"].astype(str).str.lower() == platform.lower()]
        if status:
            data = data.loc[data["order_status"].astype(str).str.casefold() == status.casefold()]
        if data.empty:
            return self._empty(timezone_name, start_at, end_at, platform, status)

        for name in ("quantity", "selling_price"):
            data[name] = pd.to_numeric(data.get(name), errors="coerce").fillna(0).clip(lower=0)
        data["order_key"] = (
            data["platform"].astype(str) + "\x00" + data["order_id"].astype(str)
        )
        data["line_revenue"] = data["selling_price"] * data["quantity"]
        cancelled = cancelled_mask(data)
        active = data.loc[~cancelled]
        order_heads = data.drop_duplicates("order_key", keep="first")
        active_heads = active.drop_duplicates("order_key", keep="first")

        total_orders = int(order_heads["order_key"].nunique())
        cancelled_orders = int(
            data.loc[cancelled, "order_key"].drop_duplicates().shape[0]
        )
        revenue = float(active["line_revenue"].sum())
        local_zone = ZoneInfo(timezone_name)
        trend_frame = active.assign(
            local_date=active["created_at"].dt.tz_convert(local_zone).dt.date.astype(str)
        )
        daily = (
            trend_frame.groupby("local_date", sort=True)
            .agg(order_count=("order_key", "nunique"), revenue=("line_revenue", "sum"))
            .reset_index()
        )
        by_status = (
            order_heads.groupby(order_heads["order_status"].astype(str), sort=True)["order_key"]
            .nunique()
            .to_dict()
        )
        by_platform = (
            order_heads.groupby(order_heads["platform"].astype(str), sort=True)["order_key"]
            .nunique()
            .to_dict()
        )
        revenue_by_platform = (
            active.groupby(active["platform"].astype(str), sort=True)["line_revenue"]
            .sum()
            .round(2)
            .to_dict()
        )
        product_group = (
            active.assign(product_name=active["product_name"].fillna("Không xác định").astype(str))
            .groupby("product_name", sort=False)
            .agg(units_sold=("quantity", "sum"), revenue=("line_revenue", "sum"))
            .reset_index()
            .sort_values(["units_sold", "revenue", "product_name"], ascending=[False, False, True])
            .head(10)
        )
        return {
            "status": "OK",
            "timezone": timezone_name,
            "filters": self._filters(start_at, end_at, platform, status),
            "revenue_definition": (
                "Tổng selling_price × quantity của đơn không hủy trong khoảng [start_at, end_at); "
                "chưa trừ hoàn tiền, phí sàn, phí giao dịch, phí dịch vụ hoặc vận chuyển."
            ),
            "total_orders": total_orders,
            "revenue": round(revenue, 2),
            "currency": "VND",
            "average_order_value": round(revenue / max(len(active_heads), 1), 2),
            "cancelled_orders": cancelled_orders,
            "orders_by_status": {str(key): int(value) for key, value in by_status.items()},
            "orders_by_platform": {str(key): int(value) for key, value in by_platform.items()},
            "revenue_by_platform": {
                str(key): float(value) for key, value in revenue_by_platform.items()
            },
            "top_products": [
                {
                    "product_name": row.product_name,
                    "units_sold": int(row.units_sold),
                    "revenue": round(float(row.revenue), 2),
                }
                for row in product_group.itertuples(index=False)
            ],
            "trend": [
                {
                    "date": row.local_date,
                    "order_count": int(row.order_count),
                    "revenue": round(float(row.revenue), 2),
                }
                for row in daily.itertuples(index=False)
            ],
        }

    @staticmethod
    def _utc(value: datetime) -> pd.Timestamp:
        stamp = pd.Timestamp(value)
        if stamp.tzinfo is None:
            stamp = stamp.tz_localize(timezone.utc)
        return stamp.tz_convert(timezone.utc)

    @staticmethod
    def _filters(
        start_at: datetime | None,
        end_at: datetime | None,
        platform: str | None,
        status: str | None,
    ) -> dict:
        return {
            "start_at": _iso(start_at),
            "end_at": _iso(end_at),
            "platform": platform,
            "status": status,
        }

    def _empty(
        self,
        timezone_name: str,
        start_at: datetime | None,
        end_at: datetime | None,
        platform: str | None,
        status: str | None,
    ) -> dict:
        return {
            "status": "OK",
            "timezone": timezone_name,
            "filters": self._filters(start_at, end_at, platform, status),
            "revenue_definition": (
                "Tổng selling_price × quantity của đơn không hủy trong khoảng [start_at, end_at); "
                "chưa trừ hoàn tiền, phí sàn, phí giao dịch, phí dịch vụ hoặc vận chuyển."
            ),
            "total_orders": 0,
            "revenue": 0.0,
            "currency": "VND",
            "average_order_value": 0.0,
            "cancelled_orders": 0,
            "orders_by_status": {},
            "orders_by_platform": {},
            "revenue_by_platform": {},
            "top_products": [],
            "trend": [],
        }
