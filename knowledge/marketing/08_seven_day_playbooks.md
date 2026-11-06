---
{
  "doc_id": "marketing.08_seven_day_playbooks",
  "title": "3 lịch đề xuất đủ 7 ngày",
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
  "content_kind": "playbooks",
  "synthetic_example": true,
  "source_ids": [],
  "updated_at": "2026-11-06",
  "version": "1.0.0",
  "tone": "friendly"
}
---

# 3 lịch đề xuất đủ 7 ngày

## Giới thiệu sản phẩm

```json
{
  "playbook_id": "playbook_1",
  "synthetic_example": true,
  "objective": "Giới thiệu sản phẩm",
  "conditions": "Dùng facts/snapshot đúng SKU; lịch ưu đãi chỉ khi BE xác nhận điều kiện và còn hiệu lực.",
  "days": [
    {
      "day": 1,
      "topic": "Tổng thể SKU",
      "channel": "facebook",
      "task": "Chuẩn bị một nội dung đã duyệt theo chủ đề; ngày không có nguồn lực có thể dùng lại bản đã rà soát.",
      "reference": null,
      "status": "needs_generation"
    },
    {
      "day": 2,
      "topic": "Cận chi tiết",
      "channel": "tiktok",
      "task": "Chuẩn bị một nội dung đã duyệt theo chủ đề; ngày không có nguồn lực có thể dùng lại bản đã rà soát.",
      "reference": null,
      "status": "needs_generation"
    },
    {
      "day": 3,
      "topic": "Tình huống dùng",
      "channel": "shopee",
      "task": "Chuẩn bị một nội dung đã duyệt theo chủ đề; ngày không có nguồn lực có thể dùng lại bản đã rà soát.",
      "reference": null,
      "status": "needs_generation"
    },
    {
      "day": 4,
      "topic": "FAQ về lựa chọn",
      "channel": "facebook",
      "task": "Chuẩn bị một nội dung đã duyệt theo chủ đề; ngày không có nguồn lực có thể dùng lại bản đã rà soát.",
      "reference": null,
      "status": "needs_generation"
    },
    {
      "day": 5,
      "topic": "Xem phân loại",
      "channel": "tiktok",
      "task": "Chuẩn bị một nội dung đã duyệt theo chủ đề; ngày không có nguồn lực có thể dùng lại bản đã rà soát.",
      "reference": null,
      "status": "needs_generation"
    },
    {
      "day": 6,
      "topic": "Ảnh nhiều góc",
      "channel": "shopee",
      "task": "Chuẩn bị một nội dung đã duyệt theo chủ đề; ngày không có nguồn lực có thể dùng lại bản đã rà soát.",
      "reference": null,
      "status": "needs_generation"
    },
    {
      "day": 7,
      "topic": "Tổng hợp thông tin",
      "channel": "facebook",
      "task": "Chuẩn bị một nội dung đã duyệt theo chủ đề; ngày không có nguồn lực có thể dùng lại bản đã rà soát.",
      "reference": null,
      "status": "needs_generation"
    }
  ],
  "measurement": "Ghi baseline lượt xem chi tiết/câu hỏi; không coi kế hoạch là đã tạo hoặc đăng nội dung."
}
```

## Giải đáp trở ngại mua

