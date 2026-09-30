"""Offline tests for deterministic decision-intelligence services."""
from __future__ import annotations

import pandas as pd

from src.schemas.commerce import MetricResult
from src.services.action_plan_service import ActionPlanService
from src.services.business_health_service import BusinessHealthService
from src.services.market_trend_service import MarketTrendService
from src.services.metric_service import MetricService
from src.services.opportunity_matching_service import OpportunityMatchingService
from src.services.product_doctor_service import ProductDoctorService
from src.services.revenue_leakage_service import RevenueLeakageService


def commerce_frame() -> pd.DataFrame:
    return pd.DataFrame([
        {"platform": "shopee", "order_id": "o1", "order_item_id": "i1", "created_at": "2026-01-01T00:00:00Z",
         "product_id": "p1", "seller_sku": "SKU-A", "product_name": "Áo thun cotton boxy đen", "variation": None,
         "quantity": 1, "original_price": 120, "selling_price": 100, "seller_discount": 20,
         "platform_discount": 0, "shipping_fee": 2, "platform_fee": 5, "transaction_fee": 2,
         "service_fee": 1, "refund_amount": 0, "order_status": "completed", "cancel_reason": None},
        {"platform": "shopee", "order_id": "o1", "order_item_id": "i2", "created_at": "2026-01-01T00:00:00Z",
         "product_id": "p2", "seller_sku": "SKU-B", "product_name": "Quần jean ống rộng", "variation": None,
         "quantity": 2, "original_price": 100, "selling_price": 90, "seller_discount": 10,
         "platform_discount": 0, "shipping_fee": 0, "platform_fee": 4, "transaction_fee": 1,
         "service_fee": 1, "refund_amount": 0, "order_status": "completed", "cancel_reason": None},
        {"platform": "shopee", "order_id": "o2", "order_item_id": "i3", "created_at": "2026-01-03T00:00:00Z",
         "product_id": "p1", "seller_sku": "SKU-A", "product_name": "Áo thun cotton boxy đen", "variation": None,
         "quantity": 1, "original_price": 120, "selling_price": 100, "seller_discount": 20,
         "platform_discount": 0, "shipping_fee": 2, "platform_fee": 5, "transaction_fee": 2,
         "service_fee": 1, "refund_amount": 100, "order_status": "refunded", "cancel_reason": None},
    ])


def test_metric_uses_distinct_order_count_for_multi_item_order() -> None:
    result = MetricService().calculate(commerce_frame())
    assert result.order_count == 2
    assert result.units_sold == 4
    assert result.revenue == 380
    # o1 repeats order-level fees on both item rows; only the first value counts.
    assert result.marketplace_fee == 16


def test_metric_returns_insufficient_data_for_missing_columns() -> None:
    result = MetricService().calculate(pd.DataFrame({"order_id": ["o1"]}))
    assert result.status.value == "INSUFFICIENT_DATA"
    assert "selling_price" in result.missing_fields


def test_metric_handles_null_numeric_values() -> None:
    frame = commerce_frame()
    frame.loc[0, "platform_fee"] = None
    assert MetricService().calculate(frame).marketplace_fee is not None


def test_revenue_leakage_returns_structured_bridge() -> None:
    result = RevenueLeakageService().analyze(commerce_frame())
    assert result["status"] == "OK"
    assert result["gmv"] >= result["net_revenue"]
    assert "refund" in result["components"]


def test_product_doctor_and_missing_sku_data() -> None:
    result = ProductDoctorService().analyze(commerce_frame())
    assert result["status"] == "OK"
    assert {item["sku"] for item in result["products"]} == {"SKU-A", "SKU-B"}
    missing = ProductDoctorService().analyze(pd.DataFrame())
    assert missing["status"] == "INSUFFICIENT_DATA"


def test_trend_state_detection() -> None:
    assert MarketTrendService._state(5, 100, 500, "7d") == "BESTSELLER"
    assert MarketTrendService._state(50, -1, 100, "30d") == "COOLING"
    assert MarketTrendService._state(50, 20, 10, "today") == "EMERGING"


def test_opportunity_confidence_drops_when_margin_inventory_missing() -> None:
    market = {"items": [{"product_name": "Áo thun cotton boxy", "sales_growth": 80, "price": 105, "trend_state": "RISING"}]}
    result = OpportunityMatchingService().match(commerce_frame(), market)
    assert result["status"] == "OK"
    assert result["opportunities"][0]["confidence"] < 1
    assert set(result["opportunities"][0]["missing_metrics"]) == {"margin", "inventory"}


def test_action_plan_prioritizes_critical_alert() -> None:
    metrics = MetricResult(status="OK", revenue=100, seller_discount=0, marketplace_fee=0,
                           cancellation_rate=20, refund_rate=0, sales_growth=0)
    health = BusinessHealthService().analyze(metrics)
    result = ActionPlanService().generate(health, {"status": "INSUFFICIENT_DATA"}, {"products": []}, {"opportunities": []})
    assert result["status"] == "OK"
    assert result["actions"][0]["title"] == "HIGH_CANCELLATION"
    assert result["actions"][0]["expected_impact"] is None
