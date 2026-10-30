# Kết nối Finora Node.js backend với AI Server

## Kiến trúc bắt buộc

```text
Browser -> Finora Client -> Finora Node.js backend -> HTTPS -> Finora AI Server
```

Browser không được gọi `ai.finora.com.vn` trực tiếp và không được nhận `FINORA_SERVICE_KEY`, `WEB_TOKEN_SECRET` hoặc LLM key. Các secret chỉ nằm trong `Finora/server/` hoặc secret manager.

## Cấu hình Node backend

```dotenv
AI_SERVER_URL=https://ai.finora.com.vn
AI_SERVER_TIMEOUT_MS=90000
AI_SERVICE_KEY=<same-value-as-AI-server-FINORA_SERVICE_KEY>
AI_TOKEN_SECRET=<same-value-as-AI-server-WEB_TOKEN_SECRET>
AI_TOKEN_ISSUER=finora-web
AI_TOKEN_AUDIENCE=finora-ai
```

Không dùng prefix `VITE_` cho bất kỳ biến nào ở trên. Với HS256 hiện tại, hai backend chia sẻ signing secret. Nên luân chuyển độc lập signing secret và service key. Một migration tương lai có thể chuyển sang asymmetric signing mà không đổi claims hoặc API contract.

## Tạo JWT ngắn hạn

JWT bắt buộc có:

```json
{
  "user_id": "usr_xxx",
  "tenant_id": "tenant_xxx",
  "shop_id": "shop_xxx",
  "role": "owner",
  "iss": "finora-web",
  "aud": "finora-ai",
  "exp": 1790784000
}
```

Node backend phải xác minh membership shop trước khi ký. Có thể thêm claim `shop_ids` nếu user được phép chuyển giữa nhiều shop; AI Server vẫn yêu cầu `shop_id` hiện hành thuộc danh sách đã ký. Không nhận `tenant_id`, `user_id` hoặc `shop_id` tự do từ browser rồi ký mà chưa authorize.

Ví dụ dùng package `jose`:

```js
import { SignJWT } from "jose";

const encoder = new TextEncoder();

export async function createAiToken({ userId, tenantId, shopId, role, shopIds }) {
  return new SignJWT({
    user_id: userId,
    tenant_id: tenantId,
    shop_id: shopId,
    role,
    ...(shopIds?.length ? { shop_ids: shopIds } : {}),
  })
    .setProtectedHeader({ alg: "HS256", typ: "JWT" })
    .setIssuer(process.env.AI_TOKEN_ISSUER ?? "finora-web")
    .setAudience(process.env.AI_TOKEN_AUDIENCE ?? "finora-ai")
    .setIssuedAt()
    .setExpirationTime("2m")
    .sign(encoder.encode(process.env.AI_TOKEN_SECRET));
}
```

## HTTP client dùng chung

```js
export async function callAiServer({ path, identity, method = "GET", body, timeoutMs }) {
  const token = await createAiToken(identity);
  const controller = new AbortController();
  const timer = setTimeout(
    () => controller.abort(),
    timeoutMs ?? Number(process.env.AI_SERVER_TIMEOUT_MS ?? 90000),
  );

  try {
    const response = await fetch(new URL(path, process.env.AI_SERVER_URL), {
      method,
      headers: {
        Authorization: `Bearer ${token}`,
        "X-Finora-Service-Key": process.env.AI_SERVICE_KEY,
        ...(body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      },
      body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });
    const payload = await response.json();
    if (!response.ok || payload.success === false) {
      const error = new Error(payload.error?.message ?? "AI Server request failed");
      error.code = payload.error?.code ?? "AI_UPSTREAM_ERROR";
      error.status = response.status;
      error.requestId = payload.meta?.request_id;
      throw error;
    }
    return payload;
  } finally {
    clearTimeout(timer);
  }
}
```

Không tự đặt `Content-Type` cho `FormData`; runtime phải tự tạo multipart boundary.

## Contract `/api/v1`

