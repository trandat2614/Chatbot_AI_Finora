---
{
  "doc_id": "marketing.07_marketing_strategies",
  "title": "8 chiến lược thực thi cho shop nhỏ",
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
  "content_kind": "strategies",
  "synthetic_example": false,
  "source_ids": [
    "HS02",
    "MC01"
  ],
  "updated_at": "2026-11-06",
  "version": "1.0.0",
  "tone": "friendly"
}
---

# 8 chiến lược thực thi cho shop nhỏ

## Hướng dẫn đọc thông tin SKU

```json
{
  "strategy_id": "strategy_1",
  "problem": "Khách chưa hiểu cách chọn",
  "suitable_when": "Khách chưa hiểu cách chọn và shop có nguồn lực duy trì nội dung",
  "conditions": [
    "Có bảng/thuộc tính được xác nhận"
  ],
  "message": "Chọn theo nhu cầu từ dữ liệu rõ ràng",
  "channels": [
    "facebook",
    "tiktok",
    "shopee"
  ],
  "actions": [
    "Chọn một câu hỏi cách chọn.",
    "Chụp thông tin/bảng thật.",
    "Viết hướng dẫn ngắn và CTA xem chi tiết.",
    "Ghi lại câu hỏi còn vướng."
  ],
  "resources": [
    "người phụ trách nội dung",
    "điện thoại",
    "dữ liệu SKU đã xác nhận"
  ],
  "assumptions": [
    "Chưa biết baseline; cần đo trước khi đặt mục tiêu."
  ],
  "kpis_to_measure": [
    "lượt mở chi tiết",
    "câu hỏi cách chọn"
  ],
  "experiment": "So hướng dẫn bằng ảnh với hướng dẫn bằng chữ",
  "stop_or_adjust_when": "Điều chỉnh khi phản hồi cho thấy hiểu sai, điều kiện đầu vào đổi hoặc công sức vượt nguồn lực; dừng nếu hết quyền dùng dữ liệu/ưu đãi. KPI là đề xuất đo, không phải kết quả."
}
```

## Demo một tình huống

```json
{
  "strategy_id": "strategy_2",
  "problem": "Ảnh tổng thể chưa cho thấy thao tác",
  "suitable_when": "Ảnh tổng thể chưa cho thấy thao tác và shop có nguồn lực duy trì nội dung",
  "conditions": [
    "Có sản phẩm và thao tác phù hợp"
  ],
  "message": "Cho thấy chi tiết trước quyết định",
  "channels": [
    "facebook",
    "tiktok",
    "shopee"
  ],
  "actions": [
    "Chọn một thao tác thật.",
    "Quay cận bằng điện thoại.",
    "Gắn chữ đúng facts.",
    "Đăng bản đã duyệt và ghi nhận phản hồi."
  ],
  "resources": [
    "người phụ trách nội dung",
    "điện thoại",
    "dữ liệu SKU đã xác nhận"
  ],
  "assumptions": [
    "Chưa biết baseline; cần đo trước khi đặt mục tiêu."
  ],
  "kpis_to_measure": [
    "thời gian xem",
    "lượt vào sản phẩm"
  ],
  "experiment": "Thay hook, giữ demo và CTA",
  "stop_or_adjust_when": "Điều chỉnh khi phản hồi cho thấy hiểu sai, điều kiện đầu vào đổi hoặc công sức vượt nguồn lực; dừng nếu hết quyền dùng dữ liệu/ưu đãi. KPI là đề xuất đo, không phải kết quả."
}
```

## FAQ tháo gỡ trở ngại

```json
{
  "strategy_id": "strategy_3",
  "problem": "Khách hỏi lặp về chi tiết",
  "suitable_when": "Khách hỏi lặp về chi tiết và shop có nguồn lực duy trì nội dung",
  "conditions": [
    "Có câu hỏi thật đã ẩn dữ liệu cá nhân"
  ],
  "message": "Giải thích một điều còn chưa rõ",
  "channels": [
    "facebook",
    "tiktok",
    "shopee"
  ],
  "actions": [
    "Tổng hợp một câu hỏi không lộ PII.",
    "Xác nhận câu trả lời với shop.",
    "Viết câu trả lời kèm hình chi tiết.",
    "Đo số câu hỏi chưa giải quyết."
  ],
  "resources": [
    "người phụ trách nội dung",
    "điện thoại",
    "dữ liệu SKU đã xác nhận"
  ],
  "assumptions": [
    "Chưa biết baseline; cần đo trước khi đặt mục tiêu."
  ],
  "kpis_to_measure": [
    "câu hỏi tiếp diễn",
    "lượt xem chi tiết"
  ],
  "experiment": "Thử câu hỏi ở hook và ở ảnh bìa",
  "stop_or_adjust_when": "Điều chỉnh khi phản hồi cho thấy hiểu sai, điều kiện đầu vào đổi hoặc công sức vượt nguồn lực; dừng nếu hết quyền dùng dữ liệu/ưu đãi. KPI là đề xuất đo, không phải kết quả."
}
```

