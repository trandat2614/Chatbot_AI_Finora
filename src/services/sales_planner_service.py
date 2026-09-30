"""Create a structured sales plan from verified opportunity and SKU data."""
from __future__ import annotations


class SalesPlannerService:
    def generate(self, opportunities: dict, products: dict, *, period: str = "week", objective: str = "conversion") -> dict:
        if opportunities.get("status") != "OK":
            return {"status": "INSUFFICIENT_DATA", "missing_fields": ["product_opportunities"], "plan": []}
        doctor = {item["sku"]: item for item in products.get("products", [])}
        plan = []
        for item in opportunities.get("opportunities", [])[:5]:
            diagnosis = doctor.get(item["sku"], {})
            plan.append({
                "sku": item["sku"], "product_name": item["product_name"],
                "objective": objective, "period": period,
                "product_strategy": diagnosis.get("classification", "MONITOR"),
                "opportunity_score": item["opportunity_score"],
                "actions": [
                    "Xác nhận tồn kho và biên lợi nhuận trước khi triển khai",
                    "Thử nghiệm giá/nội dung trên một nhóm traffic giới hạn",
                    "Đo đơn hàng, refund và cancellation sau thử nghiệm",
                ],
                "numeric_target": None,
                "confidence": item["confidence"],
                "constraints": [f"Thiếu {name}" for name in item.get("missing_metrics", [])],
            })
        return {"status": "OK", "period": period, "objective": objective, "plan": plan}