| Method | Path | Input |
| --- | --- | --- |
| `POST` | `/api/v1/data/import` | multipart field `file`; CSV/XLSX |
| `GET` | `/api/v1/data/imports/{import_id}` | path parameter |
| `GET` | `/api/v1/business/overview` | không có body |
| `GET` | `/api/v1/business/health` | không có body |
| `GET` | `/api/v1/business/revenue-leakage` | không có body |
| `GET` | `/api/v1/products` | không có body |
| `GET` | `/api/v1/products/{sku}` | URL-encoded SKU |
| `GET` | `/api/v1/products/{sku}/analysis` | URL-encoded SKU |
| `POST` | `/api/v1/market/product-trends/insights` | Nguyên JSON `{success,data}` từ API xu hướng BE web |
| `GET` | `/api/v1/opportunities` | `category`, `period` |
| `GET` | `/api/v1/action-plan` | `category`, `period` |
| `POST` | `/api/v1/chat` | `ChatRequest`; gửi thêm `trend_data` JSON BE cho câu hỏi xu hướng |
| `POST` | `/api/v1/sales-plan` | `PlannerRequest` |
| `POST` | `/api/v1/communication-plan` | `PlannerRequest` |
| `POST` | `/api/v1/knowledge/upload` | multipart field `file` |

Mọi public response dùng Pydantic schema có tên trong OpenAPI. Success:

```json
{
  "success": true,
  "data": {},
  "meta": { "request_id": "req_01..." }
}
```

Error:

```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_DATA",
    "message": "Không đủ dữ liệu để thực hiện phân tích."
  },
  "meta": { "request_id": "req_01..." }
}
```

Không đổi `INSUFFICIENT_DATA` thành số `0`; UI phải thể hiện thiếu dữ liệu.

Dữ liệu xu hướng thuộc BE web. AI Server không đọc CSV hay lưu snapshot; BE gửi
JSON đúng kỳ/ngành theo mỗi request. Xem [ví dụ insight và chatbot](PRODUCT_TRENDS.md).
GET `/api/v1/market/trends` cũ đã deprecated, không cung cấp dữ liệu cục bộ.

## Import file

```js
export async function importMarketplaceFile(identity, fileBlob, filename) {
  const form = new FormData();
  form.append("file", fileBlob, filename);
  return callAiServer({
    path: "/api/v1/data/import",
    identity,
    method: "POST",
    body: form,
    timeoutMs: 180000,
  });
}
```

`shop_id` không nằm trong query/body; nó được lấy từ JWT đã xác minh. Node nên giới hạn kích thước bằng hoặc nhỏ hơn `MAX_UPLOAD_BYTES`. Không log file, nội dung file hoặc dữ liệu khách hàng. Sau khi xử lý, AI Server xóa raw file tạm theo retention policy và chỉ giữ normalized records.

## Chat

```js
export function chatWithAi(identity, message, filters = {}) {
  return callAiServer({
    path: "/api/v1/chat",
    identity,
    method: "POST",
    body: { message, ...filters },
  });
}
```

`ChatRequest`:

```json
{
  "message": "Tôi nên tập trung vào sản phẩm nào tuần này?",
  "history": [],
  "period": "7d",
  "category": "nam",
  "platform": "shopee"
}
```

`history` và filters là tùy chọn. Không gửi `orderSummary`; AI Server tự truy vấn dữ liệu đã authorize từ repository.

## Planning

`POST /api/v1/sales-plan` và `/api/v1/communication-plan` nhận:

```json
{
  "category": "nam",
  "period": "week",
  "objective": "conversion"
}
```

`period`: `week|month`. `objective`: `awareness|new_customer_acquisition|conversion|retention|clearance`. Kết quả chỉ là khuyến nghị, không tự thực thi thay đổi marketplace.

## Timeout và lỗi

- Analytics không gọi LLM: 15–30 giây.
- Chat/LLM: 90 giây.
- Upload/embedding: 180 giây.
- `401`: token/service key sai, hết hạn, issuer hoặc audience sai; không retry mù.
- `403`: role/shop không được phép; không retry.
- `413/415/422`: file hoặc schema không hợp lệ.
- `429`: retry có exponential backoff cho request idempotent.
- `503`: LLM chưa cấu hình hoặc upstream không khả dụng.

