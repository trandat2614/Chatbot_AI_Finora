"""Deterministic anomaly and business-health alerts."""
from __future__ import annotations

from src.schemas.commerce import AnalysisStatus, BusinessAlert, MetricResult


class BusinessHealthService:
    def analyze(self, metrics: MetricResult, *, baseline: MetricResult | None = None) -> dict:
        if metrics.status != AnalysisStatus.OK:
            return {"status": AnalysisStatus.INSUFFICIENT_DATA.value, "alerts": [], "missing_fields": metrics.missing_fields}
        alerts: list[BusinessAlert] = []

        def add(code: str, severity: str, metric: str, current: float, threshold: float | None, text: str) -> None:
            alerts.append(BusinessAlert(
                code=code, severity=severity, metric=metric, current_value=current,
                baseline=threshold, difference=current - threshold if threshold is not None else None,
                entity="shop", explanation=text,
            ))

        if (metrics.cancellation_rate or 0) >= 10:
            add("HIGH_CANCELLATION", "critical", "cancellation_rate", metrics.cancellation_rate or 0, 10, "Tỷ lệ hủy đơn vượt ngưỡng 10%.")
        elif (metrics.cancellation_rate or 0) >= 5:
            add("HIGH_CANCELLATION", "warning", "cancellation_rate", metrics.cancellation_rate or 0, 5, "Tỷ lệ hủy đơn vượt ngưỡng cảnh báo 5%.")
        if (metrics.refund_rate or 0) >= 10:
            add("HIGH_REFUND", "critical", "refund_rate", metrics.refund_rate or 0, 10, "Tỷ lệ hoàn tiền cao.")
        elif (metrics.refund_rate or 0) >= 5:
            add("HIGH_REFUND", "warning", "refund_rate", metrics.refund_rate or 0, 5, "Tỷ lệ hoàn tiền cần được theo dõi.")
        discount_ratio = (metrics.seller_discount or 0) / metrics.revenue * 100 if (metrics.revenue or 0) > 0 else 0
        if discount_ratio >= 20:
            add("HIGH_DISCOUNT_DEPENDENCY", "warning", "seller_discount_rate", discount_ratio, 20, "Doanh thu phụ thuộc nhiều vào trợ giá của người bán.")
        if metrics.sales_growth is not None and metrics.sales_growth <= -10:
            add("REVENUE_DROP", "critical" if metrics.sales_growth <= -25 else "warning", "sales_growth", metrics.sales_growth, 0, "Tốc độ doanh thu kỳ hiện tại thấp hơn kỳ trước.")
        if metrics.sales_growth is not None and metrics.sales_growth >= 15:
            add("PRODUCT_GROWTH", "info", "sales_growth", metrics.sales_growth, 0, "Dữ liệu cho thấy tín hiệu tăng trưởng tích cực.")
        fee_rate = (metrics.marketplace_fee or 0) / metrics.revenue * 100 if (metrics.revenue or 0) > 0 else 0
        baseline_fee = None
        if baseline and baseline.revenue and baseline.marketplace_fee is not None:
            baseline_fee = baseline.marketplace_fee / baseline.revenue * 100
        if baseline_fee is not None and fee_rate - baseline_fee >= 2:
            add("FEE_INCREASE", "warning", "marketplace_fee_rate", fee_rate, baseline_fee, "Tỷ lệ phí sàn tăng ít nhất 2 điểm phần trăm.")
        return {
            "status": AnalysisStatus.OK.value,
            "metrics": metrics.model_dump(mode="json"),
            "alerts": [item.model_dump(mode="json") for item in alerts],
        }
