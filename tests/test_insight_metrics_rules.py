"""Unit coverage for deterministic metrics and rule edge cases."""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from services.insights.data_provider import ExpenseRecord, OrderRecord, ShopSettings
from services.insights.metrics import PeriodRange, collect_metrics
from services.insights.rules import evaluate_rules


class MemoryProvider:
    def __init__(
        self,
        orders: list[OrderRecord],
        expenses: list[ExpenseRecord] | None = None,
        shop_settings: ShopSettings | None = None,
    ) -> None:
        self.orders = orders
        self.expenses = expenses or []
        self.settings = shop_settings or ShopSettings()

    def get_orders(self, tenant_id: str, start: date, end: date) -> list[OrderRecord]:
        return [item for item in self.orders if start <= item.date <= end]

    def get_expenses(self, tenant_id: str, start: date, end: date) -> list[ExpenseRecord]:
        return [item for item in self.expenses if start <= item.date <= end]

    def get_shop_settings(self, tenant_id: str) -> ShopSettings:
        return self.settings


def _order(
    order_id: str,
    day: date,
    *,
    revenue: float = 100,
    channel: str = "fixture-channel",
    product: str = "fixture-product",
) -> OrderRecord:
    return OrderRecord(
        order_id=order_id,
        date=day,
        channel=channel,
        product=product,
        quantity=1,
        revenue=revenue,
    )


def _period() -> PeriodRange:
    return PeriodRange.ending_on("7d", date(2026, 10, 15))


def test_low_data_rule_replaces_unsupported_conclusions() -> None:
    period = _period()
    metrics = collect_metrics(
        "tenant-a",
        period,
        MemoryProvider([_order("one", period.end)]),
    )
    candidates = evaluate_rules(metrics)
    assert [item.type for item in candidates] == ["low_data"]
    assert candidates[0].evidence["order_count"] == 1


def test_zero_orders_and_previous_zero_never_divide_by_zero() -> None:
    metrics = collect_metrics("tenant-a", _period(), MemoryProvider([]))
    assert metrics.current.aov == 0
    assert metrics.current.profit_margin_pct is None
    assert metrics.changes.revenue_pct is None
    assert evaluate_rules(metrics) == []


def test_previous_period_zero_returns_unknown_change() -> None:
    period = _period()
    provider = MemoryProvider(
        [_order(str(index), period.end, revenue=100) for index in range(6)]
    )
    metrics = collect_metrics("tenant-a", period, provider)
    assert metrics.previous.revenue == 0
    assert metrics.changes.revenue_pct is None
    assert not {item.type for item in evaluate_rules(metrics)} & {
        "revenue_growth",
        "order_growth",
    }


def test_single_channel_is_dynamic_and_missing_break_even_is_ignored() -> None:
    period = _period()
    orders = [
        _order(str(index), period.end, channel="Only fixture channel")
        for index in range(6)
    ]
    metrics = collect_metrics("tenant-a", period, MemoryProvider(orders))
    assert [item.channel for item in metrics.channels] == ["Only fixture channel"]
    assert metrics.break_even is None
    concentration = next(
        item for item in evaluate_rules(metrics) if item.type == "channel_concentration"
    )
    assert concentration.evidence["channel"] == "Only fixture channel"


def test_break_even_uses_shop_configuration_when_available() -> None:
    period = _period()
    orders = [_order(str(index), period.end, revenue=200) for index in range(10)]
    expenses = [ExpenseRecord(date=period.end, amount=500, category="fixture")]
    metrics = collect_metrics(
        "tenant-a",
        period,
        MemoryProvider(
            orders,
            expenses,
            ShopSettings(
                investment_capital=10_000,
                rule_thresholds={"break_even_slow_progress_pct": 25},
            ),
        ),
    )
    assert metrics.break_even is not None
    assert metrics.break_even.additional_orders is not None
    assert "slow_break_even" in {item.type for item in evaluate_rules(metrics)}


