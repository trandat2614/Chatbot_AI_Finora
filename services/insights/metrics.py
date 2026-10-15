"""Deterministic business metrics used by insight rules."""
from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from services.insights.data_provider import InsightDataProvider, OrderRecord, ShopSettings

PeriodName = Literal["7d", "30d", "90d"]


class MetricModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PeriodRange(MetricModel):
    name: PeriodName
    start: date
    end: date
    previous_start: date
    previous_end: date

    @classmethod
    def ending_on(cls, name: PeriodName, end: date | None = None) -> "PeriodRange":
        final_day = end or date.today()
        days = int(name[:-1])
        start = final_day - timedelta(days=days - 1)
        previous_end = start - timedelta(days=1)
        return cls(
            name=name,
            start=start,
            end=final_day,
            previous_start=previous_end - timedelta(days=days - 1),
            previous_end=previous_end,
        )


class PeriodTotals(MetricModel):
    revenue: float = 0
    orders: int = 0
    units: int = 0
    aov: float = 0
    cost_of_goods: float = 0
    expenses: float = 0
    profit: float = 0
    profit_margin_pct: float | None = None


class ChangeMetrics(MetricModel):
    revenue_pct: float | None = None
    orders_pct: float | None = None
    expenses_pct: float | None = None
    profit_pct: float | None = None


class ChannelMetric(MetricModel):
    channel: str
    revenue: float
    share_pct: float
    previous_revenue: float = 0
    change_pct: float | None = None


class ProductMetric(MetricModel):
    product: str
    revenue: float
    units: int
    share_pct: float


class TrendPoint(MetricModel):
    month: str
    revenue: float
    orders: int


class BreakEvenMetrics(MetricModel):
    target: float
    progress_pct: float
    remaining_amount: float
    additional_orders: int | None = None
    estimated_days: int | None = None


class InsightMetrics(MetricModel):
    period: PeriodRange
    current: PeriodTotals
    previous: PeriodTotals
    changes: ChangeMetrics
    channels: list[ChannelMetric] = Field(default_factory=list)
    top_products: list[ProductMetric] = Field(default_factory=list)
    bottom_products: list[ProductMetric] = Field(default_factory=list)
    monthly_trend: list[TrendPoint] = Field(default_factory=list)
    break_even: BreakEvenMetrics | None = None
    rule_thresholds: dict[str, float | int] = Field(default_factory=dict)


def _percentage_change(current: float, previous: float) -> float | None:
    if previous <= 0:
        return None
    return round((current - previous) / previous * 100, 4)


def _totals(orders: list[OrderRecord], expenses: float) -> PeriodTotals:
    revenue = sum(item.revenue for item in orders)
    cogs = sum(item.cost_of_goods for item in orders)
    order_count = len({item.order_id for item in orders})
    units = sum(item.quantity for item in orders)
    profit = revenue - cogs - expenses
    return PeriodTotals(
        revenue=round(revenue, 2),
        orders=order_count,
        units=units,
        aov=round(revenue / order_count, 2) if order_count else 0,
        cost_of_goods=round(cogs, 2),
        expenses=round(expenses, 2),
        profit=round(profit, 2),
        profit_margin_pct=round(profit / revenue * 100, 4) if revenue > 0 else None,
    )


