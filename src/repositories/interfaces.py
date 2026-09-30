"""Repository protocols consumed by business services."""
from __future__ import annotations

from typing import Protocol

import pandas as pd

from src.security.auth import AuthContext


class OrderRepository(Protocol):
    def load_orders(self, tenant_id: str, shop_id: str) -> pd.DataFrame: ...

    def replace_orders(
        self, context: AuthContext, frame: pd.DataFrame, import_id: str | None = None
    ) -> object: ...


class ImportRepository(Protocol):
    def create_import(
        self,
        context: AuthContext,
        filename: str,
        filename_hash: str,
        fingerprint: str,
        total_rows: int,
    ) -> tuple[str, bool]: ...

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
    ) -> None: ...

    def fail_import(self, context: AuthContext, import_id: str, error_code: str) -> None: ...

    def get_import(self, context: AuthContext, import_id: str) -> dict | None: ...


class ProductRepository(Protocol):
    def list_products(self, tenant_id: str, shop_id: str) -> list[dict]: ...

    def get_product(self, tenant_id: str, shop_id: str, sku: str) -> dict | None: ...


class TrendRepository(Protocol):
    def upsert_snapshots(self, snapshots: list[dict]) -> int: ...

    def list_snapshots(self, category: str, period: str, limit: int = 100) -> list[dict]: ...


class RecommendationRepository(Protocol):
    def save(
        self, context: AuthContext, kind: str, request_data: dict, result_data: dict
    ) -> str: ...


class AuditRepository(Protocol):
    def append(
        self,
        context: AuthContext | None,
        action: str,
        outcome: str,
        resource: str | None,
        details: dict,
    ) -> str: ...
