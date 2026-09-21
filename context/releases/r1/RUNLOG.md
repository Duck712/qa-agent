---
type: runlog
release: 1
tier: T2
---

# RUNLOG — release 1

> **Sổ kết quả chạy test — append-only trong pha E.** Mỗi lượt bàn giao một mục
> `## Lượt chạy — bàn giao <k>`; TC chạy lại ở lượt sau = dòng MỚI trong mục lượt đó,
> không sửa dòng cũ. Kết quả nhận đúng bốn giá trị:
> `PASS` (có bằng chứng) · `FAIL` (có bug) · `BLOCKED` (không chạy được — có blocker ở
> STATE) · `SKIP` (cố tình bỏ — có dòng DECISIONS).
>
> Cột "Bằng chứng" trỏ `evidence/r1/luot-<k>/<TC-ID>/` — `gate.py E` kiểm đường dẫn
> TỒN TẠI trên đĩa; PASS không bằng chứng = chưa chạy (dấu hiệu test giả, `SPEC.md §3b`).
> `release.py --retest` append mục lượt mới kèm bảng `### Phạm vi retest` — đừng tạo tay.

---

## Lượt chạy — bàn giao 1 (mở _CHƯA ĐIỀN_)

### Nhật ký đợt

<!-- Vết kỷ luật đợt: mốc mở/đóng từng đợt + lệnh reset giữa đợt. Đợt sau chỉ mở khi đợt
     trước đóng; giữa hai đợt cần mốc dữ liệu khác nhau thì chạy make reset / make seed
     và ghi vào cột cuối. -->

| Đợt | Mốc dữ liệu | Mở | Đóng | Reset/seed sau đợt |
|---|---|---|---|---|
| 0 — meta smoke | B1 | | | |

### Kết quả chạy

<!-- Mỗi dòng một lần chạy một TC. Agent = tên spec-tester-* hoặc `meta`. -->

| Ngày | Đợt | TC | Agent | Kết quả | Bằng chứng | Bug |
|---|---|---|---|---|---|---|
| | | | | | | |

### Tổng hợp lượt

| TC trong phạm vi | Đã chạy | PASS | FAIL | BLOCKED | SKIP | Bug mới (S1/S2/S3/S4) |
|---|---|---|---|---|---|---|
| | | | | | | |
