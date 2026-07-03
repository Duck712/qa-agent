# Bug patterns — lỗi dev hay mắc, soi trước tiên
> Khi nhận feature mới, đối chiếu list này để biết "đào" chỗ nào trước.

1. **Validate chỉ ở FE, API không check lại** → luôn test thẳng API bằng curl bỏ qua UI.
2. **Search/filter không escape ký tự đặc biệt** → `%`, `_`, `'` là thử ngay.
3. **Timezone**: data tạo lúc 23h hiển thị sai ngày; filter theo ngày lệch biên 0h → test data quanh 0h và cuối tháng.
4. **Phân trang sau khi xóa/thêm item** → đứng trang 2 xóa hết item của trang → trang trống hay tự lùi?
5. **Trạng thái không đồng bộ giữa list và detail** sau khi update (cache, stale data).
6. **Race khi double-submit** → mọi nút tạo/thanh toán đều thử double-click.
7. **Quên phân quyền ở API phụ** (export, download, autocomplete) — chỉ gắn quyền ở API chính.
8. **Lỗi chỉ xuất hiện với data thật số lượng lớn** (1000+ bản ghi): chậm, timeout, UI vỡ — seed data lớn trước khi test list.
9. **Message lỗi generic "Có lỗi xảy ra"** che mất lỗi thật → luôn mở DevTools/Network xem response gốc.
10. **Ký tự unicode nhiều byte làm sai đếm độ dài** (FE đếm 1 emoji = 1, DB varchar đếm = 4).
