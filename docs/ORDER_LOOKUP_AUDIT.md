# Audit Import → Database → Orders API → Chat API

Ngày audit: 2026-10-13.

## Kết luận nguyên nhân

Import `/api/v1/data/import` chuẩn hóa CSV/XLSX rồi ghi giao dịch vào PostgreSQL/SQLite qua
`SQLAlchemyCommerceRepository.replace_orders()`. Đơn được lưu ở `orders`, sản phẩm theo đơn ở
`order_items`, và import job ở `data_imports`. Mã đơn được đọc với `dtype=str` và lưu vào
`orders.external_order_id` kiểu chuỗi.

Chat v1 và route legacy đều tạo `AdvisorService`, nhưng trước bản sửa:

- `Intent` không có intent tra cứu đơn hoặc thống kê đơn.
- `build_business_tools()` không đăng ký tool đọc một đơn cụ thể.
- `SQLAlchemyCommerceRepository` không có phương thức lookup đơn có scope tenant/shop.
- Câu hỏi có mã đơn rơi vào `GENERAL_CHAT`; chat chỉ nhận RAG hoặc số liệu tổng hợp và không hề
  truy vấn bảng `orders`.

Đó là nguyên nhân trực tiếp khiến đơn import có thể tồn tại trong database nhưng chatbot không
thấy. Ngoài ra, database PostgreSQL theo `DATABASE_URL` được kiểm tra read-only ngày 2026-10-13 có
`orders_count=0`, `imports_count=0`, và không có `260921KK6HXSNP`. Repo này cũng không chứa code UI
Quản lý đơn hàng. Vì vậy UI đang hiển thị đơn từ nguồn khác, hoặc upload UI chưa gọi endpoint import
của AI server/môi trường hiện tại. Đây là mismatch tích hợp cần được kiểm tra ở web backend; không có
bằng chứng MongoDB nằm trên đường chạy của repo này.

## Thay đổi

- `GET /api/v1/orders/{order_id}`: exact match, scope lấy từ auth context, hỗ trợ `platform`, trả 404
  trong shop hiện tại và 409 nếu cùng mã xuất hiện ở nhiều nền tảng.
- `GET /api/v1/analytics/orders/summary`: lọc `start_at`, `end_at`, `platform`, `status`; trả số đơn,
  doanh thu, AOV, đơn hủy, phân bố trạng thái/nền tảng, top sản phẩm và xu hướng ngày.
- Tool `get_order_by_id` và `get_order_statistics` được bind sẵn vào tenant/shop đã xác thực.
- Intent `ORDER_LOOKUP` được ưu tiên trước thống kê; follow-up lấy mã đã xác nhận từ `history` rồi
  truy vấn lại database. `ORDER_STATISTICS` phục vụ câu hỏi tổng hợp.
- Lookup/statistics trả lời xác định từ structured tool result, không dùng RAG hay LLM làm nguồn dữ
  liệu. Lỗi database được trả là tạm thời không thể kiểm tra, không bị đổi thành “không tìm thấy”.
- Log import/chat/tool có `request_id`; log không chứa nội dung đơn hoặc PII.
- Index `ix_order_owner_external(tenant_id, shop_id, external_order_id)` tăng tốc lookup.

Doanh thu thống kê được định nghĩa là tổng `selling_price × quantity` của đơn không hủy trong khoảng
`[start_at, end_at)`, chưa trừ hoàn tiền và các loại phí. Múi giờ mặc định là
`Asia/Ho_Chi_Minh`, cấu hình bằng `BUSINESS_TIMEZONE`.

## Kiểm thử và giới hạn

Suite kiểm tra import/persist, lookup đúng/sai scope, số 0 đầu, follow-up, thống kê, lỗi database và
end-to-end import → order API → chat. Database production/staging chưa được ghi dữ liệu trong audit;
mọi truy vấn xác minh database thật đều là read-only.

## Deployment checklist

1. Xác nhận web backend và AI server dùng cùng `DATABASE_URL`/environment, hoặc web backend phải gọi
   `POST /api/v1/data/import` sau khi người dùng upload.
2. Xác nhận JWT có đúng `tenant_id`, `shop_id`, `user_id`, `role`; không gửi shop tùy ý từ browser.
3. Cấu hình `BUSINESS_TIMEZONE=Asia/Ho_Chi_Minh` (hoặc timezone nghiệp vụ thực tế).
4. Chạy `python -m alembic upgrade head` để tạo index lookup.
5. Restart AI API service; không cần rebuild vector DB cho tính năng này.
6. Trên staging, import một file thật, kiểm tra import status, gọi order API với cùng JWT, rồi hỏi chat
   cùng mã và câu follow-up.
7. Rollback code về release trước và chạy `python -m alembic downgrade 20260930_0001` nếu cần bỏ
   index; migration không thay đổi hoặc xóa dữ liệu đơn.
