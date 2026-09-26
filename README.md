# Finora AI Server

AI server dùng Gemini API cho trợ lý phân tích kinh doanh đa kênh. Đây là dịch vụ
HTTP độc lập; không còn chạy giao diện demo Streamlit.

## Chức năng

- `POST /api/chat`: hội thoại với Gemini, nhận thêm `orderSummary` và `history`.
- RAG từ tài liệu Markdown/PDF qua ChromaDB; response có danh sách `sources`.
- `GET /health`: kiểm tra server và trạng thái kho tri thức.
- CORS theo domain, API key server tùy chọn, rate limit, kiểm tra schema/payload.
- Server không lưu lịch sử chat hoặc dữ liệu tài chính của client.

## Chạy local

Yêu cầu Python 3.11+.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
```

Điền `GEMINI_API_KEY` trong `.env`. Ở production, đổi `AI_SERVER_API_KEY` thành
chuỗi bí mật mạnh và đặt `ALLOWED_ORIGINS` đúng domain frontend.

Nạp lại kho kiến thức khi nội dung `knowledge/` thay đổi:

```bash
python ingest.py
```

Với Gemini free tier, quá trình embedding được tự động giới hạn khoảng 4 request/phút
để tránh lỗi `429`. Có thể điều chỉnh `EMBEDDING_BATCH_SIZE` và
`EMBEDDING_REQUEST_INTERVAL_SECONDS` trong `.env` nếu project có quota cao hơn.

Khởi động server:

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

- Swagger UI: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
- React demo (upload tài liệu và chat): `http://localhost:8000/demo/`

## Gọi API

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: change_me_in_production" \
  -d '{
    "message": "Tình hình kinh doanh tháng này thế nào?",
    "orderSummary": {
      "totalRevenue": 150000000,
      "totalOrders": 850,
      "refundRate": 4.2
    },
    "history": []
  }'
```

Response:

```json
{
  "answer": "...",
  "sources": [
    {"source": "revenue_analysis.md", "filename": "revenue_analysis.md", "file_type": ".md", "score": 0.81}
  ],
  "rag_context_used": true,
  "warnings": []
}
```

Ví dụ React:

```js
export async function askFinora(message, orderSummary, history = []) {
  const response = await fetch(`${import.meta.env.VITE_AI_SERVER_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": import.meta.env.VITE_AI_SERVER_KEY,
    },
    body: JSON.stringify({ message, orderSummary, history }),
  });
  if (!response.ok) throw new Error("Finora AI đang tạm thời không khả dụng");
  return response.json();
}
```

Nếu đây là web công khai, không đưa `AI_SERVER_API_KEY` vào bundle frontend. Hãy
gọi AI server qua backend chính của ứng dụng để khóa không bị lộ.

## Docker

```bash
docker compose build
docker compose run --rm api python ingest.py
docker compose up -d
```

ChromaDB được lưu trong Docker volume `finora_vector` để không mất dữ liệu khi
thay container.

## Production

Chạy một worker nếu dùng rate limiter in-memory. Với nhiều worker/instance, đặt
rate limiting ở Nginx/API Gateway hoặc Redis. Dùng HTTPS, giữ `.env` ngoài Git,
và chỉ cho phép origin thực tế của frontend.

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

## Tài liệu vận hành

- [Kiểm thử trên máy local](docs/LOCAL_TESTING.md)
- [Đưa source lên GitHub và triển khai VPS an toàn](docs/GITHUB_VPS_DEPLOYMENT.md)
- [Triển khai lên VPS](docs/VPS_DEPLOYMENT.md)
