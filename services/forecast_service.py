"""
Forecast service — orchestrates revenue forecasting.

Wraps the forecasting module with error handling and
result formatting for Streamlit UI consumption.
"""
from __future__ import annotations

import logging
from typing import Optional

import pandas as pd

from forecasting.revenue_forecast import ForecastResult, forecast_revenue
from forecasting.evaluation import EvaluationResult, evaluate_forecast_model
from core.exceptions import InsufficientDataError, ForecastError

logger = logging.getLogger(__name__)


class ForecastService:
    """Orchestrates revenue forecasting and model evaluation."""

    def run_forecast(
        self,
        df: pd.DataFrame,
        periods: int = 3,
    ) -> tuple[Optional[ForecastResult], Optional[EvaluationResult], list[str]]:
        """Run forecast and evaluation.

        Args:
            df: Historical revenue DataFrame.
            periods: Number of future periods to forecast.

        Returns:
            Tuple of (forecast_result, evaluation_result, warnings).
        """
        warnings: list[str] = []
        forecast_result: Optional[ForecastResult] = None
        eval_result: Optional[EvaluationResult] = None

        # Forecast
        try:
            forecast_result = forecast_revenue(df, periods)
            warnings.extend(forecast_result.warnings)
        except InsufficientDataError as exc:
            warnings.append(str(exc))
            logger.warning("Insufficient data for forecast: %s", exc)
        except ForecastError as exc:
            warnings.append(f"Lỗi dự báo: {exc}")
            logger.error("Forecast error: %s", exc)
        except Exception as exc:
            warnings.append(f"Lỗi không xác định trong quá trình dự báo: {exc}")
            logger.exception("Unexpected forecast error.")

        # Evaluation
        try:
            eval_result = evaluate_forecast_model(df)
            if eval_result.warning:
                warnings.append(eval_result.warning)
        except Exception as exc:
            logger.warning("Model evaluation failed: %s", exc)
            warnings.append(f"Không thể đánh giá mô hình: {exc}")

        return forecast_result, eval_result, warnings

    @staticmethod
    def format_forecast_for_llm(
        forecast_result: Optional[ForecastResult],
        eval_result: Optional[EvaluationResult],
    ) -> tuple[str, str]:
        """Format forecast results as text for LLM context.

        Args:
            forecast_result: Forecast output.
            eval_result: Evaluation output.

        Returns:
            Tuple of (forecast_text, performance_text).
        """
        if forecast_result is None:
            return "Chưa có kết quả dự báo.", ""

        # Forecast text
        lines = [
            f"Mô hình: {forecast_result.model_name}",
            f"Xu hướng/kỳ: {forecast_result.trend_per_period:+,.0f} \u20ab",
            "\nDự báo:",
        ]
        for date, rev in zip(forecast_result.forecast_dates, forecast_result.predicted_revenue):
            lines.append(f"- {date}: {rev:,.0f} \u20ab")
        lines.append(f"\n{forecast_result.confidence_warning}")
        lines.append(f"Giới hạn mô hình: {forecast_result.model_limitations}")
        forecast_text = "\n".join(lines)

        # Performance text
        perf_lines = []
        if eval_result and eval_result.can_evaluate:
            perf_lines.append(f"MAE: {eval_result.mae:,.0f} \u20ab")
            perf_lines.append(f"RMSE: {eval_result.rmse:,.0f} \u20ab")
            if eval_result.mape is not None:
                perf_lines.append(f"MAPE: {eval_result.mape:.1f}%")
            perf_lines.append(f"Số fold: {eval_result.n_folds}")
        elif eval_result:
            perf_lines.append(eval_result.warning or "Chưa đủ dữ liệu để đánh giá.")

        performance_text = "\n".join(perf_lines)
        return forecast_text, performance_text
