---
{
  "doc_id": "marketing.README",
  "title": "Tri thức marketing Finora",
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
  "source_ids": [],
  "updated_at": "2026-11-06",
  "version": "1.0.0",
  "tone": "friendly"
}
---

# Tri thức marketing Finora

## Mục lục và cách dùng
01: văn phong; 02: framework; 03: 8 caption; 04: 8 TikTok; 05: 8 listing;
06: 20 hook và 20 CTA; 07: 8 chiến lược; 08: 3 lịch 7 ngày; 09: trung thực và nền tảng;
10: 10 cặp sửa; 11: nguồn; 12: 8 Reels; 13: 8 Shopee Video; 14: quay/dựng;
15: 3 bộ chuyển thể, mỗi bộ có 3 kịch bản hoàn chỉnh cùng snapshot.
Mọi mẫu là nguyên bản giả lập, không gán cho thương hiệu thật, không có dữ liệu chứng minh hiệu quả chuyển đổi.
## Nạp, cập nhật và phân quyền
Chạy `python -m src.services.marketing.knowledge --dry-run` để kiểm tra offline;
bỏ `--dry-run` để embedding bằng provider đang cấu hình. Dùng Chroma namespace/collection riêng trong data/marketing_vectors.
Front matter là JSON trong dấu --- (JSON là tập con YAML); mỗi heading cấp 2 là một đơn vị trọn vẹn.
Giữ input facts, toàn bộ timeline và CTA dưới cùng heading. Không cắt ví dụ bằng số ký tự.
Không nhập dữ liệu shop vào scope public. CLI private cần directory riêng, --scope private --tenant-id --shop-id và front matter khớp.
Chỉ quản trị viên server chạy CLI; không có endpoint ingest công khai.
Chạy lại upsert theo hash, sửa/xóa sẽ bỏ chunk cũ đúng scope sau khi upsert thành công. Dùng đầy đủ directory cho một scope.
## Ranh giới facts
Ví dụ hướng dẫn cấu trúc, không cung cấp facts SKU thật. RAG không fine-tune model.
Khi sửa sources/rules, cập nhật version và updated_at theo lần kiểm tra thật; không tự đánh dấu nguồn đã xác minh.
Quy tắc bắt buộc còn nằm trong system prompt và validator, không phụ thuộc retrieval.
