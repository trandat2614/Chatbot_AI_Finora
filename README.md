# 📊 FINORA AI Business Advisor

> Trợ lý phân tích kinh doanh AI cho người bán hàng đa kênh — kết hợp RAG, Python Tools, Machine Learning và LLM.

---

## 🎯 Giới Thiệu Dự Án

**FINORA AI Business Advisor** là một ứng dụng phân tích kinh doanh thông minh, giúp người bán hàng đa kênh (Shopee, Lazada, TikTok Shop, Facebook...) hiểu rõ tình hình kinh doanh và đưa ra quyết định có căn cứ dữ liệu.

### Tính Năng Chính

| Tính năng | Mô tả |
|-----------|-------|
| 🤖 AI Business Advisor | Hỏi đáp kinh doanh tự do với RAG + GPT |
| 💰 Điểm Hòa Vốn | Tính break-even, contribution margin, margin of safety |
| 📈 Phân Tích Doanh Thu | Upload CSV, phân tích đa chiều theo thời gian/kênh/sản phẩm |
| 🔮 Dự Báo & Marketing | Dự báo doanh thu ML + chiến lược marketing AI |

---

## 🏗️ Kiến Trúc Hệ Thống

```
Business Data
    ↓
Data Validation (validators.py)
    ↓
Financial Calculation Tools (tools/)
    ↓
Business Rule Engine (business_rule_engine.py)
    ↓
Revenue Forecasting (forecasting/)
    ↓
RAG Retrieval (rag/)
    ↓
LLM Business Advisor (core/llm_client.py)
    ↓
Streamlit Interface (ui/)
```

**Nguyên tắc thiết kế:**
- 🔢 **Python Tools** thực hiện tất cả phép tính tài chính — LLM chỉ giải thích
- 📊 **RAG** cung cấp kiến thức về marketing, tài chính từ tài liệu nội bộ
- 🤖 **LLM** tổng hợp và đưa ra khuyến nghị dựa trên bằng chứng dữ liệu
- 📈 **ML** dự báo xu hướng doanh thu (không dùng LLM để forecast)

---

## 📁 Cấu Trúc Folder

```
finora-ai-business-advisor/
├── app.py                      # Streamlit entry point
├── ingest.py                   # CLI: nạp tài liệu vào vector DB
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── config/
│   └── settings.py             # Cấu hình từ env vars
│
├── core/
│   ├── llm_client.py           # OpenAI Responses API wrapper
│   ├── prompts.py              # System prompts
│   └── exceptions.py          # Custom exceptions
│
├── rag/
│   ├── document_loader.py      # Load MD/TXT/PDF
│   ├── text_splitter.py       # RecursiveCharacterTextSplitter
│   ├── vector_store.py        # ChromaDB + OpenAI Embeddings
│   ├── retriever.py           # Similarity search
│   └── rag_service.py         # Public RAG API
│
├── tools/
│   ├── break_even_tool.py     # Break-even analysis
│   ├── revenue_analysis_tool.py
│   ├── profit_analysis_tool.py
│   ├── marketing_metrics_tool.py
│   └── business_rule_engine.py # Deterministic business signals
│
├── forecasting/
│   ├── data_preprocessing.py  # Feature engineering
│   ├── revenue_forecast.py    # LinearRegression forecast
│   └── evaluation.py         # TimeSeriesSplit evaluation
│
├── services/
│   ├── advisor_service.py     # Orchestrates RAG + LLM
│   ├── financial_service.py   # Orchestrates financial tools
│   └── forecast_service.py   # Orchestrates forecasting
│
├── ui/
│   ├── sidebar.py, components.py
│   ├── chat_page.py
│   ├── break_even_page.py
│   ├── revenue_page.py
│   └── forecast_page.py
│
├── utils/
│   ├── currency.py, validators.py
│   ├── file_helpers.py, logger.py
│
├── knowledge/                  # Tài liệu nội bộ cho RAG
├── data/sample_revenue.csv    # Dữ liệu mẫu
├── vector_db/                 # ChromaDB (tạo sau khi chạy ingest.py)
└── tests/                     # pytest tests
```

---

## 🚀 Hướng Dẫn Cài Đặt và Chạy

### 1. Tạo Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python -m venv .venv
source .venv/bin/activate
```

### 2. Cài Đặt Dependencies

```bash
pip install -r requirements.txt
```

### 3. Tạo File .env

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Mở file `.env` và điền thông tin:

```env
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=models/gemini-embedding-001
```

> ⚠️ **Không commit file .env lên Git!** File này đã được thêm vào `.gitignore`.

### 4. Nạp Tài Liệu Kiến Thức (Bắt buộc trước lần đầu chạy)

```bash
python ingest.py
```

Script này sẽ:
- Đọc tất cả tài liệu trong `knowledge/`
- Chia thành chunks
- Tạo embeddings qua OpenAI API
- Lưu vào ChromaDB tại `vector_db/`

### 5. Chạy Ứng Dụng

```bash
streamlit run app.py
```

Mở trình duyệt tại: **http://localhost:8501**

---

## 📋 Format CSV Đầu Vào

### Cột Bắt Buộc

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `date` | date | Ngày/tháng của kỳ (YYYY-MM-DD) |
| `revenue` | number | Doanh thu kỳ đó |
| `orders` | number | Số đơn hàng |
| `marketing_cost` | number | Chi phí marketing |
| `new_customers` | number | Số khách hàng mới |

### Cột Tùy Chọn (Mở Khóa Thêm Tính Năng)

| Cột | Mở khóa |
|-----|---------|
| `channel` | Phân tích theo kênh |
| `product` | Phân tích theo sản phẩm |
| `cost_of_goods_sold` | Tính Gross Profit |
| `platform_fees`, `discounts`, `refunds`, `operating_expenses` | Tính Net Profit |
| `sessions`, `conversions` | Tính Conversion Rate |
| `returning_customers` | Tính Repeat Purchase Rate |

### Ví dụ

```csv
date,revenue,orders,marketing_cost,new_customers
2024-01-01,85000000,120,12000000,85
2024-02-01,110000000,158,15000000,110
```

Xem file mẫu đầy đủ tại: `data/sample_revenue.csv`

---

## 🧪 Chạy Tests

```bash
# Chạy tất cả tests
pytest

