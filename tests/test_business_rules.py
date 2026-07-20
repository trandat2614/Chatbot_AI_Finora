"""
Tests for the business rule engine.

All tests run offline - no OpenAI API calls.
"""
import pytest
import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.business_rule_engine import BusinessRuleEngine, evaluate_business_rules
from tools.revenue_analysis_tool import RevenueMetrics
from tools.profit_analysis_tool import ProfitMetrics
from tools.marketing_metrics_tool import MarketingMetrics, MarketingMetric


class TestRevenueSignals:
    """Test revenue-based signals."""

    def test_revenue_decline_signal(self):
        metrics = RevenueMetrics(revenue_growth_rate=-15.0)
        signals = evaluate_business_rules(revenue_metrics=metrics)
        codes = [s.code for s in signals.signals]
        assert "REVENUE_DECLINE" in codes

    def test_no_revenue_signal_when_growing(self):
        metrics = RevenueMetrics(revenue_growth_rate=20.0)
        signals = evaluate_business_rules(revenue_metrics=metrics)
        codes = [s.code for s in signals.signals]
        assert "REVENUE_DECLINE" not in codes

    def test_channel_concentration_signal(self):
        metrics = RevenueMetrics(
            revenue_by_channel={"Shopee": 800_000, "Lazada": 100_000, "Direct": 100_000},
            total_revenue=1_000_000,
        )
        signals = evaluate_business_rules(revenue_metrics=metrics)
        codes = [s.code for s in signals.signals]
        assert "CHANNEL_CONCENTRATION" in codes

    def test_no_channel_concentration_when_balanced(self):
        metrics = RevenueMetrics(
            revenue_by_channel={"Shopee": 400_000, "Lazada": 350_000, "Direct": 250_000},
            total_revenue=1_000_000,
        )
        signals = evaluate_business_rules(revenue_metrics=metrics)
        codes = [s.code for s in signals.signals]
        assert "CHANNEL_CONCENTRATION" not in codes


class TestMarketingSignals:
    """Test marketing-based signals."""

    def _make_metric(self, name, value, required=None):
        return MarketingMetric(
            name=name, value=value,
            formula="", required_fields=required or [],
            interpretation="",
        )

    def test_low_conversion_rate_signal(self):
        metrics = MarketingMetrics()
        metrics.conversion_rate = self._make_metric("Conversion Rate", 1.0)
        signals = evaluate_business_rules(marketing_metrics=metrics)
        codes = [s.code for s in signals.signals]
        assert "LOW_CONVERSION" in codes

    def test_no_low_conversion_when_above_2pct(self):
        metrics = MarketingMetrics()
        metrics.conversion_rate = self._make_metric("Conversion Rate", 3.5)
        signals = evaluate_business_rules(marketing_metrics=metrics)
        codes = [s.code for s in signals.signals]
        assert "LOW_CONVERSION" not in codes

    def test_high_refund_rate_signal(self):
        metrics = MarketingMetrics()
        metrics.refund_rate = self._make_metric("Refund Rate", 15.0)
        signals = evaluate_business_rules(marketing_metrics=metrics)
        codes = [s.code for s in signals.signals]
        assert "HIGH_REFUND_RATE" in codes
        # Should be critical
        critical = [s for s in signals.signals if s.code == "HIGH_REFUND_RATE"]
        assert critical[0].severity == "critical"

    def test_low_repeat_rate_signal(self):
        metrics = MarketingMetrics()
        metrics.repeat_purchase_rate = self._make_metric("Repeat Rate", 10.0)
        signals = evaluate_business_rules(marketing_metrics=metrics)
        codes = [s.code for s in signals.signals]
        assert "LOW_REPEAT_RATE" in codes


class TestProfitSignals:
    """Test profit-based signals."""

    def test_net_loss_signal(self):
        metrics = ProfitMetrics(
            total_net_profit=-5_000_000,
            net_profit_margin=-5.0,
        )
        signals = evaluate_business_rules(profit_metrics=metrics)
        codes = [s.code for s in signals.signals]
        assert "NET_LOSS" in codes
        # Should be critical
        critical = [s for s in signals.signals if s.code == "NET_LOSS"]
        assert critical[0].severity == "critical"

    def test_no_net_loss_when_profitable(self):
        metrics = ProfitMetrics(
            total_net_profit=10_000_000,
            net_profit_margin=10.0,
        )
        signals = evaluate_business_rules(profit_metrics=metrics)
        codes = [s.code for s in signals.signals]
        assert "NET_LOSS" not in codes

    def test_no_signal_without_data(self):
        signals = evaluate_business_rules()
        assert len(signals.signals) == 0
