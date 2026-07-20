"""
Marketing metrics tool for FINORA AI Business Advisor.

Calculates e-commerce and digital marketing KPIs from revenue data.
Each metric carries its formula and interpretation for transparency.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class MarketingMetric:
    """A single marketing metric with context."""

    name: str
    value: Optional[float]
    formula: str
    required_fields: list[str]
    interpretation: str
    unit: str = ""  # e.g. "%" or "₫" or ""


@dataclass
class MarketingMetrics:
    """Collection of computed marketing metrics."""

    cac: MarketingMetric = field(default=None)  # type: ignore[assignment]
    aov: MarketingMetric = field(default=None)  # type: ignore[assignment]
    roas: MarketingMetric = field(default=None)  # type: ignore[assignment]
    marketing_cost_ratio: MarketingMetric = field(default=None)  # type: ignore[assignment]
    conversion_rate: MarketingMetric = field(default=None)  # type: ignore[assignment]
    repeat_purchase_rate: MarketingMetric = field(default=None)  # type: ignore[assignment]
    refund_rate: MarketingMetric = field(default=None)  # type: ignore[assignment]
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        """Return all metrics as a plain dict (for display / serialisation)."""
        result = {}
        for attr in [
            "cac", "aov", "roas", "marketing_cost_ratio",
            "conversion_rate", "repeat_purchase_rate", "refund_rate",
        ]:
            m: Optional[MarketingMetric] = getattr(self, attr)
            if m is not None:
                result[m.name] = {
                    "value": m.value,
                    "unit": m.unit,
                    "formula": m.formula,
                    "interpretation": m.interpretation,
                }
        return result


class MarketingMetricsTool:
    """Compute marketing KPIs from a revenue DataFrame."""

    def compute(self, df: pd.DataFrame) -> MarketingMetrics:
        """Calculate all computable marketing metrics.

        Args:
            df: Revenue DataFrame with normalised lower-case column names.

        Returns:
            MarketingMetrics instance.
        """
        df = df.copy()
        df.columns = [c.strip().lower() for c in df.columns]

        result = MarketingMetrics()
        cols = set(df.columns)

        # Coerce numeric columns
        numeric = [
            "revenue", "orders", "marketing_cost", "new_customers",
            "returning_customers", "sessions", "conversions",
            "refunds", "discounts",
        ]
        for col in numeric:
            if col in cols:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # ---- CAC (Customer Acquisition Cost) --------------------------------
        result.cac = self._compute_cac(df, cols)

        # ---- AOV (Average Order Value) --------------------------------------
        result.aov = self._compute_aov(df, cols)

        # ---- ROAS -----------------------------------------------------------
        result.roas = self._compute_roas(df, cols)

        # ---- Marketing Cost Ratio -------------------------------------------
        result.marketing_cost_ratio = self._compute_mcr(df, cols)

        # ---- Conversion Rate ------------------------------------------------
        result.conversion_rate = self._compute_conversion_rate(df, cols)

        # ---- Repeat Purchase Rate ------------------------------------------
        result.repeat_purchase_rate = self._compute_repeat_rate(df, cols)

        # ---- Refund Rate ----------------------------------------------------
        result.refund_rate = self._compute_refund_rate(df, cols)

        return result

    # ------------------------------------------------------------------ #
    # Private metric calculators
    # ------------------------------------------------------------------ #

    @staticmethod
    def _compute_cac(df: pd.DataFrame, cols: set) -> MarketingMetric:
        required = ["marketing_cost", "new_customers"]
        if all(c in cols for c in required):
            total_new = df["new_customers"].sum()
            value = (
                float(df["marketing_cost"].sum() / total_new)
                if total_new > 0
                else None
            )
            interp = (
                f"Chi phí thu hút mỗi khách hàng mới: {value:,.0f} ₫"
                if value is not None else "Không có khách hàng mới."
            )
        else:
            value = None
            interp = f"Thiếu cột: {', '.join(c for c in required if c not in cols)}"
        return MarketingMetric(
            name="CAC (Chi phí thu hút khách hàng)",
            value=value,
            formula="Tổng Marketing Cost / Tổng New Customers",
            required_fields=required,
            interpretation=interp,
            unit="₫",
        )

    @staticmethod
    def _compute_aov(df: pd.DataFrame, cols: set) -> MarketingMetric:
        required = ["revenue", "orders"]
        if all(c in cols for c in required):
            total_orders = df["orders"].sum()
            value = (
                float(df["revenue"].sum() / total_orders)
                if total_orders > 0
                else None
            )
            interp = (
                f"Giá trị đơn hàng trung bình: {value:,.0f} ₫"
                if value is not None else "Không có đơn hàng."
            )
        else:
            value = None
            interp = f"Thiếu cột: {', '.join(c for c in required if c not in cols)}"
        return MarketingMetric(
            name="AOV (Giá trị đơn hàng trung bình)",
            value=value,
            formula="Tổng Revenue / Tổng Orders",
            required_fields=required,
            interpretation=interp,
            unit="₫",
        )

    @staticmethod
    def _compute_roas(df: pd.DataFrame, cols: set) -> MarketingMetric:
        required = ["revenue", "marketing_cost"]
        if all(c in cols for c in required):
            total_mkt = df["marketing_cost"].sum()
            value = (
                float(df["revenue"].sum() / total_mkt)
                if total_mkt > 0
                else None
            )
            if value is not None:
                interp = (
                    f"Mỗi đồng chi marketing sinh ra {value:.2f} đồng doanh thu. "
                    + ("✅ Tốt (ROAS > 3)" if value >= 3 else "⚠️ Thấp (ROAS < 3, cần xem lại)")
                )
            else:
                interp = "Marketing cost = 0, không thể tính ROAS."
        else:
            value = None
            interp = f"Thiếu cột: {', '.join(c for c in required if c not in cols)}"
        return MarketingMetric(
            name="ROAS (Return on Ad Spend)",
            value=value,
            formula="Tổng Revenue / Tổng Marketing Cost",
            required_fields=required,
            interpretation=interp,
            unit="x",
        )

    @staticmethod
    def _compute_mcr(df: pd.DataFrame, cols: set) -> MarketingMetric:
        required = ["marketing_cost", "revenue"]
        if all(c in cols for c in required):
            total_rev = df["revenue"].sum()
            value = (
                float(df["marketing_cost"].sum() / total_rev * 100)
                if total_rev > 0
                else None
            )
            interp = (
                f"Chi phí marketing chiếm {value:.1f}% doanh thu."
                if value is not None else "Doanh thu = 0."
            )
        else:
            value = None
            interp = f"Thiếu cột: {', '.join(c for c in required if c not in cols)}"
        return MarketingMetric(
            name="Marketing Cost Ratio",
            value=value,
            formula="Marketing Cost / Revenue × 100",
            required_fields=required,
            interpretation=interp,
            unit="%",
        )

    @staticmethod
    def _compute_conversion_rate(df: pd.DataFrame, cols: set) -> MarketingMetric:
        required = ["conversions", "sessions"]
        if all(c in cols for c in required):
            total_sessions = df["sessions"].sum()
            value = (
                float(df["conversions"].sum() / total_sessions * 100)
                if total_sessions > 0
                else None
            )
            if value is not None:
                interp = (
                    f"Tỷ lệ chuyển đổi: {value:.2f}%. "
                    + ("✅ Tốt (> 2%)" if value >= 2 else "⚠️ Thấp (< 2%), cần tối ưu trang sản phẩm/checkout")
                )
            else:
                interp = "Sessions = 0."
        else:
            value = None
            interp = f"Thiếu cột: {', '.join(c for c in required if c not in cols)}"
        return MarketingMetric(
            name="Conversion Rate (Tỷ lệ chuyển đổi)",
            value=value,
            formula="Conversions / Sessions × 100",
            required_fields=required,
            interpretation=interp,
            unit="%",
        )

    @staticmethod
    def _compute_repeat_rate(df: pd.DataFrame, cols: set) -> MarketingMetric:
        required = ["returning_customers", "orders"]
        if all(c in cols for c in required):
            total_orders = df["orders"].sum()
            value = (
                float(df["returning_customers"].sum() / total_orders * 100)
                if total_orders > 0
                else None
            )
            if value is not None:
                interp = (
                    f"Tỷ lệ khách hàng quay lại: {value:.1f}%. "
                    + ("✅ Tốt (> 20%)" if value >= 20 else "⚠️ Thấp (< 20%), cần cải thiện retention")
                )
            else:
                interp = "Không có đơn hàng."
        else:
            value = None
            interp = f"Thiếu cột: {', '.join(c for c in required if c not in cols)}"
        return MarketingMetric(
            name="Repeat Purchase Rate (Tỷ lệ mua lại)",
            value=value,
            formula="Returning Customers / Total Orders × 100",
            required_fields=required,
            interpretation=interp,
            unit="%",
        )

    @staticmethod
    def _compute_refund_rate(df: pd.DataFrame, cols: set) -> MarketingMetric:
        required = ["refunds", "revenue"]
        if all(c in cols for c in required):
            total_rev = df["revenue"].sum()
            value = (
                float(df["refunds"].sum() / total_rev * 100)
                if total_rev > 0
                else None
            )
            if value is not None:
                interp = (
                    f"Tỷ lệ hoàn hàng: {value:.1f}% trên doanh thu. "
                    + ("✅ Bình thường (< 5%)" if value < 5 else
                       "⚠️ Cao (5–10%)" if value < 10 else
                       "🚨 Rất cao (> 10%), ảnh hưởng nghiêm trọng đến lợi nhuận")
                )
            else:
                interp = "Doanh thu = 0."
        else:
            value = None
            interp = f"Thiếu cột: {', '.join(c for c in required if c not in cols)}"
        return MarketingMetric(
            name="Refund Rate (Tỷ lệ hoàn hàng)",
            value=value,
            formula="Refunds / Revenue × 100",
            required_fields=required,
            interpretation=interp,
            unit="%",
        )


def compute_marketing_metrics(df: pd.DataFrame) -> MarketingMetrics:
    """Convenience function wrapping MarketingMetricsTool."""
    return MarketingMetricsTool().compute(df)
