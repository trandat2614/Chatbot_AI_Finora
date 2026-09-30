# Chuẩn bị Finora AI Server trên VPS

Tài liệu này là runbook staging. Repository không tự triển khai và không thực hiện thay đổi production.

## Kiến trúc mạng

```text
Internet -> Nginx :443 -> FastAPI 127.0.0.1:8000
                              -> PostgreSQL :5432 (Docker internal only)
                              -> Chroma volume
                              -> external LLM/embedding API
```

Chỉ mở public `80` và `443`. Không publish PostgreSQL. VPS mục tiêu 2 CPU, 4 GB RAM, 35 GB NVMe; không cài local LLM, Kubernetes, Kafka hoặc Elasticsearch.

## 1. Chuẩn bị host

Ví dụ Ubuntu LTS:

```bash
sudo apt update
sudo apt install -y ca-certificates curl git nginx certbot python3-certbot-nginx
```

Cài Docker Engine/Compose theo tài liệu chính thức của Docker cho phiên bản Ubuntu đang dùng. Tạo user deploy không phải root và chỉ cấp quyền cần thiết.

## 2. Cấu hình production

Clone repository vào thư mục ứng dụng, sao chép `.env.example` thành `.env`, rồi thay toàn bộ placeholder. Cấu hình tối thiểu:

```dotenv
ENVIRONMENT=production
AUTH_REQUIRED=true
ENABLE_LEGACY_API_KEY=false
ENABLE_DEMO=false
ENABLE_API_DOCS=false

WEB_TOKEN_SECRET=<random-at-least-32-characters>
WEB_TOKEN_ISSUER=finora-web
WEB_TOKEN_AUDIENCE=finora-ai
WEB_TOKEN_ALGORITHM=HS256
FINORA_SERVICE_KEY=<different-random-at-least-32-characters>
PII_HASH_SECRET=<different-random-at-least-32-characters>

POSTGRES_PASSWORD=<random-database-password>
DATABASE_URL=postgresql+psycopg://finora:<same-password>@db:5432/finora
AUTO_CREATE_SCHEMA=false

MAX_UPLOAD_BYTES=10485760
RAW_UPLOAD_RETENTION_HOURS=24
RAW_UPLOAD_DIR=data/uploads
AUDIT_LOG_FILE=logs/audit.log
ALLOWED_ORIGINS=https://finora.com.vn

GEMINI_API_KEY=<provider-key>
```

Docker Compose tự override `DATABASE_URL` sang service `db`. Không để placeholder `AI_SERVER_API_KEY=change_me_in_production`; có thể để rỗng vì legacy auth đã tắt. Không đặt secret trong Vite variables, Git hoặc shell history.

## 3. Build, migration và test staging

```bash
docker compose build
docker compose run --rm api python -m pytest -q
docker compose run --rm api alembic upgrade head
docker compose up -d
docker compose ps
curl --fail http://127.0.0.1:8000/health
```

API container cũng chạy `alembic upgrade head` trước Uvicorn. Chạy migration thủ công trước giúp phát hiện lỗi sớm. Trước mọi migration production, backup PostgreSQL và thử restore trên staging.

Kiểm tra bảng:

```bash
docker compose exec db psql -U finora -d finora -c '\dt'
docker compose exec api alembic current
```

## 4. Public RAG

Chỉ ingest tài liệu public đã rà soát:

```bash
docker compose run --rm api python ingest.py
```

Marketplace spreadsheets/order rows không được ingest vào Chroma. Private knowledge phải đi qua endpoint authenticated để có metadata `tenant_id`, `shop_id`, `visibility`, `document_id`. Sau khi nâng cấp metadata schema, cần re-ingest public knowledge và không tái sử dụng index thiếu metadata.

## 5. Nginx và HTTPS

Thay `server_name` trong `deploy/nginx-finora.conf` bằng `ai.finora.com.vn`, cài config và xin certificate:

