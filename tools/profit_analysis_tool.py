"""
Profit analysis tool for FINORA AI Business Advisor.

Only calculates metrics when the required data is present.
Never assumes missing cost columns are zero.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ProfitMetrics:
    """Profit metrics — only populated when input data is sufficient."""

    # Gross profit
    total_gross_profit: Optional[float] = None
    gross_profit_margin: Optional[float] = None  # %

    # Net profit
    total_net_profit: Optional[float] = None
    net_profit_margin: Optional[float] = None  # %

    # Cost breakdown
    total_cogs: Optional[float] = None
    total_platform_fees: Optional[float] = None
    total_marketing_cost: Optional[float] = None
    total_discounts: Optional[float] = None
    total_refunds: Optional[float] = None
    total_operating_expenses: Optional[float] = None

    # Total revenue (reference)
    total_revenue: float = 0.0

    # Meta
    missing_for_gross: list[str] = field(default_factory=list)
    missing_for_net: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    computable_metrics: list[str] = field(default_factory=list)
    not_computable: list[str] = field(default_factory=list)


class ProfitAnalysisTool:
    """Calculates gross and net profit from a revenue DataFrame."""

    # Columns needed for each profit level
    GROSS_REQUIRED = ["revenue", "cost_of_goods_sold"]
    NET_REQUIRED = [
        "revenue",
        "cost_of_goods_sold",
        "platform_fees",
        "marketing_cost",
        "discounts",
        "refunds",
        "operating_expenses",
    ]

    def analyse(self, df: pd.DataFrame) -> ProfitMetrics:
        """Calculate profit metrics from the DataFrame.

        Args:
            df: Revenue DataFrame (normalised column names expected).

        Returns:
            ProfitMetrics.
        """
        df = df.copy()
        df.columns = [c.strip().lower() for c in df.columns]

        metrics = ProfitMetrics()
        present_cols = set(df.columns)

        # Coerce numeric
        numeric_cols = [c for c in self.NET_REQUIRED if c in present_cols]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        if "revenue" in present_cols:
            metrics.total_revenue = float(df["revenue"].sum())

        # ---- Gross Profit -----------------------------------------------
        missing_gross = [c for c in self.GROSS_REQUIRED if c not in present_cols]
        metrics.missing_for_gross = missing_gross

        if not missing_gross:
            metrics.total_cogs = float(df["cost_of_goods_sold"].sum())
            metrics.total_gross_profit = metrics.total_revenue - metrics.total_cogs
            if metrics.total_revenue > 0:
                metrics.gross_profit_margin = (
                    metrics.total_gross_profit / metrics.total_revenue * 100
                )
            metrics.computable_metrics.extend(["gross_profit", "gross_profit_margin"])
        else:
            metrics.not_computable.append(
                f"Gross Profit (thiếu: {', '.join(missing_gross)})"
            )

        # ---- Net Profit -------------------------------------------------
        missing_net = [c for c in self.NET_REQUIRED if c not in present_cols]
        metrics.missing_for_net = missing_net

        if not missing_net:
            cogs = float(df["cost_of_goods_sold"].sum())
            platform_fees = float(df["platform_fees"].sum())
            marketing_cost = float(df["marketing_cost"].sum())
            discounts = float(df["discounts"].sum())
            refunds = float(df["refunds"].sum())
            operating_expenses = float(df["operating_expenses"].sum())

            metrics.total_platform_fees = platform_fees
            metrics.total_marketing_cost = marketing_cost
            metrics.total_discounts = discounts
            metrics.total_refunds = refunds
            metrics.total_operating_expenses = operating_expenses

            metrics.total_net_profit = (
                metrics.total_revenue
                - cogs
                - platform_fees
                - marketing_cost
                - discounts
                - refunds
                - operating_expenses
            )
            if metrics.total_revenue > 0:
                metrics.net_profit_margin = (
                    metrics.total_net_profit / metrics.total_revenue * 100
                )
            metrics.computable_metrics.extend(["net_profit", "net_profit_margin"])
        else:
            metrics.not_computable.append(
                f"Net Profit (thiếu: {', '.join(missing_net)})"
            )
            if missing_net and not missing_gross:
                metrics.warnings.append(
                    "Có thể tính Gross Profit nhưng chưa đủ dữ liệu cho Net Profit. "
                    f"Còn thiếu: {', '.join(missing_net)}."
                )

        return metrics


def analyse_profit(df: pd.DataFrame) -> ProfitMetrics:
    """Convenience function wrapping ProfitAnalysisTool."""
    return ProfitAnalysisTool().analyse(df)
