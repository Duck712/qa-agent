---
description: Viết báo cáo một run — kết luận đạt/không đạt theo tiêu chí ghi trước, cho người không rành kỹ thuật
argument-hint: <run-id>
---

Run: $ARGUMENTS (trống → run mới nhất trong `qa/runs/`).

1. `python3 .claude/qa-scripts/qa_check.py run <run-id>` — phải không còn lỗi hình thức; lấy **kết luận máy tính**
   (ĐẠT / KHÔNG ĐẠT / CHƯA KẾT LUẬN / KHÔNG ÁP DỤNG (chỉ khám phá)) và số liệu. Câu hỏi "phát hành được chưa" → dùng
   `python3 .claude/qa-scripts/qa_check.py release <run gốc> <retest…> <reg…>` (gộp kết quả mới nhất của mọi TC trong
   SCOPE, xét mọi bug mở mức cấm), không dùng kết luận của riêng một run retest. `release` báo tiêu chí trong RUNLOG khác
   SCOPE → người dùng chọn: tạo lại run bằng `new-run` (chép tiêu chí hiện tại) rồi chạy lại, hoặc chốt lại SCOPE §6 theo
   tiêu chí cũ (ghi DECISIONS). Còn lỗi → chỉ chuẩn hoá **định dạng** của giá trị đã có (đường dẫn gõ sai); ngày/giá trị thiếu thì hỏi;
   thiếu/sai bằng chứng hoặc chưa có tiêu chí → báo người dùng, họ quyết chạy lại / hạ BLOCKED / chốt tiêu chí.
   **Không** sửa bằng chứng hay đổi kết quả để hết lỗi.
2. Nhật ký RUNLOG chưa có dòng `Đã soi bằng chứng …` → spawn `qa-evidence-check` trước (kèm run-id và tỉ lệ ở SCOPE §6 `Soi bằng chứng — tỉ lệ bốc mẫu PASS`; chưa có thì
   hỏi), trình lệch cho người dùng.
3. Viết `qa/runs/<run-id>/REPORT.md` theo khuôn `qa/runs/_REPORT-TEMPLATE.md`: dòng đầu là đúng kết luận máy
   tính + một câu lý do; số cụ thể; tin xấu nói trước; chưa kiểm được gì và cần gì; rủi ro còn lại
   (`qa-knowledge/techniques-judgement.md` §5). Không tự nâng kết luận — người dùng muốn chấp nhận rủi ro thì ghi DECISIONS
   với lời nguyên văn, kết luận máy vẫn giữ.
4. **Bài học**: rà bug và sự cố của run → ghi mỗi bài học một dòng `qa/LESSONS.md` (skill `qa` §6), liệt kê
   trong `REPORT §Bài học`. Bài học dùng được cho dự án khác → **hỏi người dùng** có đưa vào kho chung
   `qa-knowledge` không; đồng ý mới sửa skill, đánh dấu dòng LESSONS là `đã nâng`.
5. Đề xuất việc tiếp theo (vd test lại khi dev sửa xong).
