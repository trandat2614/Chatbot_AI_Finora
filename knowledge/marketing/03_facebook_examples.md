---
{
  "doc_id": "marketing.03_facebook_examples",
  "title": "Bài Facebook nguyên bản",
  "language": "vi",
  "scope": "public",
  "channels": [
    "facebook"
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
  "content_kind": "caption_examples",
  "synthetic_example": true,
  "source_ids": [],
  "updated_at": "2026-11-06",
  "version": "1.0.0",
  "tone": "friendly",
  "targets": [
    [
      "facebook",
      "feed",
      "caption"
    ]
  ]
}
---

# Bài Facebook nguyên bản

## Bài 1: Áo thun cổ tròn

```json
{
  "example_id": "facebook_caption_01",
  "channel": "facebook",
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
    "content_type": "caption",
    "angle": "Xem chi tiết để lựa chọn",
    "hook": "Bạn muốn xem rõ phần cổ trước khi chọn áo?",
    "body": "Áo thun cổ tròn màu trắng có chất liệu cotton. Nhìn từ tổng thể đến cận cảnh phần cổ giúp bạn hình dung kiểu áo trước khi phối với đồ đang có.",
    "cta": "Xem thông tin áo để cân nhắc lựa chọn phù hợp với bạn.",
    "hashtags": [],
    "plain_text": "Bạn muốn xem rõ phần cổ trước khi chọn áo?\n\nÁo thun cổ tròn màu trắng có chất liệu cotton. Nhìn từ tổng thể đến cận cảnh phần cổ giúp bạn hình dung kiểu áo trước khi phối với đồ đang có.\n\nXem thông tin áo để cân nhắc lựa chọn phù hợp với bạn."
  },
  "cta": "Xem thông tin áo để cân nhắc lựa chọn phù hợp với bạn.",
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```

## Bài 2: Túi đeo chéo

```json
{
  "example_id": "facebook_caption_02",
  "channel": "facebook",
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
    "content_type": "caption",
    "angle": "Xem chi tiết để lựa chọn",
    "hook": "Đồ nhỏ nên để ở đâu để bạn dễ nhớ?",
    "body": "Túi đeo chéo màu đen có hai ngăn. Bạn có thể tự chọn cách chia đồ theo thói quen mang theo. Phần dây điều chỉnh được cũng là chi tiết nên xem kỹ khi cân nhắc.",
    "cta": "Xem thông tin túi và hình các ngăn trước khi lựa chọn.",
    "hashtags": [],
    "plain_text": "Đồ nhỏ nên để ở đâu để bạn dễ nhớ?\n\nTúi đeo chéo màu đen có hai ngăn. Bạn có thể tự chọn cách chia đồ theo thói quen mang theo. Phần dây điều chỉnh được cũng là chi tiết nên xem kỹ khi cân nhắc.\n\nXem thông tin túi và hình các ngăn trước khi lựa chọn."
  },
  "cta": "Xem thông tin túi và hình các ngăn trước khi lựa chọn.",
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```

## Bài 3: Khay để bàn

```json
{
  "example_id": "facebook_caption_03",
  "channel": "facebook",
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
    "content_type": "caption",
    "angle": "Xem chi tiết để lựa chọn",
    "hook": "Bạn sẽ dành góc nào trên bàn cho một chiếc khay?",
    "body": "Khay để bàn bằng gỗ, màu nâu, có hình chữ nhật. Hãy nhìn tổng thể bàn và vị trí bạn muốn đặt trước khi lựa chọn; ảnh cận giúp bạn xem bề mặt sản phẩm rõ hơn.",
    "cta": "Xem thông tin khay để cân nhắc cách bố trí phù hợp với góc của bạn.",
    "hashtags": [],
    "plain_text": "Bạn sẽ dành góc nào trên bàn cho một chiếc khay?\n\nKhay để bàn bằng gỗ, màu nâu, có hình chữ nhật. Hãy nhìn tổng thể bàn và vị trí bạn muốn đặt trước khi lựa chọn; ảnh cận giúp bạn xem bề mặt sản phẩm rõ hơn.\n\nXem thông tin khay để cân nhắc cách bố trí phù hợp với góc của bạn."
  },
  "cta": "Xem thông tin khay để cân nhắc cách bố trí phù hợp với góc của bạn.",
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```

## Bài 4: Bình gốm trang trí

```json
{
  "example_id": "facebook_caption_04",
  "channel": "facebook",
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
    "content_type": "caption",
    "angle": "Xem chi tiết để lựa chọn",
    "hook": "Bạn thích một góc kệ có màu sắc nhẹ nhàng?",
    "body": "Bình gốm trang trí màu kem có bề mặt nhám. Hãy xem ảnh tổng thể cùng ảnh cận bề mặt để chọn theo cách bạn muốn bố trí không gian. Đây là gợi ý trang trí, bạn vẫn là người quyết định vị trí đặt.",
    "cta": "Xem thông tin bình trước khi lựa chọn.",
    "hashtags": [],
    "plain_text": "Bạn thích một góc kệ có màu sắc nhẹ nhàng?\n\nBình gốm trang trí màu kem có bề mặt nhám. Hãy xem ảnh tổng thể cùng ảnh cận bề mặt để chọn theo cách bạn muốn bố trí không gian. Đây là gợi ý trang trí, bạn vẫn là người quyết định vị trí đặt.\n\nXem thông tin bình trước khi lựa chọn."
  },
  "cta": "Xem thông tin bình trước khi lựa chọn.",
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```

## Bài 5: Kẹp tóc

```json
{
  "example_id": "facebook_caption_05",
  "channel": "facebook",
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
    "content_type": "caption",
    "angle": "Xem chi tiết để lựa chọn",
    "hook": "Muốn chọn kẹp tóc, bạn có thể bắt đầu bằng cách xem cơ chế mở.",
    "body": "Mẫu kẹp này có dạng càng cua, màu nâu và bề mặt trơn. Hình cận cùng thao tác bóp, thả giúp bạn nhìn rõ sản phẩm trước khi quyết định.",
    "cta": "Xem thông tin kẹp để cân nhắc theo cách bạn thường dùng.",
    "hashtags": [],
    "plain_text": "Muốn chọn kẹp tóc, bạn có thể bắt đầu bằng cách xem cơ chế mở.\n\nMẫu kẹp này có dạng càng cua, màu nâu và bề mặt trơn. Hình cận cùng thao tác bóp, thả giúp bạn nhìn rõ sản phẩm trước khi quyết định.\n\nXem thông tin kẹp để cân nhắc theo cách bạn thường dùng."
  },
  "cta": "Xem thông tin kẹp để cân nhắc theo cách bạn thường dùng.",
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```

## Bài 6: Hộp đựng đồ

```json
{
  "example_id": "facebook_caption_06",
  "channel": "facebook",
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
    "content_type": "caption",
    "angle": "Xem chi tiết để lựa chọn",
    "hook": "Bạn quen dùng hộp có nắp rời hay nắp liền?",
    "body": "Hộp đựng đồ này bằng nhựa trong suốt và có nắp rời. Trước khi chọn, hãy xem ảnh thân hộp cùng phần nắp để hình dung thao tác mở, đóng theo thói quen của bạn.",
    "cta": "Xem thông tin hộp để lựa chọn đúng nhu cầu.",
    "hashtags": [],
    "plain_text": "Bạn quen dùng hộp có nắp rời hay nắp liền?\n\nHộp đựng đồ này bằng nhựa trong suốt và có nắp rời. Trước khi chọn, hãy xem ảnh thân hộp cùng phần nắp để hình dung thao tác mở, đóng theo thói quen của bạn.\n\nXem thông tin hộp để lựa chọn đúng nhu cầu."
  },
  "cta": "Xem thông tin hộp để lựa chọn đúng nhu cầu.",
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```

## Bài 7: Sổ tay bìa vải

```json
{
  "example_id": "facebook_caption_07",
  "channel": "facebook",
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
    "content_type": "caption",
    "angle": "Xem chi tiết để lựa chọn",
    "hook": "Trang giấy đầu tiên của bạn sẽ dành cho điều gì?",
    "body": "Sổ tay có bìa vải màu xanh và giấy kẻ ngang. Bạn có thể xem ảnh bìa, trang mở để cân nhắc theo cách ghi chép thường ngày. Không cần bắt đầu bằng một kế hoạch lớn; chỉ cần một điều bạn muốn ghi lại.",
    "cta": "Xem thông tin sổ trước khi lựa chọn.",
    "hashtags": [],
    "plain_text": "Trang giấy đầu tiên của bạn sẽ dành cho điều gì?\n\nSổ tay có bìa vải màu xanh và giấy kẻ ngang. Bạn có thể xem ảnh bìa, trang mở để cân nhắc theo cách ghi chép thường ngày. Không cần bắt đầu bằng một kế hoạch lớn; chỉ cần một điều bạn muốn ghi lại.\n\nXem thông tin sổ trước khi lựa chọn."
  },
  "cta": "Xem thông tin sổ trước khi lựa chọn.",
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```

## Bài 8: Áo khoác có mũ

```json
{
  "example_id": "facebook_caption_08",
  "channel": "facebook",
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
    "content_type": "caption",
    "angle": "Xem chi tiết để lựa chọn",
    "hook": "Bạn thường xem mũ hay khóa áo trước khi chọn áo khoác?",
    "body": "Mẫu áo khoác màu xám này có mũ và khóa kéo. Ảnh tổng thể giúp bạn xem kiểu áo, còn ảnh cận dành cho những chi tiết bạn quan tâm. Hãy xem kỹ thông tin trước khi quyết định theo nhu cầu riêng.",
    "cta": "Xem thông tin áo và phần phân loại trong shop.",
    "hashtags": [],
    "plain_text": "Bạn thường xem mũ hay khóa áo trước khi chọn áo khoác?\n\nMẫu áo khoác màu xám này có mũ và khóa kéo. Ảnh tổng thể giúp bạn xem kiểu áo, còn ảnh cận dành cho những chi tiết bạn quan tâm. Hãy xem kỹ thông tin trước khi quyết định theo nhu cầu riêng.\n\nXem thông tin áo và phần phân loại trong shop."
  },
  "cta": "Xem thông tin áo và phần phân loại trong shop.",
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```
