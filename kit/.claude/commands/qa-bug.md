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
3. Cập nhật trạng thái → thêm dòng `Lịch sử` (`<ngày> <trạng thái> (<run-id>)`), không xoá dòng cũ. QA tự đổi được
   `mở → đã sửa` khi dev/người dùng/ticket báo đã sửa (ghi nguồn vào Lịch sử); `đã sửa → đóng` khi test lại PASS có
   bằng chứng; `đã sửa → mở` khi test lại FAIL; `đóng → mở` khi tái phát. Bug `mở` chưa ai báo sửa mà không tái hiện được
   → ghi Lịch sử "không tái hiện <x/y>" và hỏi (không tự đóng). Bug tái hiện không ổn định (AI, đồng thời, chập chờn) →
   đề xuất số lần test lại kèm lý do (tỉ lệ ban đầu, rủi ro) và hỏi; người dùng chốt (DECISIONS) rồi mới `đóng` khi 0 lần
   tái hiện, ghi `0/<n>` vào Lịch sử. Cập nhật trạng thái bug TRƯỚC khi chạy `qa_check run`. Sang
   `không sửa`/`hoãn`/`trùng`,
   hoặc đổi severity → hỏi người dùng, ghi DECISIONS trích nguyên văn, `Lịch sử` trỏ số dòng DECISIONS.
   Bug tìm từ khám phá (không có TC) → đề xuất TC tái hiện (`Nguồn: BUG-…`), người dùng duyệt thì ghi vào `TC:`.
4. S1 → báo người dùng ngay trong chat.
5. Kiểu lỗi đáng nhớ (dễ lặp lại ở tính năng/dự án khác) → thêm một dòng `qa/LESSONS.md` (skill `qa` §6).
   Bug không thuộc quan điểm test nào (tìm từ khám phá, hoặc TC ngoài lề) → dòng loại `lỗ quan điểm` + đề xuất quan
   điểm mới cho tính năng đó (`/qa-viewpoint`, người dùng duyệt).
