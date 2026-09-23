# RUNLOG — <run-id>

> Tạo bằng `python3 .claude/qa-scripts/qa_check.py new-run …` (không tạo tay — script chép tiêu chí đạt vào khối dưới).
> Kết quả: `PASS` · `FAIL` (cột cuối ghi BUG-…) · `BLOCKED` (cột cuối ghi lý do / `chờ trả lời #n`) · `SKIP` (cột cuối trỏ
> dòng DECISIONS người dùng quyết) · `CHƯA CHẠY`.
> Dòng khám phá `EXPLORE-<n>`: phát hiện bug → `FAIL` + BUG-… · câu hỏi → `BLOCKED` + `chờ trả lời #n` · phiên không thấy
> gì → `PASS` + trỏ ghi chép phiên. Không tính vào tỉ lệ PASS.
> Bằng chứng: thư mục `qa/evidence/<run-id>/<TC-ID>/` — phải tồn tại và không rỗng với PASS/FAIL.

- Bản đang kiểm: 
- Môi trường: 
- Bắt đầu: 
- Phạm vi: <tất cả TC trong SCOPE | test lại bug … | regression …>
- Scope lúc tạo run: <CHỐT | NHÁP>
- Tiêu chí (chép từ SCOPE §6 lúc tạo run; không sửa sau khi đã chạy):
  - Bug mở không được phép: 
  - Tỉ lệ PASS tối thiểu: 
  - Tỉ lệ BLOCKED tối đa: 

| TC | Kết quả | Ngày | Bằng chứng | Bug / Lý do |
|---|---|---|---|---|
| TC-FEAT-001 | CHƯA CHẠY | | | |

## Nhật ký
<!-- Mốc giờ, seed/dọn dữ liệu, sự cố môi trường, dev deploy lại giữa chừng, đợt nào chạy vai nào,
     "Đã soi bằng chứng <ngày> — <x> lệch" (sau qa-evidence-check), rác dữ liệu còn lại -->
