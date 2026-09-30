# Finora AI Decision Intelligence

## Luồng dữ liệu

```text
CSV/XLSX không tin cậy
  -> extension/MIME/signature/size/schema validation
  -> Shopee | TikTok Shop | Lazada adapter
  -> Unified Commerce Schema + PII protection
  -> PostgreSQL Order + OrderItem
  -> deterministic analytics
  -> structured context
  -> LLM giải thích/khuyến nghị
```

Marketplace spreadsheets và transaction rows không đi vào Chroma. LLM không tính authoritative revenue, AOV, fee, refund, profit, CAC, ROAS hoặc growth. Khi dữ liệu bắt buộc thiếu, service trả `INSUFFICIENT_DATA`.

## Security model

- Finora Node backend gửi JWT ngắn hạn và `X-Finora-Service-Key`.
- `AuthContext` chỉ được tạo sau khi xác minh signature, `exp`, issuer, audience, role và service credential.
- Repository queries luôn lọc `tenant_id` + `shop_id`; API v1 không tin identity từ body.
- PII khách hàng được bỏ/hash trước LLM, embeddings và logs.
- Private RAG ghi `tenant_id`, `shop_id`, `visibility`, `document_id` và áp dụng filter trong vector query.
- Product names, documents, scraped content và RAG chunks là data không tin cậy, không phải system instruction.
- Audit log ghi login/auth, upload/import, analytics/planning và admin events mà không ghi secret/body/file content.
- Các tool hiện chỉ đọc hoặc tạo khuyến nghị; không sửa giá, voucher, ad budget, listing hoặc cấu hình marketplace.

Legacy `X-API-Key` chỉ dành cho migration/local khi `ENABLE_LEGACY_API_KEY=true`.

## Data model

Order-level:

```text
order_total, platform_fee, transaction_fee, service_fee, shipping_fee, refund_amount
```

Item-level:

```text
quantity, original_price, selling_price, seller_discount, platform_discount
```

Một order nhiều item chỉ lưu phí cấp đơn một lần trong `orders`. Compatibility DataFrame chỉ đặt các phí này ở dòng item đầu để analytics cũ không nhân phí.

Các bảng: `shops`, `data_imports`, `orders`, `order_items`, `products`, `market_trend_snapshots`, `recommendations`, `recommendation_results`, `conversations`, `audit_events`.

## Services

- `DataNormalizationService`: chọn marketplace adapter, normalize và loại bản ghi trùng.
- `MetricService`: revenue, distinct orders, units, AOV, cancellation/refund, discounts, fees, net revenue và growth.
- `RevenueLeakageService`: deterministic GMV-to-net bridge.
- `BusinessHealthService`: cảnh báo cancellation, refund, discount dependency, revenue drop và fee increase.
- `ProductDoctorService`: `SCALE`, `PUSH`, `TEST`, `MONITOR`, `FIX`, `REDUCE`.
- `MarketTrendService`: lưu snapshot lịch sử bất biến trong relational database.
- `OpportunityMatchingService`: kết hợp market/shop metrics, confidence, evidence và `missing_metrics`.
- `ActionPlanService`: tạo các action ưu tiên; `expected_impact=null` nếu backend không tính chắc chắn.
- Sales/Communication planners: tạo khuyến nghị có cấu trúc, không thực thi bên ngoài.

## Chat orchestration và tools

```text
ChatRequest -> AuthContext -> Intent Router -> authorized tool
            -> tenant/shop repository -> deterministic analytics
            -> structured JSON context -> LLM -> ChatResponse
```

Tools được bind vào context, không nhận arbitrary tenant/shop từ model:

```text
get_business_overview
get_business_health
analyze_product
analyze_orders
analyze_refunds
analyze_revenue_leakage
get_market_trends
find_product_opportunities
generate_action_plan
generate_sales_plan
generate_communication_plan
```

Intent: `BUSINESS_OVERVIEW`, `BUSINESS_HEALTH`, `REVENUE_LEAKAGE`,
`PRODUCT_ANALYSIS`, `ORDER_ANALYSIS`, `REFUND_ANALYSIS`, `MARKET_TRENDS`,
`OPPORTUNITIES`, `ACTION_PLAN`, `SALES_PLAN`, `MARKETING_PLAN`,
`POLICY_QUESTION`, `GENERAL_CHAT`.

Mọi intent phụ thuộc dữ liệu shop phải có `verified_metrics` và provenance từ
tool. Nếu thiếu, orchestration trả `INSUFFICIENT_DATA` trước khi gọi LLM.
Assistant history và legacy `orderSummary` không được dùng làm metric source.
Nếu output LLM chứa số không có trong verified tool result, output đó bị loại
và thay bằng deterministic grounded summary.

## RAG

RAG dành cho policy Shopee/TikTok/Lazada, tax/fee docs, Finora knowledge và private shop documents. Public knowledge có thể dùng chung. Private retrieval phải lọc tenant/shop trong Chroma query; post-filter chỉ là defense in depth.

Sau thay đổi metadata hoặc sanitizer, rebuild public index:

```bash
python ingest.py
```

## API

Production contract là `/api/v1/*` với strict Pydantic request/response models và envelope `{success,data|error,meta}`. Xem [WEB_INTEGRATION.md](WEB_INTEGRATION.md). Các `/api/*` cũ là deprecated compatibility wrappers.
