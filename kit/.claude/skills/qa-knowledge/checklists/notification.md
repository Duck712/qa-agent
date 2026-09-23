# Checklist — Thông báo (email / SMS / push / in-app)

> Người nhận phải là hộp thư/số test ở `QA.md`. Không có → `BLOCKED`.

- [ ] Đúng người nhận: không gửi cho người đã rời nhóm/tắt thông báo/bị chặn; không gửi nhầm tenant
- [ ] Đúng số lần: một hành động → một thông báo (không nhân đôi khi retry, khi có 2 thiết bị)
- [ ] Nội dung: tên, số, ngày giờ đúng múi giờ người nhận; không lộ dữ liệu người khác; ký tự có dấu không vỡ
- [ ] **Mọi link trong thông báo mở được** và trỏ đúng môi trường (không localhost/tên miền dev)
- [ ] Link dùng một lần: dùng lại, dùng sau khi hết hạn, dùng bởi tài khoản khác
- [ ] Bấm thông báo push/in-app → mở đúng màn, đúng bản ghi, kể cả khi app đang tắt/đang ở màn khác
- [ ] Tắt/bật tuỳ chọn nhận thông báo có hiệu lực ngay; hủy đăng ký email hoạt động
- [ ] Đã đọc/chưa đọc, đếm badge đúng sau khi đọc ở thiết bị khác
- [ ] Nhà cung cấp lỗi/chậm → hành động chính vẫn thành công, thông báo gửi lại sau (không chặn luồng)
