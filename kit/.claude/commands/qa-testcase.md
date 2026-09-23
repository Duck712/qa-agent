---
description: Thiết kế test case (hoặc review bộ TC hiện có) cho tính năng / REQ trong phạm vi
argument-hint: <tính năng | REQ-… | "review">
---

Việc: $ARGUMENTS

1. Nạp skill `qa-testcase-design` (luôn) — chọn kỹ thuật theo bảng §1, mở file `qa-testcase-design/ky-thuat/…` tương ứng; `qa-knowledge` (bug-patterns + checklist hợp đối tượng/target),
   `qa-targets/<loại>.md` của target liên quan. Đọc `qa/LESSONS.md` — mỗi bài học áp dụng được phải có TC.
2. Đọc REQ liên quan trong `qa/ANALYSIS.md` và phạm vi trong `qa/SCOPE.md`. SCOPE chưa chốt, hoặc REQ còn
   `(chờ trả lời #n)` → hỏi người dùng có viết trước không; không tự đoán kỳ vọng cho phần chưa rõ. `Mức:` của TC =
   mức người dùng đã chốt cho REQ ở SCOPE §2 — chưa có thì hỏi, không tự gán.
   Dedupe với `qa/testcases/` — na ná mà không chắc trùng → hỏi.
3. Viết/bổ sung `qa/testcases/<tinh-nang>.md` theo khuôn: mật độ theo mức R (R1 ≥ 2 kỹ thuật), ghi `Kỹ thuật:`,
   có code → rút nhánh/validate/mã lỗi/kiểm quyền (`qa-testcase-design/ky-thuat/hop-trang.md`), không có đáp án chắc → chọn oracle
   (`qa-testcase-design/ky-thuat/oracle.md`), nhiều cấu hình → `python3 .claude/qa-scripts/pairwise.py`, mỗi REQ ≥ 1 normal + ≥ 1 abnormal,
   ma trận quyền → mỗi ô ✗ một TC (`python3 .claude/qa-scripts/gen_matrix_tc.py` nếu lớn), `Nguồn:` cho mọi TC, `Bằng chứng cần` cụ thể.
   Mọi con số, thông điệp, mã trạng thái trong Kỳ vọng phải có nguồn (REQ, API doc, câu trả lời ở ANALYSIS §5) — không
   ghi hai đáp án "A hoặc B". Kỳ vọng hoặc ngưỡng không suy ra được từ nguồn nào → **không bịa, không tự đặt con số**;
   viết TC với `Kỳ vọng: (chờ trả lời #n)`, gom thành câu hỏi. TC còn `(chờ trả lời)` không được đưa vào run.
   Việc là "review" → không viết mới: review ba lớp theo `qa-testcase-design/ky-thuat/review-tc.md`, báo lỗ phủ / TC thừa / kỳ vọng
   mơ hồ, sửa khi người dùng đồng ý.
4. `python3 .claude/qa-scripts/qa_check.py tc` → sửa tới khi sạch (cảnh báo R1 < 2 kỹ thuật cũng xử lý) → `python3 .claude/qa-scripts/qa_check.py trace --write` →
   tự review bằng checklist `qa-testcase-design/ky-thuat/review-tc.md` §2.
5. Trình theo khuôn `qa-testcase-design/ky-thuat/review-tc.md` §3: REQ × TC normal/abnormal × kỹ thuật; lỗ phủ; mục checklist chủ động bỏ và
   lý do; câu hỏi còn mở. Người dùng duyệt bộ TC trước khi chạy (trừ khi họ đã nói chạy luôn).
