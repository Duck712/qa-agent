---
description: Viết báo cáo một run — kết luận đạt/không đạt theo tiêu chí ghi trước, cho người không rành kỹ thuật
argument-hint: <run-id>
---

Run: $ARGUMENTS (trống → run mới nhất trong `qa/runs/`).

1. `python3 .claude/qa-scripts/qa_check.py run <run-id>` — phải không còn lỗi hình thức; lấy **kết luận máy tính**
   (ĐẠT / KHÔNG ĐẠT / CHƯA KẾT LUẬN) và số liệu. Còn lỗi → chỉ tự sửa lỗi **định dạng** (ngày, đường dẫn gõ sai);
   thiếu/sai bằng chứng hoặc chưa có tiêu chí → báo người dùng, họ quyết chạy lại / hạ BLOCKED / chốt tiêu chí.
   **Không** sửa bằng chứng hay đổi kết quả để hết lỗi.
2. Nhật ký RUNLOG chưa có dòng `Đã soi bằng chứng …` → spawn `qa-evidence-check` trước, trình lệch cho người dùng.
3. Viết `qa/runs/<run-id>/REPORT.md` theo khuôn `qa/runs/_REPORT-TEMPLATE.md`: dòng đầu là đúng kết luận máy
   tính + một câu lý do; số cụ thể; tin xấu nói trước; chưa kiểm được gì và cần gì; rủi ro còn lại
   (`qa-knowledge/techniques-judgement.md` §5). Không tự nâng kết luận — người dùng muốn chấp nhận rủi ro thì ghi DECISIONS
   với lời nguyên văn, kết luận máy vẫn giữ.
4. **Bài học**: rà bug và sự cố của run → ghi mỗi bài học một dòng `qa/LESSONS.md` (skill `qa` §6), liệt kê
   trong `REPORT §Bài học`. Bài học dùng được cho dự án khác → **hỏi người dùng** có đưa vào kho chung
   `qa-knowledge` không; đồng ý mới sửa skill, đánh dấu dòng LESSONS là `đã nâng`.
5. Đề xuất việc tiếp theo (vd test lại khi dev sửa xong).
