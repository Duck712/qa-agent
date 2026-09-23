---
description: Ghi (hoặc cập nhật) một bug đúng khuôn vào qa/BUGS.md
argument-hint: <mô tả ngắn | BUG-… <trạng thái mới>>
---

Bug: $ARGUMENTS

1. Mở `qa/BUGS.md`, lấy số tiếp theo (`BUG-<số>` lớn nhất + 1, 3 chữ số). Kiểm trùng: grep triệu chứng/TC —
   trùng rõ → thêm dòng `Lịch sử` vào bug cũ; na ná không chắc → hỏi người dùng.
2. Viết khối theo khuôn trong `BUGS.md`: tiêu đề theo **hậu quả người dùng**; severity theo hậu quả (không theo
   tần suất — ghi `Tỉ lệ tái hiện`); bước tái hiện **tối giản**; `Thấy` nguyên văn; `Kỳ vọng` trỏ REQ/bước TC;
   `Bằng chứng` là thư mục evidence đã tồn tại; `Ticket:` nếu đội dùng hệ thống ngoài.
   Triệu chứng, không kết luận hộ nguyên nhân. Một bug một vấn đề. Severity ở ranh giới (S1 hay S2?) → hỏi.
3. Cập nhật trạng thái → thêm dòng `Lịch sử` (`<ngày> <trạng thái> (<run-id>)`), không xoá dòng cũ.
4. S1 → báo người dùng ngay trong chat.
5. Kiểu lỗi đáng nhớ (dễ lặp lại ở tính năng/dự án khác) → thêm một dòng `qa/LESSONS.md` (skill `qa` §6).
