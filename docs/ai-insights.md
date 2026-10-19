# AI Business Insights

## Kiến trúc

1. `services/insights/data_provider.py`: chuẩn hóa order, expense và cấu hình shop qua `InsightDataProvider`.
2. `services/insights/metrics.py`: tính chỉ số kỳ hiện tại/kỳ trước, kênh, sản phẩm, xu hướng tháng và hòa vốn; không gọi LLM.
3. `services/insights/rules.py`: phát hiện candidate bằng tỷ lệ và ngưỡng cấu hình, mọi kết luận đều có `evidence`.
4. `services/insights/generator.py`: dùng `core.llm_client.LLMClient` hiện có để viết tiếng Việt; validate JSON bằng Pydantic, retry một lần rồi fallback template.
5. `services/insights/service.py`: hash metrics, cache, dedupe/upsert và khóa theo `(tenant_id, shop_id)` trong một process.
6. `src/api/routes/insights.py`: lấy tenant/shop duy nhất từ auth dependency và cung cấp ba endpoint dashboard.

Mọi truy vấn `ai_insights` lọc đồng thời `tenant_id` và `shop_id`. Unique key theo tenant, shop, type và kỳ ngăn bản ghi trùng; index `(tenant_id, created_at)` phục vụ danh sách gần đây. Với nhiều worker/process, unique key DB là lớp bảo vệ cuối; nếu cần chạy batch đồng thời ở quy mô lớn, backend nên điều phối mỗi tenant vào một worker.

## API

Tất cả endpoint yêu cầu `Authorization: Bearer ...` và `X-Finora-Service-Key`. Client không được gửi `tenant_id` hoặc `shop_id`; hai giá trị này chỉ lấy từ identity đã xác thực.

| Method | Endpoint | Mô tả |
| --- | --- | --- |
| `GET` | `/api/insights?limit=5&status=new` | Insight gần đây, mới nhất trước; `status` là `new`, `read` hoặc `dismissed` (mặc định `new`) |
| `POST` | `/api/insights/generate` | Chạy pipeline; body hỗ trợ `period` (`7d`, `30d`, `90d`) và `force` |
| `PATCH` | `/api/insights/{id}` | Đổi trạng thái insight thuộc đúng tenant/shop hiện tại |

Ví dụ generate:

```http
POST /api/insights/generate
Content-Type: application/json

{"period":"30d","force":false}
```

```json
{
  "items": [
    {
      "id": "21d4f11e-7864-42c0-9862-f16397806b64",
      "type": "channel_concentration",
      "severity": "warning",
      "title": "Doanh thu phụ thuộc một kênh",
      "summary": "Một kênh đang đóng góp phần lớn doanh thu kỳ này.",
      "recommendation": "Thử một chiến dịch nhỏ trên kênh khác.",
      "evidence": {"channel": "Kênh từ dữ liệu shop", "share_pct": 74.2},
      "created_at": "2026-10-15T09:00:00+00:00"
    }
  ],
  "generated_at": "2026-10-15T09:00:00+00:00",
  "empty_reason": null
}
```

Shop có 0 đơn trong kỳ nhận:

```json
{"items":[],"generated_at":"2026-10-15T09:00:00+00:00","empty_reason":"not_enough_data"}
```

Shop có ít hơn `INSIGHT_MIN_ORDERS` nhưng lớn hơn 0 nhận một insight `low_data`, không nhận kết luận kinh doanh thiếu căn cứ.

## Cấu hình

Các biến đều tùy chọn:

| Biến | Mặc định | Ý nghĩa |
| --- | ---: | --- |
| `INSIGHT_MIN_ORDERS` | `5` | Số đơn tối thiểu để áp dụng rule kinh doanh |
| `INSIGHT_SIGNIFICANT_CHANGE_PCT` | `20` | Mức thay đổi doanh thu/đơn đáng kể |
| `INSIGHT_CHANNEL_CONCENTRATION_PCT` | `70` | Ngưỡng phụ thuộc một kênh |
| `INSIGHT_WEAK_CHANNEL_DROP_PCT` | `30` | Ngưỡng giảm của kênh yếu |
| `INSIGHT_LOW_MARGIN_PCT` | `10` | Ngưỡng biên lợi nhuận thấp |
| `INSIGHT_HIGH_MARGIN_PCT` | `40` | Ngưỡng biên lợi nhuận cao |
| `INSIGHT_COST_GROWTH_GAP_PCT` | `15` | Khoảng tăng chi phí nhanh hơn doanh thu |
| `INSIGHT_PRODUCT_CONCENTRATION_PCT` | `50` | Ngưỡng phụ thuộc sản phẩm chủ lực |
| `INSIGHT_LOW_PRODUCT_SHARE_PCT` | `2` | Tỷ trọng sản phẩm ít bán |
| `INSIGHT_BREAK_EVEN_SLOW_PROGRESS_PCT` | `25` | Ngưỡng tiến độ hòa vốn chậm |
| `INSIGHT_TENANT_THRESHOLDS_JSON` | rỗng | JSON override theo tenant, chỉ nhận các key trong bảng trên |

Ví dụ override:

```env
INSIGHT_TENANT_THRESHOLDS_JSON={"tenant-a":{"min_orders":10,"channel_concentration_pct":80}}
```

Không đặt API key hoặc dữ liệu nhạy cảm trong JSON override.

## Hiển thị trên frontend

| Severity | Màu gợi ý | Icon gợi ý | Ý nghĩa |
| --- | --- | --- | --- |
| `positive` | xanh lá | trend-up/check | Tín hiệu tích cực nên duy trì |
| `info` | xanh dương/xám | info | Thông tin hoặc dữ liệu còn ít |
| `warning` | vàng/cam | warning | Cần kiểm tra và hành động sớm |
| `critical` | đỏ | alert | Rủi ro ưu tiên cao |