# Verbose
pytest -v

# Chỉ một file
pytest tests/test_break_even.py -v
```

> ✅ Tất cả tests chạy **offline** — không cần OpenAI API key.

---

## ☁️ Deploy Lên Streamlit Community Cloud

### 1. Push Code Lên GitHub

```bash
git init
git add .
git commit -m "Initial commit: Finora AI Business Advisor"
git remote add origin https://github.com/your-username/finora-ai.git
git push -u origin main
```

> ⚠️ Đảm bảo `.env` và `vector_db/` KHÔNG được commit (đã có trong `.gitignore`).

### 2. Deploy Trên Streamlit Cloud

1. Vào [share.streamlit.io](https://share.streamlit.io)
2. Connect GitHub repository
3. Chọn `app.py` làm Main file
4. Click **Deploy**

### 3. Thêm Secrets Khi Deploy

Trong Streamlit Cloud dashboard:
1. Vào **Settings** → **Secrets**
2. Thêm:

```toml
GEMINI_API_KEY = "your-key-here"
GEMINI_MODEL = "gemini-2.5-flash"
EMBEDDING_MODEL = "models/gemini-embedding-001"
```

### 4. Xử Lý Vector DB Khi Deploy

Khi deploy lên Streamlit Cloud, bạn cần một trong hai cách:

**Cách 1 (Đơn giản):** Commit vector_db/ vào Git (bỏ dòng `vector_db/` khỏi `.gitignore`):
```bash
python ingest.py  # Chạy local để tạo vector_db
git add vector_db/
git commit -m "Add vector database"
```

**Cách 2 (Nâng cao):** Dùng Pinecone hoặc Weaviate thay cho ChromaDB local (cần cập nhật code).

---

## ⚠️ Hạn Chế Của Mô Hình Dự Báo

Mô hình dự báo hiện tại (Linear Regression MVP) có các hạn chế:

1. **Chỉ nắm bắt xu hướng tuyến tính** — không xử lý tính mùa vụ phức tạp
2. **Cần ít nhất 4 kỳ dữ liệu** — độ chính xác tốt hơn khi có 8+ kỳ
3. **Không tính đến yếu tố ngoại sinh** — biến động thị trường, đối thủ, chính sách sàn
4. **Độ chính xác giảm nhanh** khi dự báo xa hơn 3–6 kỳ
5. **Không phải dự báo chắc chắn** — luôn có khoảng sai số

**Roadmap nâng cấp:** Tích hợp Prophet hoặc ARIMA để xử lý tính mùa vụ.

---

## 🔒 Nguyên Tắc Bảo Mật Dữ Liệu

| Nguyên tắc | Thực hiện |
|-----------|----------|
| API key bảo mật | Dùng env vars, không hard-code |
| Dữ liệu CSV | Chỉ xử lý trong session, không lưu server |
| Không log nhạy cảm | Logger được cấu hình để bỏ qua data |
| Không gửi raw DataFrame lên LLM | Chỉ gửi aggregated metrics |
| OpenAI API key masked | Log chỉ hiện 6 ký tự đầu và 4 ký tự cuối |

---

## 🗺️ Roadmap Nâng Cấp

### v1.1 — Cải thiện Forecasting
- [ ] Tích hợp Facebook Prophet (xử lý seasonality)
- [ ] Hỗ trợ dự báo theo kênh riêng biệt
- [ ] Confidence interval cho dự báo

### v1.2 — Mở Rộng Phân Tích
- [ ] Phân tích cohort khách hàng
- [ ] Product margin analysis tự động
- [ ] Competitive analysis (nhập dữ liệu đối thủ)

### v1.3 — Data Source
- [ ] Kết nối Shopee API trực tiếp
- [ ] Kết nối Google Sheets
- [ ] Export báo cáo PDF

### v2.0 — Production Ready
- [ ] Multi-user authentication
- [ ] Database backend (PostgreSQL)
- [ ] Persistent vector DB (Pinecone/Weaviate)
- [ ] CI/CD pipeline

---

## 📝 License

MIT License — Xem file LICENSE để biết thêm chi tiết.

---

*Built with ❤️ using Google Gemini, LangChain, ChromaDB, Streamlit*
