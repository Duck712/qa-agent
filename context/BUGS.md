---
type: bug-ledger
tier: T1
append_only: true
last_reviewed: "{{DATE}}"
---

# BUGS — {{PROJECT_NAME}}

> **Sổ bug toàn dự án, append-only phần khối** — chỉ cập nhật dòng `Trạng thái` của khối.
> Mã `BUG-r<N>-<số>` (N = release phát hiện). Severity theo `TEST-STRATEGY §5` — không hạ
> mức để đẹp số; hạ mức là một quyết định, ghi DECISIONS.
>
> Trạng thái: `mở` → `đã fix chờ retest` → `đóng (retest PASS lượt k, <ngày>)` ·
> `không sửa (QC chấp nhận — DECISIONS <ngày>)` · `deferred (release sau nhặt ở pha S)`.
> Bug S1/S2 đóng → PHẢI sinh 1 TC regression (`TEST-STRATEGY §6`).
>
> Sổ này kiêm **backlog**: phát hiện ngoài scope test đã khoá ghi vào đây với trạng thái
> `deferred` — không nới release hiện tại (luật #1). Ghi nhanh đúng khuôn: `/spec-bug`.
>
> Bug còn `mở` KHÔNG tự rơi khỏi verdict khi sang release mới — `gate.py C` đếm mọi bug
> `mở`/`chờ retest` của CẢ các release trước (cam kết PASS-có-điều-kiện được đòi nợ).
> Muốn nó thôi đếm phải chuyển `đóng` / `không sửa` / `deferred`, có vết.

<!-- Khuôn một bug — copy nguyên khối:

### BUG-r1-001 — <một câu mô tả, viết theo hậu quả người dùng>

| Mục | Nội dung |
|---|---|
| Severity | S2 |
| AC / TC | AC-2 (l2) · TC-BOOK-01-005 |
| Lượt phát hiện | bàn giao 1 · đợt 3 · spec-tester-authz |
| Bước tái hiện | 1. Đăng nhập `spec+mechanic@…` 2. PUT /api/bookings/<id-của-owner> 3. Server trả 200 |
| Kỳ vọng | 403, bản ghi không đổi |
| Bằng chứng | evidence/r1/luot-1/TC-BOOK-01-005/ |
| Trạng thái | mở |
-->

---

## Tổng hợp

<!-- Cập nhật cuối mỗi lượt chạy — gate C đối chiếu bảng này với các khối bên dưới. -->

| Severity | Mở | Chờ retest | Đóng | Không sửa | Deferred |
|---|---|---|---|---|---|
| S1 | 0 | 0 | 0 | 0 | 0 |
| S2 | 0 | 0 | 0 | 0 | 0 |
| S3 | 0 | 0 | 0 | 0 | 0 |
| S4 | 0 | 0 | 0 | 0 | 0 |

---

## Sổ bug
