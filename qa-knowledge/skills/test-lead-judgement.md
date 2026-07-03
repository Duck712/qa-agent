# Tư duy ra quyết định (Test Lead)
> Dùng khi: ước lượng phạm vi, xử lý gap coverage, chốt GO/NO-GO. Đây là cách CÂN NHẮC,
> không phải checklist — áp dụng khi không có câu trả lời đúng/sai rõ ràng.

## 1. Risk-based prioritization
Khi thời gian không đủ test hết, ưu tiên theo công thức:
**Rủi ro = Xác suất xảy ra lỗi × Mức thiệt hại nếu xảy ra**
- Feature mới toanh, code phức tạp → xác suất lỗi cao hơn feature cũ ổn định lâu.
- Đường tiền, dữ liệu, bảo mật → thiệt hại cao dù xác suất thấp cũng phải test.
- Khi phải cắt: cắt vùng (xác suất thấp × thiệt hại thấp) trước, nói rõ lý do cắt trong TEST-PLAN
  mục Gaps — không im lặng bỏ qua.

## 2. Soi AC/requirement mơ hồ
Câu mô tả sau đây KHÔNG đủ để viết TC, phải hỏi lại trước khi viết:
- "Xử lý đúng", "hiển thị hợp lý", "tối ưu trải nghiệm" → hỏi: đúng là gì, cụ thể hoá bằng con số/hành vi quan sát được.
- Chỉ có happy path, không nói gì về trường hợp lỗi → hỏi: khi input sai/thiếu thì hệ thống làm gì.
- Có 2 cách hiểu khác nhau → đưa ra CẢ 2 cách hiểu, hỏi user chọn cách nào, không tự đoán 1 cách.

## 3. Ước lượng & cắt phạm vi có trách nhiệm
Khi nhân lực/thời gian không đủ test hết mọi TC trong kho:
- Ưu tiên: (1) luồng cốt lõi mới thay đổi, (2) luồng tiền/bảo mật, (3) regression của bug đã từng xảy ra,
  (4) mới sau đó mới đến edge case hiếm.
- Mọi phần bị cắt phải: ghi vào Gaps + có lý do + hỏi user xác nhận chấp nhận rủi ro đó.

## 4. Ra quyết định GO / CONDITIONAL GO / NO-GO
Không chỉ đếm PASS/FAIL — cân nhắc theo thứ tự câu hỏi:
1. Còn bug P1 (mất dữ liệu/bảo mật/sập) đang OPEN không? → Có = NO-GO, không thương lượng.
2. Coverage có lỗ ở luồng cốt lõi không? → Có = NO-GO trừ khi user chấp nhận rủi ro rõ ràng.
3. Còn P2/P3 nhưng có workaround, hoặc BLOCKED có lý do chính đáng (chưa deploy, thiếu account)?
   → CONDITIONAL GO, nêu rõ điều kiện + ai chịu trách nhiệm nếu risk xảy ra.
4. Mọi thứ sạch → GO.
- Khi user muốn override quyết định của mình (đặc biệt NO-GO → GO), PHẢI hỏi lại rõ lý do và
  ghi vào decisions.md kèm tên người quyết định — không tự động chiều theo mà không hỏi.

## 5. Viết report cho người không rành kỹ thuật
- Kết luận trước, chi tiết sau: dòng đầu tiên phải là recommendation (GO/NO-GO) + 1 câu lý do.
- Dùng số cụ thể, tránh tính từ mơ hồ ("khá ổn", "tạm được") — nói "23/25 TC PASS, 2 FAIL đều P3".
- Nếu phải nói tin xấu (nhiều bug, trễ tiến độ) → nói thẳng ngay đầu, đừng chôn giữa report.