## Chuỗi giới thiệu từng SKU

```json
{
  "strategy_id": "strategy_4",
  "problem": "Nhiều sản phẩm dễ bị lẫn",
  "suitable_when": "Nhiều sản phẩm dễ bị lẫn và shop có nguồn lực duy trì nội dung",
  "conditions": [
    "Có danh mục và facts riêng từng SKU"
  ],
  "message": "Mỗi bài giúp hiểu một sản phẩm",
  "channels": [
    "facebook",
    "tiktok",
    "shopee"
  ],
  "actions": [
    "Chọn nhóm SKU có dữ liệu đầy đủ.",
    "Viết mỗi SKU một góc riêng.",
    "Rà giá/thuộc tính từng sản phẩm.",
    "Đăng theo lịch nguồn lực cho phép."
  ],
  "resources": [
    "người phụ trách nội dung",
    "điện thoại",
    "dữ liệu SKU đã xác nhận"
  ],
  "assumptions": [
    "Chưa biết baseline; cần đo trước khi đặt mục tiêu."
  ],
  "kpis_to_measure": [
    "lượt vào từng SKU",
    "bản nháp được duyệt"
  ],
  "experiment": "Đổi thứ tự SKU, giữ tiêu chí nội dung",
  "stop_or_adjust_when": "Điều chỉnh khi phản hồi cho thấy hiểu sai, điều kiện đầu vào đổi hoặc công sức vượt nguồn lực; dừng nếu hết quyền dùng dữ liệu/ưu đãi. KPI là đề xuất đo, không phải kết quả."
}
```

## Giới thiệu combo có thật

```json
{
  "strategy_id": "strategy_5",
  "problem": "Khách chưa biết thành phần bộ",
  "suitable_when": "Khách chưa biết thành phần bộ và shop có nguồn lực duy trì nội dung",
  "conditions": [
    "Shop thực sự bán combo, có thành phần và giá xác nhận"
  ],
  "message": "Nói rõ bộ gồm gì, không tự cộng lợi ích",
  "channels": [
    "facebook",
    "tiktok",
    "shopee"
  ],
  "actions": [
    "Xác minh mã combo và thành phần.",
    "Chụp đầy đủ món trong bộ.",
    "Nêu điều kiện/giá đã xác nhận.",
    "Theo dõi câu hỏi về thành phần."
  ],
  "resources": [
    "người phụ trách nội dung",
    "điện thoại",
    "dữ liệu SKU đã xác nhận"
  ],
  "assumptions": [
    "Chưa biết baseline; cần đo trước khi đặt mục tiêu."
  ],
  "kpis_to_measure": [
    "lượt xem combo",
    "câu hỏi thành phần"
  ],
  "experiment": "So ảnh toàn bộ với ảnh tách thành phần",
  "stop_or_adjust_when": "Điều chỉnh khi phản hồi cho thấy hiểu sai, điều kiện đầu vào đổi hoặc công sức vượt nguồn lực; dừng nếu hết quyền dùng dữ liệu/ưu đãi. KPI là đề xuất đo, không phải kết quả."
}
```

## Nội dung khách đã cho phép

