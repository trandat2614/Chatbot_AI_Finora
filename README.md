# Finora AI Business Advisor

Finora AI Business Advisor là backend FastAPI độc lập cho phân tích thương mại điện tử, RAG và tư vấn kinh doanh. Trong production, trình duyệt chỉ gọi Finora Node.js backend; Node backend gọi AI Server qua HTTPS bằng JWT ngắn hạn và service key.

```text
Browser -> Finora Vite -> Finora Node.js -> HTTPS -> Finora AI Server
                                                   -> PostgreSQL / Chroma / LLM API
```

## Phạm vi

- Chuẩn hóa file Shopee, TikTok Shop và Lazada qua marketplace adapters.
- Lưu `Order` và `OrderItem` riêng trong PostgreSQL; phí cấp đơn chỉ được tính một lần.
- Deterministic analytics: overview, Business Health, Revenue Leakage, Product Doctor, Market Trend, Opportunity Matching và Action Plan.
- Chat orchestration và các tool chỉ đọc/khuyến nghị; không tự đổi giá, ngân sách quảng cáo, voucher hoặc listing.
- RAG public/private với metadata filter tenant/shop ngay trong vector query.
- Loại PII trước LLM/embedding/log; kiểm tra upload, rate limit và audit log có cấu trúc.

Website chính tiếp tục sở hữu login, user/shop, subscription, payment, upload UI, dashboard và chat UI. Repository này không cung cấp các chức năng đó.

## Chạy local nhanh

Yêu cầu Python 3.11+.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python -m alembic upgrade head
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

Local mặc định có thể dùng SQLite. Staging/production bắt buộc dùng PostgreSQL. Điền tối thiểu `WEB_TOKEN_SECRET`, `FINORA_SERVICE_KEY`, `PII_HASH_SECRET` và key của LLM provider trong `.env`. Không commit `.env`.

- Health: <http://127.0.0.1:8000/health>
- Swagger local: <http://127.0.0.1:8000/docs>
- API production contract: `/api/v1/*`
- Demo: chỉ bật cho development bằng `ENABLE_DEMO=true`

## Authentication

Mọi endpoint tích hợp `/api/v1` yêu cầu đồng thời:

```http
Authorization: Bearer <short-lived-JWT>
X-Finora-Service-Key: <server-to-server-secret>
```

JWT phải có `user_id`, `tenant_id`, `shop_id`, `role`, `iss`, `aud`, `exp`. AI Server xác minh chữ ký, hạn dùng, issuer, audience và service key rồi tạo `AuthContext`. Tenant/shop không được lấy từ JSON body. `X-API-Key` chỉ là compatibility mode cho local/test và bị tắt trong production bằng `ENABLE_LEGACY_API_KEY=false`.

## API v1

| Method | Endpoint | Chức năng |
| --- | --- | --- |
| `POST` | `/api/v1/data/import` | Validate, chuẩn hóa và lưu CSV/XLSX |
| `GET` | `/api/v1/data/imports/{import_id}` | Trạng thái import |
| `GET` | `/api/v1/business/overview` | Tổng quan deterministic |
| `GET` | `/api/v1/business/health` | Health và alerts |
| `GET` | `/api/v1/business/revenue-leakage` | GMV-to-net leakage |
| `GET` | `/api/v1/products` | Danh sách SKU |
| `GET` | `/api/v1/products/{sku}` | Chi tiết SKU |
| `GET` | `/api/v1/products/{sku}/analysis` | Product Doctor |
| `GET` | `/api/v1/market/trends` | Trend snapshots |
| `GET` | `/api/v1/opportunities` | Opportunity matching |
| `GET` | `/api/v1/action-plan` | Action plan khuyến nghị |
| `POST` | `/api/v1/chat` | Chat với context lấy server-side |
| `POST` | `/api/v1/sales-plan` | Sales plan khuyến nghị |
| `POST` | `/api/v1/communication-plan` | Communication plan khuyến nghị |
| `POST` | `/api/v1/knowledge/upload` | Private RAG của shop |

Response thành công và lỗi có envelope ổn định:

```json
{"success":true,"data":{},"meta":{"request_id":"req_xxx"}}
```

```json
{"success":false,"error":{"code":"INSUFFICIENT_DATA","message":"..."},"meta":{"request_id":"req_xxx"}}
```

Các route `/api/*` cũ vẫn là wrapper deprecated trong giai đoạn migration.

## Test

```powershell
python -m pytest -q
python -m compileall app.py server.py config core rag services tools forecasting src
```

## Docker

```bash
docker compose build
docker compose run --rm api python -m pytest -q
docker compose up -d
```

Container chạy non-root và tự thực hiện `alembic upgrade head` trước Uvicorn. Không chạy `docker compose down -v` nếu không chủ đích xóa dữ liệu PostgreSQL/Chroma.

## Tài liệu

- [Kiểm thử local](docs/LOCAL_TESTING.md)
- [Contract cho Finora Node backend](docs/WEB_INTEGRATION.md)
- [Chuẩn bị VPS staging](docs/VPS_DEPLOYMENT.md)
- [Decision Intelligence và security](docs/AI_FEATURES.md)