```json
{
  "playbook_id": "playbook_2",
  "synthetic_example": true,
  "objective": "Giải đáp trở ngại mua",
  "conditions": "Dùng facts/snapshot đúng SKU; lịch ưu đãi chỉ khi BE xác nhận điều kiện và còn hiệu lực.",
  "days": [
    {
      "day": 1,
      "topic": "Thu câu hỏi thật",
      "channel": "facebook",
      "task": "Chuẩn bị một nội dung đã duyệt theo chủ đề; ngày không có nguồn lực có thể dùng lại bản đã rà soát.",
      "reference": null,
      "status": "needs_generation"
    },
    {
      "day": 2,
      "topic": "Trả lời cấu tạo",
      "channel": "tiktok",
      "task": "Chuẩn bị một nội dung đã duyệt theo chủ đề; ngày không có nguồn lực có thể dùng lại bản đã rà soát.",
      "reference": null,
      "status": "needs_generation"
    },
    {
      "day": 3,
      "topic": "Demo thao tác",
      "channel": "shopee",
      "task": "Chuẩn bị một nội dung đã duyệt theo chủ đề; ngày không có nguồn lực có thể dùng lại bản đã rà soát.",
      "reference": null,
      "status": "needs_generation"
    },
    {
      "day": 4,
      "topic": "Giải thích phân loại",
      "channel": "facebook",
      "task": "Chuẩn bị một nội dung đã duyệt theo chủ đề; ngày không có nguồn lực có thể dùng lại bản đã rà soát.",
      "reference": null,
      "status": "needs_generation"
    },
    {
      "day": 5,
      "topic": "Đối chiếu bảng thông tin",
      "channel": "tiktok",
      "task": "Chuẩn bị một nội dung đã duyệt theo chủ đề; ngày không có nguồn lực có thể dùng lại bản đã rà soát.",
      "reference": null,
      "status": "needs_generation"
    },
    {
      "day": 6,
      "topic": "FAQ tiếp diễn",
      "channel": "shopee",
      "task": "Chuẩn bị một nội dung đã duyệt theo chủ đề; ngày không có nguồn lực có thể dùng lại bản đã rà soát.",
      "reference": null,
      "status": "needs_generation"
    },
    {
      "day": 7,
      "topic": "Tổng hợp câu trả lời",
      "channel": "facebook",
      "task": "Chuẩn bị một nội dung đã duyệt theo chủ đề; ngày không có nguồn lực có thể dùng lại bản đã rà soát.",
      "reference": null,
      "status": "needs_generation"
    }
  ],
  "measurement": "Ghi baseline lượt xem chi tiết/câu hỏi; không coi kế hoạch là đã tạo hoặc đăng nội dung."
}
```

## Ưu đãi đã xác nhận

```json
{
  "playbook_id": "playbook_3",
  "synthetic_example": true,
  "objective": "Ưu đãi đã xác nhận",
  "conditions": "Dùng facts/snapshot đúng SKU; lịch ưu đãi chỉ khi BE xác nhận điều kiện và còn hiệu lực.",
  "days": [
    {
      "day": 1,
      "topic": "Kiểm tra điều kiện và hiệu lực",
      "channel": "facebook",
      "task": "Chuẩn bị một nội dung đã duyệt theo chủ đề; ngày không có nguồn lực có thể dùng lại bản đã rà soát.",
      "reference": null,
      "status": "needs_generation"
    },
    {
      "day": 2,
      "topic": "Giới thiệu sản phẩm áp dụng",
      "channel": "tiktok",
      "task": "Chuẩn bị một nội dung đã duyệt theo chủ đề; ngày không có nguồn lực có thể dùng lại bản đã rà soát.",
      "reference": null,
      "status": "needs_generation"
    },
    {
      "day": 3,
      "topic": "Giải thích điều kiện",
      "channel": "shopee",
      "task": "Chuẩn bị một nội dung đã duyệt theo chủ đề; ngày không có nguồn lực có thể dùng lại bản đã rà soát.",
      "reference": null,
      "status": "needs_generation"
    },
    {
      "day": 4,
      "topic": "Demo SKU",
      "channel": "facebook",
      "task": "Chuẩn bị một nội dung đã duyệt theo chủ đề; ngày không có nguồn lực có thể dùng lại bản đã rà soát.",
      "reference": null,
      "status": "needs_generation"
    },
    {
      "day": 5,
      "topic": "FAQ ưu đãi",
      "channel": "tiktok",
      "task": "Chuẩn bị một nội dung đã duyệt theo chủ đề; ngày không có nguồn lực có thể dùng lại bản đã rà soát.",
      "reference": null,
      "status": "needs_generation"
    },
    {
      "day": 6,
      "topic": "Rà thời hạn hiện tại",
      "channel": "shopee",
      "task": "Chuẩn bị một nội dung đã duyệt theo chủ đề; ngày không có nguồn lực có thể dùng lại bản đã rà soát.",
      "reference": null,
      "status": "needs_generation"
    },
    {
      "day": 7,
      "topic": "Tổng kết và dừng khi hết hạn",
      "channel": "facebook",
      "task": "Chuẩn bị một nội dung đã duyệt theo chủ đề; ngày không có nguồn lực có thể dùng lại bản đã rà soát.",
      "reference": null,
      "status": "needs_generation"
    }
  ],
  "measurement": "Ghi baseline lượt xem chi tiết/câu hỏi; không coi kế hoạch là đã tạo hoặc đăng nội dung."
}
```
