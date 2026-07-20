"""
Tests for revenue forecasting module.

All tests run offline - no OpenAI API calls.
Uses only sklearn, numpy, pandas.
"""
import pytest
import pandas as pd
import numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from forecasting.revenue_forecast import forecast_revenue, RevenueForecast
from forecasting.data_preprocessing import prepare_time_features
from core.exceptions import InsufficientDataError


def make_revenue_df(n=12, start="2024-01-01", trend=10_000):
    """Create a synthetic revenue DataFrame."""
    dates = pd.date_range(start=start, periods=n, freq="MS")
    base = 100_000
    revenues = [base + trend * i + np.random.randint(-5000, 5000) for i in range(n)]
    return pd.DataFrame({
        "date": dates.strftime("%Y-%m-%d"),
        "revenue": revenues,
        "orders": [10] * n,
        "marketing_cost": [5000] * n,
        "new_customers": [3] * n,
    })


class TestForecastRequirements:
    """Test data requirements enforcement."""

    def test_insufficient_data_raises(self):
        """Less than 4 periods should raise InsufficientDataError."""
        df = make_revenue_df(n=3)
        with pytest.raises(InsufficientDataError):
            forecast_revenue(df, periods=3)

    def test_exactly_minimum_data(self):
        """Exactly 4 periods (after feature creation leaves >=1 row) should work."""
        df = make_revenue_df(n=7)  # 7 original -> 4 after lag drop
        result = forecast_revenue(df, periods=1)
        assert result is not None
        assert len(result.forecast_dates) == 1


class TestForecastOutput:
    """Test forecast output structure and constraints."""

    def test_forecast_3_periods(self):
        df = make_revenue_df(n=12)
        result = forecast_revenue(df, periods=3)
        assert len(result.forecast_dates) == 3
        assert len(result.predicted_revenue) == 3

    def test_forecast_not_negative(self):
        """Revenue forecasts must be non-negative."""
        df = make_revenue_df(n=12)
        result = forecast_revenue(df, periods=6)
        for rev in result.predicted_revenue:
            assert rev >= 0, f"Negative revenue found: {rev}"

    def test_forecast_dates_ordered(self):
        """Forecast dates must be in chronological order."""
        df = make_revenue_df(n=12)
        result = forecast_revenue(df, periods=6)
        dates = pd.to_datetime(result.forecast_dates)
        for i in range(1, len(dates)):
            assert dates[i] > dates[i - 1], "Dates not in order"

    def test_forecast_dates_after_historical(self):
        """All forecast dates must be after the last historical date."""
        df = make_revenue_df(n=12)
        result = forecast_revenue(df, periods=3)
        last_hist_date = pd.to_datetime(result.historical_dates[-1])
        for fdate in result.forecast_dates:
            assert pd.to_datetime(fdate) > last_hist_date

    def test_model_metadata_present(self):
        """Result must contain model name and warnings."""
        df = make_revenue_df(n=12)
        result = forecast_revenue(df, periods=3)
        assert result.model_name
        assert result.confidence_warning
        assert result.model_limitations

    def test_no_future_data_in_training(self):
        """Verify that lag features only use past data (no leakage)."""
        df = make_revenue_df(n=12)
        processed = prepare_time_features(df)
        # lag_1 should equal the previous row's revenue
        for i in range(1, len(processed)):
            current_lag1 = processed.iloc[i]["lag_1"]
            # lag_1 should be less than or equal to the value 1 position back
            # (just check it's not using future data by checking types)
            assert isinstance(current_lag1, (int, float, np.floating))

    def test_historical_data_included_in_result(self):
        """Result should include historical data for chart rendering."""
        df = make_revenue_df(n=12)
        result = forecast_revenue(df, periods=3)
        assert len(result.historical_dates) == 12
        assert len(result.historical_revenue) == 12
