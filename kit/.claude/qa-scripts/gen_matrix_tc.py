#!/usr/bin/env python3
"""gen_matrix_tc.py — sinh khung TC phân quyền: MỘT TC cho MỖI ô ✗ của ma trận vai × hành động.

    python3 .claude/qa-scripts/gen_matrix_tc.py <file-có-ma-trận> --feature QUYEN --target <target> \
        [--req REQ-QUYEN-1] [--out qa/testcases/phan-quyen.md] [--start 1]

Ma trận là bảng markdown đầu tiên có cột đầu "Hành động" và các cột vai; ô ✗ (hoặc x, ✘, không, no) là bị cấm:

    | Hành động | owner | member | chưa đăng nhập |
    |---|---|---|---|
    | Sửa đơn | ✓ | ✗ | ✗ |

Chỉ sinh KHUNG: bước "gọi thẳng API/URL…" và kỳ vọng mã chặn phải điền theo sản phẩm (tài liệu API, quan sát).
Ghi nối vào --out (tạo nếu chưa có); TC đã có cùng `Ô ma trận:` thì bỏ qua. Không có --out → in ra màn hình.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DENY = {"✗", "x", "✘", "không", "no", "❌"}


def matrix(text: str) -> tuple[list[str], list[tuple[str, list[str]]]]:
    lines = [l.strip() for l in text.splitlines()]
    for i, l in enumerate(lines):
        if l.startswith("|") and re.match(r"\|\s*hành động\s*\|", l, re.I):
            roles = [c.strip() for c in l.strip("|").split("|")][1:]
            rows = []
            for r in lines[i + 2:]:
                if not r.startswith("|"):
                    break
                cells = [c.strip() for c in r.strip("|").split("|")]
                if cells and cells[0]:
                    rows.append((cells[0], cells[1:]))
            return roles, rows
    return [], []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--feature", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--req", default="")
    ap.add_argument("--out")
    ap.add_argument("--start", type=int, default=0)
    a = ap.parse_args()
    roles, rows = matrix(Path(a.src).read_text(encoding="utf-8"))
    if not roles:
        print("Không thấy bảng có cột đầu 'Hành động'.", file=sys.stderr)
        return 1
    out = Path(a.out) if a.out else None
    existing = out.read_text(encoding="utf-8") if out and out.exists() else ""
    feat = re.sub(r"[^A-Z0-9]", "", a.feature.upper())
    used = [int(n) for n in re.findall(rf"^##\s+TC-{feat}-(\d{{3}})", existing, re.M)]
    n = max([a.start - 1, *used, 0]) + 1
    blocks, skipped = [], 0
    for action, cells in rows:
        for role, cell in zip(roles, cells):
            if cell.strip().lower() not in DENY:
                continue
            key = f"Ô ma trận: {action} × {role} = ✗"
            if key in existing:
                skipped += 1
                continue
            blocks.append(f"""## TC-{feat}-{n:03d} — {role} không {action.lower()} được
- REQ: {a.req or '<REQ-…>'}
- Target: {a.target}
- Loại: phân-quyền
- Kiểu: abnormal
- Mức: R1
- Nguồn: ma trận quyền ({Path(a.src).name})
- {key}
- Regression: có
- Tiền điều kiện: đăng nhập vai `{role}` (hoặc không đăng nhập); có bản ghi QA-<run>- do vai được phép tạo
- Dữ liệu: <id bản ghi QA-<run>->
- Bước:
  1. Vai `{role}` gọi thẳng <API/URL/lệnh của hành động "{action}"> tới bản ghi trên (bỏ qua giao diện)
  2. Vai được phép mở lại bản ghi
- Kỳ vọng:
  1. Bị chặn ở server: <mã 401/403/404 theo tài liệu>, thông điệp không lộ dữ liệu
  2. Bản ghi không đổi
- Bằng chứng cần: request + response nguyên văn bước 1 · ảnh/response bước 2
""")
            n += 1
    text = "\n".join(blocks)
    if out:
        if not existing:
            existing = f"# Test case — Phân quyền ({a.feature})\n\n"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(existing.rstrip() + "\n\n" + text if blocks else existing, encoding="utf-8")
        print(f"Đã thêm {len(blocks)} TC vào {out} · bỏ qua {skipped} ô đã có TC")
    else:
        print(text)
    print("Nhớ điền <…> theo sản phẩm; chỗ nào không suy ra được từ tài liệu → hỏi người dùng.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
