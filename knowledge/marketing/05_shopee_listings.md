---
{
  "doc_id": "marketing.05_shopee_listings",
  "title": "Listing Shopee nguyên bản",
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
  "content_kind": "listing_examples",
  "synthetic_example": true,
  "source_ids": [
    "SP01"
  ],
  "updated_at": "2026-11-06",
  "version": "1.0.0",
  "tone": "friendly",
  "targets": [
    [
      "shopee",
      "product_listing",
      "listing"
    ]
  ]
}
---

# Listing Shopee nguyên bản

## Listing 1: Áo thun cổ tròn

```json
{
  "example_id": "shopee_listing_01",
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
    "content_type": "listing",
    "angle": "Thông tin để lựa chọn",
    "title": "Áo thun cổ tròn cotton màu trắng",
    "short_description": "Áo thun cổ tròn. cotton, trắng, cổ tròn.",
    "highlights": [
      "cotton",
      "trắng",
      "cổ tròn"
    ],
    "detailed_description": "Áo thun cổ tròn\n- cotton\n- trắng\n- cổ tròn",
    "attributes": [
      {
        "fact_ref": "attributes.material",
        "value": "cotton"
      },
      {
        "fact_ref": "attributes.color",
        "value": "trắng"
      },
      {
        "fact_ref": "attributes.neck",
        "value": "cổ tròn"
      }
    ],
    "cta": "Xem thông tin và phân loại của sản phẩm trong shop.",
    "plain_text": "Áo thun cổ tròn cotton màu trắng\n\nÁo thun cổ tròn. cotton, trắng, cổ tròn.\n\n- cotton\n- trắng\n- cổ tròn\n\nÁo thun cổ tròn\n- cotton\n- trắng\n- cổ tròn\n\nXem thông tin và phân loại của sản phẩm trong shop."
  },
  "cta": "Xem thông tin và phân loại của sản phẩm trong shop.",
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```

## Listing 2: Túi đeo chéo

```json
{
  "example_id": "shopee_listing_02",
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
    "content_type": "listing",
    "angle": "Thông tin để lựa chọn",
    "title": "Túi đeo chéo màu đen hai ngăn dây điều chỉnh được",
    "short_description": "Túi đeo chéo. đen, hai ngăn, dây điều chỉnh được.",
    "highlights": [
      "đen",
      "hai ngăn",
      "dây điều chỉnh được"
    ],
    "detailed_description": "Túi đeo chéo\n- đen\n- hai ngăn\n- dây điều chỉnh được",
    "attributes": [
      {
        "fact_ref": "attributes.color",
        "value": "đen"
      },
      {
        "fact_ref": "attributes.compartments",
        "value": "hai ngăn"
      },
      {
        "fact_ref": "attributes.strap",
        "value": "dây điều chỉnh được"
      }
    ],
    "cta": "Xem thông tin và phân loại của sản phẩm trong shop.",
    "plain_text": "Túi đeo chéo màu đen hai ngăn dây điều chỉnh được\n\nTúi đeo chéo. đen, hai ngăn, dây điều chỉnh được.\n\n- đen\n- hai ngăn\n- dây điều chỉnh được\n\nTúi đeo chéo\n- đen\n- hai ngăn\n- dây điều chỉnh được\n\nXem thông tin và phân loại của sản phẩm trong shop."
  },
  "cta": "Xem thông tin và phân loại của sản phẩm trong shop.",
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```

## Listing 3: Khay để bàn

