from __future__ import annotations

import pandas as pd

from services.advisor_service import AdvisorService
from src.agent.intent_router import Intent, IntentRouter
from src.services.decision_intelligence_service import DecisionIntelligenceService
from src.services.order_analytics_service import OrderAnalyticsService


def test_order_lookup_intent_has_priority_over_statistics() -> None:
    router = IntentRouter()
    assert router.route("260921KK6HXSNP tìm đơn hàng này") is Intent.ORDER_LOOKUP
    assert router.route("Đơn 260921KK6HXSNP đang ở đâu?") is Intent.ORDER_LOOKUP
    assert router.extract_order_id("Kiểm tra mã đơn 001234567890") == "001234567890"


def test_statistics_intent_routes_business_questions() -> None:
    router = IntentRouter()
    assert router.route("Hôm nay tôi có bao nhiêu đơn?") is Intent.ORDER_STATISTICS
    assert router.route("Doanh thu Shopee tuần này thế nào?") is Intent.ORDER_STATISTICS
    assert router.route("Sản phẩm nào bán chạy nhất?") is Intent.ORDER_STATISTICS


def test_followup_uses_confirmed_order_id_from_history() -> None:
    router = IntentRouter()
    history = [
        {"role": "user", "content": "Tìm đơn hàng 260921KK6HXSNP"},
        {"role": "assistant", "content": "Đơn 260921KK6HXSNP đang chờ giao hàng."},
    ]
    assert router.route("Đơn này đã giao chưa?") is Intent.ORDER_LOOKUP
    assert router.extract_order_id_from_history(history) == "260921KK6HXSNP"


def test_statistics_excludes_cancelled_revenue_and_groups_by_platform_order_key() -> None:
    frame = pd.DataFrame(
        [
            {
                "platform": "shopee", "order_id": "same", "created_at": "2026-10-13T01:00:00Z",
                "order_status": "completed", "product_name": "Áo", "quantity": 2,
                "selling_price": 100_000,
            },
            {
                "platform": "lazada", "order_id": "same", "created_at": "2026-10-13T02:00:00Z",
                "order_status": "cancelled", "product_name": "Quần", "quantity": 1,
                "selling_price": 300_000,
            },
        ]
    )
    result = OrderAnalyticsService().summarize(frame)
    assert result["total_orders"] == 2
    assert result["cancelled_orders"] == 1
    assert result["revenue"] == 200_000
    assert result["orders_by_platform"] == {"lazada": 1, "shopee": 1}


def test_database_error_is_not_reported_as_order_not_found() -> None:
    class FailingRepository:
        def get_orders_by_external_id(self, *_args, **_kwargs):
            raise RuntimeError("database unavailable")

        def load_orders(self, *_args, **_kwargs):
            raise RuntimeError("database unavailable")

    decision = DecisionIntelligenceService("tenant-a", "shop-a", FailingRepository())
    advisor = AdvisorService(llm_client=None, decision_service=decision)
    result = advisor.answer("Tìm đơn hàng 260921KK6HXSNP")

    assert result.analysis_status == "ERROR"
    assert "không thể kiểm tra" in result.answer.lower()
    assert "không tìm thấy" not in result.answer.lower()
