"""Derive channel communication from sales-plan objectives."""
from __future__ import annotations


class CommunicationPlannerService:
    CHANNEL_FORMATS = {
        "tiktok": "Video ngắn: hook vấn đề, demo sản phẩm, bằng chứng và CTA.",
        "facebook": "Bài social: insight khách hàng, lợi ích chính và CTA về gian hàng.",
        "shopee": "Tối ưu title/ảnh/mô tả và thông điệp voucher có rào chắn lợi nhuận.",
        "zalo": "Tin nhắn ngắn theo phân khúc khách đã đồng ý nhận truyền thông.",
    }

    def generate(self, sales_plan: dict, *, objective: str) -> dict:
        if sales_plan.get("status") != "OK" or not sales_plan.get("plan"):
            return {"status": "INSUFFICIENT_DATA", "missing_fields": ["sales_plan"], "channels": {}}
        products = [item["product_name"] for item in sales_plan["plan"][:3]]
        channels = {}
        for channel, template in self.CHANNEL_FORMATS.items():
            channels[channel] = {
                "objective": objective,
                "product_focus": products,
                "message_direction": template,
                "guardrails": ["Không bịa giá/ưu đãi", "Không dùng PII", "Không tự động thay đổi listing hoặc ngân sách"],
                "content_drafts": [],
            }
        return {"status": "OK", "business_objective": objective, "channels": channels}
