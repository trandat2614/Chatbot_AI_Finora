"""Transactional tenant-scoped commerce repositories."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from src.db.models import DataImport, Order, OrderItem, Product, Shop
from src.db.session import Database, get_database
from src.security.auth import AuthContext


def _uuid() -> str:
    return str(uuid.uuid4())


@dataclass(frozen=True)
class ImportWriteResult:
    orders_created: int
    order_items_created: int


def _number(value: Any) -> float:
    try:
        if pd.isna(value):
            return 0.0
        return max(float(value), 0.0)
    except (TypeError, ValueError):
        return 0.0


def _first_number(group: pd.DataFrame, name: str) -> float:
    """Take an order-level value once even when exports repeat it per item row."""
    if name not in group:
        return 0.0
    values = [_number(value) for value in group[name].tolist()]
    return next((value for value in values if value != 0), 0.0)


class SQLAlchemyCommerceRepository:
    """Single transactional boundary for orders, products and import jobs."""

    def __init__(self, database: Database | None = None) -> None:
        self.database = database or get_database()

    @staticmethod
    def _ensure_shop(session: Session, context: AuthContext, platform: str | None = None) -> None:
        shop = session.scalar(
            select(Shop).where(
                Shop.tenant_id == context.tenant_id,
                Shop.external_shop_id == context.shop_id,
            )
        )
        if shop is None:
            session.add(
                Shop(
                    id=_uuid(),
                    tenant_id=context.tenant_id,
                    external_shop_id=context.shop_id,
                    platform=platform,
                )
            )
        elif platform and not shop.platform:
            shop.platform = platform

    def create_import(
        self,
        context: AuthContext,
        filename: str,
        filename_hash: str,
        fingerprint: str,
        total_rows: int,
    ) -> tuple[str, bool]:
        import_id = _uuid()
        try:
            with self.database.session() as session:
                existing = session.scalar(
                    select(DataImport).where(
                        DataImport.tenant_id == context.tenant_id,
                        DataImport.shop_id == context.shop_id,
                        DataImport.fingerprint == fingerprint,
                    )
                )
                if existing is not None:
                    if existing.status == "FAILED":
                        existing.user_id = context.user_id
                        existing.filename = filename
                        existing.filename_hash = filename_hash
                        existing.status = "PENDING"
                        existing.total_rows = max(total_rows, 0)
                        existing.accepted_rows = 0
                        existing.rejected_rows = 0
                        existing.orders_created = 0
                        existing.order_items_created = 0
                        existing.warnings = []
                        existing.error_code = None
                        existing.completed_at = None
                        return existing.id, True
                    return existing.id, False
                self._ensure_shop(session, context)
                session.add(
                    DataImport(
                        id=import_id,
                        tenant_id=context.tenant_id,
                        shop_id=context.shop_id,
                        user_id=context.user_id,
                        filename=filename,
                        filename_hash=filename_hash,
                        fingerprint=fingerprint,
                        status="PENDING",
                        total_rows=max(total_rows, 0),
                    )
                )
                session.flush()
            return import_id, True
        except IntegrityError:
            # A concurrent request may have inserted the same fingerprint.
            with self.database.session() as session:
                existing = session.scalar(
                    select(DataImport).where(
                        DataImport.tenant_id == context.tenant_id,
                        DataImport.shop_id == context.shop_id,
                        DataImport.fingerprint == fingerprint,
                    )
                )
                if existing is None:
                    raise
                return existing.id, False

    def mark_processing(self, context: AuthContext, import_id: str) -> None:
        with self.database.session() as session:
            record = self._owned_import(session, context, import_id)
            if record is None:
                raise LookupError("Import job không tồn tại trong shop hiện tại.")
            record.status = "PROCESSING"

    def complete_import(
        self,
        context: AuthContext,
        import_id: str,
        *,
        platform: str,
        accepted_rows: int,
        rejected_rows: int,
        orders_created: int,
        order_items_created: int,
        warnings: list[str],
    ) -> None:
        with self.database.session() as session:
            record = self._owned_import(session, context, import_id)
            if record is None:
                raise LookupError("Import job không tồn tại trong shop hiện tại.")
            record.platform = platform
            record.status = "COMPLETED"
            record.accepted_rows = accepted_rows
            record.rejected_rows = rejected_rows
            record.orders_created = orders_created
            record.order_items_created = order_items_created
            record.warnings = list(warnings)
            record.completed_at = datetime.now(timezone.utc)

    def fail_import(self, context: AuthContext, import_id: str, error_code: str) -> None:
        with self.database.session() as session:
            record = self._owned_import(session, context, import_id)
            if record is None:
                return
            record.status = "FAILED"
            record.error_code = error_code
            record.completed_at = datetime.now(timezone.utc)

    @staticmethod
    def _owned_import(
        session: Session, context: AuthContext, import_id: str
    ) -> DataImport | None:
        return session.scalar(
            select(DataImport).where(
                DataImport.id == import_id,
                DataImport.tenant_id == context.tenant_id,
                DataImport.shop_id == context.shop_id,
            )
        )

    def get_import(self, context: AuthContext, import_id: str) -> dict | None:
        with self.database.session() as session:
            record = self._owned_import(session, context, import_id)
            if record is None:
                return None
            return {
                "import_id": record.id,
                "platform": record.platform,
                "filename": record.filename,
                "status": record.status,
                "total_rows": record.total_rows,
                "accepted_rows": record.accepted_rows,
                "rejected_rows": record.rejected_rows,
                "orders_created": record.orders_created,
                "order_items_created": record.order_items_created,
                "warnings": record.warnings or [],
                "created_at": record.created_at,
                "completed_at": record.completed_at,
            }

    def replace_orders(
        self, context: AuthContext, frame: pd.DataFrame, import_id: str | None = None
    ) -> ImportWriteResult:
        if frame.empty:
            return ImportWriteResult(0, 0)
        orders_created = 0
        with self.database.session() as session:
            platform = str(frame.iloc[0]["platform"])
            self._ensure_shop(session, context, platform)
            products_by_sku = {
                item.sku: item
                for item in session.scalars(
                    select(Product).where(
                        Product.tenant_id == context.tenant_id,
                        Product.shop_id == context.shop_id,
                    )
                ).all()
            }
            for (row_platform, external_order_id), group in frame.groupby(
                ["platform", "order_id"], sort=False, dropna=False
            ):
                existing = session.scalar(
                    select(Order)
                    .options(selectinload(Order.items))
                    .where(
                        Order.tenant_id == context.tenant_id,
                        Order.shop_id == context.shop_id,
                        Order.platform == str(row_platform),
                        Order.external_order_id == str(external_order_id),
                    )
                )
                if existing is not None:
                    session.delete(existing)
                    session.flush()

                first = group.iloc[0]
                created_at = pd.to_datetime(first["created_at"], utc=True).to_pydatetime()
                item_total = sum(
                    _number(row["selling_price"]) * int(_number(row["quantity"]))
                    for _, row in group.iterrows()
                )
                order = Order(
                    id=_uuid(),
                    tenant_id=context.tenant_id,
                    shop_id=context.shop_id,
                    import_id=import_id,
                    platform=str(row_platform),
                    external_order_id=str(external_order_id),
                    created_at=created_at,
                    status=str(first["order_status"]),
                    cancel_reason=(
                        str(first["cancel_reason"])
                        if pd.notna(first.get("cancel_reason")) else None
                    ),
                    order_total=item_total,
                    platform_fee=_first_number(group, "platform_fee"),
                    transaction_fee=_first_number(group, "transaction_fee"),
                    service_fee=_first_number(group, "service_fee"),
                    shipping_fee=_first_number(group, "shipping_fee"),
                    refund_amount=_first_number(group, "refund_amount"),
                )
                session.add(order)
                orders_created += 1
                for _, row in group.iterrows():
                    item = OrderItem(
                        id=_uuid(),
                        order_id=order.id,
                        tenant_id=context.tenant_id,
                        shop_id=context.shop_id,
                        external_item_id=str(row["order_item_id"]),
                        product_id=str(row["product_id"]) if pd.notna(row.get("product_id")) else None,
                        sku=str(row["seller_sku"]) if pd.notna(row.get("seller_sku")) else None,
                        product_name=str(row["product_name"]),
                        variation=str(row["variation"]) if pd.notna(row.get("variation")) else None,
                        quantity=int(_number(row["quantity"])),
                        original_price=_number(row["original_price"]) if pd.notna(row.get("original_price")) else None,
                        selling_price=_number(row["selling_price"]),
                        seller_discount=_number(row["seller_discount"]),
                        platform_discount=_number(row["platform_discount"]),
                    )
                    order.items.append(item)
                    sku = item.sku or item.product_id
                    if sku:
                        product = products_by_sku.get(sku)
                        if product is None:
                            product = Product(
                                id=_uuid(),
                                tenant_id=context.tenant_id,
                                shop_id=context.shop_id,
                                sku=sku,
                                product_id=item.product_id,
                                product_name=item.product_name,
                            )
                            session.add(product)
                            products_by_sku[sku] = product
                        else:
                            product.product_name = item.product_name
                            product.product_id = item.product_id
            session.flush()
        return ImportWriteResult(
            orders_created=orders_created,
            order_items_created=int(len(frame)),
        )

    def load_orders(self, tenant_id: str, shop_id: str) -> pd.DataFrame:
        rows: list[dict[str, Any]] = []
        with self.database.session() as session:
            orders = session.scalars(
                select(Order)
                .options(selectinload(Order.items))
                .where(Order.tenant_id == tenant_id, Order.shop_id == shop_id)
                .order_by(Order.created_at, Order.id)
            ).all()
            for order in orders:
                for index, item in enumerate(order.items):
                    rows.append(
                        {
                            "platform": order.platform,
                            "order_id": order.external_order_id,
                            "order_item_id": item.external_item_id,
                            "created_at": order.created_at,
                            "product_id": item.product_id,
                            "seller_sku": item.sku,
                            "product_name": item.product_name,
                            "variation": item.variation,
                            "quantity": item.quantity,
                            "original_price": item.original_price,
                            "selling_price": item.selling_price,
                            "seller_discount": item.seller_discount,
                            "platform_discount": item.platform_discount,
                            # Order-level values are emitted only once to keep
                            # legacy analytics safe from double counting.
                            "shipping_fee": order.shipping_fee if index == 0 else 0.0,
                            "platform_fee": order.platform_fee if index == 0 else 0.0,
                            "transaction_fee": order.transaction_fee if index == 0 else 0.0,
                            "service_fee": order.service_fee if index == 0 else 0.0,
                            "refund_amount": order.refund_amount if index == 0 else 0.0,
                            "order_status": order.status,
                            "cancel_reason": order.cancel_reason,
                            "is_order_head": index == 0,
                        }
                    )
        return pd.DataFrame(rows)

    def list_products(self, tenant_id: str, shop_id: str) -> list[dict]:
        with self.database.session() as session:
            products = session.scalars(
                select(Product)
                .where(Product.tenant_id == tenant_id, Product.shop_id == shop_id)
                .order_by(Product.sku)
            ).all()
            return [
                {
                    "sku": item.sku,
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "margin": item.margin,
                    "inventory": item.inventory,
                }
                for item in products
            ]

    def get_product(self, tenant_id: str, shop_id: str, sku: str) -> dict | None:
        with self.database.session() as session:
            item = session.scalar(
                select(Product).where(
                    Product.tenant_id == tenant_id,
                    Product.shop_id == shop_id,
                    Product.sku == sku,
                )
            )
            if item is None:
                return None
            return {
                "sku": item.sku,
                "product_id": item.product_id,
                "product_name": item.product_name,
                "margin": item.margin,
                "inventory": item.inventory,
            }
