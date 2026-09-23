# Checklist — API bất kỳ

> **Mục checklist là câu hỏi để thử, không phải kỳ vọng.** Kỳ vọng lấy từ tài liệu; tài liệu không nói → điểm hỏi.
> Không chép từ như "tử tế / rõ ràng / OK" vào Kỳ vọng. Trích nguồn trong TC: `Nguồn: <checklist> <số mục>`, vd `form-input 2.3`.

## 1. Contract
- [ ] 1.1 Response đúng schema doc: field đủ, đúng kiểu, null-handling
- [ ] 1.2 Status code đúng ngữ nghĩa: 400 (input sai) vs 401 (chưa auth) vs 403 (thiếu quyền) vs 404 vs 409 — KHÔNG phải cái gì cũng 200 kèm `{"error": ...}` hoặc cái gì cũng 500
- [ ] 1.3 Body thiếu field bắt buộc, thừa field lạ, sai kiểu (string thay số), body rỗng `{}`, không phải JSON
- [ ] 1.4 Error response có lộ stack trace / SQL / path nội bộ không? (severity theo thang BUGS.md)

## 2. Query & pagination
- [ ] 2.1 page=0, page=-1, page=999999, size=0, size=10000
- [ ] 2.2 Sort theo field không tồn tại, filter giá trị rỗng
- [ ] 2.3 Tổng số item (total) có khớp thực tế không, item có trùng/lọt giữa các trang không?

## 3. Method & idempotency
- [ ] 3.1 Gọi method sai (GET endpoint của POST) → 405?
- [ ] 3.2 Gọi lại request tạo (POST) 2 lần → 2 bản ghi trùng?
- [ ] 3.3 DELETE bản ghi đã xóa → 404 hay 500?
- [ ] 3.4 Update bản ghi không tồn tại / của tenant khác → 404/403?
- [ ] 3.5 PUT gọi 2 lần cùng payload → cùng trạng thái cuối (PUT idempotent theo RFC 9110); PATCH idempotent **chỉ khi** API doc cam kết (PATCH kiểu "tăng thêm 1" thì không)
- [ ] 3.6 POST có hỗ trợ `Idempotency-Key` header không? Gửi cùng key 2 lần trả cùng response?

## 4. Rate limit & throttling
- [ ] 4.1 Vượt giới hạn tài liệu nêu → có 429 + `Retry-After` không? **An toàn**: dùng n nhỏ nhất vừa đủ vượt ngưỡng tài liệu nêu, giãn cách, dừng ngay khi thấy 429; tài liệu không nêu ngưỡng → hỏi; gửi dồn dập chỉ khi SCOPE §7 cho phép kiểm thử tải
- [ ] 4.2 Sau khi bị 429, chờ đúng thời gian → được phép lại chưa?
- [ ] 4.3 Rate limit áp per-user vs per-IP vs per-token — đúng scope không? (multi-user chung IP có bị chặn nhầm?)
- [ ] 4.4 Response 429 có lộ chi tiết chính sách rate limit không (`X-RateLimit-*` header) → an toàn hay tiện dụng?

## 5. Versioning & error format
- [ ] 5.1 Endpoint deprecated có trả `Deprecation` / `Sunset` header không?
- [ ] 5.2 Version cũ (`/api/v1/...`) và mới (`/api/v2/...`) song song: response format có breaking change không?
- [ ] 5.3 Error envelope thống nhất chưa: mọi lỗi cùng `{error: {code, message, details}}` (hoặc format chuẩn khác) — KHÔNG lộn xộn (chỗ trả `{error: "..."}`, chỗ `{message: "..."}`, chỗ `{errors: [...]}`)
- [ ] 5.4 Error code có mã hoá cụ thể để client i18n không (vd `VALIDATION_EMAIL_INVALID`) — hay chỉ có message tiếng Anh?

## 6. CORS & cache header
- [ ] 6.1 Gửi `Origin: https://evil.example` và `Origin: null` tới endpoint có credentials → response KHÔNG phản chiếu lại origin đó kèm `Access-Control-Allow-Credentials: true` (lỗ thật; `*` + credentials thì trình duyệt đã tự chặn)
- [ ] 6.2 Preflight OPTIONS request có được chấp nhận không?
- [ ] 6.3 `Cache-Control` header đúng: endpoint trả data nhạy cảm (user info, token) → PHẢI `no-store`, không được `public, max-age=X`
- [ ] 6.4 `Content-Type` response luôn set đúng (JSON API trả `application/json`, không phải `text/html`)
- [ ] 6.5 Response có `ETag` / `Last-Modified` để hỗ trợ conditional request không (nếu áp dụng)?

## 7. Content & encoding
- [ ] 7.1 Request body UTF-8 với ký tự phi-ASCII (tiếng Việt có dấu, emoji, tiếng Trung) → save + return đúng không?
- [ ] 7.2 Content-Length khai lớn hơn body thực → server có timeout đúng cách hay treo?
- [ ] 7.3 Gửi body không đúng `Content-Type` header (JSON body nhưng khai `text/plain`) → 400 hay lặng lẽ parse?
- [ ] 7.4 Response compression (gzip, brotli): client accept gzip → server có trả compressed không? Hiệu năng payload lớn?
