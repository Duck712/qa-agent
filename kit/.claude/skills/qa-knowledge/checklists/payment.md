# Checklist — Thanh toán / tiền / số dư

> Chỉ chạy trên sandbox của cổng thanh toán. Không có sandbox → TC `BLOCKED`, không thử bằng thẻ thật.

## 1. Tính tiền
- [ ] Làm tròn: đơn giá lẻ × số lượng, giảm giá %, thuế — so với tính tay; VND không có phần thập phân
- [ ] Mã giảm giá: hết hạn, dùng quá số lượt, áp hai mã, áp rồi đổi giỏ, giảm quá giá trị đơn (âm?)
- [ ] Đổi giá giữa lúc đang thanh toán → tính giá nào, có báo không
- [ ] Số tiền 0, nhỏ nhất, lớn nhất cổng cho phép

## 2. Luồng thanh toán
- [ ] Thành công / thất bại / người dùng huỷ / hết thời gian ở trang cổng → trạng thái đơn đúng từng ca
- [ ] Bấm thanh toán 2 lần, F5 ở trang callback, Back sau khi trả tiền → không trừ tiền 2 lần
- [ ] Callback/webhook đến trước redirect, đến muộn, đến 2 lần, đến sai chữ ký → đơn không sai trạng thái
- [ ] Đóng trình duyệt ngay sau khi trả tiền → đơn vẫn được xác nhận (nhờ webhook)

## 3. Hoàn tiền & đối soát
- [ ] Hoàn một phần, hoàn toàn bộ, hoàn 2 lần, hoàn quá số đã trả
- [ ] Lịch sử giao dịch, hoá đơn, email xác nhận khớp số tiền
- [ ] Phân quyền: xem/hoàn đơn của người khác (IDOR trên mã đơn)
