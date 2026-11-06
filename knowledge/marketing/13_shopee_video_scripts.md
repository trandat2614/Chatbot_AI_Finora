---
{
  "doc_id": "marketing.13_shopee_video_scripts",
  "title": "Kịch bản video: shopee",
  "language": "vi",
  "scope": "public",
  "channels": [
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
  "content_kind": "video_examples",
  "synthetic_example": true,
  "source_ids": [
    "SP02",
    "SP03"
  ],
  "updated_at": "2026-11-06",
  "version": "1.0.0",
  "tone": "friendly",
  "targets": [
    [
      "shopee",
      "video",
      "video_script"
    ]
  ]
}
---

# Kịch bản video: shopee

## Mẫu 1: Áo thun cổ tròn

```json
{
  "example_id": "shopee_video_script_01",
  "channel": "shopee",
  "industry": "fashion",
  "audience": "người thích trang phục đơn giản",
  "objective": "introduce_product",
  "input_facts": {
    "sku": "AT001",
    "name": "Áo thun cổ tròn",
    "source": "synthetic_fixture",
    "updated_at": "2026-11-06T09:00:00+07:00",
    "industry": "fashion",
    "attributes": [
      {
        "key": "material",
        "value": "cotton",
        "source": "synthetic_fixture"
      },
      {
        "key": "color",
        "value": "trắng",
        "source": "synthetic_fixture"
      },
      {
        "key": "neck",
        "value": "cổ tròn",
        "source": "synthetic_fixture"
      }
    ],
    "price": null,
    "currency": "VND",
    "product_url": null,
    "offer": null,
    "evidence": []
  },
  "tone": "friendly",
  "framework": "FAB",
  "synthetic_example": true,
  "content": {
    "content_type": "video_script",
    "title": "Áo thun cổ tròn — Áo có kiểu cổ nào?",
    "concept": "Xem cổ và màu áo trước khi chọn phân loại.",
    "angle": "Xem chi tiết để lựa chọn",
    "objective": "introduce_product",
    "audience": "người thích trang phục đơn giản",
    "hook": "Xem cổ và màu áo trước khi chọn phân loại.",
    "key_message": "Áo thun cổ tròn",
    "total_duration_seconds": 15,
    "production_mode": "hands_only",
    "video_style": "product_demo",
    "scenes": [
      {
        "scene_id": "s1",
        "start_seconds": 0.0,
        "end_seconds": 4.0,
        "duration_seconds": 4.0,
        "visual_action": "Đặt áo lên mặt bàn, kéo phần cổ vào khung hình. Đặt nhãn tên sản phẩm cùng khung hình.",
        "shot_type": "toàn cảnh sản phẩm",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": "Đây là áo thun cổ tròn.",
        "on_screen_text": "Áo thun cổ tròn",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      },
      {
        "scene_id": "s2",
        "start_seconds": 4.0,
        "end_seconds": 10.0,
        "duration_seconds": 6.0,
        "visual_action": "Hai tay mở phẳng cổ áo rồi quay cận bề mặt vải.",
        "shot_type": "cận cảnh",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": "Chất liệu cotton, màu trắng.",
        "on_screen_text": "Cotton · trắng",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      },
      {
        "scene_id": "s3",
        "start_seconds": 10.0,
        "end_seconds": 15.0,
        "duration_seconds": 5.0,
        "visual_action": "Giữ toàn bộ áo trong khung hình, đặt thẻ tên bên cạnh.",
        "shot_type": "toàn cảnh sản phẩm",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": "Tìm sản phẩm trong shop để xem chi tiết.",
        "on_screen_text": "Tìm sản phẩm trong shop",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      }
    ],
    "cta": {
      "text": "Tìm sản phẩm trong shop để xem chi tiết.",
      "action": "view_product",
      "display_condition": "Dùng khi shop đã kiểm tra thông tin sản phẩm hiện tại."
    },
    "product_attachment_note": "Kiểm tra quyền gắn đúng SKU trước khi đăng; chưa xác nhận đã gắn.",
    "post_caption": "Áo có kiểu cổ nào? Xem chi tiết sản phẩm trong shop.",
    "hashtags": [],
    "cover_text": "Áo thun cổ tròn",
    "production": {
      "shot_list": [
        "Đặt áo lên mặt bàn, kéo phần cổ vào khung hình.",
        "Hai tay mở phẳng cổ áo rồi quay cận bề mặt vải.",
        "Giữ toàn bộ áo trong khung hình, đặt thẻ tên bên cạnh."
      ],
      "props": [
        "Áo thun cổ tròn",
        "mặt bàn"
      ],
      "location": "mặt bàn",
      "actors": 1,
      "filming_checklist": [
        "Lau ống kính.",
        "Đọc lại facts và kiểm tra sản phẩm đúng SKU.",
        "Quay dọc, kiểm tra chữ không bị giao diện che."
      ],
      "editing_guide": [
        "Ghép đúng timeline.",
        "Đồng bộ chữ với thao tác.",
        "Kiểm tra âm thanh và phụ đề trước khi xuất."
      ]
    },
    "plain_text": "Áo thun cổ tròn — Áo có kiểu cổ nào?\n\nXem cổ và màu áo trước khi chọn phân loại.\n\nThời gian — Cảnh quay — Lời thoại/voiceover — Chữ trên màn hình — Ghi chú dựng\n\n0–4s — Đặt áo lên mặt bàn, kéo phần cổ vào khung hình. Đặt nhãn tên sản phẩm cùng khung hình. — Đây là áo thun cổ tròn. — Áo thun cổ tròn — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n4–10s — Hai tay mở phẳng cổ áo rồi quay cận bề mặt vải. — Chất liệu cotton, màu trắng. — Cotton · trắng — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n10–15s — Giữ toàn bộ áo trong khung hình, đặt thẻ tên bên cạnh. — Tìm sản phẩm trong shop để xem chi tiết. — Tìm sản phẩm trong shop — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\nTìm sản phẩm trong shop để xem chi tiết.\n\nÁo có kiểu cổ nào? Xem chi tiết sản phẩm trong shop."
  },
  "cta": {
    "text": "Tìm sản phẩm trong shop để xem chi tiết.",
    "action": "view_product",
    "display_condition": "Dùng khi shop đã kiểm tra thông tin sản phẩm hiện tại."
  },
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```

## Mẫu 2: Túi đeo chéo

```json
{
  "example_id": "shopee_video_script_02",
  "channel": "shopee",
  "industry": "accessories",
  "audience": "người cần sắp xếp đồ mang theo",
  "objective": "introduce_product",
  "input_facts": {
    "sku": "TUI002",
    "name": "Túi đeo chéo",
    "source": "synthetic_fixture",
    "updated_at": "2026-11-06T09:00:00+07:00",
    "industry": "accessories",
    "attributes": [
      {
        "key": "color",
        "value": "đen",
        "source": "synthetic_fixture"
      },
      {
        "key": "compartments",
        "value": "hai ngăn",
        "source": "synthetic_fixture"
      },
      {
        "key": "strap",
        "value": "dây điều chỉnh được",
        "source": "synthetic_fixture"
      }
    ],
    "price": null,
    "currency": "VND",
    "product_url": null,
    "offer": null,
    "evidence": []
  },
  "tone": "friendly",
  "framework": "AIDA",
  "synthetic_example": true,
  "content": {
    "content_type": "video_script",
    "title": "Túi đeo chéo — Dây túi có điều chỉnh được không?",
    "concept": "Mở từng ngăn của túi trước khi chọn mua.",
    "angle": "Xem chi tiết để lựa chọn",
    "objective": "introduce_product",
    "audience": "người cần sắp xếp đồ mang theo",
    "hook": "Mở từng ngăn của túi trước khi chọn mua.",
    "key_message": "Túi đeo chéo",
    "total_duration_seconds": 30,
    "production_mode": "voiceover",
    "video_style": "tutorial",
    "scenes": [
      {
        "scene_id": "s1",
        "start_seconds": 0.0,
        "end_seconds": 5.0,
        "duration_seconds": 5.0,
        "visual_action": "Quay từ trên xuống túi đang đóng, bàn tay đặt cạnh túi. Đặt nhãn tên sản phẩm cùng khung hình.",
        "shot_type": "toàn cảnh sản phẩm",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": "Đây là túi đeo chéo màu đen.",
        "on_screen_text": "Túi đeo chéo",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      },
      {
        "scene_id": "s2",
        "start_seconds": 5.0,
        "end_seconds": 14.0,
        "duration_seconds": 9.0,
        "visual_action": "Mở ngăn phía trước rồi ngăn phía sau, giữ mỗi ngăn trong khung hình.",
        "shot_type": "cận cảnh",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": "Túi có hai ngăn để bạn chọn cách chia đồ.",
        "on_screen_text": "Hai ngăn",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      },
      {
        "scene_id": "s3",
        "start_seconds": 14.0,
        "end_seconds": 24.0,
        "duration_seconds": 10.0,
        "visual_action": "Tay điều chỉnh dây, dừng để thấy vị trí thay đổi.",
        "shot_type": "cận cảnh",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": "Dây điều chỉnh được. Hãy xem chi tiết dây khi lựa chọn.",
        "on_screen_text": "Dây điều chỉnh được",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      },
      {
        "scene_id": "s4",
        "start_seconds": 24.0,
        "end_seconds": 30.0,
        "duration_seconds": 6.0,
        "visual_action": "Đóng túi, đặt ngay ngắn dưới máy quay.",
        "shot_type": "toàn cảnh sản phẩm",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": "Tìm sản phẩm trong shop để xem chi tiết.",
        "on_screen_text": "Tìm sản phẩm trong shop",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      }
    ],
    "cta": {
      "text": "Tìm sản phẩm trong shop để xem chi tiết.",
      "action": "view_product",
      "display_condition": "Dùng khi shop đã kiểm tra thông tin sản phẩm hiện tại."
    },
    "product_attachment_note": "Kiểm tra quyền gắn đúng SKU trước khi đăng; chưa xác nhận đã gắn.",
    "post_caption": "Dây túi có điều chỉnh được không? Xem chi tiết sản phẩm trong shop.",
    "hashtags": [],
    "cover_text": "Túi đeo chéo",
    "production": {
      "shot_list": [
        "Quay từ trên xuống túi đang đóng, bàn tay đặt cạnh túi.",
        "Mở ngăn phía trước rồi ngăn phía sau, giữ mỗi ngăn trong khung hình.",
        "Tay điều chỉnh dây, dừng để thấy vị trí thay đổi.",
        "Đóng túi, đặt ngay ngắn dưới máy quay."
      ],
      "props": [
        "Túi đeo chéo",
        "bàn trống"
      ],
      "location": "bàn trống",
      "actors": 1,
      "filming_checklist": [
        "Lau ống kính.",
        "Đọc lại facts và kiểm tra sản phẩm đúng SKU.",
        "Quay dọc, kiểm tra chữ không bị giao diện che."
      ],
      "editing_guide": [
        "Ghép đúng timeline.",
        "Đồng bộ chữ với thao tác.",
        "Kiểm tra âm thanh và phụ đề trước khi xuất."
      ]
    },
    "plain_text": "Túi đeo chéo — Dây túi có điều chỉnh được không?\n\nMở từng ngăn của túi trước khi chọn mua.\n\nThời gian — Cảnh quay — Lời thoại/voiceover — Chữ trên màn hình — Ghi chú dựng\n\n0–5s — Quay từ trên xuống túi đang đóng, bàn tay đặt cạnh túi. Đặt nhãn tên sản phẩm cùng khung hình. — Đây là túi đeo chéo màu đen. — Túi đeo chéo — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n5–14s — Mở ngăn phía trước rồi ngăn phía sau, giữ mỗi ngăn trong khung hình. — Túi có hai ngăn để bạn chọn cách chia đồ. — Hai ngăn — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n14–24s — Tay điều chỉnh dây, dừng để thấy vị trí thay đổi. — Dây điều chỉnh được. Hãy xem chi tiết dây khi lựa chọn. — Dây điều chỉnh được — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n24–30s — Đóng túi, đặt ngay ngắn dưới máy quay. — Tìm sản phẩm trong shop để xem chi tiết. — Tìm sản phẩm trong shop — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\nTìm sản phẩm trong shop để xem chi tiết.\n\nDây túi có điều chỉnh được không? Xem chi tiết sản phẩm trong shop."
  },
  "cta": {
    "text": "Tìm sản phẩm trong shop để xem chi tiết.",
    "action": "view_product",
    "display_condition": "Dùng khi shop đã kiểm tra thông tin sản phẩm hiện tại."
  },
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```

## Mẫu 3: Khay để bàn

```json
{
  "example_id": "shopee_video_script_03",
  "channel": "shopee",
  "industry": "household",
  "audience": "người muốn bố trí góc làm việc",
  "objective": "introduce_product",
  "input_facts": {
    "sku": "KHAY003",
    "name": "Khay để bàn",
    "source": "synthetic_fixture",
    "updated_at": "2026-11-06T09:00:00+07:00",
    "industry": "household",
    "attributes": [
      {
        "key": "material",
        "value": "gỗ",
        "source": "synthetic_fixture"
      },
      {
        "key": "shape",
        "value": "hình chữ nhật",
        "source": "synthetic_fixture"
      },
      {
        "key": "color",
        "value": "nâu",
        "source": "synthetic_fixture"
      }
    ],
    "price": null,
    "currency": "VND",
    "product_url": null,
    "offer": null,
    "evidence": []
  },
  "tone": "friendly",
  "framework": "FAB",
  "synthetic_example": true,
  "content": {
    "content_type": "video_script",
    "title": "Khay để bàn — Khay có hình dạng gì?",
    "concept": "Xem hình dáng và chất liệu khay để bàn.",
    "angle": "Xem chi tiết để lựa chọn",
    "objective": "introduce_product",
    "audience": "người muốn bố trí góc làm việc",
    "hook": "Xem hình dáng và chất liệu khay để bàn.",
    "key_message": "Khay để bàn",
    "total_duration_seconds": 60,
    "production_mode": "text_only",
    "video_style": "scenario",
    "scenes": [
      {
        "scene_id": "s1",
        "start_seconds": 0.0,
        "end_seconds": 6.0,
        "duration_seconds": 6.0,
        "visual_action": "Quay góc bàn trống, đưa khay vào giữa khung hình. Đặt nhãn tên sản phẩm cùng khung hình.",
        "shot_type": "toàn cảnh sản phẩm",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": null,
        "on_screen_text": "Khay để bàn",
        "audio_direction": "Âm thanh thao tác thật; không cần nhạc.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      },
      {
        "scene_id": "s2",
        "start_seconds": 6.0,
        "end_seconds": 20.0,
        "duration_seconds": 14.0,
        "visual_action": "Quay cạnh dài và cạnh ngắn để thấy hình chữ nhật.",
        "shot_type": "cận cảnh",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": null,
        "on_screen_text": "Hình chữ nhật",
        "audio_direction": "Âm thanh thao tác thật; không cần nhạc.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      },
      {
        "scene_id": "s3",
        "start_seconds": 20.0,
        "end_seconds": 36.0,
        "duration_seconds": 16.0,
        "visual_action": "Đổi sang góc nghiêng, giữ cận bề mặt gỗ.",
        "shot_type": "cận cảnh",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": null,
        "on_screen_text": "Gỗ · màu nâu",
        "audio_direction": "Âm thanh thao tác thật; không cần nhạc.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      },
      {
        "scene_id": "s4",
        "start_seconds": 36.0,
        "end_seconds": 50.0,
        "duration_seconds": 14.0,
        "visual_action": "Đặt khay vào vị trí dự kiến sử dụng, quay tổng thể.",
        "shot_type": "cận cảnh",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": null,
        "on_screen_text": "Bạn sẽ đặt khay ở góc nào?",
        "audio_direction": "Âm thanh thao tác thật; không cần nhạc.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      },
      {
        "scene_id": "s5",
        "start_seconds": 50.0,
        "end_seconds": 60.0,
        "duration_seconds": 10.0,
        "visual_action": "Đưa thẻ tên sản phẩm cạnh khay, giữ khung hình tĩnh.",
        "shot_type": "toàn cảnh sản phẩm",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": null,
        "on_screen_text": "Tìm sản phẩm trong shop",
        "audio_direction": "Âm thanh thao tác thật; không cần nhạc.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      }
    ],
    "cta": {
      "text": "Tìm sản phẩm trong shop để xem chi tiết.",
      "action": "view_product",
      "display_condition": "Dùng khi shop đã kiểm tra thông tin sản phẩm hiện tại."
    },
    "product_attachment_note": "Kiểm tra quyền gắn đúng SKU trước khi đăng; chưa xác nhận đã gắn.",
    "post_caption": "Khay có hình dạng gì? Xem chi tiết sản phẩm trong shop.",
    "hashtags": [],
    "cover_text": "Khay để bàn",
    "production": {
      "shot_list": [
        "Quay góc bàn trống, đưa khay vào giữa khung hình.",
        "Quay cạnh dài và cạnh ngắn để thấy hình chữ nhật.",
        "Đổi sang góc nghiêng, giữ cận bề mặt gỗ.",
        "Đặt khay vào vị trí dự kiến sử dụng, quay tổng thể.",
        "Đưa thẻ tên sản phẩm cạnh khay, giữ khung hình tĩnh."
      ],
      "props": [
        "Khay để bàn",
        "góc bàn"
      ],
      "location": "góc bàn",
      "actors": 1,
      "filming_checklist": [
        "Lau ống kính.",
        "Đọc lại facts và kiểm tra sản phẩm đúng SKU.",
        "Quay dọc, kiểm tra chữ không bị giao diện che."
      ],
      "editing_guide": [
        "Ghép đúng timeline.",
        "Đồng bộ chữ với thao tác.",
        "Kiểm tra âm thanh và phụ đề trước khi xuất."
      ]
    },
    "plain_text": "Khay để bàn — Khay có hình dạng gì?\n\nXem hình dáng và chất liệu khay để bàn.\n\nThời gian — Cảnh quay — Lời thoại/voiceover — Chữ trên màn hình — Ghi chú dựng\n\n0–6s — Quay góc bàn trống, đưa khay vào giữa khung hình. Đặt nhãn tên sản phẩm cùng khung hình. —  — Khay để bàn — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n6–20s — Quay cạnh dài và cạnh ngắn để thấy hình chữ nhật. —  — Hình chữ nhật — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n20–36s — Đổi sang góc nghiêng, giữ cận bề mặt gỗ. —  — Gỗ · màu nâu — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n36–50s — Đặt khay vào vị trí dự kiến sử dụng, quay tổng thể. —  — Bạn sẽ đặt khay ở góc nào? — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n50–60s — Đưa thẻ tên sản phẩm cạnh khay, giữ khung hình tĩnh. —  — Tìm sản phẩm trong shop — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\nTìm sản phẩm trong shop để xem chi tiết.\n\nKhay có hình dạng gì? Xem chi tiết sản phẩm trong shop."
  },
  "cta": {
    "text": "Tìm sản phẩm trong shop để xem chi tiết.",
    "action": "view_product",
    "display_condition": "Dùng khi shop đã kiểm tra thông tin sản phẩm hiện tại."
  },
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```

## Mẫu 4: Bình gốm trang trí

```json
{
  "example_id": "shopee_video_script_04",
  "channel": "shopee",
  "industry": "handmade_decor",
  "audience": "người thích trang trí kệ nhỏ",
  "objective": "introduce_product",
  "input_facts": {
    "sku": "BINH004",
    "name": "Bình gốm trang trí",
    "source": "synthetic_fixture",
    "updated_at": "2026-11-06T09:00:00+07:00",
    "industry": "handmade_decor",
    "attributes": [
      {
        "key": "material",
        "value": "gốm",
        "source": "synthetic_fixture"
      },
      {
        "key": "color",
        "value": "kem",
        "source": "synthetic_fixture"
      },
      {
        "key": "finish",
        "value": "bề mặt nhám",
        "source": "synthetic_fixture"
      }
    ],
    "price": null,
    "currency": "VND",
    "product_url": null,
    "offer": null,
    "evidence": []
  },
  "tone": "friendly",
  "framework": "AIDA",
  "synthetic_example": true,
  "content": {
    "content_type": "video_script",
    "title": "Bình gốm trang trí — Bề mặt bình bóng hay nhám?",
    "concept": "Cận cảnh bình gốm trước khi chọn đồ trang trí.",
    "angle": "Xem chi tiết để lựa chọn",
    "objective": "introduce_product",
    "audience": "người thích trang trí kệ nhỏ",
    "hook": "Cận cảnh bình gốm trước khi chọn đồ trang trí.",
    "key_message": "Bình gốm trang trí",
    "total_duration_seconds": 30,
    "production_mode": "on_camera",
    "video_style": "presenter",
    "scenes": [
      {
        "scene_id": "s1",
        "start_seconds": 0.0,
        "end_seconds": 5.0,
        "duration_seconds": 5.0,
        "visual_action": "Người dẫn cầm bình ngang ngực, đứng cạnh kệ trống. Đặt nhãn tên sản phẩm cùng khung hình.",
        "shot_type": "toàn cảnh sản phẩm",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": "Bạn đang tìm đồ trang trí cho góc kệ?",
        "voiceover": null,
        "on_screen_text": "Góc kệ của bạn",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": true
      },
      {
        "scene_id": "s2",
        "start_seconds": 5.0,
        "end_seconds": 14.0,
        "duration_seconds": 9.0,
        "visual_action": "Đưa bình lại gần máy để thấy màu và bề mặt.",
        "shot_type": "cận cảnh",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": "Đây là bình gốm trang trí màu kem, bề mặt nhám.",
        "voiceover": null,
        "on_screen_text": "Gốm · kem · bề mặt nhám",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": true
      },
      {
        "scene_id": "s3",
        "start_seconds": 14.0,
        "end_seconds": 24.0,
        "duration_seconds": 10.0,
        "visual_action": "Đặt bình lên kệ, lùi ra để thấy vị trí.",
        "shot_type": "cận cảnh",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": "Hãy nhìn màu bình cạnh đồ bạn đang có.",
        "voiceover": null,
        "on_screen_text": "Cân nhắc vị trí đặt",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": true
      },
      {
        "scene_id": "s4",
        "start_seconds": 24.0,
        "end_seconds": 30.0,
        "duration_seconds": 6.0,
        "visual_action": "Chỉ tay về bình, giữ tên sản phẩm trên khung hình.",
        "shot_type": "toàn cảnh sản phẩm",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": "Tìm sản phẩm trong shop để xem chi tiết.",
        "voiceover": null,
        "on_screen_text": "Tìm sản phẩm trong shop",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": true
      }
    ],
    "cta": {
      "text": "Tìm sản phẩm trong shop để xem chi tiết.",
      "action": "view_product",
      "display_condition": "Dùng khi shop đã kiểm tra thông tin sản phẩm hiện tại."
    },
    "product_attachment_note": "Kiểm tra quyền gắn đúng SKU trước khi đăng; chưa xác nhận đã gắn.",
    "post_caption": "Bề mặt bình bóng hay nhám? Xem chi tiết sản phẩm trong shop.",
    "hashtags": [],
    "cover_text": "Bình gốm trang trí",
    "production": {
      "shot_list": [
        "Người dẫn cầm bình ngang ngực, đứng cạnh kệ trống.",
        "Đưa bình lại gần máy để thấy màu và bề mặt.",
        "Đặt bình lên kệ, lùi ra để thấy vị trí.",
        "Chỉ tay về bình, giữ tên sản phẩm trên khung hình."
      ],
      "props": [
        "Bình gốm trang trí",
        "kệ trống"
      ],
      "location": "kệ trống",
      "actors": 1,
      "filming_checklist": [
        "Lau ống kính.",
        "Đọc lại facts và kiểm tra sản phẩm đúng SKU.",
        "Quay dọc, kiểm tra chữ không bị giao diện che."
      ],
      "editing_guide": [
        "Ghép đúng timeline.",
        "Đồng bộ chữ với thao tác.",
        "Kiểm tra âm thanh và phụ đề trước khi xuất."
      ]
    },
    "plain_text": "Bình gốm trang trí — Bề mặt bình bóng hay nhám?\n\nCận cảnh bình gốm trước khi chọn đồ trang trí.\n\nThời gian — Cảnh quay — Lời thoại/voiceover — Chữ trên màn hình — Ghi chú dựng\n\n0–5s — Người dẫn cầm bình ngang ngực, đứng cạnh kệ trống. Đặt nhãn tên sản phẩm cùng khung hình. — Bạn đang tìm đồ trang trí cho góc kệ? — Góc kệ của bạn — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n5–14s — Đưa bình lại gần máy để thấy màu và bề mặt. — Đây là bình gốm trang trí màu kem, bề mặt nhám. — Gốm · kem · bề mặt nhám — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n14–24s — Đặt bình lên kệ, lùi ra để thấy vị trí. — Hãy nhìn màu bình cạnh đồ bạn đang có. — Cân nhắc vị trí đặt — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n24–30s — Chỉ tay về bình, giữ tên sản phẩm trên khung hình. — Tìm sản phẩm trong shop để xem chi tiết. — Tìm sản phẩm trong shop — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\nTìm sản phẩm trong shop để xem chi tiết.\n\nBề mặt bình bóng hay nhám? Xem chi tiết sản phẩm trong shop."
  },
  "cta": {
    "text": "Tìm sản phẩm trong shop để xem chi tiết.",
    "action": "view_product",
    "display_condition": "Dùng khi shop đã kiểm tra thông tin sản phẩm hiện tại."
  },
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```

## Mẫu 5: Kẹp tóc

```json
{
  "example_id": "shopee_video_script_05",
  "channel": "shopee",
  "industry": "accessories",
  "audience": "người muốn xem thao tác kẹp tóc",
  "objective": "introduce_product",
  "input_facts": {
    "sku": "KEP005",
    "name": "Kẹp tóc",
    "source": "synthetic_fixture",
    "updated_at": "2026-11-06T09:00:00+07:00",
    "industry": "accessories",
    "attributes": [
      {
        "key": "color",
        "value": "nâu",
        "source": "synthetic_fixture"
      },
      {
        "key": "mechanism",
        "value": "dạng càng cua",
        "source": "synthetic_fixture"
      },
      {
        "key": "surface",
        "value": "bề mặt trơn",
        "source": "synthetic_fixture"
      }
    ],
    "price": null,
    "currency": "VND",
    "product_url": null,
    "offer": null,
    "evidence": []
  },
  "tone": "friendly",
  "framework": "FAB",
  "synthetic_example": true,
  "content": {
    "content_type": "video_script",
    "title": "Kẹp tóc — Kẹp có cơ chế nào?",
    "concept": "Cận cảnh cơ chế kẹp tóc dạng càng cua.",
    "angle": "Xem chi tiết để lựa chọn",
    "objective": "introduce_product",
    "audience": "người muốn xem thao tác kẹp tóc",
    "hook": "Cận cảnh cơ chế kẹp tóc dạng càng cua.",
    "key_message": "Kẹp tóc",
    "total_duration_seconds": 15,
    "production_mode": "hands_only",
    "video_style": "faq",
    "scenes": [
      {
        "scene_id": "s1",
        "start_seconds": 0.0,
        "end_seconds": 4.0,
        "duration_seconds": 4.0,
        "visual_action": "Giữ kẹp trên nền sáng, nhìn từ cạnh bên. Đặt nhãn tên sản phẩm cùng khung hình.",
        "shot_type": "toàn cảnh sản phẩm",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": "Kẹp tóc dạng càng cua.",
        "on_screen_text": "Kẹp tóc",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      },
      {
        "scene_id": "s2",
        "start_seconds": 4.0,
        "end_seconds": 10.0,
        "duration_seconds": 6.0,
        "visual_action": "Bàn tay bóp rồi thả kẹp, giữ rõ phần càng.",
        "shot_type": "cận cảnh",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": "Xem thao tác mở và khép kẹp.",
        "on_screen_text": "Dạng càng cua",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      },
      {
        "scene_id": "s3",
        "start_seconds": 10.0,
        "end_seconds": 15.0,
        "duration_seconds": 5.0,
        "visual_action": "Đặt kẹp xuống, quay cận màu và thẻ tên.",
        "shot_type": "toàn cảnh sản phẩm",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": "Tìm sản phẩm trong shop để xem chi tiết.",
        "on_screen_text": "Tìm sản phẩm trong shop",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      }
    ],
    "cta": {
      "text": "Tìm sản phẩm trong shop để xem chi tiết.",
      "action": "view_product",
      "display_condition": "Dùng khi shop đã kiểm tra thông tin sản phẩm hiện tại."
    },
    "product_attachment_note": "Kiểm tra quyền gắn đúng SKU trước khi đăng; chưa xác nhận đã gắn.",
    "post_caption": "Kẹp có cơ chế nào? Xem chi tiết sản phẩm trong shop.",
    "hashtags": [],
    "cover_text": "Kẹp tóc",
    "production": {
      "shot_list": [
        "Giữ kẹp trên nền sáng, nhìn từ cạnh bên.",
        "Bàn tay bóp rồi thả kẹp, giữ rõ phần càng.",
        "Đặt kẹp xuống, quay cận màu và thẻ tên."
      ],
      "props": [
        "Kẹp tóc",
        "tấm nền sáng"
      ],
      "location": "tấm nền sáng",
      "actors": 1,
      "filming_checklist": [
        "Lau ống kính.",
        "Đọc lại facts và kiểm tra sản phẩm đúng SKU.",
        "Quay dọc, kiểm tra chữ không bị giao diện che."
      ],
      "editing_guide": [
        "Ghép đúng timeline.",
        "Đồng bộ chữ với thao tác.",
        "Kiểm tra âm thanh và phụ đề trước khi xuất."
      ]
    },
    "plain_text": "Kẹp tóc — Kẹp có cơ chế nào?\n\nCận cảnh cơ chế kẹp tóc dạng càng cua.\n\nThời gian — Cảnh quay — Lời thoại/voiceover — Chữ trên màn hình — Ghi chú dựng\n\n0–4s — Giữ kẹp trên nền sáng, nhìn từ cạnh bên. Đặt nhãn tên sản phẩm cùng khung hình. — Kẹp tóc dạng càng cua. — Kẹp tóc — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n4–10s — Bàn tay bóp rồi thả kẹp, giữ rõ phần càng. — Xem thao tác mở và khép kẹp. — Dạng càng cua — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n10–15s — Đặt kẹp xuống, quay cận màu và thẻ tên. — Tìm sản phẩm trong shop để xem chi tiết. — Tìm sản phẩm trong shop — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\nTìm sản phẩm trong shop để xem chi tiết.\n\nKẹp có cơ chế nào? Xem chi tiết sản phẩm trong shop."
  },
  "cta": {
    "text": "Tìm sản phẩm trong shop để xem chi tiết.",
    "action": "view_product",
    "display_condition": "Dùng khi shop đã kiểm tra thông tin sản phẩm hiện tại."
  },
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```

## Mẫu 6: Hộp đựng đồ

```json
{
  "example_id": "shopee_video_script_06",
  "channel": "shopee",
  "industry": "household",
  "audience": "người cần phân loại đồ nhỏ",
  "objective": "introduce_product",
  "input_facts": {
    "sku": "HOP006",
    "name": "Hộp đựng đồ",
    "source": "synthetic_fixture",
    "updated_at": "2026-11-06T09:00:00+07:00",
    "industry": "household",
    "attributes": [
      {
        "key": "material",
        "value": "nhựa",
        "source": "synthetic_fixture"
      },
      {
        "key": "lid",
        "value": "nắp rời",
        "source": "synthetic_fixture"
      },
      {
        "key": "color",
        "value": "trong suốt",
        "source": "synthetic_fixture"
      }
    ],
    "price": null,
    "currency": "VND",
    "product_url": null,
    "offer": null,
    "evidence": []
  },
  "tone": "friendly",
  "framework": "AIDA",
  "synthetic_example": true,
  "content": {
    "content_type": "video_script",
    "title": "Hộp đựng đồ — Nắp có gắn liền với hộp không?",
    "concept": "Kiểm tra hộp và nắp rời trước khi chọn.",
    "angle": "Xem chi tiết để lựa chọn",
    "objective": "introduce_product",
    "audience": "người cần phân loại đồ nhỏ",
    "hook": "Kiểm tra hộp và nắp rời trước khi chọn.",
    "key_message": "Hộp đựng đồ",
    "total_duration_seconds": 60,
    "production_mode": "voiceover",
    "video_style": "unboxing",
    "scenes": [
      {
        "scene_id": "s1",
        "start_seconds": 0.0,
        "end_seconds": 6.0,
        "duration_seconds": 6.0,
        "visual_action": "Đặt hộp trên bàn, quay toàn bộ hộp và nắp. Đặt nhãn tên sản phẩm cùng khung hình.",
        "shot_type": "toàn cảnh sản phẩm",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": "Đây là hộp đựng đồ bằng nhựa.",
        "on_screen_text": "Hộp đựng đồ",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      },
      {
        "scene_id": "s2",
        "start_seconds": 6.0,
        "end_seconds": 20.0,
        "duration_seconds": 14.0,
        "visual_action": "Nhấc nắp rời ra, đặt cạnh thân hộp.",
        "shot_type": "cận cảnh",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": "Nắp rời được nhấc ra riêng khi mở hộp.",
        "on_screen_text": "Nắp rời",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      },
      {
        "scene_id": "s3",
        "start_seconds": 20.0,
        "end_seconds": 36.0,
        "duration_seconds": 16.0,
        "visual_action": "Quay góc nghiêng của thân hộp trong suốt.",
        "shot_type": "cận cảnh",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": "Màu trong suốt giúp bạn nhìn hình dáng phần thân.",
        "on_screen_text": "Nhựa · trong suốt",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      },
      {
        "scene_id": "s4",
        "start_seconds": 36.0,
        "end_seconds": 50.0,
        "duration_seconds": 14.0,
        "visual_action": "Đặt nắp trở lại rồi mở lần nữa thật chậm.",
        "shot_type": "cận cảnh",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": "Hãy xem cách mở nắp trước khi cân nhắc lựa chọn.",
        "on_screen_text": "Xem thao tác mở nắp",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      },
      {
        "scene_id": "s5",
        "start_seconds": 50.0,
        "end_seconds": 60.0,
        "duration_seconds": 10.0,
        "visual_action": "Xếp hộp và nắp cạnh nhau cùng thẻ tên.",
        "shot_type": "toàn cảnh sản phẩm",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": "Tìm sản phẩm trong shop để xem chi tiết.",
        "on_screen_text": "Tìm sản phẩm trong shop",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      }
    ],
    "cta": {
      "text": "Tìm sản phẩm trong shop để xem chi tiết.",
      "action": "view_product",
      "display_condition": "Dùng khi shop đã kiểm tra thông tin sản phẩm hiện tại."
    },
    "product_attachment_note": "Kiểm tra quyền gắn đúng SKU trước khi đăng; chưa xác nhận đã gắn.",
    "post_caption": "Nắp có gắn liền với hộp không? Xem chi tiết sản phẩm trong shop.",
    "hashtags": [],
    "cover_text": "Hộp đựng đồ",
    "production": {
      "shot_list": [
        "Đặt hộp trên bàn, quay toàn bộ hộp và nắp.",
        "Nhấc nắp rời ra, đặt cạnh thân hộp.",
        "Quay góc nghiêng của thân hộp trong suốt.",
        "Đặt nắp trở lại rồi mở lần nữa thật chậm.",
        "Xếp hộp và nắp cạnh nhau cùng thẻ tên."
      ],
      "props": [
        "Hộp đựng đồ",
        "bàn sáng"
      ],
      "location": "bàn sáng",
      "actors": 1,
      "filming_checklist": [
        "Lau ống kính.",
        "Đọc lại facts và kiểm tra sản phẩm đúng SKU.",
        "Quay dọc, kiểm tra chữ không bị giao diện che."
      ],
      "editing_guide": [
        "Ghép đúng timeline.",
        "Đồng bộ chữ với thao tác.",
        "Kiểm tra âm thanh và phụ đề trước khi xuất."
      ]
    },
    "plain_text": "Hộp đựng đồ — Nắp có gắn liền với hộp không?\n\nKiểm tra hộp và nắp rời trước khi chọn.\n\nThời gian — Cảnh quay — Lời thoại/voiceover — Chữ trên màn hình — Ghi chú dựng\n\n0–6s — Đặt hộp trên bàn, quay toàn bộ hộp và nắp. Đặt nhãn tên sản phẩm cùng khung hình. — Đây là hộp đựng đồ bằng nhựa. — Hộp đựng đồ — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n6–20s — Nhấc nắp rời ra, đặt cạnh thân hộp. — Nắp rời được nhấc ra riêng khi mở hộp. — Nắp rời — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n20–36s — Quay góc nghiêng của thân hộp trong suốt. — Màu trong suốt giúp bạn nhìn hình dáng phần thân. — Nhựa · trong suốt — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n36–50s — Đặt nắp trở lại rồi mở lần nữa thật chậm. — Hãy xem cách mở nắp trước khi cân nhắc lựa chọn. — Xem thao tác mở nắp — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n50–60s — Xếp hộp và nắp cạnh nhau cùng thẻ tên. — Tìm sản phẩm trong shop để xem chi tiết. — Tìm sản phẩm trong shop — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\nTìm sản phẩm trong shop để xem chi tiết.\n\nNắp có gắn liền với hộp không? Xem chi tiết sản phẩm trong shop."
  },
  "cta": {
    "text": "Tìm sản phẩm trong shop để xem chi tiết.",
    "action": "view_product",
    "display_condition": "Dùng khi shop đã kiểm tra thông tin sản phẩm hiện tại."
  },
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```

## Mẫu 7: Sổ tay bìa vải

```json
{
  "example_id": "shopee_video_script_07",
  "channel": "shopee",
  "industry": "handmade_decor",
  "audience": "người thích ghi chép bằng tay",
  "objective": "introduce_product",
  "input_facts": {
    "sku": "SO007",
    "name": "Sổ tay bìa vải",
    "source": "synthetic_fixture",
    "updated_at": "2026-11-06T09:00:00+07:00",
    "industry": "handmade_decor",
    "attributes": [
      {
        "key": "cover",
        "value": "bìa vải",
        "source": "synthetic_fixture"
      },
      {
        "key": "pages",
        "value": "giấy kẻ ngang",
        "source": "synthetic_fixture"
      },
      {
        "key": "color",
        "value": "xanh",
        "source": "synthetic_fixture"
      }
    ],
    "price": null,
    "currency": "VND",
    "product_url": null,
    "offer": null,
    "evidence": []
  },
  "tone": "friendly",
  "framework": "FAB",
  "synthetic_example": true,
  "content": {
    "content_type": "video_script",
    "title": "Sổ tay bìa vải — Giấy trong sổ có dòng kẻ không?",
    "concept": "Xem bìa vải và dòng kẻ của sổ tay.",
    "angle": "Xem chi tiết để lựa chọn",
    "objective": "introduce_product",
    "audience": "người thích ghi chép bằng tay",
    "hook": "Xem bìa vải và dòng kẻ của sổ tay.",
    "key_message": "Sổ tay bìa vải",
    "total_duration_seconds": 30,
    "production_mode": "text_only",
    "video_style": "tutorial",
    "scenes": [
      {
        "scene_id": "s1",
        "start_seconds": 0.0,
        "end_seconds": 5.0,
        "duration_seconds": 5.0,
        "visual_action": "Đặt sổ đóng trên bàn, tay vuốt nhẹ bìa. Đặt nhãn tên sản phẩm cùng khung hình.",
        "shot_type": "toàn cảnh sản phẩm",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": null,
        "on_screen_text": "Sổ tay bìa vải",
        "audio_direction": "Âm thanh thao tác thật; không cần nhạc.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      },
      {
        "scene_id": "s2",
        "start_seconds": 5.0,
        "end_seconds": 14.0,
        "duration_seconds": 9.0,
        "visual_action": "Mở sổ từ từ, dừng ở trang giấy kẻ ngang.",
        "shot_type": "cận cảnh",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": null,
        "on_screen_text": "Giấy kẻ ngang",
        "audio_direction": "Âm thanh thao tác thật; không cần nhạc.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      },
      {
        "scene_id": "s3",
        "start_seconds": 14.0,
        "end_seconds": 24.0,
        "duration_seconds": 10.0,
        "visual_action": "Đặt bút cạnh trang giấy, giữ dòng kẻ trong khung hình.",
        "shot_type": "cận cảnh",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": null,
        "on_screen_text": "Bạn sẽ ghi điều gì?",
        "audio_direction": "Âm thanh thao tác thật; không cần nhạc.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      },
      {
        "scene_id": "s4",
        "start_seconds": 24.0,
        "end_seconds": 30.0,
        "duration_seconds": 6.0,
        "visual_action": "Khép sổ, đưa thẻ tên vào cạnh bìa.",
        "shot_type": "toàn cảnh sản phẩm",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": null,
        "on_screen_text": "Tìm sản phẩm trong shop",
        "audio_direction": "Âm thanh thao tác thật; không cần nhạc.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      }
    ],
    "cta": {
      "text": "Tìm sản phẩm trong shop để xem chi tiết.",
      "action": "view_product",
      "display_condition": "Dùng khi shop đã kiểm tra thông tin sản phẩm hiện tại."
    },
    "product_attachment_note": "Kiểm tra quyền gắn đúng SKU trước khi đăng; chưa xác nhận đã gắn.",
    "post_caption": "Giấy trong sổ có dòng kẻ không? Xem chi tiết sản phẩm trong shop.",
    "hashtags": [],
    "cover_text": "Sổ tay bìa vải",
    "production": {
      "shot_list": [
        "Đặt sổ đóng trên bàn, tay vuốt nhẹ bìa.",
        "Mở sổ từ từ, dừng ở trang giấy kẻ ngang.",
        "Đặt bút cạnh trang giấy, giữ dòng kẻ trong khung hình.",
        "Khép sổ, đưa thẻ tên vào cạnh bìa."
      ],
      "props": [
        "Sổ tay bìa vải",
        "bàn và bút"
      ],
      "location": "bàn và bút",
      "actors": 1,
      "filming_checklist": [
        "Lau ống kính.",
        "Đọc lại facts và kiểm tra sản phẩm đúng SKU.",
        "Quay dọc, kiểm tra chữ không bị giao diện che."
      ],
      "editing_guide": [
        "Ghép đúng timeline.",
        "Đồng bộ chữ với thao tác.",
        "Kiểm tra âm thanh và phụ đề trước khi xuất."
      ]
    },
    "plain_text": "Sổ tay bìa vải — Giấy trong sổ có dòng kẻ không?\n\nXem bìa vải và dòng kẻ của sổ tay.\n\nThời gian — Cảnh quay — Lời thoại/voiceover — Chữ trên màn hình — Ghi chú dựng\n\n0–5s — Đặt sổ đóng trên bàn, tay vuốt nhẹ bìa. Đặt nhãn tên sản phẩm cùng khung hình. —  — Sổ tay bìa vải — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n5–14s — Mở sổ từ từ, dừng ở trang giấy kẻ ngang. —  — Giấy kẻ ngang — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n14–24s — Đặt bút cạnh trang giấy, giữ dòng kẻ trong khung hình. —  — Bạn sẽ ghi điều gì? — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n24–30s — Khép sổ, đưa thẻ tên vào cạnh bìa. —  — Tìm sản phẩm trong shop — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\nTìm sản phẩm trong shop để xem chi tiết.\n\nGiấy trong sổ có dòng kẻ không? Xem chi tiết sản phẩm trong shop."
  },
  "cta": {
    "text": "Tìm sản phẩm trong shop để xem chi tiết.",
    "action": "view_product",
    "display_condition": "Dùng khi shop đã kiểm tra thông tin sản phẩm hiện tại."
  },
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```

## Mẫu 8: Áo khoác có mũ

```json
{
  "example_id": "shopee_video_script_08",
  "channel": "shopee",
  "industry": "fashion",
  "audience": "người muốn kiểm tra chi tiết áo trước khi chọn",
  "objective": "introduce_product",
  "input_facts": {
    "sku": "AO008",
    "name": "Áo khoác có mũ",
    "source": "synthetic_fixture",
    "updated_at": "2026-11-06T09:00:00+07:00",
    "industry": "fashion",
    "attributes": [
      {
        "key": "hood",
        "value": "có mũ",
        "source": "synthetic_fixture"
      },
      {
        "key": "closure",
        "value": "khóa kéo",
        "source": "synthetic_fixture"
      },
      {
        "key": "color",
        "value": "xám",
        "source": "synthetic_fixture"
      }
    ],
    "price": null,
    "currency": "VND",
    "product_url": null,
    "offer": null,
    "evidence": []
  },
  "tone": "friendly",
  "framework": "AIDA",
  "synthetic_example": true,
  "content": {
    "content_type": "video_script",
    "title": "Áo khoác có mũ — Áo dùng khóa kéo hay cúc?",
    "concept": "Xem mũ, khóa kéo và màu áo trước khi chọn phân loại.",
    "angle": "Xem chi tiết để lựa chọn",
    "objective": "introduce_product",
    "audience": "người muốn kiểm tra chi tiết áo trước khi chọn",
    "hook": "Xem mũ, khóa kéo và màu áo trước khi chọn phân loại.",
    "key_message": "Áo khoác có mũ",
    "total_duration_seconds": 60,
    "production_mode": "hands_only",
    "video_style": "objection_handling",
    "scenes": [
      {
        "scene_id": "s1",
        "start_seconds": 0.0,
        "end_seconds": 6.0,
        "duration_seconds": 6.0,
        "visual_action": "Trải áo trên bàn, quay toàn bộ mặt trước. Đặt nhãn tên sản phẩm cùng khung hình.",
        "shot_type": "toàn cảnh sản phẩm",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": "Đây là áo khoác có mũ màu xám.",
        "on_screen_text": "Áo khoác có mũ",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      },
      {
        "scene_id": "s2",
        "start_seconds": 6.0,
        "end_seconds": 20.0,
        "duration_seconds": 14.0,
        "visual_action": "Mở phần mũ, giữ góc nhìn từ trên xuống.",
        "shot_type": "cận cảnh",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": "Mở phần mũ để bạn nhìn rõ chi tiết.",
        "on_screen_text": "Chi tiết mũ",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      },
      {
        "scene_id": "s3",
        "start_seconds": 20.0,
        "end_seconds": 36.0,
        "duration_seconds": 16.0,
        "visual_action": "Kéo khóa chậm từ dưới lên, quay cận phần khóa.",
        "shot_type": "cận cảnh",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": "Áo dùng khóa kéo. Cùng xem thao tác kéo khóa.",
        "on_screen_text": "Khóa kéo",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      },
      {
        "scene_id": "s4",
        "start_seconds": 36.0,
        "end_seconds": 50.0,
        "duration_seconds": 14.0,
        "visual_action": "Mở áo trở lại, giữ màu vải trong ánh sáng tự nhiên.",
        "shot_type": "cận cảnh",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": "Nhìn tổng thể áo và từng chi tiết trước khi lựa chọn.",
        "on_screen_text": "Màu xám",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      },
      {
        "scene_id": "s5",
        "start_seconds": 50.0,
        "end_seconds": 60.0,
        "duration_seconds": 10.0,
        "visual_action": "Gấp áo, để thẻ tên bên cạnh.",
        "shot_type": "toàn cảnh sản phẩm",
        "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
        "dialogue": null,
        "voiceover": "Tìm sản phẩm trong shop để xem chi tiết.",
        "on_screen_text": "Tìm sản phẩm trong shop",
        "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
        "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
        "people_required": 1,
        "shows_face": false
      }
    ],
    "cta": {
      "text": "Tìm sản phẩm trong shop để xem chi tiết.",
      "action": "view_product",
      "display_condition": "Dùng khi shop đã kiểm tra thông tin sản phẩm hiện tại."
    },
    "product_attachment_note": "Kiểm tra quyền gắn đúng SKU trước khi đăng; chưa xác nhận đã gắn.",
    "post_caption": "Áo dùng khóa kéo hay cúc? Xem chi tiết sản phẩm trong shop.",
    "hashtags": [],
    "cover_text": "Áo khoác có mũ",
    "production": {
      "shot_list": [
        "Trải áo trên bàn, quay toàn bộ mặt trước.",
        "Mở phần mũ, giữ góc nhìn từ trên xuống.",
        "Kéo khóa chậm từ dưới lên, quay cận phần khóa.",
        "Mở áo trở lại, giữ màu vải trong ánh sáng tự nhiên.",
        "Gấp áo, để thẻ tên bên cạnh."
      ],
      "props": [
        "Áo khoác có mũ",
        "mặt bàn rộng"
      ],
      "location": "mặt bàn rộng",
      "actors": 1,
      "filming_checklist": [
        "Lau ống kính.",
        "Đọc lại facts và kiểm tra sản phẩm đúng SKU.",
        "Quay dọc, kiểm tra chữ không bị giao diện che."
      ],
      "editing_guide": [
        "Ghép đúng timeline.",
        "Đồng bộ chữ với thao tác.",
        "Kiểm tra âm thanh và phụ đề trước khi xuất."
      ]
    },
    "plain_text": "Áo khoác có mũ — Áo dùng khóa kéo hay cúc?\n\nXem mũ, khóa kéo và màu áo trước khi chọn phân loại.\n\nThời gian — Cảnh quay — Lời thoại/voiceover — Chữ trên màn hình — Ghi chú dựng\n\n0–6s — Trải áo trên bàn, quay toàn bộ mặt trước. Đặt nhãn tên sản phẩm cùng khung hình. — Đây là áo khoác có mũ màu xám. — Áo khoác có mũ — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n6–20s — Mở phần mũ, giữ góc nhìn từ trên xuống. — Mở phần mũ để bạn nhìn rõ chi tiết. — Chi tiết mũ — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n20–36s — Kéo khóa chậm từ dưới lên, quay cận phần khóa. — Áo dùng khóa kéo. Cùng xem thao tác kéo khóa. — Khóa kéo — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n36–50s — Mở áo trở lại, giữ màu vải trong ánh sáng tự nhiên. — Nhìn tổng thể áo và từng chi tiết trước khi lựa chọn. — Màu xám — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n50–60s — Gấp áo, để thẻ tên bên cạnh. — Tìm sản phẩm trong shop để xem chi tiết. — Tìm sản phẩm trong shop — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\nTìm sản phẩm trong shop để xem chi tiết.\n\nÁo dùng khóa kéo hay cúc? Xem chi tiết sản phẩm trong shop."
  },
  "cta": {
    "text": "Tìm sản phẩm trong shop để xem chi tiết.",
    "action": "view_product",
    "display_condition": "Dùng khi shop đã kiểm tra thông tin sản phẩm hiện tại."
  },
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```
