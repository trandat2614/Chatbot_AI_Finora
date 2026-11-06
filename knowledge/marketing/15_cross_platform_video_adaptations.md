---
{
  "doc_id": "marketing.15_cross_platform_video_adaptations",
  "title": "Chuyển thể cùng facts theo ba placement",
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
  "content_kind": "adaptation_examples",
  "synthetic_example": true,
  "source_ids": [],
  "updated_at": "2026-11-06",
  "version": "1.0.0",
  "tone": "friendly",
  "targets": [
    [
      "tiktok",
      "short_video",
      "video_script"
    ],
    [
      "facebook",
      "reels",
      "video_script"
    ],
    [
      "shopee",
      "video",
      "video_script"
    ]
  ]
}
---

# Chuyển thể cùng facts theo ba placement

## Bộ 1: Áo thun cổ tròn

```json
{
  "example_id": "adaptation_1",
  "synthetic_example": true,
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
  "audience": "người thích trang phục đơn giản",
  "objective": "introduce_product",
  "tone": "friendly",
  "framework": "FAB",
  "explanation": "TikTok mở bằng câu hỏi/thao tác và cắt vào chi tiết; Reels giữ hình và chữ để hiểu khi tắt âm; Shopee cho xem thông tin lựa chọn và CTA tìm sản phẩm trong shop, không giả định quyền gắn sản phẩm.",
  "scripts": [
    {
      "channel": "tiktok",
      "placement": "short_video",
      "content_type": "video_script",
      "content": {
        "content_type": "video_script",
        "title": "Áo thun cổ tròn — Áo có kiểu cổ nào?",
        "concept": "Muốn nhìn rõ cổ áo trước khi chọn?",
        "angle": "Xem chi tiết để lựa chọn",
        "objective": "introduce_product",
        "audience": "người thích trang phục đơn giản",
        "hook": "Muốn nhìn rõ cổ áo trước khi chọn?",
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
            "visual_action": "Đặt áo lên mặt bàn, kéo phần cổ vào khung hình.",
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
            "visual_action": "Hai tay mở phẳng cổ áo rồi quay cận bề mặt vải. Chuyển từ toàn cảnh sang cận bằng một nhịp cắt.",
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
            "voiceover": "Xem thông tin áo trong shop.",
            "on_screen_text": "Xem thông tin sản phẩm",
            "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
            "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
            "people_required": 1,
            "shows_face": false
          }
        ],
        "cta": {
          "text": "Xem thông tin sản phẩm trong shop.",
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
        "plain_text": "Áo thun cổ tròn — Áo có kiểu cổ nào?\n\nMuốn nhìn rõ cổ áo trước khi chọn?\n\nThời gian — Cảnh quay — Lời thoại/voiceover — Chữ trên màn hình — Ghi chú dựng\n\n0–4s — Đặt áo lên mặt bàn, kéo phần cổ vào khung hình. — Đây là áo thun cổ tròn. — Áo thun cổ tròn — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n4–10s — Hai tay mở phẳng cổ áo rồi quay cận bề mặt vải. Chuyển từ toàn cảnh sang cận bằng một nhịp cắt. — Chất liệu cotton, màu trắng. — Cotton · trắng — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n10–15s — Giữ toàn bộ áo trong khung hình, đặt thẻ tên bên cạnh. — Xem thông tin áo trong shop. — Xem thông tin sản phẩm — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\nXem thông tin sản phẩm trong shop.\n\nÁo có kiểu cổ nào? Xem chi tiết sản phẩm trong shop."
      }
    },
    {
      "channel": "facebook",
      "placement": "reels",
      "content_type": "video_script",
      "content": {
        "content_type": "video_script",
        "title": "Áo thun cổ tròn — Áo có kiểu cổ nào?",
        "concept": "Một góc quay để xem rõ chiếc áo cổ tròn.",
        "angle": "Xem chi tiết để lựa chọn",
        "objective": "introduce_product",
        "audience": "người thích trang phục đơn giản",
        "hook": "Một góc quay để xem rõ chiếc áo cổ tròn.",
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
            "visual_action": "Đặt áo lên mặt bàn, kéo phần cổ vào khung hình.",
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
            "visual_action": "Hai tay mở phẳng cổ áo rồi quay cận bề mặt vải. Giữ khung hình tĩnh để xem rõ khi tắt âm.",
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
            "voiceover": "Xem thông tin áo trong shop.",
            "on_screen_text": "Xem thông tin sản phẩm",
            "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
            "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
            "people_required": 1,
            "shows_face": false
          }
        ],
        "cta": {
          "text": "Xem thông tin sản phẩm trong shop.",
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
        "plain_text": "Áo thun cổ tròn — Áo có kiểu cổ nào?\n\nMột góc quay để xem rõ chiếc áo cổ tròn.\n\nThời gian — Cảnh quay — Lời thoại/voiceover — Chữ trên màn hình — Ghi chú dựng\n\n0–4s — Đặt áo lên mặt bàn, kéo phần cổ vào khung hình. — Đây là áo thun cổ tròn. — Áo thun cổ tròn — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n4–10s — Hai tay mở phẳng cổ áo rồi quay cận bề mặt vải. Giữ khung hình tĩnh để xem rõ khi tắt âm. — Chất liệu cotton, màu trắng. — Cotton · trắng — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n10–15s — Giữ toàn bộ áo trong khung hình, đặt thẻ tên bên cạnh. — Xem thông tin áo trong shop. — Xem thông tin sản phẩm — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\nXem thông tin sản phẩm trong shop.\n\nÁo có kiểu cổ nào? Xem chi tiết sản phẩm trong shop."
      }
    },
    {
      "channel": "shopee",
      "placement": "video",
      "content_type": "video_script",
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
      }
    }
  ]
}
```

