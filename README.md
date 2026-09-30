# Finora AI Business Advisor

Finora là AI server hỗ trợ phân tích và tư vấn kinh doanh đa kênh. Hệ thống kết hợp mô hình ngôn ngữ với kho tri thức nội bộ (RAG), dữ liệu tổng hợp đơn hàng do client cung cấp và dữ liệu xu hướng thời trang Shopee để tạo câu trả lời có căn cứ.

Dự án chạy dưới dạng REST API độc lập bằng FastAPI, kèm giao diện web demo tại `/demo/`.

## Tính năng chính

- Hội thoại tư vấn kinh doanh bằng Gemini hoặc FPT AI Factory.
- Phân tích dữ liệu tổng hợp đơn hàng và duy trì ngữ cảnh hội thoại.
- RAG với ChromaDB từ Markdown, text, PDF, Excel và CSV.
- Truy vấn xu hướng thời trang Shopee theo giới tính và khoảng thời gian.
- Upload tài liệu và lập chỉ mục lại kho tri thức qua API.
- Trả về nguồn tham khảo đã dùng trong câu trả lời.
- Xác thực bằng API key tùy chọn, giới hạn tần suất gọi API, CORS và kiểm tra kích thước payload.
- Không lưu lịch sử chat hoặc dữ liệu tài chính do client gửi đến.

## Công nghệ sử dụng

- Python 3.11+
- FastAPI, Uvicorn và Pydantic
- Google Gemini hoặc FPT AI Factory qua giao diện OpenAI-compatible
- LangChain và ChromaDB
- Pandas, scikit-learn và SQLite
- Docker, Docker Compose

## Bắt đầu nhanh

### 1. Tạo môi trường và cài thư viện

Windows PowerShell:

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

### 2. Cấu hình mô hình AI

Mặc định, Finora sử dụng Gemini. Điền ít nhất các biến sau vào `.env`:

```dotenv
GEMINI_API_KEY=your_real_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
AI_SERVER_API_KEY=local_secret
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

Để dùng FPT AI Factory thay cho Gemini:

```dotenv
AI_PROVIDER=fpt
FPT_API_KEY=your_real_fpt_api_key
FPT_BASE_URL=https://mkp-api.fptcloud.com/v1
FPT_CHAT_MODEL=DeepSeek-V4-Flash
FPT_EMBEDDING_MODEL=Vietnamese_Embedding
```

Không commit file `.env` hoặc đưa khóa bí mật vào mã nguồn.

### 3. Nạp kho tri thức

Đặt tài liệu vào thư mục `knowledge/`, sau đó tạo vector database:

```bash
python ingest.py
```

Các định dạng được hỗ trợ: `.md`, `.txt`, `.pdf`, `.xlsx`, `.xls` và `.csv`. Chạy lại lệnh trên khi tài liệu hoặc embedding model thay đổi.

Nếu chưa ingest, server vẫn có thể khởi động và chat nhưng phản hồi sẽ không sử dụng RAG. Với Gemini free tier, quá trình embedding có thể mất vài phút do khoảng nghỉ mặc định giữa các batch.

### 4. Khởi động server

Chế độ phát triển:

```bash
uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

Hoặc chạy trực tiếp:

```bash
python server.py
```

Sau khi khởi động:

- Web demo: <http://127.0.0.1:8000/demo/>
- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>
- Health check: <http://127.0.0.1:8000/health>

## API

| Phương thức | Endpoint | Xác thực | Mô tả |
| --- | --- | --- | --- |
| `GET` | `/health` | Không | Kiểm tra trạng thái server, model và RAG |
| `POST` | `/api/chat` | `X-API-Key` | Gửi câu hỏi, dữ liệu đơn hàng và lịch sử chat |
| `POST` | `/api/knowledge/upload` | `X-API-Key` | Upload tài liệu tối đa 10 MB và lập chỉ mục lại RAG |

Header `X-API-Key` chỉ bắt buộc khi `AI_SERVER_API_KEY` đã được cấu hình trên server.

### Gửi câu hỏi

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: local_secret" \
  -d '{
    "message": "Phân tích tình hình kinh doanh tháng này",
    "orderSummary": {
      "totalRevenue": 150000000,
      "totalOrders": 850,
      "refundRate": 4.2
    },
    "history": []
  }'
```

Phản hồi mẫu:

```json
{
  "answer": "...",
  "sources": [
    {
      "source": "knowledge/revenue_analysis.md",
      "filename": "revenue_analysis.md",
      "file_type": "md",
      "score": 0.81
    }
  ],
  "rag_context_used": true,
  "warnings": []
}
```

`history` là danh sách tin nhắn có dạng `{ "role": "user|assistant", "content": "..." }`. Số tin nhắn tối đa được điều khiển bởi `MAX_HISTORY_MESSAGES`.

### Upload tài liệu

```bash
curl -X POST http://127.0.0.1:8000/api/knowledge/upload \
  -H "X-API-Key: local_secret" \
  -F "file=@knowledge/revenue_analysis.md"
