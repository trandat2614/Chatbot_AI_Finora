"""
Revenue analysis tool for FINORA AI Business Advisor.

All calculations are performed by Python. The LLM only interprets results.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from core.exceptions import MissingColumnsError
from utils.validators import validate_csv_columns

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
# Constants
# ------------------------------------------------------------------ #

REQUIRED_COLUMNS = ["date", "revenue", "orders", "marketing_cost", "new_customers"]

OPTIONAL_COLUMNS = [
    "channel",
    "product",
    "category",
    "discounts",
    "platform_fees",
    "refunds",
    "cost_of_goods_sold",
    "operating_expenses",
    "returning_customers",
    "sessions",
    "conversions",
]


@dataclass
class RevenueMetrics:
    """Computed revenue metrics."""

    total_revenue: float = 0.0
    average_revenue: float = 0.0
    latest_revenue: float = 0.0
    revenue_growth_rate: Optional[float] = None  # % vs previous period
    average_order_value: Optional[float] = None
    customer_acquisition_cost: Optional[float] = None
    best_period: str = ""
    worst_period: str = ""
    revenue_trend: str = ""
    order_growth_rate: Optional[float] = None
    marketing_cost_ratio: Optional[float] = None
    revenue_by_channel: dict[str, float] = field(default_factory=dict)
    revenue_by_product: dict[str, float] = field(default_factory=dict)
    total_orders: int = 0
    total_marketing_cost: float = 0.0
    total_new_customers: int = 0
    available_columns: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    periods: int = 0


class RevenueAnalysisTool:
    """Analyse revenue data from a CSV-backed DataFrame."""

    def analyse(self, df: pd.DataFrame) -> RevenueMetrics:
        """Compute revenue metrics from the provided DataFrame.

        Args:
            df: DataFrame loaded from the user's CSV upload.

        Returns:
            RevenueMetrics with all computable fields populated.

        Raises:
            MissingColumnsError: When required columns are absent.
        """
        # ---- Normalise column names -----------------------------------------
        df = df.copy()
        df.columns = [c.strip().lower() for c in df.columns]

        missing = validate_csv_columns(list(df.columns), REQUIRED_COLUMNS)
        if missing:
            raise MissingColumnsError(missing)

        metrics = RevenueMetrics()
        metrics.available_columns = list(df.columns)

        # ---- Parse date -------------------------------------------------------
        try:
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date").reset_index(drop=True)
        except Exception as exc:
            logger.warning("Date parsing issue: %s", exc)
            metrics.warnings.append(
                "Cột 'date' không thể parse chính xác — một số thống kê theo thời gian có thể sai."
            )

        # ---- Coerce numeric columns ------------------------------------------
        for col in ["revenue", "orders", "marketing_cost", "new_customers"] + [
            c for c in OPTIONAL_COLUMNS if c in df.columns and c not in ("channel", "product", "category")
        ]:
            if col in df.columns:
                original_count = df[col].notna().sum()
                df[col] = pd.to_numeric(df[col], errors="coerce")
                coerced = original_count - df[col].notna().sum()
                if coerced > 0:
                    metrics.warnings.append(
                        f"Cột '{col}': {coerced} giá trị không hợp lệ đã được bỏ qua."
                    )

        metrics.periods = len(df)

        # ---- Core metrics ----------------------------------------------------
        metrics.total_revenue = float(df["revenue"].sum())
        metrics.average_revenue = float(df["revenue"].mean())
        metrics.latest_revenue = float(df["revenue"].iloc[-1]) if len(df) > 0 else 0.0
        metrics.total_orders = int(df["orders"].sum())
        metrics.total_marketing_cost = float(df["marketing_cost"].sum())
        metrics.total_new_customers = int(df["new_customers"].sum())

        # Best / worst period
        if "date" in df.columns:
            try:
                best_idx = df["revenue"].idxmax()
                worst_idx = df["revenue"].idxmin()
                metrics.best_period = str(df.loc[best_idx, "date"])[:10]
                metrics.worst_period = str(df.loc[worst_idx, "date"])[:10]
            except Exception:
                metrics.best_period = str(df["revenue"].idxmax())
                metrics.worst_period = str(df["revenue"].idxmin())

        # Revenue growth (last vs second-to-last)
        if len(df) >= 2:
            prev = float(df["revenue"].iloc[-2])
            curr = float(df["revenue"].iloc[-1])
            if prev > 0:
                metrics.revenue_growth_rate = (curr - prev) / prev * 100
            else:
                metrics.warnings.append(
                    "Không thể tính Revenue Growth Rate vì kỳ trước doanh thu = 0."
                )

        # Order growth
        if len(df) >= 2:
            prev_orders = float(df["orders"].iloc[-2])
            curr_orders = float(df["orders"].iloc[-1])
            if prev_orders > 0:
                metrics.order_growth_rate = (curr_orders - prev_orders) / prev_orders * 100

        # Revenue trend (linear slope direction)
        if len(df) >= 3:
            x = np.arange(len(df))
            y = df["revenue"].values.astype(float)
            slope = np.polyfit(x, y, 1)[0]
            if slope > 0:
                metrics.revenue_trend = "📈 Xu hướng tăng"
            elif slope < 0:
                metrics.revenue_trend = "📉 Xu hướng giảm"
            else:
                metrics.revenue_trend = "➡️ Xu hướng ngang"

        # AOV
        if metrics.total_orders > 0:
            metrics.average_order_value = metrics.total_revenue / metrics.total_orders

        # CAC
        if metrics.total_new_customers > 0:
            metrics.customer_acquisition_cost = (
                metrics.total_marketing_cost / metrics.total_new_customers
            )

        # Marketing cost ratio
        if metrics.total_revenue > 0:
            metrics.marketing_cost_ratio = (
                metrics.total_marketing_cost / metrics.total_revenue * 100
            )

        # Channel breakdown
        if "channel" in df.columns:
            ch_rev = df.groupby("channel")["revenue"].sum()
            metrics.revenue_by_channel = ch_rev.to_dict()

        # Product breakdown
        if "product" in df.columns:
            pr_rev = df.groupby("product")["revenue"].sum()
            metrics.revenue_by_product = pr_rev.to_dict()

        return metrics


def analyse_revenue(df: pd.DataFrame) -> RevenueMetrics:
    """Convenience function wrapping RevenueAnalysisTool."""
    return RevenueAnalysisTool().analyse(df)
