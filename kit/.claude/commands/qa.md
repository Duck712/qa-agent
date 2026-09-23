---
description: Trợ lý QA — nhờ bất kỳ việc kiểm thử nào (phân tích, kế hoạch, TC, chạy test, smoke, regression, test lại bug, khám phá, automation, báo cáo…)
argument-hint: <việc cần làm, vd "viết TC cho màn đăng ký" | "smoke sau deploy v2.3" | "dev fix BUG-012">
---

Yêu cầu: $ARGUMENTS

1. Nạp skill `qa`. Đọc `qa/QA.md` (quy trình đội đang theo, target, môi trường) và `qa/LESSONS.md` (bài học
   đã lưu của dự án). Chưa có `qa/` → báo người dùng cài bộ qa-agent: `python3 <repo qa-agent>/install.py <thư mục dự án>` (xem README repo qa-agent), dừng.
2. Xếp yêu cầu vào một (hoặc chuỗi) việc ở skill `qa` §2. Không rõ là việc gì, phạm vi đến đâu → **hỏi**, kèm đề xuất.
3. Làm việc đó theo công thức ở §2, nạp đúng skill phụ (`qa-targets`, `qa-testcase-design`, `qa-evidence`,
   `qa-knowledge`). Giữ luật §1 — đặc biệt: **chưa rõ ở đâu thì hỏi ở đó**, không suy diễn, không tự ý làm.
4. Kết thúc: tóm tắt đã làm gì, để lại file nào, bài học mới đã ghi `LESSONS.md` (nếu có), việc tiếp theo hợp lý
   theo `QA.md §Quy trình` — cập nhật dòng `Việc tiếp theo:` trong `QA.md`.
