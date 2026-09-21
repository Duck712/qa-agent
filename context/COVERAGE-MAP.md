---
type: coverage-map
tier: T0
status: DRAFT
last_reviewed: "{{DATE}}"
---

# COVERAGE MAP — {{PROJECT_NAME}}

> **Bản đồ phủ test của cả sản phẩm** — capability (tính năng) × release nào test × hạng mục
> test (TI) nào phủ × trạng thái. Tách từ danh mục tính năng trong mirror ở pha S (PRD/spec/
> release note; chế độ VIPER: `CAPABILITIES-MAP.md`), sống
> qua các release. Đây là nguồn truy vết của TI: `gate.py S` đòi mọi `TI-n` trong
> `TEST-PLAN §2` có mặt ở cột "TI phủ", và mọi capability thuộc phạm vi release có dòng ở đây.
> Xoá hết dấu `_CHƯA ĐIỀN_` khi điền xong.

---

## 1. Bảng phủ

<!-- Mỗi dòng một capability. Tài liệu nguồn đã có mã (CAP-…, epic, mã ticket) → GIỮ NGUYÊN
     để truy vết ngược; chưa có → tự đặt `CAP-<NHÓM>-<số>` và ghi nguồn ở HANDOVER truy vết.
     Cột "Giao ở": bản deploy/sprint giao tính năng đó (VIPER: loop giao).
     "Release test": release nào của SPEC test capability này (theo TEST-STRATEGY §2).
     "TI phủ": mã TI trong TEST-PLAN của release đó.
     "Trạng thái": chưa tới · đang test (r<N>) · đã certify (r<N>) · fail đang chờ fix ·
     gỡ khỏi regression (kèm DECISIONS).

     Ví dụ:
     | CAP-BOOK-01 — Đặt lịch hẹn | l2 (vòng giao) | r1 | TI-1, TI-3 | đã certify (r1) |
     | CAP-NOTI-01 — Nhắc lịch    | l4            | r2 | TI-2       | đang test (r2)  |
-->

| Capability | Giao ở | Release test | TI phủ | Trạng thái |
|---|---|---|---|---|
| _CHƯA ĐIỀN_ | | | | |

## 2. Lát cắt release hiện tại

<!-- Một đoạn ngắn: release này phủ capability nào, vì sao (đối chiếu TEST-STRATEGY §2),
     và ranh giới với phần chưa test. Cập nhật MỖI release — bản cũ nằm ở archive. -->

_CHƯA ĐIỀN_

## 3. Change log

| Ngày | Thay đổi | Lý do |
|---|---|---|
| {{DATE}} | Tạo từ template SPEC | — |
