"""FastAPI end-to-end tests for the production integration contract."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

from config.settings import settings
from src.api.app import create_app
from src.db.session import Database, reset_database


def _token(*, audience: str = "finora-ai") -> str:
    return jwt.encode(
        {
            "user_id": "usr-a",
            "tenant_id": "tenant-a",
            "shop_id": "shop-a",
            "role": "owner",
            "iss": "finora-web",
            "aud": audience,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=2),
        },
        settings.WEB_TOKEN_SECRET,
        algorithm="HS256",
    )


@pytest.fixture
def api_client(tmp_path, monkeypatch):
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
    database = Database(f"sqlite:///{tmp_path / 'api.db'}")
    reset_database(database)
    monkeypatch.setattr("src.api.app.vector_store_exists", lambda: False)
    app = create_app()
    with TestClient(app) as client:
        yield client
    reset_database(None)


def _headers(token: str | None = None) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token or _token()}",
        "X-Finora-Service-Key": "s" * 48,
    }


def test_v1_import_status_and_overview_end_to_end(api_client: TestClient) -> None:
    csv = (
        "Mã đơn hàng,Mã sản phẩm trong đơn,SKU phân loại hàng,Tên sản phẩm,"
        "Ngày đặt hàng,Trạng Thái Đơn Hàng,Số lượng,Giá bán,Phí sàn\n"
        "ORDER-1,ITEM-1,SKU-1,Áo cotton,2026-09-01,Hoàn thành,1,100000,5000\n"
    ).encode()
    response = api_client.post(
        "/api/v1/data/import",
        headers=_headers(),
        files={"file": ("orders.csv", csv, "text/csv")},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["status"] == "COMPLETED"
    assert payload["meta"]["request_id"].startswith("req_")

    import_id = payload["data"]["import_id"]
    status_response = api_client.get(
        f"/api/v1/data/imports/{import_id}", headers=_headers()
    )
    assert status_response.status_code == 200
    assert status_response.json()["data"]["accepted_rows"] == 1

    overview = api_client.get("/api/v1/business/overview", headers=_headers())
    assert overview.status_code == 200
    assert overview.json()["data"]["metrics"]["order_count"] == 1


def test_v1_rejects_invalid_audience_with_standard_error(api_client: TestClient) -> None:
    response = api_client.get(
        "/api/v1/business/overview",
        headers=_headers(_token(audience="wrong")),
    )
    assert response.status_code == 401
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "INVALID_AUDIENCE"
    assert response.json()["meta"]["request_id"].startswith("req_")


def test_v1_rejects_oversized_request_before_processing(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/v1/chat",
        headers={**_headers(), "Content-Length": str(settings.MAX_REQUEST_BYTES + 1)},
        content=b"{}",
    )
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "REQUEST_TOO_LARGE"


def test_openapi_v1_has_strict_named_response_contracts(api_client: TestClient) -> None:
    schema = api_client.get("/openapi.json").json()
    required = {
        "/api/v1/data/import",
        "/api/v1/data/imports/{import_id}",
        "/api/v1/business/overview",
        "/api/v1/business/health",
        "/api/v1/business/revenue-leakage",
        "/api/v1/products",
        "/api/v1/products/{sku}",
        "/api/v1/products/{sku}/analysis",
        "/api/v1/market/trends",
        "/api/v1/opportunities",
        "/api/v1/action-plan",
        "/api/v1/chat",
        "/api/v1/sales-plan",
        "/api/v1/communication-plan",
    }
    assert required.issubset(schema["paths"])
    for path in required:
        operation = next(
            value for method, value in schema["paths"][path].items()
            if method in {"get", "post"}
        )
        success_schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
        assert "$ref" in success_schema