## Bộ 2: Khay để bàn

```json
{
  "example_id": "adaptation_2",
  "synthetic_example": true,
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
  "audience": "người muốn bố trí góc làm việc",
  "objective": "introduce_product",
  "tone": "friendly",
  "framework": "FAB",
  "explanation": "TikTok mở bằng câu hỏi/thao tác và cắt vào chi tiết; Reels giữ hình và chữ để hiểu khi tắt âm; Shopee cho xem thông tin lựa chọn và CTA tìm sản phẩm trong shop, không giả định quyền gắn sản phẩm.",
  "scripts": [
    {
      "channel": "tiktok",
      "placement": "short_video",
      "content_type": "video_script",
      "content": {
        "content_type": "video_script",
        "title": "Khay để bàn — Khay có hình dạng gì?",
        "concept": "Thử chọn một vị trí cố định cho đồ trên bàn.",
        "angle": "Xem chi tiết để lựa chọn",
        "objective": "introduce_product",
        "audience": "người muốn bố trí góc làm việc",
        "hook": "Thử chọn một vị trí cố định cho đồ trên bàn.",
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
            "visual_action": "Quay góc bàn trống, đưa khay vào giữa khung hình.",
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
            "visual_action": "Quay cạnh dài và cạnh ngắn để thấy hình chữ nhật. Chuyển từ toàn cảnh sang cận bằng một nhịp cắt.",
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
            "on_screen_text": "Xem thông tin trong shop",
            "audio_direction": "Âm thanh thao tác thật; không cần nhạc.",
            "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
            "people_required": 1,
            "shows_face": false
          }
        ],
        "cta": {
          "text": "Xem thông tin sản phẩm trong shop.",
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
        "plain_text": "Khay để bàn — Khay có hình dạng gì?\n\nThử chọn một vị trí cố định cho đồ trên bàn.\n\nThời gian — Cảnh quay — Lời thoại/voiceover — Chữ trên màn hình — Ghi chú dựng\n\n0–6s — Quay góc bàn trống, đưa khay vào giữa khung hình. —  — Khay để bàn — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n6–20s — Quay cạnh dài và cạnh ngắn để thấy hình chữ nhật. Chuyển từ toàn cảnh sang cận bằng một nhịp cắt. —  — Hình chữ nhật — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n20–36s — Đổi sang góc nghiêng, giữ cận bề mặt gỗ. —  — Gỗ · màu nâu — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n36–50s — Đặt khay vào vị trí dự kiến sử dụng, quay tổng thể. —  — Bạn sẽ đặt khay ở góc nào? — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n50–60s — Đưa thẻ tên sản phẩm cạnh khay, giữ khung hình tĩnh. —  — Xem thông tin trong shop — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\nXem thông tin sản phẩm trong shop.\n\nKhay có hình dạng gì? Xem chi tiết sản phẩm trong shop."
      }
    },
    {
      "channel": "facebook",
      "placement": "reels",
      "content_type": "video_script",
      "content": {
        "content_type": "video_script",
        "title": "Khay để bàn — Khay có hình dạng gì?",
        "concept": "Một góc bàn, một khay để bạn tự sắp xếp.",
        "angle": "Xem chi tiết để lựa chọn",
        "objective": "introduce_product",
        "audience": "người muốn bố trí góc làm việc",
        "hook": "Một góc bàn, một khay để bạn tự sắp xếp.",
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
            "visual_action": "Quay góc bàn trống, đưa khay vào giữa khung hình.",
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
            "visual_action": "Quay cạnh dài và cạnh ngắn để thấy hình chữ nhật. Giữ khung hình tĩnh để xem rõ khi tắt âm.",
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
            "on_screen_text": "Xem thông tin trong shop",
            "audio_direction": "Âm thanh thao tác thật; không cần nhạc.",
            "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
            "people_required": 1,
            "shows_face": false
          }
        ],
        "cta": {
          "text": "Xem thông tin sản phẩm trong shop.",
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
        "plain_text": "Khay để bàn — Khay có hình dạng gì?\n\nMột góc bàn, một khay để bạn tự sắp xếp.\n\nThời gian — Cảnh quay — Lời thoại/voiceover — Chữ trên màn hình — Ghi chú dựng\n\n0–6s — Quay góc bàn trống, đưa khay vào giữa khung hình. —  — Khay để bàn — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n6–20s — Quay cạnh dài và cạnh ngắn để thấy hình chữ nhật. Giữ khung hình tĩnh để xem rõ khi tắt âm. —  — Hình chữ nhật — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n20–36s — Đổi sang góc nghiêng, giữ cận bề mặt gỗ. —  — Gỗ · màu nâu — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n36–50s — Đặt khay vào vị trí dự kiến sử dụng, quay tổng thể. —  — Bạn sẽ đặt khay ở góc nào? — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n50–60s — Đưa thẻ tên sản phẩm cạnh khay, giữ khung hình tĩnh. —  — Xem thông tin trong shop — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\nXem thông tin sản phẩm trong shop.\n\nKhay có hình dạng gì? Xem chi tiết sản phẩm trong shop."
      }
    },
    {
      "channel": "shopee",
      "placement": "video",
      "content_type": "video_script",
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
      }
    }
  ]
}
```

