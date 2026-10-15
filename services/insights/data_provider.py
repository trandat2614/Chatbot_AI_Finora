"""Typed boundary between the insights pipeline and Finora commerce data."""
from __future__ import annotations

from datetime import date
from typing import Protocol

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from src.repositories.interfaces import CommerceRepository
from src.services.metric_service import cancelled_mask


class ProviderModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class OrderRecord(ProviderModel):
    order_id: str
    date: date
    channel: str
    product: str
    quantity: int = Field(ge=0)
    revenue: float = Field(ge=0)
    cost_of_goods: float = Field(default=0, ge=0)
    fees: float = Field(default=0, ge=0)


class ExpenseRecord(ProviderModel):
    date: date
    amount: float = Field(ge=0)
    category: str


class ShopSettings(ProviderModel):
    investment_capital: float | None = Field(default=None, ge=0)
    fixed_costs: float | None = Field(default=None, ge=0)
    break_even_target: float | None = Field(default=None, ge=0)
    rule_thresholds: dict[str, float | int] = Field(default_factory=dict)


class InsightDataProvider(Protocol):
    def get_orders(self, tenant_id: str, start: date, end: date) -> list[OrderRecord]: ...

    def get_expenses(self, tenant_id: str, start: date, end: date) -> list[ExpenseRecord]: ...

    def get_shop_settings(self, tenant_id: str) -> ShopSettings: ...


class DefaultDataProvider:
    """Map the existing dashboard order source to typed insight records.

    The provider is bound to the authenticated shop at construction time. The
    public methods still require ``tenant_id`` so every data access is explicit
    about its tenant boundary.
    """

    def __init__(self, repository: CommerceRepository, shop_id: str) -> None:
        self.repository = repository
        self.shop_id = shop_id

    def _period_frame(self, tenant_id: str, start: date, end: date) -> pd.DataFrame:
        frame = self.repository.load_orders(tenant_id, self.shop_id)
        if frame.empty:
            return frame
        data = frame.copy()
        data["created_at"] = pd.to_datetime(data.get("created_at"), errors="coerce", utc=True)
        data = data.dropna(subset=["created_at", "order_id"])
        day = data["created_at"].dt.date
        data = data.loc[(day >= start) & (day <= end)]
        if data.empty:
            return data
        return data.loc[~cancelled_mask(data)].copy()

    def get_orders(self, tenant_id: str, start: date, end: date) -> list[OrderRecord]:
        data = self._period_frame(tenant_id, start, end)
        if data.empty:
            return []
        numeric = (
            "quantity", "selling_price", "platform_fee", "transaction_fee",
            "service_fee", "shipping_fee", "refund_amount",
        )
        for column in numeric:
            if column not in data:
                data[column] = 0
            data[column] = pd.to_numeric(data[column], errors="coerce").fillna(0).clip(lower=0)
        records: list[OrderRecord] = []
        for row in data.itertuples(index=False):
            fee = sum(
                float(getattr(row, name, 0) or 0)
                for name in ("platform_fee", "transaction_fee", "service_fee", "shipping_fee")
            )
            records.append(
                OrderRecord(
                    order_id=str(row.order_id),
                    date=pd.Timestamp(row.created_at).date(),
                    channel=str(getattr(row, "platform", "unknown")),
                    product=str(getattr(row, "product_name", "Không xác định")),
                    quantity=int(row.quantity),
                    revenue=float(row.selling_price) * int(row.quantity),
                    fees=fee,
                )
            )
        return records

    def get_expenses(self, tenant_id: str, start: date, end: date) -> list[ExpenseRecord]:
        data = self._period_frame(tenant_id, start, end)
        if data.empty:
            return []
        records: list[ExpenseRecord] = []
        mappings = {
            "platform_fee": "platform_fee",
            "transaction_fee": "transaction_fee",
            "service_fee": "service_fee",
            "shipping_fee": "shipping_fee",
            "refund_amount": "refund",
        }
        for row in data.itertuples(index=False):
            record_date = pd.Timestamp(row.created_at).date()
            for column, category in mappings.items():
                amount = max(float(getattr(row, column, 0) or 0), 0)
                if amount:
                    records.append(ExpenseRecord(date=record_date, amount=amount, category=category))
        return records

    def get_shop_settings(self, tenant_id: str) -> ShopSettings:
        # The current production schema has no persisted capital/fixed-cost
        # settings. Integrators can replace this provider without changing the
        # metrics/rules/generator pipeline.
        return ShopSettings()
