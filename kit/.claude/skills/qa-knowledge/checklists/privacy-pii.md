# Checklist — Dữ liệu cá nhân / quyền riêng tư

> Áp cho mọi sản phẩm có dữ liệu người dùng. Kỳ vọng cụ thể (trường nào che, giữ bao lâu) lấy từ tài liệu/chính sách —
> không có thì hỏi.

> **Mục checklist là câu hỏi để thử, không phải kỳ vọng.** Kỳ vọng lấy từ tài liệu; tài liệu không nói → điểm hỏi.
> Không chép từ như "tử tế / rõ ràng / OK" vào Kỳ vọng. Trích nguồn trong TC: `Nguồn: <checklist> <số mục>`, vd `form-input 2.3`.

## 1. Hiển thị & lưu vết
- [ ] 1.1 PII (SĐT, email, số giấy tờ, địa chỉ) bị che/ẩn đúng ở danh sách, log, export, thông báo theo tài liệu
- [ ] 1.2 PII không nằm trong URL/query string, log phía client, analytics, thông báo lỗi
- [ ] 1.3 Ảnh upload bị gỡ EXIF/GPS nếu tài liệu yêu cầu

## 2. Quyền của chủ dữ liệu
- [ ] 2.1 Người dùng tải dữ liệu của mình: đủ, đúng định dạng, không lẫn dữ liệu người khác
- [ ] 2.2 Xoá tài khoản → dữ liệu cá nhân bị xoá/ẩn danh ở mọi nơi (tìm kiếm, export, bản ghi liên quan) theo chính sách; bản ghi liên quan hiển thị ra sao
- [ ] 2.3 Đồng ý / thu hồi đồng ý (marketing, cookie, chia sẻ) có hiệu lực ngay và được ghi nhận

## 3. Truy cập
- [ ] 3.1 Nhân viên/admin xem PII có để lại nhật ký truy cập (nếu tài liệu yêu cầu)
- [ ] 3.2 Dữ liệu của người dùng/tenant khác không lộ qua tìm kiếm, gợi ý, đếm, export, thông báo
