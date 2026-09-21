---
description: Vệ sinh tài liệu context/ — chạy báo cáo, gấp phần đã hết hiệu lực vào archive/ledger/ bằng tay, xác nhận gate không đỏ thêm
---

# /spec-compact — dọn sổ mà không phá mỏ neo

> **Không thuộc 4 pha.** Đáng chạy nhất ở đầu pha S của một release, hoặc trước
> `release.py --go`. Không hỏi QC trong suốt lệnh này.

SPEC cố ý **không reset** tài liệu khi đóng release (`SPEC.md §1.2`) — reset là mất trí nhớ giữa các release. Cái giá: sau 5–7 release, các sổ chỉ-thêm-không-bớt (DECISIONS, BUGS, API-SURFACE, challenge log) dài tới mức không ai đọc.

## Bước 1 — Đọc báo cáo

```bash
python3 scripts/compact.py
```

Chỉ đọc, luôn exit 0. Ba phần: **A. Rác** (gấp được) · **B. Mồ côi** (LỖI — sửa, không gấp) · **C. Dòng neo** (gate/hook đang grep — TUYỆT ĐỐI không đụng).

## Bước 2 — Gấp bằng tay

Đích: `context/archive/ledger/<DOC>.md`, tạo tay khi cần. **Không** đổ vào `context/archive/release-<N>/` (đó là snapshot theo release, và là cờ "release N đã đóng" mà `release.py` dựa vào).

Mỗi lần gấp: **cắt** dòng khỏi file sống, **dán** vào ledger, để lại một dòng trỏ:

```markdown
<!-- Bug đã đóng của release 1–3 đã gấp: context/archive/ledger/BUGS.md -->
```

Ba luật:

1. **Không đụng phần C.** Nặng nhất: dòng mốc `(release N)` trong DECISIONS, dòng `Chốt bởi QC`, header ma trận `| Target |` — xoá là gate mù vĩnh viễn.
2. **Không gấp bằng cách bọc `<!-- -->`.** `read_live()` bỏ sạch comment trước khi đếm — nội dung bọc comment biến mất khỏi mọi phép đếm trong khi nhìn file vẫn thấy. Muốn giữ thì **chuyển sang ledger**.
3. **Đừng đụng tiêu đề `##` / heading `### TC-`/`### BUG-`.** Nhiều tiêu đề là mỏ neo regex.

Phần B sửa thật: TC thiếu meta thì bổ sung, TI lệch COVERAGE-MAP thì đồng bộ, evidence chết thì chạy lại TC.

## Bước 3 — Xác nhận không hỏng gì

```bash
python3 scripts/gate.py            # pha hiện tại
python3 scripts/gate.py S          # và pha S — phần lớn mỏ neo nằm ở gate S
python3 scripts/compact.py         # phần A vơi, phần B sạch
```

**Kết quả phải giống hệt trước khi gấp.** Đỏ thêm một mục = cắt nhầm mỏ neo — `git diff` tìm, khôi phục, chạy lại.

## Bước 4 — Commit riêng

```
vệ sinh tài liệu — gấp <x> dòng vào archive/ledger/, sửa <y> mục mồ côi
```

Đừng trộn với thay đổi khác — lần sau ai thấy gate đỏ sẽ không biết đỏ vì test hay vì dọn nhầm.

## Ranh giới

- **Không dọn giữa pha E.** Đang chạy test mà tài liệu đổi chỗ thì mất dấu.
- **Không gấp sổ của release hiện tại và release ngay trước** — pha S còn đọc chúng để rà chiến lược, `spec-tester-compat` còn đọc `API-SURFACE` release trước.
- **Không xoá `context/archive/release-<N>/`** — cờ "release N đã đóng".
- **Không tự sửa `compact.py` cho nó ghi hộ** — không có `--go` là có chủ đích.
