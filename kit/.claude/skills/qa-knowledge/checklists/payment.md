# Checklist — Thanh toán / tiền / số dư

> Chỉ chạy trên sandbox của cổng thanh toán. Không có sandbox → TC `BLOCKED`, không thử bằng thẻ thật.

> **Mục checklist là câu hỏi để thử, không phải kỳ vọng.** Kỳ vọng lấy từ tài liệu; tài liệu không nói → điểm hỏi.
> Không chép từ như "tử tế / rõ ràng / OK" vào Kỳ vọng. Trích nguồn trong TC: `Nguồn: <checklist> <số mục>`, vd `form-input 2.3`.

## 1. Tính tiền
- [ ] 1.1 Làm tròn: đơn giá lẻ × số lượng, giảm giá %, thuế — so với tính tay; VND không có phần thập phân
- [ ] 1.2 Mã giảm giá: hết hạn, dùng quá số lượt, áp hai mã, áp rồi đổi giỏ, giảm quá giá trị đơn (âm?)
- [ ] 1.3 Đổi giá giữa lúc đang thanh toán → tính giá nào, có báo không
- [ ] 1.4 Số tiền 0, nhỏ nhất, lớn nhất cổng cho phép

## 2. Luồng thanh toán
- [ ] 2.1 Thành công / thất bại / người dùng huỷ / hết thời gian ở trang cổng → trạng thái đơn đúng từng ca
- [ ] 2.2 Bấm thanh toán 2 lần, F5 ở trang callback, Back sau khi trả tiền → không trừ tiền 2 lần
- [ ] 2.3 Callback/webhook đến trước redirect, đến muộn, đến 2 lần, đến sai chữ ký → đơn không sai trạng thái
- [ ] 2.4 Đóng trình duyệt ngay sau khi trả tiền → đơn vẫn được xác nhận (nhờ webhook)

## 3. Hoàn tiền & đối soát
- [ ] 3.1 Hoàn một phần, hoàn toàn bộ, hoàn 2 lần, hoàn quá số đã trả
- [ ] 3.2 Lịch sử giao dịch, hoá đơn, email xác nhận khớp số tiền
- [ ] 3.3 Phân quyền: xem/hoàn đơn của người khác (IDOR trên mã đơn)

## 4. Toàn vẹn phía server
- [ ] 4.1 Sửa số tiền / giá / mã giảm giá / số lượng trong request hoặc callback phía client → server tính lại từ dữ liệu của mình, không tin client
- [ ] 4.2 Hai người cùng dùng lượt cuối của một mã giảm giá (đồng thời) → chỉ một người được
- [ ] 4.3 Replay webhook cũ đúng chữ ký → không xử lý lại (idempotent theo mã giao dịch)
- [ ] 4.4 Tiền tệ khác nhau: số chữ số thập phân theo ISO 4217 (VND/JPY 0, USD 2, KWD 3), làm tròn khi đổi tiền
