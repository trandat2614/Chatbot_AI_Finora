# Kiểm thử Finora AI Server trên máy local

## 1. Yêu cầu

- Python 3.11 hoặc 3.12.
- Git.
- Gemini API key.
- Docker Desktop chỉ cần thiết nếu muốn kiểm thử bằng container.

Kiểm tra Python:

```powershell
py --version
```

Nếu lệnh không tìm thấy Python, cài Python từ python.org và bật tùy chọn thêm
Python Launcher/Python vào PATH. Không dùng lại `.venv` được tạo từ bản Python đã
bị gỡ.

## 2. Tạo môi trường sạch

PowerShell trên Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Điền ít nhất các biến sau trong `.env`:

```dotenv
GEMINI_API_KEY=your_real_key
AI_SERVER_API_KEY=local_test_secret
ALLOWED_ORIGINS=http://localhost:3000
```

Không commit `.env`.

## 3. Chạy test offline

Các test hiện tại không gọi Gemini API:

```powershell
python -m pytest -q
```

Chạy riêng test API server:

```powershell
python -m pytest tests/test_api_server.py -q
```

Kiểm tra nhanh syntax/import:

```powershell
python -m compileall app.py server.py config core rag services tools forecasting
```

## 4. Nạp kho tri thức

Lệnh này gọi Gemini Embedding API và tạo dữ liệu trong `vector_db/`:

```powershell
python ingest.py
```

Chạy lại sau mỗi lần thay đổi file trong `knowledge/`.

## 5. Chạy API server

```powershell
uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

Ở terminal khác:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Kết quả phải có `status: ok`; `rag_ready: true` nghĩa là ChromaDB đã được nạp.

Kiểm tra chat:

```powershell
$headers = @{ "X-API-Key" = "local_test_secret" }
$body = @{
  message = "Điểm hòa vốn được tính như thế nào?"
  orderSummary = $null
  history = @()
} | ConvertTo-Json -Depth 10

Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/chat `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

Kiểm tra thêm tại `http://127.0.0.1:8000/docs`.

## 6. Kiểm thử Docker trước khi deploy

```powershell
docker compose build
docker compose run --rm api python -m pytest -q
docker compose run --rm api python ingest.py
docker compose up -d
docker compose ps
```

Xem log nếu container không healthy:

```powershell
docker compose logs --tail=200 api
```