Không retry import tự động nếu chưa có idempotency key. Không trả stack trace hay upstream secret về browser.

## Chat demo cho khách chưa đăng nhập

Hướng dẫn từng bước kèm router Express, widget landing page và proxy local/production: [LANDING_CHATBOT_INTEGRATION.md](LANDING_CHATBOT_INTEGRATION.md).

Luồng landing page vẫn là Browser -> Node backend -> AI Server. Node gọi:

- `GET /api/chatbot/demo/config`
- `POST /api/chatbot/demo/chat`, body `{ "messages": [{"role":"user","content":"Doanh thu hôm qua bao nhiêu?"}] }`

Hai endpoint này chỉ cần `X-Finora-Service-Key`; không tạo/gửi JWT tenant giả cho khách. BE xác định IP thật và **ghi đè** `X-Client-IP` (hoặc `X-Forwarded-For`), không tin header do browser tự gửi. Không dùng helper `callAiServer()` phía trên vì helper đó luôn yêu cầu identity và ký JWT.

```js
export async function callDemoAi(messages, verifiedClientIp) {
  const response = await fetch(new URL("/api/chatbot/demo/chat", process.env.AI_SERVER_URL), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Finora-Service-Key": process.env.AI_SERVICE_KEY,
      "X-Client-IP": verifiedClientIp,
    },
    body: JSON.stringify({ messages }),
    signal: AbortSignal.timeout(90000),
  });
  const payload = await response.json();
  if (!response.ok) {
    const error = new Error(payload.error ?? "Trợ lý demo tạm thời chưa sẵn sàng.");
    error.status = response.status;
    error.requestId = response.headers.get("X-Request-ID");
    error.retryAfter = response.headers.get("Retry-After");
    throw error;
  }
  return payload; // { reply, mode: "demo" }
}
```

Client giữ lịch sử. User tối đa 500 ký tự, assistant cắt còn 2.000 ký tự; server giữ tối đa 10 tin gần nhất, body tối đa 20 KiB. Tin đầu/cuối request phải là user. Rate limit mặc định 15 chat/phút/IP. Lỗi dùng `{ "error": "Thông báo tiếng Việt" }`: `400` input sai, `401` service key sai, `404` demo tắt, `429` hết quota (chờ `Retry-After`), `503` LLM chưa sẵn sàng/timeout/quá tải, `500` lỗi khác.

Cấu hình AI server mới: `DEMO_ENABLED=true`, `DEMO_RATE_LIMIT_PER_MIN=15`, `DEMO_MODEL=` (mặc định Flash-Lite cho Gemini hoặc `FPT_CHAT_MODEL` cho FPT), `BRAND_NAME=Finora`, `WEBSITE_URL=https://finora.com.vn/`, `LOGIN_URL=https://finora.com.vn/signin`, `SIGNUP_URL=https://finora.com.vn/signup`. `ENABLE_DEMO` cũ chỉ điều khiển UI tĩnh, không tắt endpoint mới.

Demo dùng dataset riêng, không đọc dữ liệu shop. Khi knowledge/RAG thiếu nội dung về marketing, bán hàng hoặc vận hành, cả demo và chat đã đăng nhập có thể dùng kiến thức nền LLM; không dùng fallback này để đoán số liệu hay tính năng Finora chưa xác nhận. Xem [DEMO_CHATBOT.md](DEMO_CHATBOT.md) cho curl, allow-list knowledge, giới hạn nhiều worker và UAT.

## Compatibility

Các endpoint `/api/*` cũ đang được giữ dưới dạng deprecated wrappers. `X-API-Key` chỉ dùng cho local/test hoặc migration có kiểm soát khi `ENABLE_LEGACY_API_KEY=true`; production phải dùng `/api/v1`, JWT + service key và đặt `ENABLE_LEGACY_API_KEY=false`.
