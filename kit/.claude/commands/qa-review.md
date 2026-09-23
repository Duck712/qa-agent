---
description: Review tài liệu test — quan điểm test, test case, kế hoạch/SCOPE — máy soát + checklist + đối chiếu nguồn
argument-hint: <vp | tc | scope | all> [tính năng | REQ-… | file.csv]
---

Review: $ARGUMENTS (trống → `all`)

1. Nạp skill `qa`, `qa-testcase-design`, `qa-knowledge`. Đọc `qa/LESSONS.md`. Review là **báo**, không sửa nội dung: mọi
   thay đổi vào quan điểm/TC/SCOPE chỉ làm khi người dùng đồng ý (tài liệu người khác viết lại càng phải hỏi). Ngoại lệ
   duy nhất là bước 2 — chép định dạng file Excel vào `qa/` để máy soát được, nội dung giữ nguyên.
2. Tài liệu đưa vào dạng Excel/Sheets → người dùng lưu CSV UTF-8 → `python3 .claude/qa-scripts/qa_check.py import <tc|vp> <file.csv> --feature <tên>`
   (chỉ đổi định dạng; trường trống giữ trống; dòng sai mã báo ra, không tự đặt mã). `.xlsx` → hướng dẫn lưu CSV, dừng.
3. **Máy soát** (in nguyên văn kết quả):
   - `vp` → `python3 .claude/qa-scripts/qa_check.py vp [<tính năng>]`
   - `tc` → `python3 .claude/qa-scripts/qa_check.py tc [<tính năng>|REQ-…]`
   - luôn → `python3 .claude/qa-scripts/qa_check.py src --list` (REQ + quan điểm có nguồn, trích dẫn khớp tài liệu) và
     `python3 .claude/qa-scripts/qa_check.py trace` (REQ → quan điểm → TC, lỗ phủ)
   - `scope` → `python3 .claude/qa-scripts/qa_check.py status` (tiêu chí đọc được, REQ chưa có mức)
4. **Checklist nội dung**: quan điểm → `qa-testcase-design/ky-thuat/quan-diem.md` §3 · TC → `qa-testcase-design/ky-thuat/review-tc.md` §2 ·
   SCOPE → `qa-knowledge/scope-review.md` §1. Mục chủ động bỏ ghi lý do.
5. **Đối chiếu nguồn — chống tự nghĩ ra**: spawn `qa-source-check` (kèm phạm vi, danh sách nguồn máy không mở được ở
   bước 3, và tỉ lệ bốc mẫu — lấy tỉ lệ soi bằng chứng ở SCOPE §6 nếu người dùng chưa cho tỉ lệ riêng; không có → hỏi).
6. Trình gộp theo khuôn `qa-testcase-design/ky-thuat/quan-diem.md` §3 · `qa-testcase-design/ky-thuat/review-tc.md` §3 · `qa-knowledge/scope-review.md` §2, xếp theo mức nặng: (a) không có căn
   cứ trong đặc tả / trích sai, (b) lỗ phủ, (c) kỳ vọng mơ hồ / hai đáp án, (d) hình thức. Mỗi mục: đề xuất + rủi ro.
   Hỏi người dùng sửa mục nào; đồng ý mới sửa, rồi chạy lại bước 3. Kiểu lỗi review lặp lại → `qa/LESSONS.md`.
