# Bug patterns — lỗi dev hay mắc, soi trước tiên
> Khi nhận feature mới, đối chiếu list này để biết "đào" chỗ nào trước.

1. **Validate chỉ ở FE, API không check lại** → luôn test thẳng API bằng curl bỏ qua UI.
2. **Search/filter không escape ký tự đặc biệt** → `%`, `_`, `'` là thử ngay.
3. **Timezone**: data tạo lúc 23h hiển thị sai ngày; filter theo ngày lệch biên 0h → test data quanh 0h và cuối tháng.
4. **Phân trang sau khi xóa/thêm item** → đứng trang 2 xóa hết item của trang → trang trống hay tự lùi?
5. **Trạng thái không đồng bộ giữa list và detail** sau khi update (cache, stale data).
6. **Race khi double-submit** → mọi nút tạo/thanh toán đều thử double-click.
7. **Quên phân quyền ở API phụ** (export, download, autocomplete) — chỉ gắn quyền ở API chính.
8. **Lỗi chỉ xuất hiện với dữ liệu số lượng lớn**: chậm, timeout, UI vỡ → đề xuất cỡ dữ liệu (theo giới hạn tài liệu/hệ
   thống) và hỏi; seed vượt trần `qa-targets` §3 mục 4 → hỏi.
9. **Message lỗi generic "Có lỗi xảy ra"** che mất lỗi thật → luôn mở DevTools/Network xem response gốc.
10. **Đếm độ dài lệch giữa các tầng**: JS `.length` đếm UTF-16 (😀 = 2, 👨‍👩‍👧 = 8) trong khi người dùng thấy 1 ký tự; cột
    MySQL `utf8` (mb3) từ chối ký tự 4 byte (emoji); Oracle `VARCHAR2` theo BYTE; tiếng Việt dạng tổ hợp (NFD, "ệ" = 2–3
    code point) → thử emoji, emoji ghép, tiếng Việt NFC và NFD ở đúng giới hạn độ dài.
11. **Luật nghiệp vụ chỉ chặn ở UI** (tối thiểu N người, bắt buộc chọn…) → gọi thẳng API là vượt được.
12. **Token/link dùng một lần dùng lại được** (mời, kích hoạt, đặt lại mật khẩu) sau khi đã dùng hoặc sau khi tài khoản đã active → ghi đè dữ liệu. Thử dùng lại mọi link một lần.
13. **Bản ghi trùng treo vĩnh viễn**: mời trùng email, tạo trùng tên → không bị chặn, để lại trạng thái `pending` không ai xử.
14. **Sửa một trường làm mất trường khác** (PUT ghi đè cả object, form không gửi lại danh sách con) → sau mỗi lần sửa, kiểm lại MỌI trường không đụng tới.
15. **Sự kiện lặp / phạm vi "chỉ lần này" vs "cả chuỗi"** bị bỏ qua, cắt mất giây/múi giờ khi lưu → nhân đôi hoặc mất buổi.
16. **Link sinh tự động trỏ sai host** (localhost, tên miền dev, tên miền không tồn tại) → mở thử mọi link trong email/thông báo.
17. **Trạng thái realtime không dọn khi client biến mất** (đóng tab, mất mạng) → đếm sai người online/trong cuộc, "đang gọi" treo.
18. **Lọt thông tin qua kênh phụ**: không đọc được nội dung nhưng đoán được sự tồn tại (đếm, thông báo, lịch sử, mã lỗi khác nhau 403 vs 404).
19. **Tên dành riêng không bị chặn** (`admin`, `api`, `www`, trùng tên miền hạ tầng) khi cho người dùng đặt tên không gian/subdomain.
20. **Hành động bị chặn đúng nhưng không để lại vết** trong nhật ký kiểm toán, hoặc vết thiếu bên bị chạm.
21. **Hàng rào có lỗ đúng chỗ hay dùng nhất** (chặn SSRF mọi dải nội bộ trừ `127.0.0.1`/`localhost`) → thử đủ biến thể: `127.0.0.1`, `localhost`, `0.0.0.0`, `[::1]`, IP thập phân, DNS trỏ nội bộ.
22. **Đích tới bị xoá/vô hiệu nhưng hành động vẫn nhận** (gọi/mời/giao việc cho người đã rời tổ chức).
23. **Thông báo/sự kiện nhân đôi** cho một hành động (hai webhook, hai thông báo cùng phút).
24. **Tài liệu tự mâu thuẫn**: AC, design, API doc nói ba kiểu → ghi thành điểm mơ hồ trước khi viết TC, đừng chọn đại.
