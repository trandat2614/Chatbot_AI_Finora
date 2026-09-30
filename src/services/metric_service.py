"""Deterministic metrics over Unified Commerce data."""
from __future__ import annotations

import unicodedata

import pandas as pd

from src.schemas.commerce import AnalysisStatus, MetricResult

REQUIRED_COLUMNS = {
    "order_id", "created_at", "quantity", "selling_price", "order_status",
    "seller_discount", "platform_fee", "transaction_fee", "service_fee", "refund_amount",
}


def _fold(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(char for char in text if not unicodedata.combining(char)).lower()


def cancelled_mask(frame: pd.DataFrame) -> pd.Series:
    return frame["order_status"].map(
        lambda value: any(term in _fold(value) for term in ("cancel", "huy", "cancelled", "canceled"))
    )


def first_order_value(values: pd.Series) -> float:
    """Return one order-level amount even if a marketplace repeats it per item."""
    numeric = pd.to_numeric(values, errors="coerce").fillna(0).clip(lower=0)
    nonzero = numeric.loc[numeric.ne(0)]
    return float(nonzero.iloc[0]) if not nonzero.empty else 0.0


def order_level_values(frame: pd.DataFrame) -> pd.DataFrame:
    """Collapse fields whose monetary ownership is ORDER_LEVEL."""
    fields = [
        "platform_fee", "transaction_fee", "service_fee",
        "shipping_fee", "refund_amount",
    ]
    available = [name for name in fields if name in frame.columns]
    if frame.empty or not available:
        return pd.DataFrame(columns=available)
    return frame.groupby(frame["order_id"].astype(str), sort=False)[available].agg(
        first_order_value
    )


class MetricService:
    def calculate(self, frame: pd.DataFrame) -> MetricResult:
        missing = sorted(REQUIRED_COLUMNS.difference(frame.columns))
        if frame.empty or missing:
            return MetricResult(
                status=AnalysisStatus.INSUFFICIENT_DATA,
                missing_fields=missing or ["orders"],
            )
        data = frame.copy()
        for name in REQUIRED_COLUMNS.difference({"order_id", "created_at", "order_status"}):
            data[name] = pd.to_numeric(data[name], errors="coerce").fillna(0).clip(lower=0)
        data["created_at"] = pd.to_datetime(data["created_at"], errors="coerce", utc=True)
        data = data.dropna(subset=["order_id", "created_at"])
        if data.empty:
            return MetricResult(status=AnalysisStatus.INSUFFICIENT_DATA, missing_fields=["valid created_at/order_id"])

        total_orders = int(data["order_id"].astype(str).nunique())
        is_cancelled = cancelled_mask(data)
        active = data.loc[~is_cancelled]
        active_order_values = order_level_values(active)
        cancelled_orders = int(data.loc[is_cancelled, "order_id"].astype(str).nunique())
        refunded_orders = int(data.loc[data["refund_amount"] > 0, "order_id"].astype(str).nunique())
        revenue = float((active["selling_price"] * active["quantity"]).sum())
        units = int(active["quantity"].sum())
        refunds = float(active_order_values.get("refund_amount", pd.Series(dtype=float)).sum())
        seller_discount = float(active["seller_discount"].sum())
        fee_columns = [
            name for name in ("platform_fee", "transaction_fee", "service_fee")
            if name in active_order_values
        ]
        fees = float(active_order_values[fee_columns].sum().sum()) if fee_columns else 0.0
        net_revenue = revenue - refunds - fees

        warnings: list[str] = []
        growth = self._growth(active)
        if growth is None:
            warnings.append("Không đủ ít nhất hai ngày dữ liệu để tính sales_growth.")
        span_days = max((data["created_at"].max() - data["created_at"].min()).days + 1, 1)
        return MetricResult(
            status=AnalysisStatus.OK,
            revenue=round(revenue, 2),
            order_count=total_orders,
            units_sold=units,
            aov=round(revenue / max(total_orders - cancelled_orders, 1), 2),
            cancellation_rate=round(cancelled_orders / total_orders * 100, 4) if total_orders else None,
            refund_rate=round(refunded_orders / total_orders * 100, 4) if total_orders else None,
            seller_discount=round(seller_discount, 2),
            marketplace_fee=round(fees, 2),
            net_revenue=round(net_revenue, 2),
            sales_growth=round(growth, 4) if growth is not None else None,
            sales_velocity=round(units / span_days, 4),
            warnings=warnings,
        )

    @staticmethod
    def _growth(frame: pd.DataFrame) -> float | None:
        if frame.empty:
            return None
        daily = (
            frame.assign(revenue=frame["selling_price"] * frame["quantity"])
            .groupby(frame["created_at"].dt.date)["revenue"].sum().sort_index()
        )
        if len(daily) < 2:
            return None
        midpoint = max(len(daily) // 2, 1)
        previous = float(daily.iloc[:midpoint].mean())
        current = float(daily.iloc[midpoint:].mean())
        return None if previous <= 0 else (current - previous) / previous * 100
