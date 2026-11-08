# Kết quả kiểm chứng marketing — 2026-11-06

## Phạm vi đã thực hiện

- 7 route marketing được đăng ký trong OpenAPI, gồm capabilities và 6 POST. Có enum/tổ hợp target và discriminated union caption/listing/video.
- Tái sử dụng FastAPI, auth JWT + service key, LLM client FPT/Gemini, embedding client và Chroma hiện hữu; không thay provider/model hoặc thêm queue.
- Database AI có migration `20261106_0004` cho cache idempotency TTL; không thêm hệ quản lý bản nháp/sản phẩm/phiên bản BE.
- Contract BE, adapter Node dùng built-in crypto/fetch, 6 cặp JSON request/response đầy đủ và HTTP collection.

## Tri thức và kiểm chứng nguồn

16 Markdown trong `knowledge/marketing/`: 8 caption, 8 listing, 8 TikTok, 8 Reels, 8 Shopee Video; 3 bộ chuyển thể có đủ 3 script/bộ (các script dùng lại kịch bản cùng snapshot để so sánh). Ngoài ra có 20 hook, 20 CTA, 8 chiến lược, 3 lịch đủ 7 ngày, 10 cặp sửa và hướng dẫn sản xuất.

10 nguồn đã mở/đọc từ 5 đơn vị: TikTok, HubSpot, Shopee, Buffer, Mailchimp. 2 URL Meta chuyển tới đăng nhập/chặn nên unverified, không gán spec Meta cho code. URL, ngày kiểm tra, nội dung áp dụng và trạng thái tại [11_sources.md](../knowledge/marketing/11_sources.md).

Index thật bằng `Vietnamese_Embedding` của FPT vào `finora_marketing_v1`, trong `data/marketing_vectors`:

```json
{"total":352,"upserted":352,"deleted":0,"dry_run":false}
```

Truy xuất thật đã trả 3 chunk cho mỗi placement `tiktok/short_video`, `facebook/reels`, `shopee/video`, đúng các doc `04_tiktok_scripts`, `12_facebook_reels_scripts`, `13_shopee_video_scripts`, không có warning. Generation filter đúng loại bài mẫu; strategy filter `strategies`. Điểm L2 dùng mapping có miền (0,1] để tránh loại toàn bộ kết quả do mapping unit-vector mặc định. Nạp lại cùng thư mục cho kết quả upsert 0, delete 0, vẫn 352 chunk.

Vector data là artifact local được gitignore; khi triển khai cần chạy lệnh index ở môi trường đích. Không reset collection tài chính. Không fine-tune hoặc thay trọng số model.

## Kiểm thử

- Bộ test marketing: 93 bài đạt, mock LLM và embedding; có test Chroma adapter thật với embedding offline.
- Phủ auth thiếu/sai, role viewer, giả ID trong body, scope private/cross-shop, malformed JSON và repair hữu hạn, retry đúng slot, prompt injection input/KB, secret output, facts/giá/ưu đãi/link, emoji grapheme, video timeline/mode/nguồn lực, 6 script trong một request, rewrite/adapt provenance, calendar 7 ngày/reference, strategy, idempotency concurrent worker và TTL, index lặp/sửa/xóa, JSON fixtures và các route HTTP.
- Kiểm thử hồi quy lần đầu: **267 passed, 1 failed**. Lỗi duy nhất ở `tests/test_demo_chat.py::test_system_chat_uses_only_system_info_prompt_and_llm`: test đòi đúng chuỗi “chỉ giới thiệu tổng quát trong 1-2 câu”, trong khi prompt hiện tại dùng “giới thiệu ngắn gọn trong 2-3 câu”.
- Đã tạo worktree từ **HEAD 26b37939**, chạy riêng test trên bản gốc và tái hiện cùng lỗi. Worktree đã được dọn. Không sửa prompt/test demo ngoài phạm vi.
- Sau bổ sung test: hồi quy **275 passed, 1 deselected** (chỉ loại test demo đã xác nhận lỗi gốc). Lần kiểm tra cuối riêng marketing đạt 93 bài.
- OpenAPI/import/compile kiểm tra được; `git diff --check` đạt; Node adapter qua `node --check`.
- Alembic upgrade → downgrade một revision → upgrade đạt trên SQLite tạm trong `.cache`; không chạy migration lên PostgreSQL đang cấu hình. Production cần chạy migration trước khi gọi POST có idempotency.

## Provider live và phần BE còn cần cấu hình

Provider hiện hữu: **FPT**, chat model **DeepSeek-V4-Flash**. Một lần smoke test generation và một lần chẩn đoán request tối giản đều trả **HTTP 403**: `Model 'DeepSeek-V4-Flash' is not allowed for this API key.` Không đổi model hoặc thử key khác. Embedding FPT hoạt động và đã nạp/truy xuất thật như trên.

Do quyền model bị từ chối, **chưa xác minh sinh nội dung live thành công**, chất lượng copy của model, token usage thành công và latency thực tế. Tài liệu JSON response là fixture offline có nhãn rõ, không phải kết quả model live. Khi key được cấp quyền, chạy smoke test qua route thực, kiểm tra chất lượng/facts, thời gian và usage trên dữ liệu giả lập trước khi mở cho shop.