def _break_even(
    totals: PeriodTotals,
    settings: ShopSettings,
    period: PeriodRange,
) -> BreakEvenMetrics | None:
    target = settings.break_even_target or settings.investment_capital
    if target is None:
        return None
    remaining = max(target - totals.profit, 0)
    contribution_per_order = totals.profit / totals.orders if totals.orders and totals.profit > 0 else 0
    additional = None
    if remaining > 0 and contribution_per_order > 0:
        additional = int(-(-remaining // contribution_per_order))
    elapsed_days = (period.end - period.start).days + 1
    daily_profit = totals.profit / elapsed_days if totals.profit > 0 else 0
    estimated_days = int(-(-remaining // daily_profit)) if remaining > 0 and daily_profit > 0 else None
    return BreakEvenMetrics(
        target=round(target, 2),
        progress_pct=round(min(max(totals.profit / target * 100, 0), 100), 4) if target > 0 else 100,
        remaining_amount=round(remaining, 2),
        additional_orders=additional,
        estimated_days=estimated_days,
    )


def collect_metrics(
    tenant_id: str,
    period: PeriodName | PeriodRange,
    provider: InsightDataProvider,
) -> InsightMetrics:
    """Collect comparable metrics exclusively through ``InsightDataProvider``."""
    selected = PeriodRange.ending_on(period) if isinstance(period, str) else period
    current_orders = provider.get_orders(tenant_id, selected.start, selected.end)
    previous_orders = provider.get_orders(
        tenant_id, selected.previous_start, selected.previous_end
    )
    current_expenses = sum(
        item.amount for item in provider.get_expenses(tenant_id, selected.start, selected.end)
    )
    previous_expenses = sum(
        item.amount
        for item in provider.get_expenses(
            tenant_id, selected.previous_start, selected.previous_end
        )
    )
    shop_settings = provider.get_shop_settings(tenant_id)
    current = _totals(current_orders, current_expenses)
    previous = _totals(previous_orders, previous_expenses)

    by_channel: dict[str, float] = defaultdict(float)
    previous_by_channel: dict[str, float] = defaultdict(float)
    by_product: dict[str, list[float | int]] = defaultdict(lambda: [0.0, 0])
    by_month: dict[str, dict[str, object]] = defaultdict(lambda: {"revenue": 0.0, "orders": set()})
    for item in current_orders:
        by_channel[item.channel] += item.revenue
        by_product[item.product][0] += item.revenue
        by_product[item.product][1] += item.quantity
        month = item.date.strftime("%Y-%m")
        by_month[month]["revenue"] = float(by_month[month]["revenue"]) + item.revenue
        order_ids = by_month[month]["orders"]
        assert isinstance(order_ids, set)
        order_ids.add(item.order_id)
    for item in previous_orders:
        previous_by_channel[item.channel] += item.revenue

    channels = [
        ChannelMetric(
            channel=name,
            revenue=round(revenue, 2),
            share_pct=round(revenue / current.revenue * 100, 4) if current.revenue else 0,
            previous_revenue=round(previous_by_channel.get(name, 0), 2),
            change_pct=_percentage_change(revenue, previous_by_channel.get(name, 0)),
        )
        for name, revenue in sorted(by_channel.items(), key=lambda pair: (-pair[1], pair[0]))
    ]
    products = [
        ProductMetric(
            product=name,
            revenue=round(float(values[0]), 2),
            units=int(values[1]),
            share_pct=round(float(values[0]) / current.revenue * 100, 4) if current.revenue else 0,
        )
        for name, values in by_product.items()
    ]
    products.sort(key=lambda item: (-item.revenue, item.product))
    bottom = sorted(products, key=lambda item: (item.revenue, item.product))[:5]
    trend = [
        TrendPoint(
            month=month,
            revenue=round(float(values["revenue"]), 2),
            orders=len(values["orders"]),  # type: ignore[arg-type]
        )
        for month, values in sorted(by_month.items())
    ]
    return InsightMetrics(
        period=selected,
        current=current,
        previous=previous,
        changes=ChangeMetrics(
            revenue_pct=_percentage_change(current.revenue, previous.revenue),
            orders_pct=_percentage_change(current.orders, previous.orders),
            expenses_pct=_percentage_change(current.expenses, previous.expenses),
            profit_pct=_percentage_change(current.profit, previous.profit),
        ),
        channels=channels,
        top_products=products[:5],
        bottom_products=bottom,
        monthly_trend=trend,
        break_even=_break_even(current, shop_settings, selected),
        rule_thresholds=shop_settings.rule_thresholds,
    )
