"""Relational tenant isolation and Order/OrderItem accounting tests."""
from __future__ import annotations

import pandas as pd

from src.db.session import Database
from src.repositories.commerce_repository import SQLAlchemyCommerceRepository
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
    match = repository.get_orders_by_external_id("tenant-a", "shop-a", "order-1")
    assert len(match) == 1
    assert match[0]["order_id"] == "order-1"
    assert match[0]["total_amount"] == 200
    assert len(match[0]["items"]) == 2
    assert repository.get_orders_by_external_id("tenant-b", "shop-a", "order-1") == []
    assert repository.get_orders_by_external_id("tenant-a", "shop-b", "order-1") == []
    database.dispose()


def test_repository_preserves_leading_zero_order_id(tmp_path) -> None:
    database = Database(f"sqlite:///{tmp_path / 'leading-zero.db'}")
    database.create_schema()
    repository = SQLAlchemyCommerceRepository(database)
    context = AuthContext("user-a", "tenant-a", "shop-a", "owner")
    value = frame()
    value["order_id"] = "001234567890"
    repository.replace_orders(context, value)

    match = repository.get_orders_by_external_id("tenant-a", "shop-a", "001234567890")
    assert match[0]["order_id"] == "001234567890"
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
