#!/usr/bin/env python3
"""pairwise.py — sinh bộ cấu hình phủ mọi CẶP giá trị (all-pairs), có ràng buộc. Python chuẩn, tất định.

    python3 .claude/qa-scripts/pairwise.py "Trình duyệt=Chrome,Firefox,Safari" "OS=Windows,macOS,Linux" \
        "Vai=admin,member,guest" [--khong "Safari&Windows"] [--khong "OS=Linux&Vai=guest"] [--tat-ca]

  "Tên=giá trị,giá trị,…"   một tham số (ít nhất 2 tham số)
  --khong "A&B[&C]"         tổ hợp không tồn tại / không được chạy (giá trị trần, hoặc Tên=giá trị nếu trùng tên)
  --tat-ca                  in tích đầy đủ (trừ tổ hợp bị cấm) thay vì pairwise — dùng cho cặp tham số R1

In bảng markdown + thống kê. Kỹ thuật: skill qa-testcase-design, ky-thuat/to-hop.md.
"""
from __future__ import annotations

import argparse
import itertools
import sys


def parse_params(specs: list[str]) -> list[tuple[str, list[str]]]:
    out = []
    for s in specs:
        if "=" not in s:
            raise SystemExit(f"✗ `{s}` phải có dạng Tên=giá trị,giá trị")
        name, vals = s.split("=", 1)
        values = [v.strip() for v in vals.split(",") if v.strip()]
        if len(values) < 1:
            raise SystemExit(f"✗ tham số `{name}` không có giá trị")
        if len(set(values)) != len(values):
            raise SystemExit(f"✗ tham số `{name}` có giá trị trùng")
        out.append((name.strip(), values))
    if len(out) < 2:
        raise SystemExit("✗ cần ít nhất 2 tham số")
    names = [n for n, _ in out]
    if len(set(names)) != len(names):
        raise SystemExit(f"✗ tên tham số trùng: {', '.join(sorted({n for n in names if names.count(n) > 1}))}")
    return out


def parse_constraints(specs: list[str], params: list[tuple[str, list[str]]]) -> list[set[tuple[int, str]]]:
    """Mỗi ràng buộc → tập (chỉ số tham số, giá trị) không được cùng xuất hiện."""
    cons = []
    for s in specs:
        items = set()
        for part in s.split("&"):
            part = part.strip()
            if "=" in part:
                n, v = (x.strip() for x in part.split("=", 1))
                idx = [i for i, (pn, vs) in enumerate(params) if pn == n and v in vs]
            else:
                v = part
                idx = [i for i, (_, vs) in enumerate(params) if v in vs]
            if not idx:
                raise SystemExit(f"✗ ràng buộc `{s}`: không thấy giá trị `{part}`")
            if len(idx) > 1:
                raise SystemExit(f"✗ ràng buộc `{s}`: `{part}` có ở nhiều tham số — viết Tên=giá trị")
            items.add((idx[0], v))
        if len(items) < 2:
            raise SystemExit(f"✗ ràng buộc `{s}` cần ít nhất 2 giá trị")
        if len({i for i, _ in items}) < len(items):
            raise SystemExit(f"✗ ràng buộc `{s}` có hai giá trị của CÙNG một tham số — không bao giờ khớp, xem lại")
        cons.append(items)
    return cons


def violates(row: dict[int, str], cons: list[set[tuple[int, str]]]) -> bool:
    return any(all(row.get(i) == v for i, v in c) for c in cons)


def pairs_of(row: dict[int, str]) -> set[tuple[int, str, int, str]]:
    keys = sorted(row)
    return {(a, row[a], b, row[b]) for a, b in itertools.combinations(keys, 2)}


_MEMO: dict = {}


def can_complete(row: dict[int, str], params, cons) -> bool:
    """Còn cách gán các tham số chưa gán mà không vi phạm ràng buộc không.
    Chỉ tham số có dính ràng buộc mới cần thử (tham số tự do luôn gán được); cắt nhánh sớm + nhớ kết quả."""
    if violates(row, cons):
        return False
    involved = sorted({i for c in cons for i, _ in c} - set(row))
    key = (frozenset(row.items()), id(cons))
    if key in _MEMO:
        return _MEMO[key]
    def rec(k: int, cur: dict[int, str]) -> bool:
        if k == len(involved):
            return True
        i = involved[k]
        for v in params[i][1]:
            cur[i] = v
            if not violates(cur, cons) and rec(k + 1, cur):
                del cur[i]
                return True
            del cur[i]
        return False
    _MEMO[key] = rec(0, dict(row))
    return _MEMO[key]


