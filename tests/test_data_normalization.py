"""Normalization tests for schema, duplicate items and untrusted values."""
import pandas as pd
import pytest

from src.services.data_normalization_service import DataNormalizationService


def unified_frame() -> pd.DataFrame:
    row = {
        "platform": "shopee", "order_id": "o1", "order_item_id": "i1",
        "created_at": "2026-01-01", "product_id": "p1", "seller_sku": "s1",
        "product_name": "=HYPERLINK('bad')", "variation": None, "quantity": "1",
        "original_price": "100", "selling_price": "90", "seller_discount": "10",
        "platform_discount": "0", "shipping_fee": "0", "platform_fee": "1",
        "transaction_fee": "1", "service_fee": "0", "refund_amount": "0",
        "order_status": "completed", "cancel_reason": None,
    }
    return pd.DataFrame([row, row.copy()])


def test_normalizer_deduplicates_order_items_and_neutralizes_formula() -> None:
    result = DataNormalizationService().normalize(unified_frame())
    assert len(result.frame) == 1
    assert result.frame.iloc[0]["product_name"].startswith("'")
    assert any("trùng lặp" in warning for warning in result.warnings)


def test_normalizer_rejects_missing_required_schema() -> None:
    with pytest.raises(ValueError, match="Thiếu cột"):
        DataNormalizationService().normalize(pd.DataFrame({"order_id": ["o1"], "platform": ["shopee"]}), "shopee")
