"""API cache, authorization, status and multi-tenant isolation tests."""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import jwt
import pytest
from fastapi import Depends
from fastapi.testclient import TestClient

from config.settings import settings
from services.insights.data_provider import ExpenseRecord, OrderRecord, ShopSettings
from src.api.app import create_app
from src.api.dependencies.context import require_auth_context
from src.api.dependencies.context import auth_rate_limiter, rate_limiter
from src.api.dependencies.services import insight_data_provider
from src.db.session import Database, reset_database
from src.security.auth import AuthContext


class TenantProvider:
    def __init__(self, orders: list[OrderRecord]) -> None:
        self.orders = orders

    def get_orders(self, tenant_id: str, start: date, end: date) -> list[OrderRecord]:
        return [item for item in self.orders if start <= item.date <= end]

    def get_expenses(self, tenant_id: str, start: date, end: date) -> list[ExpenseRecord]:
        return []

    def get_shop_settings(self, tenant_id: str) -> ShopSettings:
        return ShopSettings(rule_thresholds={"min_orders": 5})


class CountingLLM:
    def __init__(self) -> None:
        self.calls = 0

    def generate_response(self, user_message: str, **kwargs) -> str:
        self.calls += 1
        return (
            '{"items":[{"type":"revenue_growth","title":"Doanh thu tăng tốt",'
            '"summary":"Doanh thu kỳ này tăng so với kỳ trước.",'
            '"recommendation":"Duy trì nguồn tăng trưởng hiệu quả nhất."}]}'
        )


def _orders(prefix: str, *, current: bool = True) -> list[OrderRecord]:
    today = date.today()
    current_day = today - timedelta(days=1)
    previous_day = today - timedelta(days=31)
    records: list[OrderRecord] = []
    if current:
        records.extend(
            OrderRecord(
                order_id=f"{prefix}-current-{index}",
                date=current_day,
                channel=f"{prefix}-channel",
                product=f"{prefix}-product",
                quantity=1,
                revenue=200,
            )
            for index in range(6)
        )
        records.extend(
            OrderRecord(
                order_id=f"{prefix}-previous-{index}",
                date=previous_day,
                channel=f"{prefix}-channel",
                product=f"{prefix}-product",
                quantity=1,
                revenue=100,
            )
            for index in range(6)
        )
    return records


