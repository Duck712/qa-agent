# RUNLOG — <run-id>

> `/qa-run` tạo file này ở `qa/runs/<run-id>/RUNLOG.md` với mỗi TC trong phạm vi một dòng `CHƯA CHẠY`.
> Kết quả: `PASS` · `FAIL` (cột cuối ghi BUG-…) · `BLOCKED` (cột cuối ghi lý do) · `SKIP` (cột cuối ghi dòng DECISIONS) · `CHƯA CHẠY`.
> Bằng chứng: thư mục `qa/evidence/<run-id>/<TC-ID>/` — phải tồn tại và không rỗng với PASS/FAIL.

- Bản đang kiểm: 
- Môi trường: 
- Bắt đầu: 
- Phạm vi: <tất cả TC trong SCOPE | test lại bug … | regression …>

| TC | Kết quả | Ngày | Bằng chứng | Bug / Lý do |
|---|---|---|---|---|
| TC-FEAT-001 | CHƯA CHẠY | | | |

## Nhật ký
<!-- Mốc giờ, sự cố môi trường, dev deploy lại giữa chừng, đợt nào chạy vai nào -->
