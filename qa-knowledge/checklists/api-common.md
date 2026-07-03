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
