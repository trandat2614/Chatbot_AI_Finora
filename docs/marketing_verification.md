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
