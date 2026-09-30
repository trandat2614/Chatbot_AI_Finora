"""Tenant- and shop-isolated storage for normalized commerce data."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd

from config.settings import settings


def _scope_hash(value: str) -> str:
    if not value or len(value) > 200:
        raise ValueError("Scope identifier không hợp lệ.")
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class TenantDataStore:
    """Persist only normalized, PII-free records below a hashed tenant scope."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or settings.get_tenant_data_dir()).resolve()

    def _shop_dir(self, tenant_id: str, shop_id: str) -> Path:
        path = (self.root / _scope_hash(tenant_id) / _scope_hash(shop_id)).resolve()
        if self.root != path and self.root not in path.parents:
            raise ValueError("Tenant storage path không hợp lệ.")
        return path

    def save_orders(self, tenant_id: str, shop_id: str, frame: pd.DataFrame) -> int:
        directory = self._shop_dir(tenant_id, shop_id)
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / "orders.jsonl"
        records = frame.where(pd.notna(frame), None).to_dict(orient="records")
        with NamedTemporaryFile("w", encoding="utf-8", dir=directory, delete=False) as handle:
            temporary = Path(handle.name)
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
        os.replace(temporary, target)
        return len(records)

    def load_orders(self, tenant_id: str, shop_id: str) -> pd.DataFrame:
        target = self._shop_dir(tenant_id, shop_id) / "orders.jsonl"
        if not target.exists():
            return pd.DataFrame()
        records: list[dict] = []
        with target.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    records.append(json.loads(line))
        return pd.DataFrame(records)

    def scope_token(self, tenant_id: str, shop_id: str) -> str:
        return hashlib.sha256(f"{tenant_id}\x00{shop_id}".encode("utf-8")).hexdigest()[:24]

    def tenant_knowledge_dir(self, tenant_id: str, shop_id: str) -> Path:
        path = self._shop_dir(tenant_id, shop_id) / "knowledge"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def tenant_vector_dir(self, tenant_id: str, shop_id: str) -> Path:
        path = self._shop_dir(tenant_id, shop_id) / "vector_db"
        path.mkdir(parents=True, exist_ok=True)
        return path