def _token(tenant_id: str, shop_id: str) -> str:
    return jwt.encode(
        {
            "user_id": f"user-{tenant_id}",
            "tenant_id": tenant_id,
            "shop_id": shop_id,
            "role": "owner",
            "iss": "finora-web",
            "aud": "finora-ai",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        settings.WEB_TOKEN_SECRET,
        algorithm="HS256",
    )


def _headers(tenant_id: str, shop_id: str, **extra: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {_token(tenant_id, shop_id)}",
        "X-Finora-Service-Key": "s" * 48,
        **extra,
    }


@pytest.fixture
def insights_client(tmp_path, monkeypatch):
    auth_rate_limiter._requests.clear()
    rate_limiter._requests.clear()
    settings_class = type(settings)
    monkeypatch.setattr(settings_class, "WEB_TOKEN_SECRET", "t" * 48)
    monkeypatch.setattr(settings_class, "FINORA_SERVICE_KEY", "s" * 48)
    monkeypatch.setattr(settings_class, "WEB_TOKEN_ISSUER", "finora-web")
    monkeypatch.setattr(settings_class, "WEB_TOKEN_AUDIENCE", "finora-ai")
    monkeypatch.setattr(settings_class, "WEB_TOKEN_ALGORITHM", "HS256")
    monkeypatch.setattr(settings_class, "WEB_TOKEN_LEEWAY_SECONDS", 0)
    monkeypatch.setattr(settings_class, "ENABLE_LEGACY_API_KEY", False)
    monkeypatch.setattr(settings_class, "AUTO_CREATE_SCHEMA", True)
    monkeypatch.setattr(settings_class, "AUTH_REQUIRED", True)
    monkeypatch.setattr(settings_class, "ENVIRONMENT", "testing")
    monkeypatch.setattr(settings_class, "AUDIT_LOG_FILE", str(tmp_path / "audit.log"))
    database = Database(f"sqlite:///{tmp_path / 'insights.db'}")
    reset_database(database)
    monkeypatch.setattr("src.api.app.vector_store_exists", lambda: False)
    providers = {
        "tenant-a": TenantProvider(_orders("tenant-a")),
        "tenant-b": TenantProvider(_orders("tenant-b")),
        "tenant-empty": TenantProvider([]),
    }

    def provider_override(
        context: AuthContext = Depends(require_auth_context),
    ) -> TenantProvider:
        return providers[context.tenant_id]

    app = create_app()
    app.dependency_overrides[insight_data_provider] = provider_override
    llm = CountingLLM()
    with TestClient(app) as client:
        app.state.llm_client = llm
        yield client, llm
    reset_database(None)


def test_fixture_defines_three_distinct_shops() -> None:
    path = Path(__file__).parent / "fixtures" / "insight_shops.json"
    fixture = json.loads(path.read_text(encoding="utf-8"))
    assert set(fixture) == {"full_shop", "low_data_shop", "empty_shop"}
    assert fixture["full_shop"]["order_count"] == 39
    assert fixture["empty_shop"]["order_count"] == 0


def test_auth_cache_force_and_status_patch(insights_client) -> None:
    client, llm = insights_client
    headers = _headers("tenant-a", "shop-a")
    first = client.post(
        "/api/insights/generate",
        headers=headers,
        json={"period": "30d", "force": False},
    )
    assert first.status_code == 200, first.text
    assert first.json()["items"]
    calls_after_first = llm.calls

    cached = client.post(
        "/api/insights/generate",
        headers=headers,
        json={"period": "30d", "force": False},
    )
    assert cached.status_code == 200
    assert llm.calls == calls_after_first

    forced = client.post(
        "/api/insights/generate",
        headers=headers,
        json={"period": "30d", "force": True},
    )
    assert forced.status_code == 200
    assert llm.calls == calls_after_first + 1

    insight_id = forced.json()["items"][0]["id"]
    patched = client.patch(
        f"/api/insights/{insight_id}", headers=headers, json={"status": "read"}
    )
    assert patched.status_code == 200
    new_items = client.get("/api/insights?status=new", headers=headers)
    assert new_items.status_code == 200
    assert insight_id not in {item["id"] for item in new_items.json()["items"]}
    assert new_items.json()["empty_reason"] is None


def test_multi_tenant_isolation_and_client_tenant_fields_rejected(insights_client) -> None:
    client, _ = insights_client
    response_a = client.post(
        "/api/insights/generate",
        headers=_headers("tenant-a", "shop-a", **{"X-Tenant-ID": "tenant-b"}),
        json={"period": "30d"},
    )
    response_b = client.post(
        "/api/insights/generate",
        headers=_headers("tenant-b", "shop-b"),
        json={"period": "30d"},
    )
    assert response_a.status_code == response_b.status_code == 200
    id_a = response_a.json()["items"][0]["id"]
    assert id_a != response_b.json()["items"][0]["id"]

    own_list = client.get("/api/insights", headers=_headers("tenant-b", "shop-b"))
    assert own_list.status_code == 200
    assert id_a not in {item["id"] for item in own_list.json()["items"]}
    cross_patch = client.patch(
        f"/api/insights/{id_a}",
        headers=_headers("tenant-b", "shop-b"),
        json={"status": "dismissed"},
    )
    assert cross_patch.status_code == 404

    injected = client.post(
        "/api/insights/generate?tenant_id=tenant-b",
        headers=_headers("tenant-a", "shop-a"),
        json={"period": "30d", "tenant_id": "tenant-b"},
    )
    assert injected.status_code == 422


def test_empty_shop_returns_explicit_empty_reason(insights_client) -> None:
    client, llm = insights_client
    before = llm.calls
    response = client.post(
        "/api/insights/generate",
        headers=_headers("tenant-empty", "shop-empty"),
        json={"period": "30d"},
    )
    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["empty_reason"] == "not_enough_data"
    assert llm.calls == before


def test_insights_require_authentication(insights_client) -> None:
    client, _ = insights_client
    response = client.get("/api/insights")
    assert response.status_code == 401
