# Checklist — API bất kỳ

## 1. Contract
- [ ] Response đúng schema doc: field đủ, đúng kiểu, null-handling
- [ ] Status code đúng ngữ nghĩa: 400 (input sai) vs 401 (chưa auth) vs 403 (thiếu quyền) vs 404 vs 409 — KHÔNG phải cái gì cũng 200 kèm `{"error": ...}` hoặc cái gì cũng 500
- [ ] Body thiếu field bắt buộc, thừa field lạ, sai kiểu (string thay số), body rỗng `{}`, không phải JSON
- [ ] Error response có lộ stack trace / SQL / path nội bộ không? (P2-security)

## 2. Query & pagination
- [ ] page=0, page=-1, page=999999, size=0, size=10000
- [ ] Sort theo field không tồn tại, filter giá trị rỗng
- [ ] Tổng số item (total) có khớp thực tế không, item có trùng/lọt giữa các trang không?

## 3. Method & idempotency
- [ ] Gọi method sai (GET endpoint của POST) → 405?
- [ ] Gọi lại request tạo (POST) 2 lần → 2 bản ghi trùng?
- [ ] DELETE bản ghi đã xóa → 404 hay 500?
- [ ] Update bản ghi không tồn tại / của tenant khác → 404/403?
- [ ] PUT/PATCH gọi 2 lần cùng payload → kết quả có giống nhau (đúng ngữ nghĩa idempotent)?
- [ ] POST có hỗ trợ `Idempotency-Key` header không? Gửi cùng key 2 lần trả cùng response?

## 4. Rate limit & throttling
- [ ] Gửi liên tục N request/giây (vượt giới hạn) → có trả 429 với `Retry-After` header không?
- [ ] Sau khi bị 429, chờ đúng thời gian → được phép lại chưa?
- [ ] Rate limit áp per-user vs per-IP vs per-token — đúng scope không? (multi-user chung IP có bị chặn nhầm?)
- [ ] Response 429 có lộ chi tiết chính sách rate limit không (`X-RateLimit-*` header) → an toàn hay tiện dụng?

## 5. Versioning & error format
- [ ] Endpoint deprecated có trả `Deprecation` / `Sunset` header không?
- [ ] Version cũ (`/api/v1/...`) và mới (`/api/v2/...`) song song: response format có breaking change không?
- [ ] Error envelope thống nhất chưa: mọi lỗi cùng `{error: {code, message, details}}` (hoặc format chuẩn khác) — KHÔNG lộn xộn (chỗ trả `{error: "..."}`, chỗ `{message: "..."}`, chỗ `{errors: [...]}`)
- [ ] Error code có mã hoá cụ thể để client i18n không (vd `VALIDATION_EMAIL_INVALID`) — hay chỉ có message tiếng Anh?

## 6. CORS & cache header
- [ ] Endpoint public: `Access-Control-Allow-Origin` có đúng whitelist không (không phải `*` cho endpoint có credentials)?
- [ ] Preflight OPTIONS request có được chấp nhận không?
- [ ] `Cache-Control` header đúng: endpoint trả data nhạy cảm (user info, token) → PHẢI `no-store`, không được `public, max-age=X`
- [ ] `Content-Type` response luôn set đúng (JSON API trả `application/json`, không phải `text/html`)
- [ ] Response có `ETag` / `Last-Modified` để hỗ trợ conditional request không (nếu áp dụng)?

## 7. Content & encoding
- [ ] Request body UTF-8 với ký tự phi-ASCII (tiếng Việt có dấu, emoji, tiếng Trung) → save + return đúng không?
- [ ] Content-Length khai lớn hơn body thực → server có timeout đúng cách hay treo?
- [ ] Gửi body không đúng `Content-Type` header (JSON body nhưng khai `text/plain`) → 400 hay lặng lẽ parse?
- [ ] Response compression (gzip, brotli): client accept gzip → server có trả compressed không? Hiệu năng payload lớn?
