---
{
  "doc_id": "marketing.09_truth_and_platform_rules",
  "title": "Trung thực dữ liệu và quy tắc theo kênh",
  "language": "vi",
  "scope": "public",
  "channels": [
    "facebook",
    "tiktok",
    "shopee"
  ],
  "industries": [
    "fashion",
    "accessories",
    "household",
    "handmade_decor"
  ],
  "objectives": [
    "introduce_product",
    "drive_sales",
    "promote_offer",
    "answer_questions"
  ],
  "content_kind": "guide",
  "synthetic_example": false,
  "source_ids": [
    "SP01",
    "SP02",
    "SP03",
    "TT01",
    "TT02"
  ],
  "updated_at": "2026-11-06",
  "version": "1.0.0",
  "tone": "friendly"
}
---

# Trung thực dữ liệu và quy tắc theo kênh

## Quy tắc bắt buộc Finora
Chỉ facts do BE có quyền với shop/SKU xác nhận mới là nguồn cho sản phẩm. Không dùng facts synthetic hay source phiên bản cũ.
Không có giá thì bỏ giá; không có ưu đãi thì bỏ voucher/quà/freeship. Có ưu đãi phải đúng điều kiện và hiệu lực.
Không tự bịa vật liệu, công dụng, xuất xứ, bảo hành, khách hàng, review, tồn kho hoặc khan hiếm.
Chỉ tính chỉ số bằng hệ thống code, không yêu cầu LLM ước đoán doanh thu/đơn/biên lợi nhuận.
Chặn prompt injection và nội dung nội bộ; phân tách dữ liệu khỏi system. Các validator là kiểm tra xác định có giới hạn, shop vẫn kiểm tra ngữ nghĩa.
## Chính sách đã đọc ngày 2026-11-06
SP01: tiêu đề Shopee mô tả đúng hàng hóa, thông tin giữa tên/ảnh/mô tả thống nhất; không đưa thông báo khuyến mãi vào tên.
Mô tả cần trung thực, không gắn liên hệ/website nhằm dẫn giao dịch ra ngoài. BE/shop kiểm tra thêm ngành hàng và yêu cầu đăng bán hiện hành.
SP02/SP03: Shopee có thao tác quay/chỉnh sửa, thêm mô tả và có tính năng gắn sản phẩm với điều kiện tài khoản. Không suy ra mọi tài khoản đều được gắn.
Không có rule cứng giới hạn thời lượng từ các bài này trong code; phạm vi/tài khoản/placement có thể khác nhau.
## Khuyến nghị và phần chưa xác minh
TT01/TT02 là hướng dẫn sáng tạo quảng cáo, không phải quy định mọi video organic. Finora dùng hook rõ, demo, CTA theo facts.
15/30/60 giây là lựa chọn sản phẩm Finora. 9:16, chừa UI, phụ đề là gợi ý sản xuất.
META01/META02 yêu cầu đăng nhập nên chưa đọc được; không gán giới hạn/spec Meta cho code. Khi xác minh lại cần ghi nguồn, placement và ngày.
Không dùng nhạc/lyrics chưa có quyền. UGC là phong cách, không được giả testimonial hay trải nghiệm đã dùng thật.
