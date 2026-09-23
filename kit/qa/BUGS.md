# BUGS — {{PROJECT_NAME}}

> Mỗi bug một khối `## BUG-<số> — <tiêu đề>` (lệnh `/qa-bug`). Severity theo hậu quả:
> **S1** mất dữ liệu / sai tiền / lộ quyền / sập luồng lõi · **S2** tính năng chính hỏng, có đường vòng khó ·
> **S3** hỏng phụ, có đường vòng · **S4** lặt vặt (chữ, căn lề).
> Trạng thái: `mở` · `đã sửa` (dev báo sửa, chờ test lại) · `đóng` (test lại đạt) · `không sửa` · `hoãn` · `trùng`.
> Mọi trạng thái trừ `đóng`/`không sửa`/`hoãn`/`trùng` (kể cả "đã sửa (chờ test lại)") tính là **còn mở** khi xét tiêu chí.
> **Ai đổi**: QA tự đổi được `mở → đã sửa` (dev/ticket báo, ghi nguồn), `mở`/`đã sửa → đóng` (test lại PASS có bằng chứng;
> bug không ổn định phải test lại đủ số lần bằng mẫu số ban đầu), `đã sửa → mở` (test lại FAIL), `đóng → mở` (tái phát).
> Đổi sang `không sửa`/`hoãn`/`trùng`, hoặc
> đổi severity → **người dùng quyết**, ghi DECISIONS (trích nguyên văn) và `Lịch sử` trỏ tới dòng đó.
> Severity chỉ theo thang trên — lộ dữ liệu/quyền của người khác luôn là S1.

<!-- Khuôn:

## BUG-001 — <triệu chứng theo hậu quả người dùng>
- Severity: S2
- Trạng thái: mở
- TC: TC-XXX-001        (bug từ khám phá: viết TC tái hiện, người dùng duyệt, rồi ghi vào đây)
- Run: <run-id>
- Target: <tên target>
- Môi trường / bản: staging · v1.2.0
- Tỉ lệ tái hiện: 3/3
- Bước tái hiện:
  1. ...
- Thấy: ...
- Kỳ vọng: ... (REQ-XXX-1)
- Bằng chứng: qa/evidence/<run-id>/TC-XXX-001/
- Lịch sử:
  - <ngày> mở (<run-id>)
-->
