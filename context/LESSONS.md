---
type: lessons
tier: T1
append_only: true
last_reviewed: "{{DATE}}"
---

# LESSONS — {{PROJECT_NAME}}

> **Bài học sau mỗi release — append-only, mỗi release một mục `## Release N`.** Ghi ở pha C
> (`/spec-certify`), SAU khi QC ký verdict. Đây là nhật ký thô: không đổi cách test cho tới
> khi QC duyệt đưa vào kho kinh nghiệm dùng chung — skill `spec-knowledge`
> (`checklists/*.md`, `bug-patterns.md`).
>
> Hai tầng:
> 1. **Tầng 1 — meta tự ghi, bắt buộc**: 1–3 lesson từ release (bug pattern mới, ca bị bỏ
>    sót, chấm severity sai, TC thừa/thiếu, cách dựng môi trường…). Không có gì đáng ghi →
>    VẪN ghi một dòng `Không có lesson mới — <lý do>`. Không sửa mục của release cũ.
> 2. **Tầng 2 — QC duyệt từng đề xuất trong chat** (pha C có QC ký nên được trình): duyệt →
>    meta sửa file trong `spec-knowledge`, cột "QC duyệt" ghi ngày + nguyên văn câu duyệt;
>    không duyệt → giữ ở đây, ghi `không`. KHÔNG sửa `spec-knowledge` khi chưa có lời QC.
>
> Mỗi lesson trỏ về bằng chứng (BUG-…, TC-…, dòng DECISIONS) — lesson không nguồn là cảm tưởng.

<!-- Mẫu một mục:

## Release 1 — 2026-09-20

| # | Bài học | Nguồn | Đề xuất đưa vào `spec-knowledge` | QC duyệt |
|---|---|---|---|---|
| 1 | Validate số điện thoại chỉ ở client, API nhận chuỗi rác | BUG-r1-004 · TC-BOOK-01-012 | `bug-patterns.md`: thêm "SĐT/email chỉ validate ở FE" | 2026-09-20 — "ok đưa vào" |
| 2 | Chấm S3 cho lỗi lộ stack trace, sau hạ… | DECISIONS 2026-09-18 | — (chỉ ghi nhận) | — |
-->