```json
{
  "strategy_id": "strategy_6",
  "problem": "Thiếu góc nhìn sử dụng có nguồn",
  "suitable_when": "Thiếu góc nhìn sử dụng có nguồn và shop có nguồn lực duy trì nội dung",
  "conditions": [
    "Có đồng ý sử dụng và nội dung thật; không tự chế review"
  ],
  "message": "Dẫn lời đúng phạm vi khách cho phép",
  "channels": [
    "facebook",
    "tiktok",
    "shopee"
  ],
  "actions": [
    "Lưu bằng chứng đồng ý ở BE.",
    "Ẩn thông tin cá nhân theo quyền.",
    "Giữ đúng lời thật và bối cảnh.",
    "Cho shop duyệt trước sử dụng."
  ],
  "resources": [
    "người phụ trách nội dung",
    "điện thoại",
    "dữ liệu SKU đã xác nhận"
  ],
  "assumptions": [
    "Chưa biết baseline; cần đo trước khi đặt mục tiêu."
  ],
  "kpis_to_measure": [
    "phản hồi có nội dung",
    "yêu cầu gỡ"
  ],
  "experiment": "So nội dung demo của shop với phản hồi đã được phép, không đổi lời khách",
  "stop_or_adjust_when": "Điều chỉnh khi phản hồi cho thấy hiểu sai, điều kiện đầu vào đổi hoặc công sức vượt nguồn lực; dừng nếu hết quyền dùng dữ liệu/ưu đãi. KPI là đề xuất đo, không phải kết quả."
}
```

## Hướng dẫn sau mua và mua lại

```json
{
  "strategy_id": "strategy_7",
  "problem": "Khách chưa biết cách dùng/chọn tiếp",
  "suitable_when": "Khách chưa biết cách dùng/chọn tiếp và shop có nguồn lực duy trì nội dung",
  "conditions": [
    "Có hướng dẫn xác nhận, kênh liên hệ được phép, khách đồng ý nhận"
  ],
  "message": "Giúp dùng đúng trước khi đề nghị mua tiếp",
  "channels": [
    "facebook",
    "tiktok",
    "shopee"
  ],
  "actions": [
    "Chọn hướng dẫn liên quan SKU đã mua.",
    "Soạn tin ngắn có ích.",
    "Chỉ gửi qua kênh/quyền được phép.",
    "Ghi nhận từ chối và dừng gửi."
  ],
  "resources": [
    "người phụ trách nội dung",
    "điện thoại",
    "dữ liệu SKU đã xác nhận"
  ],
  "assumptions": [
    "Chưa biết baseline; cần đo trước khi đặt mục tiêu."
  ],
  "kpis_to_measure": [
    "phản hồi hữu ích",
    "tỷ lệ từ chối",
    "mua lại có gắn nguồn"
  ],
  "experiment": "Đổi chủ đề hướng dẫn, không tăng tần suất tùy tiện",
  "stop_or_adjust_when": "Điều chỉnh khi phản hồi cho thấy hiểu sai, điều kiện đầu vào đổi hoặc công sức vượt nguồn lực; dừng nếu hết quyền dùng dữ liệu/ưu đãi. KPI là đề xuất đo, không phải kết quả."
}
```

## Thử hai góc tiếp cận

```json
{
  "strategy_id": "strategy_8",
  "problem": "Chưa biết khách cần tình huống hay chi tiết",
  "suitable_when": "Chưa biết khách cần tình huống hay chi tiết và shop có nguồn lực duy trì nội dung",
  "conditions": [
    "Có baseline và đủ năng lực duy trì đo"
  ],
  "message": "Tìm góc có ích bằng dữ liệu",
  "channels": [
    "facebook",
    "tiktok",
    "shopee"
  ],
  "actions": [
    "Chọn một SKU và một chỉ số chính.",
    "Giữ ảnh/CTA, chỉ đổi góc hook.",
    "Đo baseline rồi thử trong điều kiện tương đương.",
    "Xem độ bất định trước quyết định."
  ],
  "resources": [
    "người phụ trách nội dung",
    "điện thoại",
    "dữ liệu SKU đã xác nhận"
  ],
  "assumptions": [
    "Chưa biết baseline; cần đo trước khi đặt mục tiêu."
  ],
  "kpis_to_measure": [
    "chỉ số chính đã chọn",
    "chi phí/nỗ lực",
    "phân phối tiếp cận"
  ],
  "experiment": "Không kết luận từ vài view; không bịa cỡ mẫu hoặc ngưỡng thành công",
  "stop_or_adjust_when": "Điều chỉnh khi phản hồi cho thấy hiểu sai, điều kiện đầu vào đổi hoặc công sức vượt nguồn lực; dừng nếu hết quyền dùng dữ liệu/ưu đãi. KPI là đề xuất đo, không phải kết quả."
}
```
