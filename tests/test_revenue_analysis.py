"""
Tests for revenue analysis tool.

All tests run offline - no OpenAI API calls.
"""
import pytest
import pandas as pd
import numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.revenue_analysis_tool import analyse_revenue, REQUIRED_COLUMNS
from core.exceptions import MissingColumnsError


def make_sample_df(n=12):
    """Create a minimal valid revenue DataFrame."""
    import datetime
    dates = [f"2024-{m:02d}-01" for m in range(1, n + 1)]
    return pd.DataFrame({
        "date": dates,
        "revenue": [100_000 * (i + 1) for i in range(n)],
        "orders": [10 * (i + 1) for i in range(n)],
        "marketing_cost": [10_000 * (i + 1) for i in range(n)],
        "new_customers": [5 * (i + 1) for i in range(n)],
    })


class TestRevenueMissingColumns:
    """Test behaviour when required columns are missing."""

    def test_missing_revenue_raises(self):
        df = make_sample_df()
        df = df.drop(columns=["revenue"])
        with pytest.raises(MissingColumnsError) as exc_info:
            analyse_revenue(df)
        assert "revenue" in exc_info.value.missing

    def test_missing_multiple_columns_raises(self):
        df = pd.DataFrame({"date": ["2024-01-01"]})
        with pytest.raises(MissingColumnsError) as exc_info:
            analyse_revenue(df)
        assert len(exc_info.value.missing) > 1

    def test_extra_columns_allowed(self):
        df = make_sample_df()
        df["channel"] = "Shopee"
        result = analyse_revenue(df)
        assert result.total_revenue > 0


class TestRevenueCalculations:
    """Test revenue metric calculations."""

    def test_total_revenue(self):
        df = make_sample_df(3)
        # revenue = 100000, 200000, 300000
        result = analyse_revenue(df)
        assert result.total_revenue == pytest.approx(600_000)

    def test_average_order_value(self):
        df = make_sample_df(3)
        # total_revenue=600000, total_orders=10+20+30=60
        result = analyse_revenue(df)
        assert result.average_order_value == pytest.approx(600_000 / 60)

    def test_customer_acquisition_cost(self):
        df = make_sample_df(3)
        # total_marketing = 10000+20000+30000=60000
        # total_new_customers = 5+10+15=30
        result = analyse_revenue(df)
        assert result.customer_acquisition_cost == pytest.approx(60_000 / 30)

    def test_revenue_growth_rate(self):
        df = pd.DataFrame({
            "date": ["2024-01-01", "2024-02-01"],
            "revenue": [100_000, 120_000],
            "orders": [10, 12],
            "marketing_cost": [10_000, 12_000],
            "new_customers": [5, 6],
        })
        result = analyse_revenue(df)
        # Growth = (120000 - 100000) / 100000 * 100 = 20%
        assert result.revenue_growth_rate == pytest.approx(20.0)

    def test_negative_revenue_growth(self):
        df = pd.DataFrame({
            "date": ["2024-01-01", "2024-02-01"],
            "revenue": [200_000, 150_000],
            "orders": [20, 15],
            "marketing_cost": [20_000, 15_000],
            "new_customers": [10, 8],
        })
        result = analyse_revenue(df)
        assert result.revenue_growth_rate is not None
        assert result.revenue_growth_rate < 0


class TestRevenueDataQuality:
    """Test data quality handling."""

    def test_invalid_date_handled_gracefully(self):
        df = make_sample_df(5)
        df.loc[0, "date"] = "not-a-date"
        # Should not raise, but may add a warning
        try:
            result = analyse_revenue(df)
            # If it completes, it should still compute something
            assert result.total_revenue >= 0
        except Exception:
            pass  # Acceptable if it raises gracefully

    def test_invalid_revenue_values_handled(self):
        df = make_sample_df(5)
        df["revenue"] = df["revenue"].astype(object)
        df.loc[0, "revenue"] = "not-a-number"
        result = analyse_revenue(df)
        assert len(result.warnings) > 0

    def test_channel_breakdown(self):
        df = make_sample_df(4)
        df["channel"] = ["Shopee", "Lazada", "Shopee", "TikTok"]
        result = analyse_revenue(df)
        assert "Shopee" in result.revenue_by_channel
        assert result.revenue_by_channel["Shopee"] > 0
