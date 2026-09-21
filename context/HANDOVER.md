---
type: handover
tier: T1
status: DRAFT
last_reviewed: "{{DATE}}"
---

# HANDOVER — {{PROJECT_NAME}}

> **Sổ dịch bàn giao** — ghi ở pha S mỗi release: tài liệu nguồn nào (trong mirror) nuôi
> file context nào, và lỗ hổng thông tin đã vá ra sao. KHÔNG đóng băng: release nào cũng
> dịch nên sổ này cập nhật delta — dòng cũ giữ nguyên, thêm dòng mới ghi rõ cột Release.
>
> Dòng marker dưới đây phải nằm NGOÀI comment — `gate.py S` đọc nó, và đường dẫn phải
> khớp dòng `Repo nguồn:` của manifest. Dạng: `NGUỒN: <tên nguồn> — <path>`
> (chế độ VIPER: `NGUỒN: VIPER — <path>`).

NGUỒN: _CHƯA ĐIỀN_ — _CHƯA ĐIỀN_ <!-- vd: NGUỒN: tài liệu đội booking — ../booking-docs · VIPER: NGUỒN: VIPER — ../repo-viper -->

---

## Truy vết nguồn → context

<!-- Mỗi dòng: file context của SPEC lấy từ đâu trong mirror `intake/releases/r<N>/nguon/`
     (chế độ VIPER: `…/viper/`). Trỏ ĐÚNG file + mục — "từ tài liệu dev" chung chung là dấu
     hiệu dịch hời hợt. gate.py S đòi ≥3 dòng (VIPER ≥5). Release ≥2: thêm dòng cho tài liệu
     mới của release, ghi rõ cột Release.

     Ví dụ (chế độ khác):
     | 1 | context/PERSONAS.md | nguon/PRD-booking.pdf §2 "Phân quyền" | Dựng ma trận vai × hành động |
     | 1 | context/ARCHITECTURE.md | nguon/openapi.yaml + nguon/DEPLOY.md | Target + URL staging |
     Ví dụ (VIPER):
     | 1 | context/COVERAGE-MAP.md | viper/CAPABILITIES-MAP.md + viper/vong-2/PRD.md §3 | AC-1..4 (l2) |
-->

| Release | Mục context | Nguồn trong mirror | Ghi chú dịch |
|---|---|---|---|
| 1 | _CHƯA ĐIỀN_ | | |

## Lỗ hổng & cách xử

<!-- Thứ tài liệu dev (viết cho dev) KHÔNG nói đủ cho việc test — gần như luôn có:
     AC mơ hồ ("xử lý đúng", "hiển thị hợp lý") · thiếu ca lỗi/negative · hai cách hiểu ·
     tài khoản admin lấy đâu · tenant test tạo thế nào · hộp thư nhận notification test ·
     sandbox thanh toán/SMS · giới hạn rate limit thật · seed endpoint có không · build mobile ·
     quyền kiểm thử bảo mật (nếu tick loại `bảo-mật`).
     Thứ tự xử: tìm trong mirror → hỏi QC (vẫn pha S — mỗi câu kèm đề xuất của meta + rủi ro
     nếu đề xuất sai) → tự quyết + 1 dòng DECISIONS mỗi lỗ.
     Không lỗ hổng nào được ghi = dấu hiệu dịch hời hợt (SPEC.md §3a). -->

| Release | Lỗ hổng | Nguồn phát sinh | Đề xuất của meta (rủi ro nếu sai) | Cách xử |
|---|---|---|---|---|
| 1 | _CHƯA ĐIỀN_ | _CHƯA ĐIỀN_ (file + mục trong mirror) | _CHƯA ĐIỀN_ | _CHƯA ĐIỀN_ (QC trả lời ngày … nguyên văn: "…" / tự quyết — DECISIONS dòng …) |
