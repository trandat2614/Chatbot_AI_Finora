"""
Financial service — orchestrates financial analysis tools.

Provides a unified interface for computing all financial metrics
from user-uploaded data.
"""
from __future__ import annotations

import logging
from typing import Optional

import pandas as pd

from tools.revenue_analysis_tool import RevenueMetrics, analyse_revenue
from tools.profit_analysis_tool import ProfitMetrics, analyse_profit
from tools.marketing_metrics_tool import MarketingMetrics, compute_marketing_metrics
from tools.business_rule_engine import BusinessSignals, evaluate_business_rules
from core.exceptions import DataValidationError

logger = logging.getLogger(__name__)


class FinancialService:
    """Orchestrates all financial analysis tools for a given DataFrame."""

    def analyse(
        self, df: pd.DataFrame
    ) -> tuple[
        Optional[RevenueMetrics],
        Optional[ProfitMetrics],
        Optional[MarketingMetrics],
        BusinessSignals,
        list[str],
    ]:
        """Run the full financial analysis pipeline.

        Args:
            df: User-uploaded revenue DataFrame.

        Returns:
            Tuple of (revenue_metrics, profit_metrics, marketing_metrics,
                     business_signals, warnings).
        """
        warnings: list[str] = []
        revenue_metrics: Optional[RevenueMetrics] = None
        profit_metrics: Optional[ProfitMetrics] = None
        marketing_metrics: Optional[MarketingMetrics] = None

        # Revenue analysis
        try:
            revenue_metrics = analyse_revenue(df)
            warnings.extend(revenue_metrics.warnings)
        except DataValidationError as exc:
            logger.warning("Revenue analysis failed: %s", exc)
            warnings.append(f"Phân tích doanh thu không thành công: {exc}")
        except Exception as exc:
            logger.error("Unexpected error in revenue analysis: %s", exc)
            warnings.append("Lỗi không xác định trong phân tích doanh thu.")

        # Profit analysis
        try:
            profit_metrics = analyse_profit(df)
            warnings.extend(profit_metrics.warnings)
        except Exception as exc:
            logger.warning("Profit analysis failed: %s", exc)
            warnings.append(f"Phân tích lợi nhuận không thành công: {exc}")

        # Marketing metrics
        try:
            marketing_metrics = compute_marketing_metrics(df)
            warnings.extend(marketing_metrics.warnings)
        except Exception as exc:
            logger.warning("Marketing metrics failed: %s", exc)
            warnings.append(f"Tính toán marketing metrics không thành công: {exc}")

        # Business rules
        signals = evaluate_business_rules(
            revenue_metrics=revenue_metrics,
            profit_metrics=profit_metrics,
            marketing_metrics=marketing_metrics,
        )

        return revenue_metrics, profit_metrics, marketing_metrics, signals, warnings

    @staticmethod
    def format_metrics_for_llm(
        revenue_metrics: Optional[RevenueMetrics],
        profit_metrics: Optional[ProfitMetrics],
        marketing_metrics: Optional[MarketingMetrics],
    ) -> str:
        """Format computed metrics as a compact text block for the LLM.

        Only sends aggregated metrics, NOT the raw DataFrame.

        Args:
            revenue_metrics: Computed revenue metrics.
            profit_metrics: Computed profit metrics.
            marketing_metrics: Computed marketing metrics.

        Returns:
            Formatted string for injection into an LLM prompt.
        """
        lines = ["## Dữ liệu Kinh doanh (Kết quả tính toán chính xác từ Python)"]

        if revenue_metrics:
            lines.append("\n### Doanh thu")
            lines.append(f"- Tổng doanh thu: {revenue_metrics.total_revenue:,.0f} \u20ab")
            lines.append(f"- Doanh thu trung bình/kỳ: {revenue_metrics.average_revenue:,.0f} \u20ab")
            lines.append(f"- Doanh thu kỳ gần nhất: {revenue_metrics.latest_revenue:,.0f} \u20ab")
            if revenue_metrics.revenue_growth_rate is not None:
                lines.append(f"- Tăng trưởng doanh thu: {revenue_metrics.revenue_growth_rate:.1f}%")
            if revenue_metrics.revenue_trend:
                lines.append(f"- Xu hướng: {revenue_metrics.revenue_trend}")
            lines.append(f"- Kỳ tốt nhất: {revenue_metrics.best_period}")
            lines.append(f"- Kỳ xấu nhất: {revenue_metrics.worst_period}")
            lines.append(f"- Số kỳ phân tích: {revenue_metrics.periods}")

            if revenue_metrics.average_order_value:
                lines.append(f"- AOV: {revenue_metrics.average_order_value:,.0f} \u20ab")
            if revenue_metrics.customer_acquisition_cost:
                lines.append(f"- CAC: {revenue_metrics.customer_acquisition_cost:,.0f} \u20ab")
            if revenue_metrics.marketing_cost_ratio:
                lines.append(f"- Marketing Cost Ratio: {revenue_metrics.marketing_cost_ratio:.1f}%")

            if revenue_metrics.revenue_by_channel:
                lines.append("\n### Doanh thu theo kênh")
                for ch, rev in sorted(revenue_metrics.revenue_by_channel.items(), key=lambda x: -x[1]):
                    lines.append(f"- {ch}: {rev:,.0f} \u20ab")

            if revenue_metrics.revenue_by_product:
                lines.append("\n### Doanh thu theo sản phẩm (top 5)")
                sorted_products = sorted(revenue_metrics.revenue_by_product.items(), key=lambda x: -x[1])[:5]
                for pr, rev in sorted_products:
                    lines.append(f"- {pr}: {rev:,.0f} \u20ab")

        if profit_metrics:
            lines.append("\n### Lợi nhuận")
            if profit_metrics.total_gross_profit is not None:
                lines.append(f"- Gross Profit: {profit_metrics.total_gross_profit:,.0f} \u20ab")
                if profit_metrics.gross_profit_margin is not None:
                    lines.append(f"- Gross Margin: {profit_metrics.gross_profit_margin:.1f}%")
            if profit_metrics.total_net_profit is not None:
                lines.append(f"- Net Profit: {profit_metrics.total_net_profit:,.0f} \u20ab")
                if profit_metrics.net_profit_margin is not None:
                    lines.append(f"- Net Margin: {profit_metrics.net_profit_margin:.1f}%")
            if profit_metrics.not_computable:
                for nc in profit_metrics.not_computable:
                    lines.append(f"- Chưa tính được: {nc}")

        if marketing_metrics:
            mkt_dict = marketing_metrics.as_dict()
            if mkt_dict:
                lines.append("\n### Marketing Metrics")
                for metric_name, data in mkt_dict.items():
                    if data["value"] is not None:
                        val = data["value"]
                        unit = data["unit"]
                        lines.append(f"- {metric_name}: {val:,.2f} {unit}")

        return "\n".join(lines)
