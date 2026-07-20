"""
Business Rule Engine for FINORA AI Business Advisor.

Generates deterministic business signals from computed metrics.
The LLM receives signals as structured facts, not raw data.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from tools.revenue_analysis_tool import RevenueMetrics
from tools.profit_analysis_tool import ProfitMetrics
from tools.marketing_metrics_tool import MarketingMetrics

logger = logging.getLogger(__name__)

# Severity levels
SEVERITY_INFO = "info"
SEVERITY_WARNING = "warning"
SEVERITY_CRITICAL = "critical"


@dataclass
class BusinessSignal:
    """A single actionable business signal."""

    code: str
    severity: str  # info | warning | critical
    title: str
    description: str
    evidence: str
    recommended_action: str


@dataclass
class BusinessSignals:
    """Container for all generated business signals."""

    signals: list[BusinessSignal] = field(default_factory=list)

    def has_critical(self) -> bool:
        return any(s.severity == SEVERITY_CRITICAL for s in self.signals)

    def has_warnings(self) -> bool:
        return any(s.severity == SEVERITY_WARNING for s in self.signals)

    def by_severity(self, severity: str) -> list[BusinessSignal]:
        return [s for s in self.signals if s.severity == severity]

    def as_text(self) -> str:
        """Render signals as a readable text block for LLM context."""
        if not self.signals:
            return "Không có tín hiệu bất thường nào được phát hiện."
        lines = []
        severity_order = [SEVERITY_CRITICAL, SEVERITY_WARNING, SEVERITY_INFO]
        for sev in severity_order:
            for sig in self.by_severity(sev):
                icon = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}.get(sev, "")
                lines.append(f"{icon} [{sev.upper()}] {sig.title}")
                lines.append(f"   Mô tả: {sig.description}")
                lines.append(f"   Bằng chứng: {sig.evidence}")
                lines.append(f"   Hành động đề xuất: {sig.recommended_action}")
                lines.append("")
        return "\n".join(lines)


class BusinessRuleEngine:
    """Evaluates business rules and generates signals.

    Rules are explicit and deterministic — no LLM involvement.
    Each rule only fires when the required data is present.
    """

    def evaluate(
        self,
        revenue_metrics: Optional[RevenueMetrics] = None,
        profit_metrics: Optional[ProfitMetrics] = None,
        marketing_metrics: Optional[MarketingMetrics] = None,
    ) -> BusinessSignals:
        """Run all applicable rules and return detected signals.

        Args:
            revenue_metrics: Output from RevenueAnalysisTool.
            profit_metrics: Output from ProfitAnalysisTool.
            marketing_metrics: Output from MarketingMetricsTool.

        Returns:
            BusinessSignals container.
        """
        signals = BusinessSignals()

        if revenue_metrics:
            self._check_revenue_decline(revenue_metrics, signals)
            self._check_channel_concentration(revenue_metrics, signals)

        if marketing_metrics:
            self._check_cac(marketing_metrics, signals)
            self._check_conversion_rate(marketing_metrics, signals)
            self._check_repeat_rate(marketing_metrics, signals)
            self._check_refund_rate(marketing_metrics, signals)
            self._check_roas(marketing_metrics, signals)

        if revenue_metrics and marketing_metrics:
            self._check_marketing_efficiency(revenue_metrics, marketing_metrics, signals)

        if profit_metrics:
            self._check_net_loss(profit_metrics, signals)

        logger.debug("BusinessRuleEngine: %d signals generated.", len(signals.signals))
        return signals

    # ------------------------------------------------------------------ #
    # Individual rules
    # ------------------------------------------------------------------ #

    @staticmethod
    def _check_revenue_decline(metrics: RevenueMetrics, signals: BusinessSignals) -> None:
        if metrics.revenue_growth_rate is None:
            return
        if metrics.revenue_growth_rate < 0:
            signals.signals.append(BusinessSignal(
                code="REVENUE_DECLINE",
                severity=SEVERITY_WARNING,
                title="Doanh thu đang giảm",
                description="Doanh thu kỳ gần nhất thấp hơn kỳ trước.",
                evidence=f"Revenue Growth Rate: {metrics.revenue_growth_rate:.1f}%",
                recommended_action=(
                    "Phân tích nguyên nhân suy giảm: traffic, conversion rate hay AOV? "
                    "Xem xét chạy campaign kích cầu hoặc kiểm tra chất lượng sản phẩm."
                ),
            ))
        elif metrics.revenue_growth_rate == 0:
            signals.signals.append(BusinessSignal(
                code="REVENUE_FLAT",
                severity=SEVERITY_INFO,
                title="Doanh thu không tăng trưởng",
                description="Doanh thu kỳ gần nhất bằng kỳ trước.",
                evidence="Revenue Growth Rate: 0%",
                recommended_action="Đánh giá lại chiến lược growth và tìm cơ hội mới.",
            ))

    @staticmethod
    def _check_channel_concentration(
        metrics: RevenueMetrics, signals: BusinessSignals
    ) -> None:
        if not metrics.revenue_by_channel or metrics.total_revenue <= 0:
            return
        for channel, rev in metrics.revenue_by_channel.items():
            ratio = rev / metrics.total_revenue * 100
            if ratio > 70:
                signals.signals.append(BusinessSignal(
                    code="CHANNEL_CONCENTRATION",
                    severity=SEVERITY_WARNING,
                    title="Phụ thuộc lớn vào một kênh bán hàng",
                    description=(
                        f"Kênh '{channel}' chiếm {ratio:.1f}% tổng doanh thu. "
                        "Rủi ro cao nếu kênh này gặp vấn đề."
                    ),
                    evidence=f"{channel}: {rev:,.0f} ₫ ({ratio:.1f}% / tổng {metrics.total_revenue:,.0f} ₫)",
                    recommended_action=(
                        "Đa dạng hoá kênh bán hàng. "
                        "Đặt mục tiêu kênh phụ đóng góp ít nhất 30% doanh thu trong 6 tháng."
                    ),
                ))

    @staticmethod
    def _check_cac(metrics: MarketingMetrics, signals: BusinessSignals) -> None:
        if metrics.cac is None or metrics.cac.value is None:
            return
        # Flag if CAC > 30% of AOV (general e-commerce benchmark)
        if metrics.aov and metrics.aov.value and metrics.aov.value > 0:
            cac_to_aov = metrics.cac.value / metrics.aov.value * 100
            if cac_to_aov > 30:
                signals.signals.append(BusinessSignal(
                    code="HIGH_CAC",
                    severity=SEVERITY_WARNING,
                    title="Chi phí thu hút khách hàng cao",
                    description=(
                        f"CAC chiếm {cac_to_aov:.1f}% so với AOV — "
                        "doanh nghiệp cần nhiều đơn hàng để bù đắp chi phí thu hút."
                    ),
                    evidence=(
                        f"CAC: {metrics.cac.value:,.0f} ₫ | AOV: {metrics.aov.value:,.0f} ₫ "
                        f"| CAC/AOV: {cac_to_aov:.1f}%"
                    ),
                    recommended_action=(
                        "Tối ưu targeting quảng cáo, tăng organic traffic, "
                        "cải thiện referral program."
                    ),
                ))

    @staticmethod
    def _check_conversion_rate(
        metrics: MarketingMetrics, signals: BusinessSignals
    ) -> None:
        if metrics.conversion_rate is None or metrics.conversion_rate.value is None:
            return
        if metrics.conversion_rate.value < 2:
            signals.signals.append(BusinessSignal(
                code="LOW_CONVERSION",
                severity=SEVERITY_WARNING,
                title="Tỷ lệ chuyển đổi thấp",
                description="Conversion Rate dưới 2% — phần lớn traffic không chuyển thành đơn hàng.",
                evidence=f"Conversion Rate: {metrics.conversion_rate.value:.2f}%",
                recommended_action=(
                    "Kiểm tra tốc độ trang, hình ảnh sản phẩm, mô tả, giá so sánh. "
                    "A/B test trang sản phẩm và checkout flow."
                ),
            ))

    @staticmethod
    def _check_repeat_rate(metrics: MarketingMetrics, signals: BusinessSignals) -> None:
        if metrics.repeat_purchase_rate is None or metrics.repeat_purchase_rate.value is None:
            return
        if metrics.repeat_purchase_rate.value < 20:
            signals.signals.append(BusinessSignal(
                code="LOW_REPEAT_RATE",
                severity=SEVERITY_WARNING,
                title="Tỷ lệ khách hàng quay lại thấp",
                description="Dưới 20% đơn hàng đến từ khách hàng cũ — retention cần cải thiện.",
                evidence=f"Repeat Purchase Rate: {metrics.repeat_purchase_rate.value:.1f}%",
                recommended_action=(
                    "Triển khai loyalty program, email remarketing, "
                    "cross-sell/upsell sau mua, chăm sóc sau bán hàng."
                ),
            ))

    @staticmethod
    def _check_refund_rate(metrics: MarketingMetrics, signals: BusinessSignals) -> None:
        if metrics.refund_rate is None or metrics.refund_rate.value is None:
            return
        rate = metrics.refund_rate.value
        if rate > 10:
            severity = SEVERITY_CRITICAL
            action = (
                "Ưu tiên cao nhất: Điều tra nguyên nhân hoàn hàng (chất lượng? mô tả sai?). "
                "Tỷ lệ này ảnh hưởng nghiêm trọng đến lợi nhuận và uy tín sàn."
            )
        elif rate > 5:
            severity = SEVERITY_WARNING
            action = (
                "Xem xét lại mô tả sản phẩm, chất lượng đóng gói và quy trình kiểm tra hàng."
            )
        else:
            return
        signals.signals.append(BusinessSignal(
            code="HIGH_REFUND_RATE",
            severity=severity,
            title="Tỷ lệ hoàn hàng cao",
            description=f"Refund Rate: {rate:.1f}% — vượt ngưỡng chấp nhận.",
            evidence=f"Refund Rate: {rate:.1f}%",
            recommended_action=action,
        ))

    @staticmethod
    def _check_roas(metrics: MarketingMetrics, signals: BusinessSignals) -> None:
        if metrics.roas is None or metrics.roas.value is None:
            return
        if metrics.roas.value < 2:
            signals.signals.append(BusinessSignal(
                code="LOW_ROAS",
                severity=SEVERITY_WARNING,
                title="ROAS thấp — hiệu quả chi tiêu quảng cáo kém",
                description=f"ROAS = {metrics.roas.value:.2f}x, dưới ngưỡng 2x.",
                evidence=f"ROAS: {metrics.roas.value:.2f}x",
                recommended_action=(
                    "Tạm dừng campaign hiệu quả thấp, tối ưu creative/audience targeting, "
                    "kiểm tra attribution model."
                ),
            ))

    @staticmethod
    def _check_marketing_efficiency(
        revenue: RevenueMetrics,
        marketing: MarketingMetrics,
        signals: BusinessSignals,
    ) -> None:
        """Detect rising marketing cost with declining revenue."""
        if (
            revenue.revenue_growth_rate is not None
            and revenue.revenue_growth_rate < 0
            and marketing.marketing_cost_ratio is not None
            and marketing.marketing_cost_ratio.value is not None
            and marketing.marketing_cost_ratio.value > 25
        ):
            signals.signals.append(BusinessSignal(
                code="DECLINING_MARKETING_EFFICIENCY",
                severity=SEVERITY_WARNING,
                title="Hiệu quả chi tiêu marketing suy giảm",
                description=(
                    "Doanh thu đang giảm trong khi tỷ lệ chi phí marketing ở mức cao. "
                    "Marketing đang tiêu tốn nhiều hơn nhưng mang lại ít doanh thu hơn."
                ),
                evidence=(
                    f"Revenue Growth: {revenue.revenue_growth_rate:.1f}% | "
                    f"Marketing Cost Ratio: {marketing.marketing_cost_ratio.value:.1f}%"
                ),
                recommended_action=(
                    "Dừng phân bổ ngân sách theo quán tính. "
                    "Phân tích từng kênh: giữ kênh có ROAS tốt, cắt giảm kênh kém hiệu quả."
                ),
            ))

    @staticmethod
    def _check_net_loss(metrics: ProfitMetrics, signals: BusinessSignals) -> None:
        if metrics.total_net_profit is None:
            return
        if metrics.total_net_profit < 0:
            signals.signals.append(BusinessSignal(
                code="NET_LOSS",
                severity=SEVERITY_CRITICAL,
                title="Doanh nghiệp đang ghi nhận lỗ ròng",
                description=(
                    f"Net Profit âm: {metrics.total_net_profit:,.0f} ₫. "
                    "Doanh thu chưa đủ bù đắp tất cả chi phí."
                ),
                evidence=(
                    f"Net Profit: {metrics.total_net_profit:,.0f} ₫ | "
                    f"Net Margin: {metrics.net_profit_margin:.1f}%"
                    if metrics.net_profit_margin is not None
                    else f"Net Profit: {metrics.total_net_profit:,.0f} ₫"
                ),
                recommended_action=(
                    "Ưu tiên tuyệt đối: rà soát từng mục chi phí, "
                    "cắt giảm chi phí không thiết yếu, "
                    "tăng biên lợi nhuận trên sản phẩm hoặc điều chỉnh giá bán."
                ),
            ))


def evaluate_business_rules(
    revenue_metrics: Optional[RevenueMetrics] = None,
    profit_metrics: Optional[ProfitMetrics] = None,
    marketing_metrics: Optional[MarketingMetrics] = None,
) -> BusinessSignals:
    """Convenience function wrapping BusinessRuleEngine.evaluate."""
    engine = BusinessRuleEngine()
    return engine.evaluate(revenue_metrics, profit_metrics, marketing_metrics)