```

File được lưu vào `knowledge/`; sau đó toàn bộ kho tri thức được đọc và lập chỉ mục lại. Không dùng endpoint này cho người dùng không đáng tin cậy nếu chưa có lớp phân quyền phù hợp.

## Biến môi trường

Các giá trị mặc định đầy đủ nằm trong `.env.example`.

| Biến | Mặc định | Ý nghĩa |
| --- | --- | --- |
| `AI_PROVIDER` | `gemini` | Nhà cung cấp AI: `gemini` hoặc `fpt` |
| `GEMINI_API_KEY` | — | API key Gemini |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Model chat Gemini |
| `EMBEDDING_MODEL` | `models/gemini-embedding-001` | Model embedding Gemini |
| `FPT_API_KEY` | — | API key FPT khi dùng provider `fpt` |
| `FPT_BASE_URL` | `https://mkp-api.fptcloud.com/v1` | OpenAI-compatible endpoint của FPT |
| `FPT_CHAT_MODEL` | `DeepSeek-V4-Flash` | Model chat FPT |
| `FPT_EMBEDDING_MODEL` | `Vietnamese_Embedding` | Model embedding FPT |
| `KNOWLEDGE_DIR` | `knowledge` | Thư mục tài liệu RAG |
| `VECTOR_DB_DIR` | `vector_db` | Thư mục lưu ChromaDB |
| `CHUNK_SIZE` | `700` | Kích thước mỗi chunk |
| `CHUNK_OVERLAP` | `100` | Độ chồng lấn giữa các chunk |
| `RETRIEVAL_TOP_K` | `4` | Số chunk được truy xuất cho mỗi câu hỏi |
| `EMBEDDING_BATCH_SIZE` | `20` | Số chunk trong một batch embedding |
| `EMBEDDING_REQUEST_INTERVAL_SECONDS` | `15` | Khoảng nghỉ giữa các batch |
| `LLM_TEMPERATURE` | `0.3` | Temperature mặc định của model |
| `ADAPTIVE_RESPONSE_TEMPERATURE` | `0.6` | Temperature cho luồng tư vấn thích ứng |
| `LLM_MAX_TOKENS` | `2048` | Số token tối đa của phản hồi |
| `LLM_TIMEOUT` | `60` | Thời gian chờ API AI, tính bằng giây |
| `HOST` | `0.0.0.0` | Địa chỉ bind server |
| `PORT` | `8000` | Cổng server |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | Danh sách CORS origin, phân cách bằng dấu phẩy |
| `AI_SERVER_API_KEY` | rỗng | Khóa bảo vệ các endpoint nghiệp vụ |
| `RATE_LIMIT_PER_MINUTE` | `30` | Số request tối đa mỗi phút trên mỗi IP |
| `MAX_HISTORY_MESSAGES` | `20` | Số tin nhắn lịch sử tối đa |
| `MAX_REQUEST_BYTES` | `1048576` | Kích thước request chat tối đa, tính bằng byte |

## Kiểm thử

Bộ test hiện tại chạy offline, không gọi API Gemini/FPT:

```bash
python -m pytest -q
```

Kiểm tra nhanh syntax và import:

```bash
python -m compileall app.py server.py config core rag services tools forecasting src
```

## Chạy bằng Docker

```bash
docker compose build
docker compose run --rm api python -m pytest -q
docker compose run --rm api python ingest.py
docker compose up -d
```

Kiểm tra trạng thái và log:

```bash
docker compose ps
docker compose logs --tail=200 api
```

ChromaDB được lưu trong volume `finora_vector`, vì vậy dữ liệu RAG vẫn tồn tại khi container được tạo lại. Không chạy `docker compose down -v` trừ khi muốn xóa vector database.

## Cấu trúc dự án

```text
.
├── server.py              # FastAPI app và các endpoint
├── app.py                 # ASGI entrypoint
├── ingest.py              # CLI tạo kho vector
├── config/                # Cấu hình từ biến môi trường
├── core/                  # LLM client, prompt và exception
├── rag/                   # Đọc, chia nhỏ, truy xuất và lưu tài liệu
├── services/              # Điều phối tư vấn và phân tích tài chính
├── forecasting/           # Dự báo doanh thu
├── tools/                 # Công cụ phân tích nghiệp vụ
├── src/agent/             # Workflow tư vấn xu hướng
├── src/services/          # Xử lý dữ liệu xu hướng Shopee
├── data/trends/           # CSV và SQLite xu hướng mẫu
├── knowledge/             # Tài liệu nguồn cho RAG
├── web/                   # Giao diện demo tĩnh
├── tests/                 # Bộ kiểm thử pytest
├── deploy/                # Cấu hình Nginx mẫu
└── docs/                  # Tài liệu kiểm thử và triển khai
```

## Lưu ý khi triển khai production

- Dùng HTTPS và đặt một `AI_SERVER_API_KEY` đủ mạnh.
- Chỉ cho phép đúng domain frontend trong `ALLOWED_ORIGINS`.
- Không nhúng `AI_SERVER_API_KEY` vào bundle frontend công khai; nên gọi Finora qua backend chính của ứng dụng.
- Rate limiter hiện lưu trong bộ nhớ của một process. Nếu chạy nhiều worker hoặc nhiều instance, hãy chuyển rate limiting sang Nginx, API Gateway hoặc Redis.
- Sao lưu `.env`, thư mục `knowledge/` và volume ChromaDB định kỳ.

Xem thêm:

- [Kiểm thử trên máy local](docs/LOCAL_TESTING.md)
- [Triển khai lên VPS](docs/VPS_DEPLOYMENT.md)