Backend nghiệp vụ Node không có trong workspace: cần nối adapter với auth/shop membership/catalog/quota và giao dịch lưu phiên bản/lịch; cấp JWT/service key đúng môi trường, chạy migration AI, nạp knowledge ở server đích, và cấp quyền FPT cho model hiện tại. Frontend/BE chịu trách nhiệm duyệt ready/archive/history, phát hiện giá/ưu đãi đổi, nhắc nội dung chưa lưu và copy/export. Không có bước đăng bài, chạy ads hoặc render/upload video trong tính năng này.

## Kiểm chứng lại — 2026-11-08

Provider đang cấu hình: **Gemini**, `GEMINI_MODEL=gemini-3.5-flash`, embedding `models/gemini-embedding-001`. Index marketing hiện có 352 chunk, vector 3072 chiều khớp embedding đang dùng (index lại: upserted 0).

- `gemini-3.5-flash` trả **429 RESOURCE_EXHAUSTED**: key free tier giới hạn 20 request/ngày/model. `DEMO_MODEL` cũng là model này nên chat landing page dùng chung hạn mức.
- Vì vậy kiểm thử live chạy bằng **`gemini-3.5-flash-lite`** qua biến môi trường của tiến trình test (không sửa `.env`). Kết quả với `gemini-3.5-flash` **chưa xác minh**; chạy lại smoke test khi quota reset hoặc khi dùng key trả phí.
- Luồng live đã chạy: BE Finora (Node, MongoDB local) → AI Server → Gemini, và giao diện web. Lượt cuối đạt 44/45 kiểm tra; ưu đãi đạt 3/3 trong 2 lượt liên tiếp với ngày/giá đúng; phần thiếu duy nhất là 1/3 phương án Facebook bị loại do model trích sai `fact_claims` (thử lại phần lỗi tạo được ngay).
- Bộ test: 293 passed; 1 lỗi cũ không thuộc marketing (`tests/test_demo_chat.py`, assertion còn đòi câu chữ prompt trước commit 88b38bf).

Lỗi đã sửa trong lần kiểm chứng này (đều có test):

1. Lỗi tạm thời của provider (429/5xx/mất kết nối) bị bỏ ngay → nay thử lại có backoff trong deadline; hết quota theo ngày trả nhanh `PROVIDER_RATE_LIMITED` với thời gian chờ.
2. Ưu đãi có số tiền (`Giảm 20.000đ`) luôn bị coi là sai giá → số tiền lấy từ ưu đãi đã xác nhận được chấp nhận; "giá 20.000đ" vẫn bị chặn.
3. Hạn ưu đãi bắt buộc dạng ISO trong bài → chấp nhận dd/mm/yyyy, d/m, "ngày d tháng m" theo `BUSINESS_TIMEZONE`.
4. Nhận diện ưu đãi bỏ sót số tiền nhiều chữ số (`giảm 20.000đ`) → đã sửa regex.
5. Ngày bịa trong bài (ví dụ "đến 15/03" khi ưu đãi hết 15/11) không bị phát hiện, số đứng cuối câu ("năm 2029.") bị bỏ qua → thêm kiểm tra `unprovided_date`, sửa nhận diện số.
6. Facts ưu đãi dạng `2026-11-15 03:05` khiến model viết "15/03" → facts hiển thị `15/11/2026 03:05 (Asia/Ho_Chi_Minh)`.
7. Bài Facebook quảng bá ưu đãi thiếu điều kiện/hạn → server bổ sung nguyên văn từ dữ liệu shop kèm cảnh báo.
8. Kịch bản video không có lời nói vẫn hợp lệ (trái AC-02) → bắt buộc có lời (trừ `text_only`) và chữ trên màn hình.
9. `fact_claims` khác chữ hoa/thường hoặc dấu câu cuối với bài bị loại cả bản → so khớp chuẩn hóa.
10. Model nhận schema gồm cả 3 loại nội dung và đôi khi trả sai loại → gửi schema đúng loại của target (caption ~1,7k ký tự thay vì ~8,8k).
11. Lệnh index báo thành công dù embedding model đổi khác vector đã lưu → kiểm tra số chiều, báo `EmbeddingModelMismatch`.

Còn cần quyết định/cấu hình:

- `AUTH_RATE_LIMIT_PER_MINUTE` (mặc định 10) đếm mọi request đã xác thực theo IP. Kiến trúc hiện tại chỉ có BE gọi AI từ một IP, nên toàn hệ thống bị giới hạn 10 request/phút cho mọi tính năng AI. Cần tăng giá trị này hoặc chỉ đếm lần xác thực thất bại.
- Khi đổi provider/embedding model: dùng `MARKETING_VECTOR_DIR`/`MARKETING_COLLECTION` mới hoặc xóa thư mục vector marketing, rồi index lại public và từng thư mục private.
- Khởi động lại AI Server đang chạy để nạp các thay đổi trên.
