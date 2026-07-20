"""
Revenue forecasting using Linear Regression (MVP model).

Design decisions:
- No random train/test split: uses time-ordered data only.
- Forecasted values clipped to >= 0.
- Minimum 4 periods of historical data required.
- Returns confidence warnings along with predictions.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from core.exceptions import InsufficientDataError, ForecastError
from forecasting.data_preprocessing import prepare_time_features, get_feature_columns
from utils.validators import validate_periods

logger = logging.getLogger(__name__)

MIN_TRAINING_ROWS = 4  # After lag feature creation (drops first 3 rows)


@dataclass
class ForecastResult:
    """Result of revenue forecasting."""

    forecast_dates: list[str] = field(default_factory=list)
    predicted_revenue: list[float] = field(default_factory=list)
    trend_per_period: float = 0.0
    model_name: str = "Linear Regression"
    model_limitations: str = ""
    confidence_warning: str = ""
    historical_dates: list[str] = field(default_factory=list)
    historical_revenue: list[float] = field(default_factory=list)
    periods_forecasted: int = 0
    training_rows: int = 0
    warnings: list[str] = field(default_factory=list)


class RevenueForecast:
    """Linear regression-based revenue forecaster."""

    def __init__(self) -> None:
        self._model: Optional[LinearRegression] = None
        self._feature_cols: list[str] = []
        self._last_known_revenue: float = 0.0
        self._last_known_lag1: float = 0.0
        self._last_known_lag2: float = 0.0
        self._last_time_idx: int = 0

    def fit_and_forecast(
        self,
        df: pd.DataFrame,
        periods: int = 3,
    ) -> ForecastResult:
        """Fit a linear regression model and generate forecasts.

        Args:
            df: Historical revenue DataFrame.
            periods: Number of future periods to forecast (1–12).

        Returns:
            ForecastResult with predictions and metadata.

        Raises:
            InsufficientDataError: When not enough training data.
            ForecastError: On model fitting failure.
        """
        validate_periods(periods)

        result = ForecastResult()
        result.periods_forecasted = periods

        # ---- Preprocess -------------------------------------------------------
        try:
            processed = prepare_time_features(df)
        except InsufficientDataError:
            raise
        except Exception as exc:
            raise ForecastError(f"Lỗi tiền xử lý dữ liệu: {exc}") from exc

        if len(processed) < MIN_TRAINING_ROWS:
            raise InsufficientDataError(
                required=MIN_TRAINING_ROWS + 3,  # original rows needed
                actual=len(processed),
                operation="training the forecasting model",
            )

        feature_cols = get_feature_columns(processed)
        result.training_rows = len(processed)
        result.model_name = "Linear Regression"

        # ---- Train -----------------------------------------------------------
        X = processed[feature_cols].values
        y = processed["revenue"].values

        try:
            model = LinearRegression()
            model.fit(X, y)
            self._model = model
            self._feature_cols = feature_cols
        except Exception as exc:
            raise ForecastError(f"Không thể huấn luyện mô hình: {exc}") from exc

        # Store last known values for iterative forecasting
        last_row = processed.iloc[-1]
        self._last_known_revenue = float(last_row["revenue"])
        self._last_known_lag1 = float(last_row["revenue"])
        self._last_known_lag2 = float(processed.iloc[-2]["revenue"]) if len(processed) > 1 else 0.0
        self._last_time_idx = int(last_row["time_index"])

        # Trend per period (model coefficient for time_index)
        if "time_index" in feature_cols:
            ti_idx = feature_cols.index("time_index")
            result.trend_per_period = float(model.coef_[ti_idx])

        # ---- Historical reference -------------------------------------------
        orig_df = df.copy()
        orig_df.columns = [c.strip().lower() for c in orig_df.columns]
        orig_df["date"] = pd.to_datetime(orig_df["date"])
        orig_df = orig_df.sort_values("date")
        orig_df["revenue"] = pd.to_numeric(orig_df["revenue"], errors="coerce").fillna(0)
        result.historical_dates = [str(d)[:10] for d in orig_df["date"]]
        result.historical_revenue = orig_df["revenue"].tolist()

        # ---- Forecast -------------------------------------------------------
        last_date = orig_df["date"].iloc[-1]
        forecasted_dates = []
        forecasted_values = []

        lag1 = self._last_known_revenue
        lag2 = self._last_known_lag1
        lag3 = self._last_known_lag2
        rolling_vals = list(orig_df["revenue"].iloc[-3:].values)

        for i in range(1, periods + 1):
            next_time = self._last_time_idx + i
            next_date = last_date + pd.DateOffset(months=i)
            rolling_mean = float(np.mean(rolling_vals[-3:])) if len(rolling_vals) >= 1 else lag1

            row = {}
            for col in feature_cols:
                if col == "time_index":
                    row[col] = next_time
                elif col == "month":
                    row[col] = next_date.month
                elif col == "quarter":
                    row[col] = next_date.quarter
                elif col == "lag_1":
                    row[col] = lag1
                elif col == "lag_2":
                    row[col] = lag2
                elif col == "lag_3":
                    row[col] = lag3
                elif col == "rolling_mean_3":
                    row[col] = rolling_mean

            X_pred = np.array([[row[c] for c in feature_cols]])
            pred = float(model.predict(X_pred)[0])
            pred = max(0.0, pred)  # No negative revenue

            forecasted_dates.append(str(next_date)[:10])
            forecasted_values.append(pred)

            # Update lags iteratively
            lag3 = lag2
            lag2 = lag1
            lag1 = pred
            rolling_vals.append(pred)

        result.forecast_dates = forecasted_dates
        result.predicted_revenue = forecasted_values

        # ---- Metadata -------------------------------------------------------
        result.model_limitations = (
            "Mô hình Linear Regression (MVP): giả sử xu hướng tuyến tính, "
            "không nắm bắt được tính thời vụ phức tạp. "
            f"Huấn luyện trên {result.training_rows} kỳ dữ liệu."
        )
        result.confidence_warning = (
            "⚠️ Dự báo chỉ mang tính ước tính. Kết quả thực tế có thể sai lệch "
            "do biến động thị trường, chiến dịch marketing, hoặc yếu tố bất ngờ. "
            "Không sử dụng để ra quyết định tài chính quan trọng."
        )

        if result.training_rows < 8:
            result.warnings.append(
                f"Chỉ có {result.training_rows} kỳ dữ liệu huấn luyện — "
                "dự báo có độ chính xác thấp."
            )

        return result


def forecast_revenue(df: pd.DataFrame, periods: int = 3) -> ForecastResult:
    """Convenience function wrapping RevenueForecast."""
    return RevenueForecast().fit_and_forecast(df, periods)
