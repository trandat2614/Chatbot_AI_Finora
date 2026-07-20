"""
Model evaluation for revenue forecasting.

Uses TimeSeriesSplit (walk-forward) to avoid data leakage.
Handles edge cases gracefully (actual=0, insufficient data).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import TimeSeriesSplit

from forecasting.data_preprocessing import prepare_time_features, get_feature_columns

logger = logging.getLogger(__name__)

MIN_PERIODS_FOR_VALIDATION = 8


@dataclass
class EvaluationResult:
    """Evaluation metrics for the forecasting model."""

    mae: Optional[float] = None
    rmse: Optional[float] = None
    mape: Optional[float] = None  # None if any actual=0
    n_folds: int = 0
    training_periods: int = 0
    can_evaluate: bool = False
    warning: str = ""
    details: list[str] = field(default_factory=list)


def evaluate_forecast_model(df: pd.DataFrame) -> EvaluationResult:
    """Evaluate the revenue forecasting model via TimeSeriesSplit.

    Args:
        df: Historical revenue DataFrame.

    Returns:
        EvaluationResult with cross-validation metrics.
    """
    result = EvaluationResult()

    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]

    if "revenue" not in df.columns:
        result.warning = "Không có cột 'revenue' để đánh giá."
        return result

    n_rows = len(df)
    result.training_periods = n_rows

    if n_rows < MIN_PERIODS_FOR_VALIDATION:
        result.warning = (
            f"Cần ít nhất {MIN_PERIODS_FOR_VALIDATION} kỳ dữ liệu để thực hiện "
            f"cross-validation. Hiện có {n_rows} kỳ."
        )
        return result

    try:
        processed = prepare_time_features(df)
    except Exception as exc:
        result.warning = f"Không thể chuẩn bị dữ liệu cho đánh giá: {exc}"
        return result

    feature_cols = get_feature_columns(processed)
    X = processed[feature_cols].values
    y = processed["revenue"].values

    n_splits = min(3, len(processed) - 2)
    tscv = TimeSeriesSplit(n_splits=n_splits)

    mae_scores, rmse_scores, mape_scores = [], [], []
    has_zero_actual = False

    for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        if len(X_train) < 2:
            continue

        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = np.clip(model.predict(X_test), 0, None)

        mae_scores.append(np.mean(np.abs(y_test - y_pred)))
        rmse_scores.append(np.sqrt(np.mean((y_test - y_pred) ** 2)))

        # MAPE: skip if any actual = 0
        if np.any(y_test == 0):
            has_zero_actual = True
        else:
            mape_scores.append(np.mean(np.abs((y_test - y_pred) / y_test)) * 100)

    result.n_folds = len(mae_scores)
    result.can_evaluate = result.n_folds > 0

    if result.can_evaluate:
        result.mae = float(np.mean(mae_scores))
        result.rmse = float(np.mean(rmse_scores))
        if mape_scores and not has_zero_actual:
            result.mape = float(np.mean(mape_scores))
        elif has_zero_actual:
            result.details.append(
                "MAPE không được tính vì có kỳ doanh thu = 0 (chia cho 0)."
            )

    return result
