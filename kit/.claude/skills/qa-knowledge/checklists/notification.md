# Checklist — Thông báo (email / SMS / push / in-app)

> Người nhận phải là hộp thư/số test ở `QA.md`. Không có → `BLOCKED`.

> **Mục checklist là câu hỏi để thử, không phải kỳ vọng.** Kỳ vọng lấy từ tài liệu; tài liệu không nói → điểm hỏi.
> Không chép từ như "tử tế / rõ ràng / OK" vào Kỳ vọng. Trích nguồn trong TC: `Nguồn: <checklist> <số mục>`, vd `form-input 2.3`.

- [ ] 1.1 Đúng người nhận: không gửi cho người đã rời nhóm/tắt thông báo/bị chặn; không gửi nhầm tenant
- [ ] 1.2 Đúng số lần: một hành động → một thông báo (không nhân đôi khi retry, khi có 2 thiết bị)
- [ ] 1.3 Nội dung: tên, số, ngày giờ đúng múi giờ người nhận; không lộ dữ liệu người khác; ký tự có dấu không vỡ
- [ ] 1.4 **Mọi link trong thông báo mở được** và trỏ đúng môi trường (không localhost/tên miền dev)
- [ ] 1.5 Link dùng một lần: dùng lại, dùng sau khi hết hạn, dùng bởi tài khoản khác
- [ ] 1.6 Bấm thông báo push/in-app → mở đúng màn, đúng bản ghi, kể cả khi app đang tắt/đang ở màn khác
- [ ] 1.7 Tắt/bật tuỳ chọn nhận thông báo có hiệu lực ngay; hủy đăng ký email hoạt động
- [ ] 1.8 Đã đọc/chưa đọc, đếm badge đúng sau khi đọc ở thiết bị khác
- [ ] 1.9 Nhà cung cấp lỗi/chậm → hành động chính vẫn thành công, thông báo gửi lại sau (không chặn luồng)

## 2. Bổ sung
- [ ] 2.1 SMS có dấu dùng mã UCS-2: 70 ký tự/đoạn (không phải 160) → tách đoạn/tính phí đúng
- [ ] 2.2 Hiển thị theo ngôn ngữ và múi giờ của NGƯỜI NHẬN
- [ ] 2.3 Giờ yên lặng / gộp thông báo (nếu có) hoạt động theo tài liệu
