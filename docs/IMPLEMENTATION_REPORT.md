# Implementation report — 2026-09-30

## 1. Final architecture

```text
Browser
  -> Finora Vite client
  -> Finora Node.js backend (login, user/shop authorization, JWT signing)
  -> HTTPS + Bearer JWT + X-Finora-Service-Key
  -> Nginx
  -> FastAPI /api/v1
       -> AuthContext + role/shop enforcement
       -> marketplace adapters -> relational repositories -> deterministic analytics
       -> tenant-filtered RAG -> external LLM
  -> PostgreSQL / Chroma
```

`server.py` chỉ bootstrap `create_app()`. Routes nằm trong `src/api/routes`, database trong `src/db`, repository trong `src/repositories`, API contracts trong `src/schemas`, controls trong `src/security` và nghiệp vụ trong `src/services`.

## 2. Project tree chính

```text
finora-ai-business-advisor/
├── src/
│   ├── api/{dependencies,routes}/
│   ├── db/
│   ├── repositories/
│   ├── schemas/
│   ├── security/
│   ├── services/normalization/
│   ├── agent/
│   └── tools/
├── rag/
├── services/
├── migrations/versions/
├── tests/
├── docs/
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
└── server.py
```

## 3. Files created

- Migration: `alembic.ini`, `migrations/env.py`, `migrations/script.py.mako`, `migrations/versions/20260930_0001_initial_schema.py`.
- API: `src/api/app.py`, dependencies và route modules `business`, `chat`, `data`, `knowledge`, `legacy`, `market`, `planning`, `products`, `v1`.
- Persistence: `src/db/*`; `src/repositories/interfaces.py`, `commerce_repository.py`, `trend_repository.py`, `recommendation_repository.py`, `audit_repository.py`.
- Contracts/security: `src/schemas/*`; `src/security/auth.py`, `audit.py`, `privacy.py`, `uploads.py`.
- Services: marketplace adapters dưới `src/services/normalization/`; Decision Intelligence services, `raw_upload_service.py`, `tenant_store.py`, `src/tools/business_tools.py`, `src/agent/intent_router.py`.
- Tests: `test_api_v1.py`, `test_data_normalization.py`, `test_decision_intelligence.py`, `test_marketplace_adapters.py`, `test_repositories.py`, `test_security.py`, `test_web_auth.py`.
- Docs: `docs/AI_FEATURES.md`, `docs/WEB_INTEGRATION.md`, file report này.

## 4. Files modified

`.dockerignore`, `.env.example`, `.gitignore`, `Dockerfile`, `README.md`, `requirements.txt`, `docker-compose.yml`, `deploy/nginx-finora.conf`, `config/settings.py`, `server.py`, `core/llm_client.py`, `services/advisor_service.py`, `rag/document_loader.py`, `rag/rag_service.py`, `rag/retriever.py`, `src/agent/prompt.py`, `src/services/trend_service.py`, `tools/revenue_analysis_tool.py`, `web/index.html`, các docs local/VPS và compatibility tests.

Generated/sensitive artifacts `knowledge/Shopee.xlsx` và `vector_db/chroma.sqlite3` đã được bỏ khỏi Git index trong worktree hiện tại. `data/trends/shopee_trends.sqlite3` đang có thay đổi generated data và phải được review riêng trước commit.

## 5. Database schema

Tables: `shops`, `data_imports`, `orders`, `order_items`, `products`, `market_trend_snapshots`, `recommendations`, `recommendation_results`, `conversations`, `audit_events`.

Order-level money: `order_total`, `platform_fee`, `transaction_fee`, `service_fee`, `shipping_fee`, `refund_amount`. Item-level money: `original_price`, `selling_price`, `seller_discount`, `platform_discount`. Tenant-private tables carry tenant/shop ownership and repository queries use SQLAlchemy bound parameters.

## 6. Migration commands

```bash
alembic upgrade head
alembic current
alembic history
```

Docker runs `alembic upgrade head` before Uvicorn. Initial migration was verified on a clean SQLite database and created all expected tables. PostgreSQL execution remains a staging gate.

## 7. Authentication flow

Node authorizes membership, signs a 1–5 minute JWT containing `user_id`, `tenant_id`, `shop_id`, `role`, `iss`, `aud`, `exp` and optionally `shop_ids`. AI Server verifies `X-Finora-Service-Key`, signature, expiration, issuer, audience and claims, then creates `AuthContext`. Repository scope comes only from that context. Legacy `X-API-Key` is disabled by default and remains a migration wrapper only.

## 8. `/api/v1` contract

