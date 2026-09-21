---
type: api-surface
tier: T1
append_only: true
last_reviewed: "{{DATE}}"
---

# API SURFACE — {{PROJECT_NAME}}

> **Sổ surface API do SPEC TỰ QUAN SÁT và ghi** — kể cả khi dev có giao API spec (OpenAPI/
> Postman), spec là lời hứa còn sổ này là cái server THẬT SỰ trả; spec lệch sổ là phát hiện. `spec-tester-api` ghi ở
> pha E mỗi release: endpoint đã chạm, field chính của request/response, mã lỗi đã thấy.
>
> Giá trị của sổ này nằm ở release SAU: nó là **baseline độc lập** để `spec-tester-compat`
> đối chiếu — response đổi hình dạng so với sổ này là ứng viên bug tương thích ngược,
> kể cả khi tài liệu của dev không nhắc gì.
>
> Append theo release — mục cũ KHÔNG sửa (nó là bản chụp thời điểm đó; surface đổi hợp lệ
> thì mục release mới ghi hình dạng mới, kèm ghi chú "đổi so với r<N-1>, hợp lệ vì …").

<!-- Khuôn một mục release:

## Release 1 — ghi trong lượt bàn giao 1, {{ISO}}

| Endpoint | Method | Request field chính | Response field client đang dùng | Mã lỗi đã thấy | Ghi từ TC |
|---|---|---|---|---|---|
| /api/bookings | POST | customerName, startsAt | id, status, startsAt | 200 · 400 (thiếu tên) · 401 · 409 (trùng giờ) | TC-BOOK-01-001/-002 |
-->
