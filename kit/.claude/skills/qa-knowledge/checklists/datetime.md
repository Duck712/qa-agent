# Checklist — Ngày giờ / lịch / múi giờ / lặp lại

> **Mục checklist là câu hỏi để thử, không phải kỳ vọng.** Kỳ vọng lấy từ tài liệu; tài liệu không nói → điểm hỏi.
> Không chép từ như "tử tế / rõ ràng / OK" vào Kỳ vọng. Trích nguồn trong TC: `Nguồn: <checklist> <số mục>`, vd `form-input 2.3`.

- [ ] 1.1 Tạo lúc 23:30 và 00:30 → hiển thị đúng ngày; lọc theo ngày không lệch biên 0h
- [ ] 1.2 Người dùng ở múi giờ khác nhau cùng xem một sự kiện → giờ đúng theo từng người
- [ ] 1.3 Cuối tháng, 29/2, năm mới, đổi giờ mùa hè (nếu có người dùng ở vùng có DST)
- [ ] 1.4 Lặp lại: sửa "chỉ lần này" vs "cả chuỗi" vs "từ lần này trở đi"; xoá tương tự; buổi đã qua xử lý thế nào
- [ ] 1.5 Sửa một trường (tiêu đề) không làm mất trường khác (người dự, nhắc nhở); không cắt giây/múi giờ
- [ ] 1.6 Trùng lịch, sự kiện 0 phút, kéo dài qua nửa đêm, kéo dài nhiều ngày, cả ngày
- [ ] 1.7 Mời người dự: đúng một lời mời, đúng người; người đã rời tổ chức; người ngoài tổ chức/đối tác
- [ ] 1.8 Nhắc nhở đúng giờ; hạn chót tính theo múi giờ nào

## 2. Bổ sung
- [ ] 2.1 Lặp hằng tháng vào ngày 31 / 29–30 → tháng thiếu ngày xử lý thế nào (theo tài liệu)
- [ ] 2.2 Lặp hằng tuần qua mốc đổi giờ mùa hè → giữ đúng giờ địa phương
- [ ] 2.3 Nhập/hiển thị dd/mm và mm/dd theo locale — 03/04 không bị hiểu nhầm