```json
{
  "example_id": "shopee_listing_03",
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
    "content_type": "listing",
    "angle": "Thông tin để lựa chọn",
    "title": "Khay để bàn gỗ hình chữ nhật màu nâu",
    "short_description": "Khay để bàn. gỗ, hình chữ nhật, nâu.",
    "highlights": [
      "gỗ",
      "hình chữ nhật",
      "nâu"
    ],
    "detailed_description": "Khay để bàn\n- gỗ\n- hình chữ nhật\n- nâu",
    "attributes": [
      {
        "fact_ref": "attributes.material",
        "value": "gỗ"
      },
      {
        "fact_ref": "attributes.shape",
        "value": "hình chữ nhật"
      },
      {
        "fact_ref": "attributes.color",
        "value": "nâu"
      }
    ],
    "cta": "Xem thông tin và phân loại của sản phẩm trong shop.",
    "plain_text": "Khay để bàn gỗ hình chữ nhật màu nâu\n\nKhay để bàn. gỗ, hình chữ nhật, nâu.\n\n- gỗ\n- hình chữ nhật\n- nâu\n\nKhay để bàn\n- gỗ\n- hình chữ nhật\n- nâu\n\nXem thông tin và phân loại của sản phẩm trong shop."
  },
  "cta": "Xem thông tin và phân loại của sản phẩm trong shop.",
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```

## Listing 4: Bình gốm trang trí

```json
{
  "example_id": "shopee_listing_04",
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
    "content_type": "listing",
    "angle": "Thông tin để lựa chọn",
    "title": "Bình gốm trang trí màu kem bề mặt nhám",
    "short_description": "Bình gốm trang trí. gốm, kem, bề mặt nhám.",
    "highlights": [
      "gốm",
      "kem",
      "bề mặt nhám"
    ],
    "detailed_description": "Bình gốm trang trí\n- gốm\n- kem\n- bề mặt nhám",
    "attributes": [
      {
        "fact_ref": "attributes.material",
        "value": "gốm"
      },
      {
        "fact_ref": "attributes.color",
        "value": "kem"
      },
      {
        "fact_ref": "attributes.finish",
        "value": "bề mặt nhám"
      }
    ],
    "cta": "Xem thông tin và phân loại của sản phẩm trong shop.",
    "plain_text": "Bình gốm trang trí màu kem bề mặt nhám\n\nBình gốm trang trí. gốm, kem, bề mặt nhám.\n\n- gốm\n- kem\n- bề mặt nhám\n\nBình gốm trang trí\n- gốm\n- kem\n- bề mặt nhám\n\nXem thông tin và phân loại của sản phẩm trong shop."
  },
  "cta": "Xem thông tin và phân loại của sản phẩm trong shop.",
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```

## Listing 5: Kẹp tóc

```json
{
  "example_id": "shopee_listing_05",
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
    "content_type": "listing",
    "angle": "Thông tin để lựa chọn",
    "title": "Kẹp tóc dạng càng cua màu nâu bề mặt trơn",
    "short_description": "Kẹp tóc. nâu, dạng càng cua, bề mặt trơn.",
    "highlights": [
      "nâu",
      "dạng càng cua",
      "bề mặt trơn"
    ],
    "detailed_description": "Kẹp tóc\n- nâu\n- dạng càng cua\n- bề mặt trơn",
    "attributes": [
      {
        "fact_ref": "attributes.color",
        "value": "nâu"
      },
      {
        "fact_ref": "attributes.mechanism",
        "value": "dạng càng cua"
      },
      {
        "fact_ref": "attributes.surface",
        "value": "bề mặt trơn"
      }
    ],
    "cta": "Xem thông tin và phân loại của sản phẩm trong shop.",
    "plain_text": "Kẹp tóc dạng càng cua màu nâu bề mặt trơn\n\nKẹp tóc. nâu, dạng càng cua, bề mặt trơn.\n\n- nâu\n- dạng càng cua\n- bề mặt trơn\n\nKẹp tóc\n- nâu\n- dạng càng cua\n- bề mặt trơn\n\nXem thông tin và phân loại của sản phẩm trong shop."
  },
  "cta": "Xem thông tin và phân loại của sản phẩm trong shop.",
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```

## Listing 6: Hộp đựng đồ