FE nên hiển thị `evidence` trong tooltip/chi tiết để người dùng truy ngược mọi con số. Với `items=[]` và `empty_reason=not_enough_data`, hiển thị “Chưa có dữ liệu”. `dismissed` nên bị ẩn khỏi ô dashboard mặc định.

## Chi phí LLM và cache

- Metrics và rules luôn deterministic, không dùng token LLM.
- Tối đa 5 candidate được gửi trong một request LLM; prompt chỉ chứa aggregate/evidence của đúng một tenant/shop.
- Nếu `data_hash` không đổi, pipeline trả cache và không gọi LLM lại. `force=true` bỏ qua cache và phát sinh chi phí mới.
- Khi LLM timeout/lỗi/JSON sai hai lần, template fallback tạo response hợp lệ mà không phát sinh lỗi API.
- Không log prompt, evidence, token hay dữ liệu đơn hàng nhạy cảm.

## Migration và kiểm thử

```powershell
alembic upgrade head
python -m pytest
```

Migration mới: `20261015_0003_ai_insights.py`. Production phải chạy migration; `AUTO_CREATE_SCHEMA` chỉ dành cho local/test theo convention hiện có.

## BE cần làm gì để nối

### 1. Mount router

Router đã được mount trong `src/api/app.py`:

```python
app.include_router(insights.router)
```

Nếu backend chính có app factory riêng, mount `src.api.routes.insights.router` tại đó. Không nhận `tenant_id`/`shop_id` từ request body, query hoặc header phụ.

### 2. Cung cấp `InsightDataProvider`

`DefaultDataProvider` hiện đọc đúng nguồn dashboard là `SQLAlchemyCommerceRepository.load_orders(tenant_id, shop_id)`. Nếu backend chính có ledger chi phí/cấu hình shop riêng, tạo implementation mới và đổi dependency `insight_data_provider`; không sửa metrics/rules/generator.

| Nguồn thật | Model/trường đích | Mapping mặc định hiện tại |
| --- | --- | --- |
| Order ID | `OrderRecord.order_id` | `orders.external_order_id` qua `load_orders().order_id` |
| Ngày đặt | `OrderRecord.date` | `orders.created_at` |
| Kênh | `OrderRecord.channel` | `orders.platform` |
| Sản phẩm | `OrderRecord.product` | `order_items.product_name` |
| Số lượng | `OrderRecord.quantity` | `order_items.quantity` |
| Doanh thu dòng | `OrderRecord.revenue` | `selling_price × quantity`, bỏ đơn hủy |
| Giá vốn | `OrderRecord.cost_of_goods` | Chưa có trong schema, mặc định chưa xác định; BE phải nối ledger/COGS thật |
| Phí order | `ExpenseRecord.amount/category` | platform, transaction, service, shipping fee và refund |
| Vốn đầu tư | `ShopSettings.investment_capital` | Chưa có trong schema hiện tại |
| Chi phí cố định | `ShopSettings.fixed_costs` | Chưa có trong schema hiện tại |
| Mục tiêu hòa vốn | `ShopSettings.break_even_target` | Chưa có trong schema hiện tại |
| Override rule | `ShopSettings.rule_thresholds` | `INSIGHT_TENANT_THRESHOLDS_JSON` |

Không suy ra COGS từ `Product.margin` nếu chưa thống nhất margin là số tiền hay tỷ lệ. Khi chưa có cấu hình hòa vốn, phần hòa vốn được bỏ qua và không báo lỗi.
Khi COGS chưa có, `profit`/`profit_margin_pct` được xem là chưa xác định và các rule về lợi nhuận/hòa vốn không chạy; hệ thống không giả định giá vốn bằng 0.

### 3. Gọi refresh sau thay đổi dữ liệu

Import endpoint hiện thêm FastAPI background task sau khi import thành công:

```python
refresh_insights_for_tenant(
    context.tenant_id,
    shop_id=context.shop_id,
    database=request.app.state.database,
    repository=repository,
    llm_client=request.app.state.llm_client,
)
```

Backend chính nên gọi cùng hàm sau khi tạo/cập nhật đơn hoặc hoàn tất import. `refresh_insights_for_tenants([...])` xử lý danh sách tenant tuần tự. Repo chưa có scheduler nên không thêm hạ tầng mới; scheduler bên ngoài có thể gọi hai hàm này mỗi ngày.

### 4. Xác nhận mapping dữ liệu

Trước production, BE cần xác nhận status nào là đơn hủy, timezone của ngày đơn, monetary ownership của các khoản phí, nguồn COGS và ý nghĩa mục tiêu hòa vốn. Provider phải trả channel/product động từ shop; không đưa tên kênh, sản phẩm hoặc số tiền mẫu vào code chạy thật.

## Curl

Đặt token/service key do web backend cấp:

```bash
curl -sS 'http://localhost:8000/api/insights?limit=5&status=new' \
  -H 'Authorization: Bearer <token>' \
  -H 'X-Finora-Service-Key: <service-key>'

curl -sS -X POST 'http://localhost:8000/api/insights/generate' \
  -H 'Authorization: Bearer <token>' \
  -H 'X-Finora-Service-Key: <service-key>' \
  -H 'Content-Type: application/json' \
  -d '{"period":"30d","force":false}'

curl -sS -X PATCH 'http://localhost:8000/api/insights/<insight-id>' \
  -H 'Authorization: Bearer <token>' \
  -H 'X-Finora-Service-Key: <service-key>' \
  -H 'Content-Type: application/json' \
  -d '{"status":"read"}'
```