def allpairs(params, cons) -> tuple[list[dict[int, str]], int, int]:
    need = set()
    for a, b in itertools.combinations(range(len(params)), 2):
        for va in params[a][1]:
            for vb in params[b][1]:
                if can_complete({a: va, b: vb}, params, cons):
                    need.add((a, va, b, vb))
    total_pairs = len(need)
    rows: list[dict[int, str]] = []
    while need:
        a, va, b, vb = sorted(need, key=lambda p: (p[0], params[p[0]][1].index(p[1]), p[2], params[p[2]][1].index(p[3])))[0]
        row = {a: va, b: vb}
        for i in range(len(params)):
            if i in row:
                continue
            best, best_gain = None, -1
            for v in params[i][1]:
                cand = dict(row)
                cand[i] = v
                if violates(cand, cons) or not can_complete(cand, params, cons):
                    continue
                gain = sum(1 for p in pairs_of(cand) if p in need and (p[0] == i or p[2] == i))
                if gain > best_gain:
                    best, best_gain = v, gain
            if best is None:
                break
            row[i] = best
        if len(row) != len(params):
            need.discard((a, va, b, vb))   # không dựng được dòng hợp lệ chứa cặp này
            continue
        covered = pairs_of(row) & need
        need -= covered
        rows.append(row)
    return rows, total_pairs, len(need)


def main() -> int:
    ap = argparse.ArgumentParser(description="Sinh bộ pairwise có ràng buộc")
    ap.add_argument("params", nargs="+")
    ap.add_argument("--khong", action="append", default=[], help='tổ hợp cấm, vd "Safari&Windows"')
    ap.add_argument("--tat-ca", action="store_true", help="in tích đầy đủ (trừ tổ hợp cấm)")
    a = ap.parse_args()
    params = parse_params(a.params)
    cons = parse_constraints(a.khong, params)
    n_full = 1
    for _, vs in params:
        n_full *= len(vs)
    if a.tat_ca:
        if n_full > 100000:
            raise SystemExit(f"✗ tích đầy đủ {n_full} dòng — quá lớn, dùng pairwise hoặc tách tham số")
        full = [dict(enumerate(combo)) for combo in itertools.product(*(vs for _, vs in params))]
        rows, total_pairs, left = [r for r in full if not violates(r, cons)], None, 0
    else:
        rows, total_pairs, left = allpairs(params, cons)
    esc = lambda x: x.replace("|", "\\|")
    names = [esc(n) for n, _ in params]
    print("| # | " + " | ".join(names) + " |")
    print("|---|" + "---|" * len(names))
    for k, r in enumerate(rows, 1):
        print(f"| {k} | " + " | ".join(esc(r[i]) for i in range(len(params))) + " |")
    print()
    if a.tat_ca:
        print(f"Tích đầy đủ: {len(rows)} dòng (đã bỏ {n_full - len(rows)} tổ hợp cấm).")
    else:
        print(f"Pairwise: {len(rows)} dòng thay cho tối đa {n_full} dòng tích đầy đủ · phủ {total_pairs - left}/{total_pairs} cặp hợp lệ"
              + (f" · {len(cons)} ràng buộc" if cons else ""))
        if left:
            print(f"⚠ {left} cặp không dựng được dòng hợp lệ (xem lại ràng buộc)", file=sys.stderr)
    unused = [f"{n}={v}" for i, (n, vs) in enumerate(params) for v in vs if not any(r.get(i) == v for r in rows)]
    if unused:
        print(f"⚠ giá trị không xuất hiện ở dòng nào (ràng buộc loại hết): {', '.join(unused)} — hỏi người dùng có đúng ý không",
              file=sys.stderr)
    if not rows:
        print("✗ không dựng được dòng nào — ràng buộc loại hết mọi tổ hợp", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
