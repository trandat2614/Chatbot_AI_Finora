"""Scale-independent, explainable rules for business insight candidates."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from config.settings import settings
from services.insights.metrics import InsightMetrics

Severity = Literal["info", "warning", "critical", "positive"]


class InsightCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    severity: Severity
    evidence: dict[str, float | int | str | None] = Field(default_factory=dict)


def _thresholds(metrics: InsightMetrics) -> dict[str, float | int]:
    # A custom provider can return only overridden keys; fill missing values
    # from the central defaults without embedding thresholds in rule code.
    return {**settings.insight_thresholds(""), **metrics.rule_thresholds}


def evaluate_rules(metrics: InsightMetrics) -> list[InsightCandidate]:
    """Return deterministic candidates, each grounded in numeric evidence."""
    values = _thresholds(metrics)
    current = metrics.current
    if current.orders == 0:
        return []
    if current.orders < int(values["min_orders"]):
        return [
            InsightCandidate(
                type="low_data",
                severity="info",
                evidence={
                    "order_count": current.orders,
                    "minimum_order_count": int(values["min_orders"]),
                    "period_start": metrics.period.start.isoformat(),
                    "period_end": metrics.period.end.isoformat(),
                },
            )
        ]

    candidates: list[InsightCandidate] = []
    significant = float(values["significant_change_pct"])
    revenue_change = metrics.changes.revenue_pct
    order_change = metrics.changes.orders_pct
    if revenue_change is not None and abs(revenue_change) >= significant:
        candidates.append(
            InsightCandidate(
                type="revenue_growth" if revenue_change > 0 else "revenue_decline",
                severity="positive" if revenue_change > 0 else ("critical" if revenue_change <= -2 * significant else "warning"),
                evidence={
                    "current_revenue": current.revenue,
                    "previous_revenue": metrics.previous.revenue,
                    "change_pct": revenue_change,
                },
            )
        )
    if order_change is not None and abs(order_change) >= significant:
        candidates.append(
            InsightCandidate(
                type="order_growth" if order_change > 0 else "order_decline",
                severity="positive" if order_change > 0 else ("critical" if order_change <= -2 * significant else "warning"),
                evidence={
                    "current_orders": current.orders,
                    "previous_orders": metrics.previous.orders,
                    "change_pct": order_change,
                },
            )
        )

    if metrics.channels:
        leading = metrics.channels[0]
        if leading.share_pct >= float(values["channel_concentration_pct"]):
            candidates.append(
                InsightCandidate(
                    type="channel_concentration",
                    severity="warning",
                    evidence={
                        "channel": leading.channel,
                        "revenue": leading.revenue,
                        "share_pct": leading.share_pct,
                        "channel_count": len(metrics.channels),
                    },
                )
            )
        weak = next(
            (
                channel
                for channel in reversed(metrics.channels)
                if channel.change_pct is not None
                and channel.change_pct <= -float(values["weak_channel_drop_pct"])
            ),
            None,
        )
        if weak is not None:
            candidates.append(
                InsightCandidate(
                    type="weak_channel",
                    severity="warning",
                    evidence={
                        "channel": weak.channel,
                        "current_revenue": weak.revenue,
                        "previous_revenue": weak.previous_revenue,
                        "change_pct": weak.change_pct,
                    },
                )
            )

    margin = current.profit_margin_pct
    if margin is not None and margin <= float(values["low_margin_pct"]):
        candidates.append(
            InsightCandidate(
                type="low_profit_margin",
                severity="critical" if margin < 0 else "warning",
                evidence={
                    "profit": current.profit,
                    "revenue": current.revenue,
                    "profit_margin_pct": margin,
                },
            )
        )
    elif margin is not None and margin >= float(values["high_margin_pct"]):
        candidates.append(
            InsightCandidate(
                type="high_profit_margin",
                severity="positive",
                evidence={
                    "profit": current.profit,
                    "revenue": current.revenue,
                    "profit_margin_pct": margin,
                },
            )
        )

    expense_growth = metrics.changes.expenses_pct
    if (
        expense_growth is not None
        and revenue_change is not None
        and expense_growth - revenue_change >= float(values["cost_growth_gap_pct"])
    ):
        candidates.append(
            InsightCandidate(
                type="costs_outpace_revenue",
                severity="warning",
                evidence={
                    "expense_change_pct": expense_growth,
                    "revenue_change_pct": revenue_change,
                    "growth_gap_pct": round(expense_growth - revenue_change, 4),
                    "current_expenses": current.expenses,
                },
            )
        )

    if metrics.top_products:
        leader = metrics.top_products[0]
        if leader.share_pct >= float(values["product_concentration_pct"]):
            candidates.append(
                InsightCandidate(
                    type="product_concentration",
                    severity="warning",
                    evidence={
                        "product": leader.product,
                        "revenue": leader.revenue,
                        "units": leader.units,
                        "share_pct": leader.share_pct,
                    },
                )
            )
    low_product = next(
        (
            product
            for product in metrics.bottom_products
            if product.share_pct <= float(values["low_product_share_pct"])
        ),
        None,
    )
    if low_product is not None and len(metrics.top_products) > 1:
        candidates.append(
            InsightCandidate(
                type="low_selling_product",
                severity="info",
                evidence={
                    "product": low_product.product,
                    "revenue": low_product.revenue,
                    "units": low_product.units,
                    "share_pct": low_product.share_pct,
                },
            )
        )

    if (
        metrics.break_even is not None
        and metrics.break_even.remaining_amount > 0
        and metrics.break_even.progress_pct < float(values["break_even_slow_progress_pct"])
    ):
        candidates.append(
            InsightCandidate(
                type="slow_break_even",
                severity="warning",
                evidence={
                    "target": metrics.break_even.target,
                    "progress_pct": metrics.break_even.progress_pct,
                    "remaining_amount": metrics.break_even.remaining_amount,
                    "additional_orders": metrics.break_even.additional_orders,
                    "estimated_days": metrics.break_even.estimated_days,
                },
            )
        )
    return candidates
