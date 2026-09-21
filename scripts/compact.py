#!/usr/bin/env python3
"""compact.py — báo cáo vệ sinh tài liệu `context/`. CHỈ ĐỌC, không ghi gì.

VÌ SAO CÓ FILE NÀY
    SPEC không reset tài liệu khi đóng release (SPEC.md §1.2) — các sổ chỉ-thêm-không-bớt
    cứ dài ra: DECISIONS, BUGS, API-SURFACE, challenge log/blocker trong STATE, và mỗi
    release một cụm releases/r<N>/. Sau 5–7 release thì phần đọc được lẫn trong phần đã
    hết hiệu lực. Công cụ này chỉ nói ba điều: chỗ nào là rác gấp được, chỗ nào mồ côi
    (lỗi — sửa chứ không gấp), và chỗ nào TUYỆT ĐỐI không được đụng (mỏ neo của gate).
    Việc gấp là của người, theo /spec-compact.

VÌ SAO KHÔNG CÓ --go
    Script tự sửa sổ append-only phải đoán ý người viết; đoán sai một lần là mất vĩnh
    viễn thứ không ai nhớ để khôi phục. Báo cáo đọc 30 giây rẻ hơn nhiều.

Usage:  python3 scripts/compact.py     # luôn exit 0 — báo cáo, không phải gate
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _counts as C  # noqa: E402

ROOT = C.ROOT
BUSY_LINES = 80


def main() -> int:
    st = C.state()
    n = st.get("release") or 0
    print(f"\n=== compact.py — báo cáo vệ sinh (release {n}, chỉ đọc) ===\n")

    # --- A. Rác tích tụ ------------------------------------------------------
    print("A. RÁC TÍCH TỤ — cân nhắc gấp tay vào context/archive/ledger/ (xem /spec-compact)")
    for rel, label in (("context/DECISIONS.md", "quyết định các release đã đóng (GIỮ dòng mốc + dòng gate còn đếm)"),
                       ("context/BUGS.md", "bug đã `đóng` từ ≥2 release trước"),
                       ("context/API-SURFACE.md", "mục release cũ (giữ 2 release gần nhất làm baseline)")):
        lines = C.read(rel).count("\n")
        flag = "  ← dài, đáng dọn" if lines > BUSY_LINES else ""
        print(f"  · {rel}: {lines} dòng{flag} — {label}")
    ch = C.section(C.read_live("STATE.md"), "## Challenge log")
    rows = len(C.table_rows(ch))
    if rows > 15:
        print(f"  · STATE.md §Challenge log: {rows} dòng — gấp phần release cũ (gate chỉ đếm ngày ≥ mốc)")
    print()

    # --- B. Mồ côi — LỖI, sửa chứ không gấp ---------------------------------
    print("B. MỤC MỒ CÔI — đây là lỗi, sửa tay:")
    issues = 0
    tcs = C.all_testcases()
    for t in tcs:
        need = ("Loại", "Tầng", "Mức", "Regression", "Release vào")
        if not t["removed"] and not all(t["meta"].get(k1) for k1 in need):
            print(f"  ✗ {t['id']} ({t['file']}): dòng meta thiếu nhãn — TC vô hình với gate")
            issues += 1
    if n:
        p = C.plan(n)
        cov = C.read_live("context/COVERAGE-MAP.md")
        for ti in p["ti"]:
            if ti[0] not in cov:
                print(f"  ✗ {ti[0]} có trong TEST-PLAN nhưng vắng ở COVERAGE-MAP")
                issues += 1
        rl = C.runlog(n)
        for k, sec in rl["sections"].items():
            for row in sec["rows"]:
                ev = row.get("evidence") or ""
                if row["kq"] == "PASS" and ev.startswith("evidence/") \
                        and not (ROOT / ev).exists():
                    print(f"  ✗ RUNLOG lượt {k}: {row['tc']} trỏ bằng chứng không tồn tại ({ev})")
                    issues += 1
        tc_ids = {t["id"] for t in tcs}
        for x in p["regression"]:
            if x not in tc_ids:
                print(f"  ✗ TEST-PLAN §5 chọn {x} nhưng TC không tồn tại")
                issues += 1
    for rel in ("context/TEST-STRATEGY.md", "context/COVERAGE-MAP.md",
                "context/ENVIRONMENT.md", "context/HANDOVER.md"):
        if C.UNFILLED in C.read(rel) and n >= 1 and (st.get("pha") or "S") != "S":
            print(f"  ✗ {rel}: còn dấu {C.UNFILLED} sau pha S")
            issues += 1
    if not issues:
        print("  ✓ không thấy mục mồ côi")
    print()

    # --- C. Dòng neo — TUYỆT ĐỐI không đụng ---------------------------------
    print("C. DÒNG NEO — gate/hook đang grep, đụng vào là gate mù IM LẶNG:")
    print("""  · STATE.md: `Pha hiện tại :` · `Release :` · `Lần bàn giao :` · `Release mở:` ·
    `Bàn giao mở:` · ô `- [ ] **Scope khoá**` · tiêu đề `## Challenge log` / `## Blocker`
  · Manifest: dòng máy đọc + mục `## Dev đã fix`
  · TEST-PLAN: 4 dòng đầu + tiêu đề `## 1.`…`## 8.` + dòng `Chốt bởi QC:` + bảng §4
  · TEST-STRATEGY: dòng `Chốt bởi QC:` + tiêu đề `## 2.`/`## 3.`/`## 6.`/`## 11.` +
    header `| Target |` của ma trận + dòng `Số TC regression tối thiểu`
  · testcases: heading `### TC-…` + dòng meta ngay dưới
  · RUNLOG: heading `## Lượt chạy — bàn giao <k>` + `### Phạm vi retest` + `### Kết quả chạy`
  · BUGS: heading `### BUG-r<N>-<số>` + ô `| Severity |` + `| Trạng thái |`
  · REPORT: heading `## Kết luận — bàn giao <k>` + dòng `Verdict:` + `Ký bởi QC:`
  · DECISIONS: dòng mốc `| (release N) |` / `| (release N — bàn giao k) |`
  · ENVIRONMENT: các dòng `- [ ] (mỗi release)`
  KHÔNG gấp bằng cách bọc <!-- --> — read_live() bỏ comment, nội dung biến mất khỏi
  mọi phép đếm trong khi nhìn file vẫn thấy nó. Muốn giữ thì CHUYỂN sang archive/ledger/.""")
    print("\nGấp xong chạy lại: python3 scripts/gate.py && python3 scripts/compact.py — kết quả phải y hệt trước khi gấp.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