def test_channel_drop_and_cost_growth_are_compared_to_same_shop() -> None:
    period = _period()
    previous_day = period.previous_end
    current_orders = [
        _order(f"current-{index}", period.end, revenue=100, channel="fixture-a")
        for index in range(6)
    ]
    previous_orders = [
        _order(f"previous-{index}", previous_day, revenue=200, channel="fixture-a")
        for index in range(6)
    ]
    expenses = [
        ExpenseRecord(date=previous_day, amount=50, category="fee"),
        ExpenseRecord(date=period.end, amount=100, category="fee"),
    ]
    candidates = evaluate_rules(
        collect_metrics(
            "tenant-a", period, MemoryProvider(current_orders + previous_orders, expenses)
        )
    )
    types = {item.type for item in candidates}
    assert "weak_channel" in types
    assert "costs_outpace_revenue" in types


def test_positive_and_concentration_rules_have_numeric_evidence() -> None:
    period = _period()
    current = [
        _order(
            f"current-{index}",
            period.end,
            revenue=1 if index == 5 else 200,
            channel="dynamic-channel",
            product="small-product" if index == 5 else "hero-product",
        )
        for index in range(6)
    ]
    previous = [
        _order(f"previous-{index}", period.previous_end, revenue=100)
        for index in range(5)
    ]
    metrics = collect_metrics(
        "tenant-a",
        period,
        MemoryProvider(
            current + previous,
            shop_settings=ShopSettings(investment_capital=10_000),
        ),
    )
    candidates = evaluate_rules(metrics)
    by_type = {item.type: item for item in candidates}
    assert {
        "revenue_growth",
        "order_growth",
        "channel_concentration",
        "high_profit_margin",
        "product_concentration",
        "low_selling_product",
        "slow_break_even",
    }.issubset(by_type)
    assert all(item.evidence for item in by_type.values())


def test_decline_and_low_margin_rules_are_detected() -> None:
    period = _period()
    current = [
        _order(f"current-{index}", period.end, revenue=100, channel="declining")
        for index in range(5)
    ]
    previous = [
        _order(f"previous-{index}", period.previous_end, revenue=200, channel="declining")
        for index in range(10)
    ]
    expenses = [
        ExpenseRecord(date=period.previous_end, amount=50, category="fee"),
        ExpenseRecord(date=period.end, amount=490, category="fee"),
    ]
    types = {
        item.type
        for item in evaluate_rules(
            collect_metrics(
                "tenant-a", period, MemoryProvider(current + previous, expenses)
            )
        )
    }
    assert {
        "revenue_decline",
        "order_decline",
        "weak_channel",
        "low_profit_margin",
        "costs_outpace_revenue",
    }.issubset(types)


def test_positive_and_concentration_rules_have_numeric_evidence() -> None:
    period = _period()
    current = [
        _order(
            f"current-{index}",
            period.end,
            revenue=1 if index == 5 else 200,
            channel="dynamic-channel",
            product="small-product" if index == 5 else "hero-product",
        )
        for index in range(6)
    ]
    previous = [
        _order(f"previous-{index}", period.previous_end, revenue=100)
        for index in range(5)
    ]
    metrics = collect_metrics(
        "tenant-a",
        period,
        MemoryProvider(
            current + previous,
            shop_settings=ShopSettings(investment_capital=10_000),
        ),
    )
    candidates = evaluate_rules(metrics)
    by_type = {item.type: item for item in candidates}
    assert {
        "revenue_growth",
        "order_growth",
        "channel_concentration",
        "high_profit_margin",
        "product_concentration",
        "low_selling_product",
        "slow_break_even",
    }.issubset(by_type)
    assert all(item.evidence for item in by_type.values())


def test_decline_and_low_margin_rules_are_detected() -> None:
    period = _period()
    current = [
        _order(f"current-{index}", period.end, revenue=100, channel="declining")
        for index in range(5)
    ]
    previous = [
        _order(f"previous-{index}", period.previous_end, revenue=200, channel="declining")
        for index in range(10)
    ]
    expenses = [
        ExpenseRecord(date=period.previous_end, amount=50, category="fee"),
        ExpenseRecord(date=period.end, amount=490, category="fee"),
    ]
    types = {
        item.type
        for item in evaluate_rules(
            collect_metrics(
                "tenant-a", period, MemoryProvider(current + previous, expenses)
            )
        )
    }
    assert {
        "revenue_decline",
        "order_decline",
        "weak_channel",
        "low_profit_margin",
        "costs_outpace_revenue",
    }.issubset(types)