## Bộ 3: Bình gốm trang trí

```json
{
  "example_id": "adaptation_3",
  "synthetic_example": true,
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
  "audience": "người thích trang trí kệ nhỏ",
  "objective": "introduce_product",
  "tone": "friendly",
  "framework": "FAB",
  "explanation": "TikTok mở bằng câu hỏi/thao tác và cắt vào chi tiết; Reels giữ hình và chữ để hiểu khi tắt âm; Shopee cho xem thông tin lựa chọn và CTA tìm sản phẩm trong shop, không giả định quyền gắn sản phẩm.",
  "scripts": [
    {
      "channel": "tiktok",
      "placement": "short_video",
      "content_type": "video_script",
      "content": {
        "content_type": "video_script",
        "title": "Bình gốm trang trí — Bề mặt bình bóng hay nhám?",
        "concept": "Một chiếc bình có thể bắt đầu từ góc kệ trống.",
        "angle": "Xem chi tiết để lựa chọn",
        "objective": "introduce_product",
        "audience": "người thích trang trí kệ nhỏ",
        "hook": "Một chiếc bình có thể bắt đầu từ góc kệ trống.",
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
            "visual_action": "Người dẫn cầm bình ngang ngực, đứng cạnh kệ trống.",
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
            "visual_action": "Đưa bình lại gần máy để thấy màu và bề mặt. Chuyển từ toàn cảnh sang cận bằng một nhịp cắt.",
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
            "dialogue": "Xem thông tin bình trong shop.",
            "voiceover": null,
            "on_screen_text": "Xem thông tin sản phẩm",
            "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
            "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
            "people_required": 1,
            "shows_face": true
          }
        ],
        "cta": {
          "text": "Xem thông tin sản phẩm trong shop.",
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
        "plain_text": "Bình gốm trang trí — Bề mặt bình bóng hay nhám?\n\nMột chiếc bình có thể bắt đầu từ góc kệ trống.\n\nThời gian — Cảnh quay — Lời thoại/voiceover — Chữ trên màn hình — Ghi chú dựng\n\n0–5s — Người dẫn cầm bình ngang ngực, đứng cạnh kệ trống. — Bạn đang tìm đồ trang trí cho góc kệ? — Góc kệ của bạn — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n5–14s — Đưa bình lại gần máy để thấy màu và bề mặt. Chuyển từ toàn cảnh sang cận bằng một nhịp cắt. — Đây là bình gốm trang trí màu kem, bề mặt nhám. — Gốm · kem · bề mặt nhám — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n14–24s — Đặt bình lên kệ, lùi ra để thấy vị trí. — Hãy nhìn màu bình cạnh đồ bạn đang có. — Cân nhắc vị trí đặt — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n24–30s — Chỉ tay về bình, giữ tên sản phẩm trên khung hình. — Xem thông tin bình trong shop. — Xem thông tin sản phẩm — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\nXem thông tin sản phẩm trong shop.\n\nBề mặt bình bóng hay nhám? Xem chi tiết sản phẩm trong shop."
      }
    },
    {
      "channel": "facebook",
      "placement": "reels",
      "content_type": "video_script",
      "content": {
        "content_type": "video_script",
        "title": "Bình gốm trang trí — Bề mặt bình bóng hay nhám?",
        "concept": "Xem bề mặt nhám của chiếc bình màu kem.",
        "angle": "Xem chi tiết để lựa chọn",
        "objective": "introduce_product",
        "audience": "người thích trang trí kệ nhỏ",
        "hook": "Xem bề mặt nhám của chiếc bình màu kem.",
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
            "visual_action": "Người dẫn cầm bình ngang ngực, đứng cạnh kệ trống.",
            "shot_type": "toàn cảnh sản phẩm",
            "camera_direction": "Máy cố định, lấy nét vào sản phẩm.",
            "dialogue": "Bạn đang tìm đồ trang trí cho góc kệ?",
            "voiceover": null,
            "on_screen_text": "Bình gốm trang trí",
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
            "visual_action": "Đưa bình lại gần máy để thấy màu và bề mặt. Giữ khung hình tĩnh để xem rõ khi tắt âm.",
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
            "dialogue": "Xem thông tin bình trong shop.",
            "voiceover": null,
            "on_screen_text": "Xem thông tin sản phẩm",
            "audio_direction": "Giọng rõ, để khoảng nghỉ cho thao tác.",
            "editing_notes": "Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.",
            "people_required": 1,
            "shows_face": true
          }
        ],
        "cta": {
          "text": "Xem thông tin sản phẩm trong shop.",
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
        "plain_text": "Bình gốm trang trí — Bề mặt bình bóng hay nhám?\n\nXem bề mặt nhám của chiếc bình màu kem.\n\nThời gian — Cảnh quay — Lời thoại/voiceover — Chữ trên màn hình — Ghi chú dựng\n\n0–5s — Người dẫn cầm bình ngang ngực, đứng cạnh kệ trống. — Bạn đang tìm đồ trang trí cho góc kệ? — Bình gốm trang trí — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n5–14s — Đưa bình lại gần máy để thấy màu và bề mặt. Giữ khung hình tĩnh để xem rõ khi tắt âm. — Đây là bình gốm trang trí màu kem, bề mặt nhám. — Gốm · kem · bề mặt nhám — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n14–24s — Đặt bình lên kệ, lùi ra để thấy vị trí. — Hãy nhìn màu bình cạnh đồ bạn đang có. — Cân nhắc vị trí đặt — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\n24–30s — Chỉ tay về bình, giữ tên sản phẩm trên khung hình. — Xem thông tin bình trong shop. — Xem thông tin sản phẩm — Cắt gọn khoảng trống, giữ chữ cách vùng giao diện.\n\nXem thông tin sản phẩm trong shop.\n\nBề mặt bình bóng hay nhám? Xem chi tiết sản phẩm trong shop."
      }
    },
    {
      "channel": "shopee",
      "placement": "video",
      "content_type": "video_script",
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
      }
    }
  ]
}
```
