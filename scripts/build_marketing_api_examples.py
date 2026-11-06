"""Export schema-checked offline HTTP examples; no real shop or provider calls."""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.schemas.marketing import (AdaptRequest, CalendarRequest, GenerationRequest,
    MarketingResponse, RewriteRequest, StrategyRequest)
from src.security.auth import AuthContext
from src.services.marketing.service import MarketingService
from tests.marketing_fixtures import FakeLLM, request_body

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "docs" / "examples" / "marketing"
CONTEXT = AuthContext(user_id="example-user", tenant_id="example-tenant", shop_id="example-shop", role="owner")


async def build():
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    service = MarketingService(FakeLLM())
    cases = []
    for name, body, cls, method in (
        ("generate", {**request_body(), "channels": ["facebook"]}, GenerationRequest, "generate"),
        ("video_generate", request_body(videos=True), GenerationRequest, "generate"),
        ("calendar", {**request_body(videos=True), "start_date": "2026-11-09", "generate_content": False}, CalendarRequest, "calendar"),
        ("strategy", {"shop_context": "Shop nhỏ, có một người chuẩn bị nội dung.", "objective": "introduce_product",
                      "products": [request_body()["product"]]}, StrategyRequest, "strategy"),
    ):
        request = cls.model_validate(body)
        result = await getattr(service, method)(request, CONTEXT, f"req_example_{name}")
        cases.append((name, body, result))
    video = next(result for name, _, result in cases if name == "video_generate").items[0]
    source = dict(client_reference=video.client_reference, version_reference="example-be-version-1",
        sku=video.sku, target=video.target.model_dump(), content=video.content.model_dump(mode="json"),
        product_snapshot=request_body()["product"])
    rewrite_body = {**request_body(videos=True), "targets": [source["target"]], "variants": 1,
                    "source": source, "instructions": "Chuyển sang chỉ có chữ, không lời thoại.", "production_mode": "text_only"}
    result = await service.generate(RewriteRequest.model_validate(rewrite_body), CONTEXT, "req_example_rewrite", operation="rewrite")
    cases.append(("rewrite", rewrite_body, result))
    adapt_body = {**request_body(videos=True), "targets": request_body(videos=True)["targets"][1:], "source": source,
                  "instructions": "Điều chỉnh cảnh và CTA cho placement đích."}
    result = await service.generate(AdaptRequest.model_validate(adapt_body), CONTEXT, "req_example_adapt", operation="adapt")
    cases.append(("adapt", adapt_body, result))
    for name, body, result in cases:
        if result.status != "success":
            raise RuntimeError(f"Invalid example {name}: {result.model_dump()}")
        result.metadata.duration_ms = 0  # Static fixture, not a measured provider latency.
        MarketingResponse.model_validate(result.model_dump(mode="json"))
        for suffix, data in (("request", body), ("response", result.model_dump(mode="json"))):
            (DIRECTORY / f"{name}.{suffix}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    http = """# Offline fixtures; replace variables with credentials issued by your BE.
@baseUrl = http://127.0.0.1:8000
@token = REPLACE_WITH_SHORT_LIVED_JWT
@serviceKey = REPLACE_WITH_SERVER_SERVICE_KEY

### Supported targets and product choices
GET {{baseUrl}}/api/v1/marketing/capabilities
Authorization: Bearer {{token}}
X-Finora-Service-Key: {{serviceKey}}

"""
    routes = {"generate": "generate", "video_generate": "video-scripts/generate", "rewrite": "rewrite",
              "adapt": "video-scripts/adapt", "calendar": "calendar", "strategy": "strategy"}
    for name, body, _ in cases:
        http += f"### {name}\nPOST {{{{baseUrl}}}}/api/v1/marketing/{routes[name]}\nAuthorization: Bearer {{{{token}}}}\nX-Finora-Service-Key: {{{{serviceKey}}}}\nIdempotency-Key: example-{name}-REPLACE-ON-NEW-ACTION\nContent-Type: application/json\n\n{json.dumps(body, ensure_ascii=False, indent=2)}\n\n"
    (ROOT / "docs" / "marketing_api.http").write_text(http, encoding="utf-8")
    print("Exported 6 request/response pairs and HTTP collection; all responses validated offline.")


if __name__ == "__main__":
    asyncio.run(build())