```bash
sudo cp deploy/nginx-finora.conf /etc/nginx/sites-available/finora-ai
sudo ln -s /etc/nginx/sites-available/finora-ai /etc/nginx/sites-enabled/finora-ai
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d ai.finora.com.vn
```

Sau HTTPS, kiểm tra:

```bash
curl --fail https://ai.finora.com.vn/health
```

Nginx phải chuyển tiếp `Authorization` và `X-Finora-Service-Key`, giới hạn body tương thích `MAX_UPLOAD_BYTES`, rate limit và timeout. Không log các header xác thực.

## 6. Smoke test authenticated từ Node host

Tạo token ngắn hạn từ Finora Node backend bằng identity đã authorize, sau đó gọi:

```bash
curl --fail --show-error \
  -H "Authorization: Bearer $AI_TEST_TOKEN" \
  -H "X-Finora-Service-Key: $AI_SERVICE_KEY" \
  https://ai.finora.com.vn/api/v1/business/overview
```

Trên server thật, đọc secret vào biến tạm với history tắt; không gõ secret trực tiếp vào command lưu history. Token tenant A không được thấy import/product của tenant B.

## 7. Kết nối Finora web

Trong environment của `Finora/server/`:

```dotenv
AI_SERVER_URL=https://ai.finora.com.vn
AI_SERVICE_KEY=<same-as-FINORA_SERVICE_KEY>
AI_TOKEN_SECRET=<same-as-WEB_TOKEN_SECRET>
AI_TOKEN_ISSUER=finora-web
AI_TOKEN_AUDIENCE=finora-ai
AI_SERVER_TIMEOUT_MS=90000
```

Không expose các biến này qua `VITE_*`. Xem [WEB_INTEGRATION.md](WEB_INTEGRATION.md) để ký token và gọi `/api/v1`.

## 8. Dữ liệu, retention và backup

- Backup PostgreSQL có mã hóa và kiểm tra restore định kỳ.
- Backup Chroma/public knowledge theo chính sách; private vectors vẫn phải tenant-filtered khi restore.
- Rotate audit log; log chỉ chứa identifiers đã hash và metadata an toàn.
- Raw upload chỉ là dữ liệu tạm, được xóa sau xử lý; cleanup xóa file tồn dư quá `RAW_UPLOAD_RETENTION_HOURS`.
- Theo dõi dung lượng volume vì VPS chỉ có 35 GB.
- Không dùng `docker compose down -v` trừ khi chủ đích xóa toàn bộ dữ liệu và đã backup.

## 9. Monitoring tối thiểu

Theo dõi `/health`, restart count, CPU/RAM/disk, PostgreSQL connections/storage, lỗi `401/403/413/422/429/5xx`, latency LLM và audit events. Không log request body, Authorization, service key, API key, PII hoặc file upload.

## 10. Rollback

1. Backup database trước release.
2. Gắn tag image/commit đang ổn định.
3. Migration schema hiện tại chỉ có initial upgrade; tạo migration forward-fix cho thay đổi tiếp theo.
4. Nếu application rollback không tương thích schema, restore database theo runbook đã thử trên staging; không tự chạy downgrade phá dữ liệu.

## 11. Giới hạn trước production

- Rate limiter FastAPI là in-memory; Nginx là outer limiter nhưng multi-instance cần gateway/shared limiter nếu mở rộng.
- HS256 dùng shared signing secret; asymmetric signing/key rotation chưa có.
- Chưa có idempotency key/background worker cho import lớn.
- Cần chạy thử migration và load test trên PostgreSQL thật, không chỉ SQLite.
- Cần tích hợp repository web thật và thực hiện UAT end-to-end với quyền shop thật.
- Cần quy trình backup/restore, monitoring, secret rotation và incident response đã được vận hành thử.

Vì các điểm này, kết nối staging có thể chuẩn bị sau khi các smoke test pass, nhưng không được suy ra production-ready chỉ từ pytest.
