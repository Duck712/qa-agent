# Review kế hoạch / SCOPE

> Dùng sau khi soạn `qa/SCOPE.md` (`/qa-plan`) và khi được nhờ review kế hoạch test của người khác. Mỗi phát hiện kèm
> đề xuất + rủi ro nếu bỏ qua; con số/quyết định vẫn do người dùng chốt — không tự điền.

## 1. Checklist
**Phạm vi**
- [ ] §1 mục tiêu trả lời được bằng có/không (vd "bản 2.3 đủ điều kiện phát hành?").
- [ ] Mọi REQ trong §2 có trong `ANALYSIS §3`, có nguồn + trích nguyên văn (`qa_check.py src`).
- [ ] Mọi REQ trong §2 có mức R người dùng xác nhận; lệch rõ với bảng rủi ro `ANALYSIS §6` đã hỏi.
- [ ] §3 ngoài phạm vi có lý do; không có REQ "biến mất" (có ở ANALYSIS mà không ở §2 lẫn §3).
- [ ] Yêu cầu phi chức năng (`ANALYSIS §7`) trong phạm vi có loại test tương ứng ở §4.
- [ ] Quan điểm test phủ mọi REQ trong §2 (`qa_check.py trace`) hoặc đã có kế hoạch viết.

**Chạy được**
- [ ] §5 môi trường, bản, tài khoản từng vai, cách tạo/dọn dữ liệu đều có thật (không phải "sẽ có").
- [ ] §9 tiêu chí vào đo được; điều kiện tạm dừng rõ (vd môi trường chết > 2 giờ).
- [ ] §10 có người và hạn cho từng việc; không một người gánh việc song song vượt sức.
- [ ] §7 quyền đặc biệt: mọi `có` có dòng DECISIONS trích nguyên văn lời cho phép.

**Kết luận được**
- [ ] §6 tiêu chí đạt đủ ba dòng, đúng định dạng máy đọc (`qa_check.py status` không báo KHÔNG ĐỌC ĐƯỢC).
- [ ] §6 tỉ lệ bốc mẫu soi bằng chứng đã chốt.
- [ ] §11 sản phẩm bàn giao khớp điều đội cần (định dạng, người nhận).
- [ ] §12 rủi ro dự án có cách giảm và người lo.

## 2. Trình kết quả
```
SCOPE <đợt>: <NHÁP/CHỐT> · REQ <n> (có mức <x>/<n>) · tiêu chí đạt <đọc được/không>
Lỗ: <mục checklist chưa đạt + đề xuất + rủi ro>
Câu hỏi cho người dùng: #…
```
