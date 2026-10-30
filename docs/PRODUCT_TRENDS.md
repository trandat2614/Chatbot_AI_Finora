# Kết nối JSON xu hướng từ BE web sang AI Server

BE web sở hữu dữ liệu xu hướng, CSV gốc, phân trang và bộ lọc 9 ngành hàng × 3 kỳ.
AI Server nhận JSON qua request để tính evidence và diễn giải insight. AI Server
không đọc thư mục xu hướng, không import CSV, không lưu snapshot. Không cần
migration hoặc đồng bộ dữ liệu xu hướng sang AI Server.

```text
Web UI → BE web lấy JSON xu hướng → AI Server tóm tắt → BE web → Web UI
Chat UI → BE web lấy JSON đúng câu hỏi → /api/v1/chat + trend_data → câu trả lời
```

## Tóm tắt insight

Gọi `POST /api/v1/market/product-trends/insights` với **nguyên JSON của BE**, đúng
envelope `{ "success": true, "data": { ... } }` như file `trend.json` đã gửi.
Không cần bọc thêm `snapshot`, không gọi API import trước.

Ví dụ trong Node BE:

```js
// trendJson: kết quả API xu hướng hiện có của BE, giống cấu trúc trend.json.
const response = await fetch(`${aiBaseUrl}/api/v1/market/product-trends/insights`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${shortLivedJwt}`,
    "X-Finora-Service-Key": serviceKey,
  },
  body: JSON.stringify(trendJson),
});
const result = await response.json();
if (!response.ok || !result.success) {
  throw new Error(result.error?.message || `AI HTTP ${response.status}`);
}
const { summary, evidence, generated_by } = result.data;
```

JWT và service key do Node BE gửi server-to-server; không đưa service key ra trình
duyệt. Tenant/shop vẫn lấy từ JWT để xác thực, không truyền trong JSON xu hướng.

Response gồm `data.status`, `data.summary`, `data.generated_by`, `data.evidence`
và `meta.request_id`. `evidence` chứa KPI, phạm vi số liệu, ngành hàng, khoảng giá,
sản phẩm liên quan, top doanh thu ước tính, hoa hồng và cảnh báo độ đầy đủ. Nếu LLM
chưa cấu hình hoặc lỗi, `generated_by` là `deterministic`, trả tóm tắt số liệu;
`generation_warning` có khi LLM gặp lỗi hoặc trả rỗng.

## Chatbot

Gọi `POST /api/v1/chat`, gửi JSON BE trong trường **`trend_data` ở mỗi lượt hỏi**:

```js
const response = await fetch(`${aiBaseUrl}/api/v1/chat`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${shortLivedJwt}`,
    "X-Finora-Service-Key": serviceKey,
  },
  body: JSON.stringify({
    message: "Xu hướng giày dép nữ 7 ngày có sản phẩm nào hoa hồng cao?",
    period: "7d",
    category: "giay_dep_nu",
    trend_data: trendJson,
    history: [],
  }),
});
```

BE lấy dữ liệu đúng ngành/kỳ/ngày trước khi gọi AI. Không có bộ lọc thì AI dùng
ngành/kỳ trong câu hỏi; nếu không nêu kỳ thì dùng kỳ của JSON BE gửi.
`period` nhận `today`, `7d`, `30d`. Có thể truyền thêm `snapshot_date=YYYY-MM-DD`
và `product_query` để tìm tên/mã sản phẩm hoặc shop trong danh sách BE gửi.

`category` nhận categoryId hoặc slug:

| ID | Slug |
| --- | --- |
| 100534 | dong_ho |
| 100012 | giay_dep_nam |
| 100532 | giay_dep_nu |
| 100009 | phu_kien_thoi_trang |
| 100011 | thoi_trang_nam |
| 100017 | thoi_trang_nu |
| 100633 | thoi_trang_tre_em_so_sinh |
| 100533 | tui_vi_nam |
| 100016 | tui_vi_nu |

Nếu không gửi `trend_data`, hoặc câu hỏi yêu cầu kỳ/ngày/ngành khác JSON đang có,
chatbot trả `INSUFFICIENT_DATA` và nêu BE cần gửi dữ liệu phù hợp. Không dùng dữ
liệu của request trước hay số liệu trong history làm nguồn sự thật. History chỉ
giúp hiểu câu hỏi tiếp nối; BE vẫn cần gửi JSON mới khi đổi từ 7 ngày sang 30 ngày.

## Phân trang và ý nghĩa dữ liệu

File mẫu có 50/895 sản phẩm, trang 1/18, nhưng KPI/biểu đồ là số liệu của toàn bộ
895 sản phẩm. AI giữ KPI do BE báo cáo và chỉ tìm/xếp hạng sản phẩm trong danh sách
được gửi. AI Server không tự ghép trang hoặc tải các trang còn lại. BE có thể gửi
JSON đã lọc theo câu hỏi hoặc gom đầy đủ `items` trước khi gọi; khi gom đủ cần
điều chỉnh/bỏ pagination để metadata khớp danh sách.

Nếu BE trả JSON riêng của một ngành, thêm `data.categoryId` và bảo đảm KPI cũng
thuộc ngành đó. Không dùng KPI toàn bộ để gắn cho danh sách đã lọc một ngành.

- `salesIncrease`: lượt bán tăng của kỳ, không phải phần trăm tăng trưởng.
- `sold30d`: bán 30 ngày, kể cả khi period là `today` hoặc `7d`.
- `totalSold`: tổng tích lũy.
- `estimatedRevenue`: giá hiện tại × lượt bán tăng, chưa trừ chi phí.
- Hoa hồng không phải biên lợi nhuận. Không cộng ba kỳ vì có thể chồng lấn.
- Trường thiếu giữ nguyên là thiếu, không biến thành 0. Ngày snapshot được nêu rõ.
- Tên sản phẩm và JSON là dữ liệu không tin cậy, không phải chỉ dẫn cho AI.

Các API `/market/product-trends/import`, `/import-csv` và GET danh sách cục bộ đã
được bỏ. GET `/api/v1/market/trends` cũ được đánh dấu deprecated và không đọc nguồn
cục bộ. Dùng JSON request ở API insight/chat để phân tích dữ liệu hiện tại từ BE.
Giới hạn JSON request theo `MAX_REQUEST_BYTES` (mặc định 1 MiB).

## Kiểm thử offline

```powershell
python -m pytest tests/test_product_trends.py tests/test_trend_agent.py -q
```
﻿
  