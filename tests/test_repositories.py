"""Relational tenant isolation and Order/OrderItem accounting tests."""
from __future__ import annotations

import pandas as pd

from src.db.session import Database
from src.repositories.commerce_repository import SQLAlchemyCommerceRepository
from src.repositories.trend_repository import SQLAlchemyTrendRepository
from src.security.auth import AuthContext
from src.services.metric_service import MetricService


def frame() -> pd.DataFrame:
    base = {
        "platform": "shopee",
        "order_id": "order-1",
        "created_at": "2026-09-01T00:00:00Z",
        "product_id": "p1",
        "seller_sku": "sku-1",
        "product_name": "Áo cotton",
        "variation": None,
        "quantity": 1,
        "original_price": 100,
        "selling_price": 90,
        "seller_discount": 10,
        "platform_discount": 0,
        "shipping_fee": 5,
        "platform_fee": 30,
        "transaction_fee": 2,
        "service_fee": 1,
        "refund_amount": 0,
        "order_status": "completed",
        "cancel_reason": None,
    }
    second = dict(base)
    second.update(
        order_item_id="item-2", product_id="p2", seller_sku="sku-2",
        product_name="Quần jean", selling_price=110,
    )
    first = dict(base)
    first["order_item_id"] = "item-1"
    return pd.DataFrame([first, second])


def test_repository_isolates_tenant_and_deduplicates_order_fees(tmp_path) -> None:
    database = Database(f"sqlite:///{tmp_path / 'test.db'}")
    database.create_schema()
    repository = SQLAlchemyCommerceRepository(database)
    context = AuthContext("user-a", "tenant-a", "shop-a", "owner")
    repository.replace_orders(context, frame())

    own = repository.load_orders("tenant-a", "shop-a")
    assert len(own) == 2
    assert repository.load_orders("tenant-b", "shop-a").empty
    assert repository.load_orders("tenant-a", "shop-b").empty
    assert own["platform_fee"].sum() == 30
    assert MetricService().calculate(own).marketplace_fee == 33
    database.dispose()


def test_repository_uses_bound_parameters_for_hostile_scope(tmp_path) -> None:
    database = Database(f"sqlite:///{tmp_path / 'injection.db'}")
    database.create_schema()
    repository = SQLAlchemyCommerceRepository(database)
    hostile_tenant = "tenant'; DROP TABLE orders;--"
    context = AuthContext("user-a", hostile_tenant, "shop-a", "owner")
    repository.replace_orders(context, frame())

    assert len(repository.load_orders(hostile_tenant, "shop-a")) == 2
    assert repository.load_orders("tenant-a", "shop-a").empty
    database.dispose()


def test_trend_snapshots_are_persistent_and_append_only(tmp_path) -> None:
    database = Database(f"sqlite:///{tmp_path / 'trends.db'}")
    database.create_schema()
    repository = SQLAlchemyTrendRepository(database)
    snapshot = {
        "snapshot_id": "snapshot-20260930-product-1",
        "capture_date": "2026-09-30T00:00:00+00:00",
        "platform": "shopee",
        "category": "nam",
        "period": "7d",
        "product_id": "product-1",
        "product_name": "Áo cotton",
        "shop_name": "Public shop",
        "rank": 1,
        "price": 100_000,
        "sales_growth": 25,
        "sales_30d": 100,
        "rating": 4.8,
        "source_url": "https://example.invalid/product-1",
    }

    assert repository.upsert_snapshots([snapshot]) == 1
    assert repository.upsert_snapshots([snapshot]) == 0
    stored = repository.list_snapshots("nam", "7d")
    assert len(stored) == 1
    assert stored[0]["snapshot_id"] == snapshot["snapshot_id"]
    assert stored[0]["capture_date"].date().isoformat() == "2026-09-30"
    database.dispose()