- `POST /api/v1/data/import` → `DataImportResponse`.
- `GET /api/v1/data/imports/{import_id}` → `ImportStatusResponse`.
- `GET /api/v1/business/overview` → `BusinessOverviewResponse`.
- `GET /api/v1/business/health` → `BusinessHealthResponse`.
- `GET /api/v1/business/revenue-leakage` → `RevenueLeakageResponse`.
- `GET /api/v1/products` → `ProductListResponse`.
- `GET /api/v1/products/{sku}` → `ProductResponse`.
- `GET /api/v1/products/{sku}/analysis` → `ProductAnalysisResponse`.
- `GET /api/v1/market/trends` → `MarketTrendResponse`.
- `GET /api/v1/opportunities` → `OpportunityResponse`.
- `GET /api/v1/action-plan` → `ActionPlanResponse`.
- `POST /api/v1/chat` (`ChatRequest`) → `ChatResponse`.
- `POST /api/v1/sales-plan` (`PlannerRequest`) → `SalesPlanResponse`.
- `POST /api/v1/communication-plan` (`PlannerRequest`) → `CommunicationPlanResponse`.
- `POST /api/v1/knowledge/upload` → `KnowledgeUploadResponse`.

All success/error responses carry `request_id`. Old `/api/*` endpoints are marked deprecated.

## 9. Upload flow

Node forwards multipart file → auth → role/shop context → size/name/extension/MIME/signature/archive validation → platform detection → PII/formula/prompt-injection protection → adapter → normalized schema → PostgreSQL → deterministic metrics/audit. Marketplace imports support CSV/XLSX; legacy binary XLS is rejected. Raw files use generated temporary names and are deleted after processing; crash leftovers follow `RAW_UPLOAD_RETENTION_HOURS`.

## 10. Chat/tool flow

`ChatRequest` contains message/history plus safe filters only. The server retrieves tenant/shop data itself. Available bound tools: `get_business_health`, `analyze_product`, `analyze_revenue_leakage`, `get_market_trends`, `find_product_opportunities`, `generate_action_plan`, `generate_sales_plan`, `generate_communication_plan`. They are read-only/recommendation-only and cannot accept arbitrary tenant identifiers from the LLM.

## 11. Node.js integration

See `docs/WEB_INTEGRATION.md` for JWT signing, shared HTTP client, import/chat examples, timeout and error handling. Secrets stay in `Finora/server/`, never `VITE_*`.

## 12. New environment variables

`DATABASE_URL`, `AUTO_CREATE_SCHEMA`, `POSTGRES_PASSWORD`, `WEB_TOKEN_SECRET`, `WEB_TOKEN_ISSUER`, `WEB_TOKEN_AUDIENCE`, `WEB_TOKEN_ALGORITHM`, `WEB_TOKEN_LEEWAY_SECONDS`, `FINORA_SERVICE_KEY`, `ENABLE_LEGACY_API_KEY`, `DEFAULT_SHOP_ID`, `PII_HASH_SECRET`, `RAW_UPLOAD_RETENTION_HOURS`, `RAW_UPLOAD_DIR`, `TENANT_DATA_DIR`, `AUDIT_LOG_FILE`, `TREND_IMPORT_DATE`.

## 13. Dependencies and test result

New dependencies: SQLAlchemy, Alembic, psycopg 3 binary and PyJWT. Result: **90 passed, 2 warnings**; `compileall` and `git diff --check` pass. Alembic was tested on clean SQLite. Docker could not be built because Docker CLI is unavailable on this workstation.

## 14. Backward compatibility risks

- Legacy `/api/*` response shapes remain but now read from relational storage, not old JSONL.
- Existing JSONL data has no automated one-time migration yet.
- Old public/private Chroma indexes without new metadata must be re-ingested.
- Chat v1 rejects client `orderSummary`; Node/UI must switch to the small request contract.
- Binary `.xls` marketplace imports are now rejected; export CSV/XLSX instead.
- Deprecated API-key auth must be explicitly enabled only during migration.

## 15. Remaining blockers before VPS staging

- Run migrations/tests against PostgreSQL 16 and build/run Docker Compose on a Docker-capable host.
- Integrate the separate Finora Node repository and run end-to-end membership/JWT tests.
- Add sanitized real marketplace export fixtures; current adapter fixtures are representative inline samples.
- Create/execute a reviewed legacy JSONL-to-PostgreSQL migration if existing tenant data must be preserved.
- Re-ingest RAG and verify private metadata using the staging Chroma version.
- Validate backup/restore, secret rotation, TLS, monitoring, disk retention and load limits.

Technical debt: in-memory application rate limiter, HS256 shared signing secret, synchronous imports without idempotency/background queue, float money fields instead of fixed-point numeric, and two third-party deprecation/date-parsing warnings.

## 16. Local and Docker commands

```bash
alembic upgrade head
uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

```bash
docker compose build
docker compose run --rm api python -m pytest -q
docker compose up -d
```

## 17. Staging classification

**PARTIALLY_READY**. P0/P1 application architecture and automated tests are implemented, but PostgreSQL/Docker execution, real Node integration, legacy data migration and operational staging controls are not yet verified. This is not a production-readiness claim.
