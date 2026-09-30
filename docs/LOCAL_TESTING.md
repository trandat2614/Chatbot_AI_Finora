# Kiểm thử Finora AI Server trên máy local

## 1. Chuẩn bị

Yêu cầu Python 3.11/3.12. Docker Desktop chỉ cần cho bài test PostgreSQL/container. Chat/RAG thật cần API key của Gemini hoặc FPT; unit/integration tests không gọi provider ngoài.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Local tối thiểu trong `.env`:

```dotenv
ENVIRONMENT=development
AUTH_REQUIRED=true
WEB_TOKEN_SECRET=local-signing-secret-at-least-32-characters
WEB_TOKEN_ISSUER=finora-web
WEB_TOKEN_AUDIENCE=finora-ai
FINORA_SERVICE_KEY=local-service-secret-at-least-32-characters
PII_HASH_SECRET=local-pii-hash-secret-at-least-32-characters
DATABASE_URL=sqlite:///data/finora.db
AUTO_CREATE_SCHEMA=true
ENABLE_LEGACY_API_KEY=false
ENABLE_DEMO=true
ENABLE_API_DOCS=true
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

Thêm `GEMINI_API_KEY` hoặc `FPT_API_KEY` nếu test chat/RAG thật. Không commit `.env`.

## 2. Migration và test tự động

```powershell
python -m alembic upgrade head
python -m pytest -q
python -m compileall app.py server.py config core rag services tools forecasting src
```

Các test bao phủ signed token, token hết hạn/sai audience, service key, tenant/shop isolation, adapters Shopee/TikTok/Lazada, multi-item order không nhân phí, PII/upload, prompt injection, RAG metadata filter, strict OpenAPI và FastAPI end-to-end.

## 3. Chạy server

```powershell
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

Trong terminal khác:

```powershell
$baseUrl = "http://127.0.0.1:8000"
Invoke-RestMethod "$baseUrl/health"
```

Swagger chỉ có khi `ENABLE_API_DOCS=true`: <http://127.0.0.1:8000/docs>.

## 4. Tạo token test local

Không đặt token thật vào shell history trên server production. Đoạn này chỉ dành cho local:

```powershell
$env:LOCAL_WEB_TOKEN_SECRET = "local-signing-secret-at-least-32-characters"
$token = python -c "import os,jwt; from datetime import datetime,timedelta,timezone; print(jwt.encode({'user_id':'usr-local','tenant_id':'tenant-local','shop_id':'shop-local','role':'owner','iss':'finora-web','aud':'finora-ai','exp':datetime.now(timezone.utc)+timedelta(minutes=5)}, os.environ['LOCAL_WEB_TOKEN_SECRET'], algorithm='HS256'))"
$headers = @{
  Authorization = "Bearer $token"
  "X-Finora-Service-Key" = "local-service-secret-at-least-32-characters"
}
```

Thiếu token, service key sai hoặc audience sai phải nhận `401` với error envelope và `request_id`.

## 5. Import và analytics

Tạo file `tmp/orders-local.csv` không chứa PII:

```csv
Mã đơn hàng,Mã sản phẩm trong đơn,SKU phân loại hàng,Tên sản phẩm,Ngày đặt hàng,Trạng Thái Đơn Hàng,Số lượng,Giá bán,Phí sàn
ORDER-001,ITEM-001,SKU-001,Áo thun cotton,2026-09-01,Hoàn thành,2,150000,5000
```

Upload:

```powershell
curl.exe -X POST "$baseUrl/api/v1/data/import" `
  -H "Authorization: Bearer $token" `
  -H "X-Finora-Service-Key: local-service-secret-at-least-32-characters" `
  -F "file=@tmp/orders-local.csv"
```

Sau đó kiểm tra:

```powershell
Invoke-RestMethod "$baseUrl/api/v1/business/overview" -Headers $headers
Invoke-RestMethod "$baseUrl/api/v1/business/health" -Headers $headers
Invoke-RestMethod "$baseUrl/api/v1/business/revenue-leakage" -Headers $headers
Invoke-RestMethod "$baseUrl/api/v1/products/SKU-001/analysis" -Headers $headers
Invoke-RestMethod "$baseUrl/api/v1/action-plan?category=nam&period=7d" -Headers $headers
```

`shop_id` đến từ JWT, không gửi trong body/query. Khi dữ liệu thiếu, API phải trả `INSUFFICIENT_DATA`, không tự tạo số.

## 6. Chat

Chat cần LLM provider hoạt động:

```powershell
$body = @{
  message = "Tóm tắt sức khỏe kinh doanh hiện tại"
  period = "7d"
  category = "nam"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "$baseUrl/api/v1/chat" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

Không gửi `orderSummary` hoặc PII. AI Server lấy business context từ repository theo `AuthContext`.

## 7. Test tenant/shop isolation thủ công

Tạo hai token cùng signing secret nhưng có `tenant_id`/`shop_id` khác nhau, import dữ liệu bằng token A rồi gọi import status/product bằng token B. Kết quả phải là `404` hoặc không có dữ liệu, không được trả record của A. Không thay `tenant_id` trong body vì API v1 không nhận field này.

## 8. Test với Docker/PostgreSQL

Điền `POSTGRES_PASSWORD` và các production-like secret trong `.env`, rồi:

```powershell
docker compose build
docker compose run --rm api python -m pytest -q
docker compose up -d
docker compose ps
Invoke-RestMethod http://127.0.0.1:8000/health
docker compose logs --tail=200 api
```

Container API tự chạy `alembic upgrade head`. Không dùng `docker compose down -v` trong quy trình bình thường vì lệnh đó xóa PostgreSQL và Chroma volumes.

## 9. Test Node backend local

Trong `.env` của `Finora/server/`, không phải Vite client:

```dotenv
AI_SERVER_URL=http://127.0.0.1:8000
AI_SERVICE_KEY=local-service-secret-at-least-32-characters
AI_TOKEN_SECRET=local-signing-secret-at-least-32-characters
AI_SERVER_TIMEOUT_MS=90000
```

Node phải authorize user/shop, ký JWT 1–5 phút rồi gọi `/api/v1`. Xem code mẫu đầy đủ trong [WEB_INTEGRATION.md](WEB_INTEGRATION.md).

## 10. Checklist local

- Migration chạy trên database sạch.
- Toàn bộ pytest pass.
- `/health` trả `200`.
- Token/service key sai trả `401`; shop trái phép không đọc được dữ liệu.
- File sai extension/MIME, path traversal, formula injection hoặc quá lớn bị từ chối/làm sạch.
- Multi-item order không nhân order-level fee.
- Chat không gửi raw PII, order rows hoặc tài chính tự tính sang LLM.
- Browser không chứa service/signing secret.
- `.env`, local DB, raw uploads, audit logs và vector DB không được commit.

Nếu `.venv` báo `No Python at ...`, môi trường đã trỏ tới interpreter cũ. Đổi tên `.venv`, tạo lại bằng Python hiện hành và cài lại `requirements.txt`; chỉ xóa bản cũ sau khi test pass.
