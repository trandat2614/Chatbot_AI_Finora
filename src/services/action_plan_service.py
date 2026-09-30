"""Prioritize deterministic findings into an AI-ready action plan."""
from __future__ import annotations

from src.schemas.commerce import ActionItem, AnalysisStatus


class ActionPlanService:
    def generate(self, health: dict, leakage: dict, products: dict, opportunities: dict) -> dict:
        candidates: list[tuple[int, ActionItem]] = []
        severity_rank = {"critical": 100, "warning": 70, "info": 30}
        recommendations = {
            "HIGH_CANCELLATION": "Rà soát nguyên nhân hủy theo SKU và quy trình xác nhận đơn.",
            "HIGH_REFUND": "Kiểm tra chất lượng, mô tả và đóng gói của SKU có hoàn tiền cao.",
            "HIGH_DISCOUNT_DEPENDENCY": "Giảm phụ thuộc voucher bằng bundle và tối ưu giá trị đơn hàng.",
            "REVENUE_DROP": "Phân tích traffic, conversion và SKU giảm mạnh trước khi tăng ngân sách.",
            "FEE_INCREASE": "Đối soát cơ cấu phí sàn và các gói dịch vụ đang sử dụng.",
            "PRODUCT_GROWTH": "Bảo đảm tồn kho và thử tăng hiển thị cho nhóm đang tăng trưởng.",
        }
        for alert in health.get("alerts", []):
            evidence = f"{alert['metric']}={alert['current_value']}"
            candidates.append((severity_rank.get(alert["severity"], 20), ActionItem(
                priority=1, title=alert["code"], problem=alert["explanation"], evidence=[evidence],
                recommendation=recommendations.get(alert["code"], "Điều tra nguyên nhân bằng dữ liệu chi tiết."),
                expected_impact=None, confidence=0.9,
            )))
        if leakage.get("status") == "OK" and (leakage.get("leakage_rate") or 0) > 15:
            candidates.append((85, ActionItem(
                priority=1, title="Giảm thất thoát doanh thu", problem="Khoảng cách GMV tới net revenue đang cao.",
                evidence=[f"leakage_rate={leakage['leakage_rate']}%", f"total_leakage={leakage['total_leakage']}"],
                recommendation="Ưu tiên đối soát refund, phí sàn và phí dịch vụ có giá trị lớn nhất.",
                expected_impact=None, confidence=0.95,
            )))
        for item in products.get("products", []):
            if item["classification"] in {"FIX", "REDUCE"}:
                candidates.append((65, ActionItem(
                    priority=1, title=f"{item['classification']} SKU {item['sku']}",
                    problem="SKU có tín hiệu rủi ro từ dữ liệu đơn hàng.",
                    evidence=[f"refund_rate={item['metrics']['refund_rate']}%", f"cancellation_rate={item['metrics']['cancellation_rate']}%"],
                    recommendation="Sửa vấn đề chất lượng/định vị trước khi tiếp tục mở rộng.",
                    expected_impact=None, confidence=item["confidence"],
                )))
        for item in opportunities.get("opportunities", [])[:2]:
            if item["opportunity_score"] >= 50:
                candidates.append((55, ActionItem(
                    priority=1, title=f"Thử cơ hội cho SKU {item['sku']}",
                    problem="SKU có mức phù hợp đáng chú ý với xu hướng thị trường.",
                    evidence=[f"opportunity_score={item['opportunity_score']}", f"trend_state={item['trend_state']}"],
                    recommendation="Chạy thử nghiệm nhỏ, giữ rào chắn biên lợi nhuận và đo conversion.",
                    expected_impact=None, confidence=item["confidence"],
                )))
        candidates.sort(key=lambda item: item[0], reverse=True)
        actions = []
        for priority, (_, item) in enumerate(candidates[:5], start=1):
            actions.append(item.model_copy(update={"priority": priority}).model_dump(mode="json"))
        return {"status": AnalysisStatus.OK.value if actions else AnalysisStatus.INSUFFICIENT_DATA.value, "actions": actions}