```json
{
  "example_id": "shopee_listing_06",
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
    "content_type": "listing",
    "angle": "Thông tin để lựa chọn",
    "title": "Hộp đựng đồ nhựa trong suốt có nắp rời",
    "short_description": "Hộp đựng đồ. nhựa, nắp rời, trong suốt.",
    "highlights": [
      "nhựa",
      "nắp rời",
      "trong suốt"
    ],
    "detailed_description": "Hộp đựng đồ\n- nhựa\n- nắp rời\n- trong suốt",
    "attributes": [
      {
        "fact_ref": "attributes.material",
        "value": "nhựa"
      },
      {
        "fact_ref": "attributes.lid",
        "value": "nắp rời"
      },
      {
        "fact_ref": "attributes.color",
        "value": "trong suốt"
      }
    ],
    "cta": "Xem thông tin và phân loại của sản phẩm trong shop.",
    "plain_text": "Hộp đựng đồ nhựa trong suốt có nắp rời\n\nHộp đựng đồ. nhựa, nắp rời, trong suốt.\n\n- nhựa\n- nắp rời\n- trong suốt\n\nHộp đựng đồ\n- nhựa\n- nắp rời\n- trong suốt\n\nXem thông tin và phân loại của sản phẩm trong shop."
  },
  "cta": "Xem thông tin và phân loại của sản phẩm trong shop.",
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```

## Listing 7: Sổ tay bìa vải

```json
{
  "example_id": "shopee_listing_07",
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
    "content_type": "listing",
    "angle": "Thông tin để lựa chọn",
    "title": "Sổ tay bìa vải màu xanh giấy kẻ ngang",
    "short_description": "Sổ tay bìa vải. bìa vải, giấy kẻ ngang, xanh.",
    "highlights": [
      "bìa vải",
      "giấy kẻ ngang",
      "xanh"
    ],
    "detailed_description": "Sổ tay bìa vải\n- bìa vải\n- giấy kẻ ngang\n- xanh",
    "attributes": [
      {
        "fact_ref": "attributes.cover",
        "value": "bìa vải"
      },
      {
        "fact_ref": "attributes.pages",
        "value": "giấy kẻ ngang"
      },
      {
        "fact_ref": "attributes.color",
        "value": "xanh"
      }
    ],
    "cta": "Xem thông tin và phân loại của sản phẩm trong shop.",
    "plain_text": "Sổ tay bìa vải màu xanh giấy kẻ ngang\n\nSổ tay bìa vải. bìa vải, giấy kẻ ngang, xanh.\n\n- bìa vải\n- giấy kẻ ngang\n- xanh\n\nSổ tay bìa vải\n- bìa vải\n- giấy kẻ ngang\n- xanh\n\nXem thông tin và phân loại của sản phẩm trong shop."
  },
  "cta": "Xem thông tin và phân loại của sản phẩm trong shop.",
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```

## Listing 8: Áo khoác có mũ

```json
{
  "example_id": "shopee_listing_08",
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
    "content_type": "listing",
    "angle": "Thông tin để lựa chọn",
    "title": "Áo khoác có mũ màu xám khóa kéo",
    "short_description": "Áo khoác có mũ. có mũ, khóa kéo, xám.",
    "highlights": [
      "có mũ",
      "khóa kéo",
      "xám"
    ],
    "detailed_description": "Áo khoác có mũ\n- có mũ\n- khóa kéo\n- xám",
    "attributes": [
      {
        "fact_ref": "attributes.hood",
        "value": "có mũ"
      },
      {
        "fact_ref": "attributes.closure",
        "value": "khóa kéo"
      },
      {
        "fact_ref": "attributes.color",
        "value": "xám"
      }
    ],
    "cta": "Xem thông tin và phân loại của sản phẩm trong shop.",
    "plain_text": "Áo khoác có mũ màu xám khóa kéo\n\nÁo khoác có mũ. có mũ, khóa kéo, xám.\n\n- có mũ\n- khóa kéo\n- xám\n\nÁo khoác có mũ\n- có mũ\n- khóa kéo\n- xám\n\nXem thông tin và phân loại của sản phẩm trong shop."
  },
  "cta": "Xem thông tin và phân loại của sản phẩm trong shop.",
  "analysis": "Mở bằng câu hỏi có thể quan sát; cho xem chi tiết đã có trong input; kết thúc bằng một bước xem thông tin. Không thêm giá, ưu đãi hoặc hiệu quả chưa có bằng chứng."
}
```
