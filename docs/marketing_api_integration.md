# Tích hợp API tạo nội dung marketing theo SKU

Luồng: Frontend → BE Finora → AI Server → LLM/RAG → BE. Repository này là AI Server; backend Node nghiệp vụ không có trong workspace. Adapter Node ở [examples/marketing_backend.mjs](examples/marketing_backend.mjs) là code mẫu, chưa gắn vào database/quyền của BE thực tế.

## Chạy và cấu hình

Giữ provider/model hiện có trong `.env`; không cần đổi sang provider khác. Dùng Python 3.11/3.12 trong môi trường dự án:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m src.services.marketing.knowledge --dry-run
.\.venv\Scripts\python.exe -m src.services.marketing.knowledge
.\.venv\Scripts\python.exe -m uvicorn server:app --host 127.0.0.1 --port 8000
```

Migration `20261106_0004` chỉ thêm bảng TTL `marketing_idempotency` trong database AI, không tạo bảng quản lý bản nháp/sản phẩm của BE. Với `AUTO_CREATE_SCHEMA=true`, startup có thể tạo bảng ở local; production chạy migration trước. Dry-run chỉ đọc/validate Markdown và đếm chunk, không gọi provider. Lệnh index thật gọi embedding đã cấu hình và upsert Chroma; chạy tuần tự, không chạy nhiều CLI index cùng một scope. Khởi động lại API sau khi nạp lần đầu.

| Biến | Mặc định và ý nghĩa |
| --- | --- |
| `MARKETING_TIMEOUT_SECONDS` | 60 giây tổng cho sinh nội dung, gồm retrieval, chờ slot, repair |
| `MARKETING_CALL_TIMEOUT_SECONDS` | 20 giây mỗi lượt model; thời gian còn lại nhỏ hơn sẽ được dùng |
| `MARKETING_MAX_REPAIRS` | 1; code giới hạn tối đa 2 lần sửa sau lượt đầu |
| `MARKETING_MAX_WORKLOAD` | 15 phương án/request, 1–3 mỗi target |
| `MARKETING_MAX_TOKENS` | 6000 cho một phương án; giữ nguyên model |
| `MARKETING_RAG_TOP_K` / `MARKETING_RAG_MIN_SCORE` | 3 / 0.25 |
| `MARKETING_CONTEXT_CHARS` | 22000; không cắt ngang ví dụ/timeline |
| `MARKETING_EMBEDDING_TIMEOUT_SECONDS` / `MARKETING_EMBEDDING_RETRIES` | 20 giây / 2 lần thử lại mỗi batch index; embedding FPT tắt retry SDK, API retrieval nằm trong deadline chung |
| `MARKETING_COLLECTION` / `MARKETING_VECTOR_DIR` | `finora_marketing_v1` / `data/marketing_vectors`, tách khỏi collection tài chính |
| `MARKETING_IDEMPOTENCY_TTL_SECONDS` | 86400; tối thiểu timeout tổng + 60 giây |
| `MARKETING_SPEECH_UNITS_PER_SECOND` | 3.5 đơn vị tách khoảng trắng/giây, dùng 80% cảnh cho lời; chỉ là ước lượng |
| `MARKETING_FACEBOOK_STANDARD_UNITS` / `MARKETING_FACEBOOK_SHORT_UNITS` | 120 / 60, mục tiêu biên tập |
| `MARKETING_SHOPEE_TITLE_CHARS` | 120 ký tự, cấu hình biên tập Finora |

Các mốc 15/30/60 giây, độ dài bài và tỷ lệ quay gợi ý là lựa chọn của Finora; không tuyên bố là giới hạn chính thức của nền tảng.

## Xác thực và ràng buộc shop

Mọi endpoint dưới đây cần cả hai header:

```http
Authorization: Bearer <JWT-do-BE-ky>
X-Finora-Service-Key: <FINORA_SERVICE_KEY-phia-server>
Idempotency-Key: <khoa-luu-cung-thao-tac-BE>
```

`Idempotency-Key` bắt buộc ở POST, gồm chữ/số/`.`/`_`/`:`/`-`, tối đa 120 ký tự. GET capabilities không cần key này. JWT HS256 có `user_id`, `tenant_id`, `shop_id`, `role`, `iss`, `aud`, `exp`; issuer/audience/secret khớp cấu hình hiện hữu. Role `owner/admin/analyst` được tạo nội dung; `viewer` chỉ xem capabilities. Marketing không dùng auth legacy ngay cả khi endpoint cũ còn bật chế độ đó.

BE phải xác thực thành viên shop, quyền quản lý nội dung, SKU, snapshot, references và hạn mức trước khi ký token/gọi AI. Service key chung chứng minh caller là BE tin cậy; JWT ràng buộc user/tenant/shop do BE xác minh. Service key không tự cấp quyền người dùng. Triển khai hiện có một issuer/shared service caller; không phát cùng key cho bên thứ ba. Nhiều caller độc lập cần credentials/issuer và scope riêng trước khi mở quyền.

Không truyền `tenant_id/shop_id/user_id/verified` trong JSON: schema từ chối các trường này. AI tin snapshot vì nó đến từ BE đã được xác thực, không vì cờ `verified=true`. AI không có quyền tự đối chiếu database catalog bên ngoài repo. Không cho trình duyệt gọi AI trực tiếp hoặc thấy service/provider key.

## Endpoint và schema

| Method | Route `/api/v1/marketing` | Hành vi |
| --- | --- | --- |
| GET | `/capabilities` | Tổ hợp target, enum mục tiêu, duration, mode, cấu hình |
| POST | `/generate` | Một SKU, nhiều target; 1–3 phương án/target |
| POST | `/video-scripts/generate` | Chung service `/generate`, chỉ cho target video |
| POST | `/rewrite` | Một source/version + target cũ, tạo đúng một bản mới |
| POST | `/video-scripts/adapt` | Source video + snapshot hiện tại + target video đích |
| POST | `/calendar` | Lịch đề xuất 7 ngày liên tiếp, có thể kèm sinh nội dung trong workload |
| POST | `/strategy` | 2–3 chiến lược ưu tiên từ shop context và snapshot |

Swagger/OpenAPI: `/docs`, `/openapi.json` khi bật `ENABLE_API_DOCS`. Content response dùng discriminated union theo `content_type`.

| channel | placement | content_type |
| --- | --- | --- |
| facebook | feed | caption |
| facebook | reels | video_script |
| tiktok | short_video | video_script |
| shopee | product_listing | listing |
| shopee | video | video_script |

Dùng `targets` để yêu cầu caption và Reels cùng Facebook. `channels` tương thích ánh xạ Facebook→feed/caption, TikTok→short_video/video_script, Shopee→product_listing/listing. Gửi đồng thời `channels` và `targets`, lặp target hoặc tổ hợp sai trả 422; không âm thầm tạo hai lần.

Snapshot bắt buộc: `sku`, `name`, `source`, `updated_at` có timezone. `attributes` là mảng `{key,value,source}`, tối đa 30; `evidence` tương tự, tối đa 15, dành cho số bán/tồn/review do hệ thống tính và xác minh. `price` tùy chọn, số không âm tối đa 2 chữ số thập phân; `currency` ISO 3 chữ. `product_url` chỉ http(s), không credentials. `offer` cần description, conditions, starts_at/ends_at có timezone và source; phải có hiệu lực tại lượt tạo. Không tự tính giá giảm hoặc suy công dụng từ vật liệu.

`objective`: `introduce_product`, `drive_sales`, `promote_offer`, `answer_questions`. `promote_offer` thiếu offer trả `needs_input` với `missing_fields`, không gọi model. Thiếu giá vẫn tạo nội dung giới thiệu. Dữ liệu ít không phải lý do bịa chi tiết.

Cấu hình chung: `brand` (name/voice/address_as/avoid_terms), audience, tone, length short/standard, variants, emoji_limit 0–2 (mặc định 0), include_hashtags=false, instructions, opening_requirement, cta. Các chuỗi/mảng bị giới hạn trong schema. Brand profile do BE nạp cấu hình shop; màn hình quản trị và quyền sửa profile thuộc BE.

Video có `duration_seconds`, `video_style`, `production_mode`, `resources`, `cta_type`, `include_post_caption`, `include_shot_list`. Một số trường có thể ghi đè từng target. `commerce_context` theo channel: `product_attachment=confirmed/unavailable/unknown` (mặc định unknown), messaging_supported và listing_reference. Không xác nhận thì không viết “bấm giỏ hàng”. Shopee không giao dịch ra ngoài sàn. Resources thiếu thì ghi giả định một người/điện thoại; không chặn tạo.

Video response có title/concept/angle/objective/audience/hook/key_message, scenes, CTA có điều kiện, cover_text, post_caption, production/checklist và plain_text. Scene có ID, start/end/duration, visual_action, shot_type, camera_direction, dialogue/voiceover, on_screen_text, audio_direction, editing_notes. Timeline liên tục từ 0 đến đúng tổng; text_only không lời, hands_only/voiceover không ép lộ mặt. Speech validator chỉ ước lượng khả năng đọc, chưa đo audio thật.

## Request/response đầy đủ

Các file dưới đây là fixture giả lập, đã validate theo schema và chạy qua pipeline với model mock `offline-fixture`. Không phải response provider thật, không fake token usage hoặc nguồn RAG; `duration_ms=0` là fixture tĩnh. Mọi timeline trong response là dữ liệu đầy đủ, không thay bằng dấu ba chấm.

| Tình huống | Request JSON | Response JSON |
| --- | --- | --- |
| Facebook không giá/không ưu đãi | [generate.request.json](examples/marketing/generate.request.json) | [generate.response.json](examples/marketing/generate.response.json) |
| Cùng SKU → TikTok + Reels + Shopee Video | [video_generate.request.json](examples/marketing/video_generate.request.json) | [video_generate.response.json](examples/marketing/video_generate.response.json) |
| Viết lại video thành text_only | [rewrite.request.json](examples/marketing/rewrite.request.json) | [rewrite.response.json](examples/marketing/rewrite.response.json) |
| Chuyển TikTok sang Reels/Shopee Video | [adapt.request.json](examples/marketing/adapt.request.json) | [adapt.response.json](examples/marketing/adapt.response.json) |
| Lịch đủ 7 ngày, chưa tạo bản nháp | [calendar.request.json](examples/marketing/calendar.request.json) | [calendar.response.json](examples/marketing/calendar.response.json) |
| Chiến lược shop nhỏ | [strategy.request.json](examples/marketing/strategy.request.json) | [strategy.response.json](examples/marketing/strategy.response.json) |

HTTP collection có đủ JSON: [marketing_api.http](marketing_api.http). Ví dụ gọi từ PowerShell bằng curl.exe, đọc credentials từ môi trường server/test, không lưu key vào file:

```powershell
curl.exe --request POST 'http://127.0.0.1:8000/api/v1/marketing/video-scripts/generate' --header "Authorization: Bearer $env:FINORA_AI_JWT" --header "X-Finora-Service-Key: $env:FINORA_SERVICE_KEY" --header 'Idempotency-Key: video-action-001' --header 'Content-Type: application/json' --data-binary '@docs/examples/marketing/video_generate.request.json'
```

Envelope marketing được trả trực tiếp (khác lớp `success/data/meta` của endpoint cũ): request_id, status, items, errors, warnings, missing_fields, metadata; calendar/strategies khi phù hợp. `status` là kết quả xử lý AI (`success/partial_success/failed/needs_input`), không phải trạng thái bản nháp của BE. Mọi item có `status=draft`. Metadata gồm prompt version, hash knowledge thực sự đã dùng hoặc null, sources là doc/chunk/version/hash/source_ids thật sự đưa vào prompt, model và usage chỉ nếu provider trả. Source_ids trỏ [sổ nguồn](../knowledge/marketing/11_sources.md); ví dụ giả lập không trở thành fact của shop.

## Lỗi, timeout, retry và idempotency

| HTTP | Cách xử lý |
| --- | --- |
| 200 success | Lưu item thành bản nháp; shop xem lại trước khi ready |
| 200 partial_success | Giữ item thành công, hiển thị errors theo target/variant; chỉ retry phần lỗi |
| 200 needs_input | Hiển thị missing_fields, bổ sung dữ liệu rồi tạo thao tác/key mới |
| 401/403 | Sửa JWT/service credential/quyền; không retry model |
| 422 | Sửa schema; `error.fields` có đường dẫn và kiểu lỗi, không echo payload riêng tư |
| 409 IDEMPOTENCY_CONFLICT | Cùng key khác body; kiểm tra thao tác BE, không tự thay body |
| 409 IDEMPOTENCY_IN_PROGRESS | Cùng thao tác đang chạy/gián đoạn; dùng cùng key/body, theo Retry-After; cần đối soát nếu worker đã chết |
| 429 | Rate limiter hiện hữu; BE/proxy đặt backoff và hạn mức |
| 502 | Không có item hợp lệ do model/upstream/validator; errors có mã cụ thể |
| 503 | Chưa cấu hình LLM |
| 504 | Tất cả slot hết thời gian; một phần timeout nhưng còn item thì 200 partial_success |

Auth/schema/role errors dùng envelope lỗi hiện hữu của repo; lỗi sau pipeline dùng MarketingResponse. Giới hạn tổng mặc định 60s, tối đa 3 slot model đồng thời/request; SDK không thêm retry ẩn. Chỉ repair schema/facts/style của slot lỗi, tối đa MARKETING_MAX_REPAIRS; lỗi network/timeout không tạo vòng gọi vô hạn. BE đặt HTTP/proxy timeout lớn hơn AI, ví dụ 70s, và theo dõi latency thực tế. Thread I/O có thể hoàn tất muộn sau khi bỏ chờ; không dùng kết quả muộn, không phát sinh upload/đăng bài. Không coi timeout là bằng chứng provider chưa tính phí.

POST cần Idempotency-Key lưu tại BE trước lần gọi đầu. Database unique key gồm caller issuer/auth method + user + tenant + shop + endpoint + key, lưu payload hash, operation ID, response và HTTP status. Cùng key/body trả lại item/reference và request_id gốc, metadata.idempotency_replayed=true; X-Request-ID header vẫn là HTTP attempt hiện tại. Cache có cả failed/needs_input: retry nghiệp vụ phải dùng key mới.

TTL mặc định 24 giờ; request đầu sau TTL dọn record hết hạn. Sau TTL hoặc khi mất database không có bảo đảm chống trùng; BE vẫn cần unique client_reference. Các worker phải dùng chung database PostgreSQL. Pending record khi worker crash được giữ đến TTL để tránh tự gọi model lần hai; không có bảo đảm exactly-once với provider sau crash/timeout. Không dùng RAM để cam kết chống trùng. Chỉ cache kết quả tạm thời; không lưu snapshot request, không thay kho phiên bản BE. Response text có dữ liệu shop nên database/backups cần cùng quyền truy cập như AI server.

Retry riêng một slot gửi lại cấu hình/snapshot, `previous_request_id`, cùng danh sách targets và `retry_slots` như sau, với key thao tác mới:

```json
{"previous_request_id":"req_example_failed","retry_slots":[{"target":{"channel":"shopee","placement":"video","content_type":"video_script"},"variant":2}]}
```

Đây là phần bổ sung vào request gốc, không phải body hoàn chỉnh. Server chỉ tạo slot được chỉ định; BE quyết định slot nào thật sự lỗi từ response cũ. `previous_request_id` là provenance, không cấp quyền đọc job khác.

## BE lưu phiên bản và lịch

1. Xác thực shop/SKU, lấy snapshot hiện tại, merge bổ sung đã được người dùng xác nhận; lưu input cùng thao tác BE. Không cập nhật catalog ngầm.
   BE đặt thao tác ở trạng thái đang xử lý ngay trước khi gọi AI; endpoint AI xử lý đồng bộ và trả kết quả trong deadline, không cung cấp queue/job polling riêng.
2. Giữ mỗi item bằng client_reference duy nhất theo tenant/shop. Lưu structured content, plain_text, SKU, target, objective, cấu hình, product snapshot, creator, thời điểm BE lưu, prompt/knowledge metadata, warnings và nguồn.
3. Rewrite/adapt nhận source.client_reference + version_reference + target + content có cấu trúc, tùy chọn product_snapshot cũ; dùng product hiện tại làm nguồn facts. Response trả source refs và client ref mới. Nếu snapshot nguồn thiếu/khác thì cảnh báo rà thông tin cũ. Tạo version mới, giữ source version nguyên vẹn, trạng thái mới draft. `change_summary` là mô tả thao tác, không phải semantic diff tự xác minh.
4. Sửa thủ công tạo version riêng ở BE; nhắc thay đổi chưa lưu ở frontend. Chỉ shop duyệt mới ready. So giá/ưu đãi snapshot với catalog hiện tại; khác thì đánh dấu cần rà soát và chặn ready đến khi xác nhận lại. Archive/history/filter/export/copy nằm tại BE/frontend; AI không tạo thêm hệ quản lý trùng.
5. Calendar nhận references `{client_reference,draft_reference?,version_reference,sku,target,status}` do BE kiểm tra quyền. Lịch ghim phiên bản cụ thể; reference mới sinh chỉ có client_reference, BE lưu content trước rồi ánh xạ sang draft/version DB. Không có content thì needs_generation và reference null. Một ngày có thể nhiều target. `generate_content=true` chỉ tạo số variant theo workload một lần, có thể tái sử dụng cho lịch; không tự sinh 7×n video. Đây là phân bổ biên tập xác định, không dự báo giờ đăng tối ưu.
6. BE cho đổi ngày/bản nháp/bỏ mục; khi phiên bản thay đổi, chỉ rõ lịch đang ghim version nào, cho cập nhật có chủ ý. Không tự coi lịch/AI output đã đăng.

Strategy nhận shop_context, objective, products (1–5), audience/budget/resources tùy chọn. Trả priority, problem, suitable_when, conditions, message, channels, 3–5 actions, resources, assumptions, kpis_to_measure, experiment và stop_or_adjust_when. KPI mục tiêu là gợi ý cần đo; không giả số liệu hiện tại, không cam kết doanh thu.

## Chat và RAG

`POST /api/v1/chat` hỗ trợ typed tool intent `marketing_action={sku,targets,objective,variants}` do BE định tuyến. AI resolve SKU từ commerce repository theo tenant/shop đã xác thực; không nhận raw snapshot trong chat. Câu hỏi tự do và các intent cũ giữ luồng hiện tại; BE dùng intent/tool selector hiện có để chọn action rõ ràng, không dựa vào một từ khóa. Khi catalog AI chưa có SKU, chat trả 404; gọi marketing API với snapshot BE đã xác nhận thay thế. Chat dùng chung generation service, nhưng contract idempotency POST ở trên áp dụng cho router `/marketing`; BE muốn chống trùng thao tác sáng tạo nên dùng router này.

Public marketing chỉ ở collection riêng, private retrieval phải khớp tenant+shop+placement+content_type; có post-filter chống vector backend trả nhầm. Tài liệu ví dụ được giữ nguyên facts/timeline/CTA trong một chunk, top_k và budget giới hạn. Thiếu/lỗi RAG thì cảnh báo và sinh từ rule cốt lõi + snapshot, sources rỗng; không giả đã fine-tune.

Generation ưu tiên loại tài liệu `caption_examples/listing_examples/video_examples` tương ứng; strategy chỉ lấy `strategies`. Điểm truy xuất của collection L2 được quy đổi `1 / (1 + distance)` về (0,1], là điểm xếp hạng cấu hình, không phải xác suất đúng hoặc cosine. Điều chỉnh ngưỡng bằng đánh giá nội dung thực tế. Tránh dùng mapping mặc định giả định unit-vector khiến điểm âm và loại toàn bộ kết quả.

CLI private là thao tác quản trị server:

```powershell
.\.venv\Scripts\python.exe -m src.services.marketing.knowledge --directory 'D:\private-marketing\shop-a' --scope private --tenant-id tenant-a --shop-id shop-a --dry-run
```

Front matter private cần tenant_id/shop_id khớp CLI. Không đưa đánh giá/tài sản riêng của shop vào tài liệu public. Xem [knowledge/marketing/README.md](../knowledge/marketing/README.md) và [11_sources.md](../knowledge/marketing/11_sources.md) để cập nhật.

## Kiểm thử và giới hạn đã biết

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_marketing.py -q
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/build_marketing_examples.py
.\.venv\Scripts\python.exe scripts/build_marketing_api_examples.py
```

Test tự động dùng mock LLM/vector store; không gọi provider trả phí. Validator kiểm tra schema, arithmetic, references, số/giá/link, một số claim rủi ro, style và timeline. Kiểm tra ngữ nghĩa mọi câu tiếng Việt và chứng từ nguồn vẫn cần BE/shop; metadata.requires_human_review luôn true. Có thể từ chối nhầm/không phát hiện một diễn đạt claim mới; theo dõi mã OUTPUT_REJECTED và tập test khi chỉnh rules. `fact_claims` là annotation từ model với reference đã kiểm tra, không phải chứng nhận mọi mệnh đề đã được chứng minh.

Rate limit hiện hữu trong RAM theo process, cần proxy/gateway và quota BE cho nhiều worker. Idempotency là database, tách khỏi rate limit. API không render video, tạo giọng đọc, chạy ads, upload hoặc đăng bài. Tình trạng kiểm thử live/index thực tế được ghi trong [marketing_verification.md](marketing_verification.md).
