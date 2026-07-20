"""
Time-series data preprocessing for revenue forecasting.

Creates features from historical revenue data while avoiding data leakage.
"""
from __future__ import annotations

import logging
from typing import Optional

import numpy as np
import pandas as pd

from core.exceptions import InsufficientDataError

logger = logging.getLogger(__name__)

MIN_PERIODS_FOR_LAG = 4  # Need at least 4 to create lag-3


def prepare_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare time-series features for the forecasting model.

    Creates a clean feature matrix from a revenue DataFrame.
    Only includes lag/rolling features when there is enough data.
    Does NOT create features that would require future data.

    Args:
        df: DataFrame with at least 'date' and 'revenue' columns.
            Assumes column names are already normalised to lower-case.

    Returns:
        Feature DataFrame suitable for LinearRegression training.

    Raises:
        InsufficientDataError: When fewer than 4 periods are provided.
    """
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]

    if "date" not in df.columns or "revenue" not in df.columns:
        raise ValueError("DataFrame must contain 'date' and 'revenue' columns.")

    # Sort chronologically
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0)

    n = len(df)
    if n < MIN_PERIODS_FOR_LAG:
        raise InsufficientDataError(
            required=MIN_PERIODS_FOR_LAG,
            actual=n,
            operation="revenue forecasting",
        )

    # ---- Time index features -----------------------------------------------
    df["time_index"] = range(n)

    if df["date"].dtype == "datetime64[ns]" or hasattr(df["date"].dt, "month"):
        df["month"] = df["date"].dt.month
        df["quarter"] = df["date"].dt.quarter

    # ---- Lag features (only when enough data) ------------------------------
    df["lag_1"] = df["revenue"].shift(1)
    df["lag_2"] = df["revenue"].shift(2)
    df["lag_3"] = df["revenue"].shift(3)

    # ---- Rolling mean -------------------------------------------------------
    df["rolling_mean_3"] = df["revenue"].shift(1).rolling(window=3).mean()

    # Drop rows with NaN from lags (first 3 rows)
    df = df.dropna(subset=["lag_1", "lag_2", "lag_3"]).reset_index(drop=True)

    return df


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    """Return the list of feature column names available in the DataFrame."""
    candidates = [
        "time_index", "month", "quarter",
        "lag_1", "lag_2", "lag_3", "rolling_mean_3",
    ]
    return [c for c in candidates if c in df.columns]
