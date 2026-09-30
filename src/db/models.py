"""Relational persistence models for tenant-scoped commerce and AI data."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Shop(Base):
    __tablename__ = "shops"
    __table_args__ = (UniqueConstraint("tenant_id", "external_shop_id", name="uq_shop_owner"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    external_shop_id: Mapped[str] = mapped_column(String(200), nullable=False)
    platform: Mapped[str | None] = mapped_column(String(50))
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )


class DataImport(Base):
    __tablename__ = "data_imports"
    __table_args__ = (
        Index("ix_import_owner_created", "tenant_id", "shop_id", "created_at"),
        UniqueConstraint(
            "tenant_id", "shop_id", "fingerprint", name="uq_import_owner_fingerprint"
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(200), nullable=False)
    shop_id: Mapped[str] = mapped_column(String(200), nullable=False)
    user_id: Mapped[str] = mapped_column(String(200), nullable=False)
    platform: Mapped[str | None] = mapped_column(String(50))
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    filename_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    fingerprint: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    total_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    accepted_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rejected_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    orders_created: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    order_items_created: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    warnings: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    error_code: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Order(Base):
    """Order-level monetary fields must be stored exactly once per order."""

    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "shop_id", "platform", "external_order_id",
            name="uq_order_external_owner",
        ),
        Index("ix_order_owner_created", "tenant_id", "shop_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(200), nullable=False)
    shop_id: Mapped[str] = mapped_column(String(200), nullable=False)
    import_id: Mapped[str | None] = mapped_column(ForeignKey("data_imports.id", ondelete="SET NULL"))
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    external_order_id: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(200), nullable=False)
    cancel_reason: Mapped[str | None] = mapped_column(Text)
    order_total: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    platform_fee: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    transaction_fee: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    service_fee: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    shipping_fee: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    refund_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", passive_deletes=True
    )


class OrderItem(Base):
    """Item-level prices and discounts; no order-level fee columns live here."""

    __tablename__ = "order_items"
    __table_args__ = (
        UniqueConstraint("order_id", "external_item_id", name="uq_order_item_external"),
        Index("ix_order_item_owner_sku", "tenant_id", "shop_id", "sku"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    order_id: Mapped[str] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tenant_id: Mapped[str] = mapped_column(String(200), nullable=False)
    shop_id: Mapped[str] = mapped_column(String(200), nullable=False)
    external_item_id: Mapped[str] = mapped_column(String(200), nullable=False)
    product_id: Mapped[str | None] = mapped_column(String(200))
    sku: Mapped[str | None] = mapped_column(String(200))
    product_name: Mapped[str] = mapped_column(String(1000), nullable=False)
    variation: Mapped[str | None] = mapped_column(String(500))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    original_price: Mapped[float | None] = mapped_column(Float)
    selling_price: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    seller_discount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    platform_discount: Mapped[float] = mapped_column(Float, nullable=False, default=0)

    order: Mapped[Order] = relationship(back_populates="items")


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("tenant_id", "shop_id", "sku", name="uq_product_owner_sku"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    shop_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(200), nullable=False)
    product_name: Mapped[str] = mapped_column(String(1000), nullable=False)
    product_id: Mapped[str | None] = mapped_column(String(200))
    margin: Mapped[float | None] = mapped_column(Float)
    inventory: Mapped[int | None] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )


class MarketTrendSnapshot(Base):
    __tablename__ = "market_trend_snapshots"
    __table_args__ = (
        UniqueConstraint("snapshot_id", name="uq_market_snapshot"),
        Index("ix_market_trend_lookup", "platform", "category", "period", "capture_date"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    snapshot_id: Mapped[str] = mapped_column(String(64), nullable=False)
    capture_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    period: Mapped[str] = mapped_column(String(20), nullable=False)
    product_id: Mapped[str | None] = mapped_column(String(200))
    product_name: Mapped[str] = mapped_column(String(1000), nullable=False)
    shop_name: Mapped[str | None] = mapped_column(String(500))
    rank: Mapped[int | None] = mapped_column(Integer)
    price: Mapped[float | None] = mapped_column(Float)
    sales_growth: Mapped[float | None] = mapped_column(Float)
    sales_30d: Mapped[int | None] = mapped_column(Integer)
    rating: Mapped[float | None] = mapped_column(Float)
    source_url: Mapped[str | None] = mapped_column(Text)
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"
    __table_args__ = (Index("ix_recommendation_owner", "tenant_id", "shop_id", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(200), nullable=False)
    shop_id: Mapped[str] = mapped_column(String(200), nullable=False)
    user_id: Mapped[str] = mapped_column(String(200), nullable=False)
    kind: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    request_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    results: Mapped[list["RecommendationResult"]] = relationship(
        back_populates="recommendation", cascade="all, delete-orphan"
    )


class RecommendationResult(Base):
    __tablename__ = "recommendation_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    recommendation_id: Mapped[str] = mapped_column(
        ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tenant_id: Mapped[str] = mapped_column(String(200), nullable=False)
    shop_id: Mapped[str] = mapped_column(String(200), nullable=False)
    result_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    recommendation: Mapped[Recommendation] = relationship(back_populates="results")


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (Index("ix_conversation_owner", "tenant_id", "shop_id", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(200), nullable=False)
    shop_id: Mapped[str] = mapped_column(String(200), nullable=False)
    user_id: Mapped[str] = mapped_column(String(200), nullable=False)
    title: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = (Index("ix_audit_owner_created", "tenant_id", "shop_id", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str | None] = mapped_column(String(200))
    shop_id: Mapped[str | None] = mapped_column(String(200))
    user_id: Mapped[str | None] = mapped_column(String(200))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    outcome: Mapped[str] = mapped_column(String(30), nullable=False)
    resource: Mapped[str | None] = mapped_column(String(100))
    details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
