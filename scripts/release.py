#!/usr/bin/env python3
"""release.py — đóng release hiện tại / mở lượt bàn giao mới (SPEC.md §1.2).

VÌ SAO CÓ FILE NÀY
    SPEC không reset tài liệu — hàng rào chống "gate xanh sẵn nhờ vết cũ" là các phép
    đếm theo release/lượt: mốc `(release N)` trong DECISIONS, ngày ≥ `Release mở` /
    `Bàn giao mở`, mỗi lượt một mục RUNLOG, re-arm mục `(mỗi release)`. Thao tác nhiều
    file dễ sai bằng tay, nên nó là script — và là chỗ DUY NHẤT máy tự đổi pha hộ.

HAI CHẾ ĐỘ
    --go      Đóng release N (verdict PASS / PASS-có-điều-kiện + Ký bởi QC), mở release N+1:
              archive snapshot tài liệu sống → context/archive/release-N/ (chỉ copy) ·
              STATE: Release N+1 · Release mở · Lần bàn giao 1 · pha S · bỏ tick §Gate ·
              scaffold context/releases/r<N+1>/ + intake/releases/r<N+1>/ rỗng ·
              mốc `(release N+1)` vào DECISIONS · bỏ tick `(mỗi release)` trong ENVIRONMENT.
              KHÔNG đụng: TEST-STRATEGY, testcases sống, BUGS, sổ/evidence cũ, manifest cũ.
    --retest  Verdict FAIL, dev đã fix, QC đã thả RELEASE-<k+1>.md (có mục `## Dev đã fix`
              — định dạng VIPER cũ `## VIPER đã fix` vẫn đọc) — mở lượt bàn giao k+1 TRONG CÙNG release: STATE: Lần bàn giao k+1 ·
              Bàn giao mở · pha E · bỏ tick gate E và C (GIỮ S và P) · append mục lượt mới
              + bảng `### Phạm vi retest` vào RUNLOG · mốc `(release N — bàn giao k+1)`.
              KHÔNG đổi ngưỡng — verdict lượt mới so nguyên bảng TEST-PLAN §4 cũ.

    Không tham số = xem trước (kiểm điều kiện, không ghi gì). Không tự commit.

Windows: dùng `python scripts\\release.py`.

Exit codes: 0 ok · 1 điều kiện chưa đạt / lỗi · 2 sai tham số
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _counts as C  # noqa: E402

ROOT = C.ROOT
TODAY = date.today().isoformat()

ARCHIVE_FILES = [
    "context/TEST-STRATEGY.md", "context/HANDOVER.md", "context/COVERAGE-MAP.md",
    "context/PERSONAS.md", "context/ARCHITECTURE.md", "context/ENVIRONMENT.md",
    "context/API-SURFACE.md", "context/BUGS.md", "context/LESSONS.md", "STATE.md",
]
ARCHIVE_DIRS = ["context/testcases"]

PLAN_SCAFFOLD = """---
type: test-plan
release: {n}
tier: T0
status: DRAFT
---

# TEST PLAN — release {n}

> Viết ở pha S, QC chốt, rồi KHOÁ (guard_frozen). Ngưỡng §4 ghi TRƯỚC khi chạy test.
> Khuôn đầy đủ + hướng dẫn từng mục: xem `context/archive/release-{prev}/` hoặc bản gốc template.

NGUỒN: intake/releases/r{n}/ — dịch ngày _CHƯA ĐIỀN_
Phạm vi: _CHƯA ĐIỀN_
Lượt bàn giao tối đa: {luot_max}
Rà lại chiến lược (release {n}): _CHƯA ĐIỀN_

## 1. Phạm vi — AC mới

| AC | Nguồn | Capability | Diễn giải 1 dòng |
|---|---|---|---|
| _CHƯA ĐIỀN_ | | | |

## 2. Hạng mục test (TI)

| TI | Tên | Loại test | Nguồn | Mức |
|---|---|---|---|---|
| TI-1 | _CHƯA ĐIỀN_ | | | |
| TI-2 | _CHƯA ĐIỀN_ | | | |
| TI-3 | _CHƯA ĐIỀN_ | | | |

## 3. Out-of-scope của release này

- _CHƯA ĐIỀN_

## 4. Ngưỡng verdict — GHI TRƯỚC, KHÔNG SỬA SAU KHI EXECUTE BẮT ĐẦU

| Điều kiện | Ngưỡng release này |
|---|---|
| Bug S1 mở | 0 |
| Bug S2 mở | 0 (PASS) / ≤ _CHƯA ĐIỀN_ có cam kết (PASS-có-điều-kiện) |
| AC mới có ≥1 TC PASS | 100% |
| Regression khu vực R1 | 100% PASS |
| Tổng TC PASS | ≥ _CHƯA ĐIỀN_ % |

## 5. Regression scope

| TC | Lý do chọn |
|---|---|
| _CHƯA ĐIỀN_ | |

## 6. Phân công đợt

| Đợt | Mốc dữ liệu | Agent (≤3) | Phủ TI |
|---|---|---|---|
| 0 | B1 | meta tự tay — smoke luồng lõi | — |

## 7. Rủi ro release này

| Rủi ro | Ứng phó |
|---|---|
| _CHƯA ĐIỀN_ | |

## 8. Truy vết TEST-STRATEGY

| Mục STRATEGY | Áp vào release này |
|---|---|
| §2 dòng r{n} | _CHƯA ĐIỀN_ |

---

Chốt bởi QC: _CHƯA ĐIỀN_
"""

RUNLOG_SCAFFOLD = """---
type: runlog
release: {n}
tier: T2
---

# RUNLOG — release {n}

> Sổ kết quả chạy — append-only trong pha E. Mỗi lượt bàn giao một mục; TC chạy lại =
> dòng MỚI. Kết quả: PASS (có bằng chứng) · FAIL (có bug) · BLOCKED (có blocker) ·
> SKIP (có DECISIONS). `release.py --retest` append mục lượt mới — đừng tạo tay.

---

## Lượt chạy — bàn giao 1 (mở _CHƯA ĐIỀN_)

### Nhật ký đợt

| Đợt | Mốc dữ liệu | Mở | Đóng | Reset/seed sau đợt |
|---|---|---|---|---|
| 0 — meta smoke | B1 | | | |

### Kết quả chạy

| Ngày | Đợt | TC | Agent | Kết quả | Bằng chứng | Bug |
|---|---|---|---|---|---|---|
| | | | | | | |

### Tổng hợp lượt

| TC trong phạm vi | Đã chạy | PASS | FAIL | BLOCKED | SKIP | Bug mới (S1/S2/S3/S4) |
|---|---|---|---|---|---|---|
| | | | | | | |
"""

REPORT_SCAFFOLD = """---
type: release-report
release: {n}
tier: T0
status: DRAFT
---

# BÁO CÁO KIỂM THỬ — release {n}

> Viết ở pha C, sau khi gate E xanh (guard_verdict chặn tới lúc đó). Verdict phải khớp
> verdict máy tính (`python3 scripts/gate.py C`).

## 1. Executive summary

_CHƯA ĐIỀN_

## 2. Số liệu

| Chỉ số | Giá trị |
|---|---|
| TC trong phạm vi / đã chạy / PASS lượt cuối | |
| AC mới có ≥1 TC PASS | |
| Regression (trong đó khu vực R1) | |
| Bug S1/S2/S3/S4 — mở cuối kỳ | |
| Lượt bàn giao đã dùng / tối đa | |

## 3. So ngưỡng (TEST-PLAN §4 — đã khoá trước khi chạy)

| Điều kiện | Ngưỡng | Thực tế | Đạt? |
|---|---|---|---|
| | | | |

## 4. Kết quả theo hạng mục (TI)

| TI | TC pass/tổng | Bug liên quan | Ghi chú |
|---|---|---|---|
| | | | |

## 5. Bàn giao lại cho dev

| Bug | Severity | Một câu | Bằng chứng |
|---|---|---|---|
| | | | |

---

## Kết luận — bàn giao 1

Verdict: _CHƯA ĐIỀN_

Điều kiện kèm theo (PASS-có-điều-kiện): —

Ký bởi QC: _CHƯA ĐIỀN_
"""

RETEST_SECTION = """

---

## Lượt chạy — bàn giao {k} (mở {today})

### Phạm vi retest

<!-- Sinh cơ học từ BUGS (bug chưa đóng) — meta BỔ SUNG dòng regression chọn lọc theo
     TEST-STRATEGY §6 (TC cùng target với chỗ sửa + luồng lõi mỗi release cũ) rồi mới chạy. -->

| TC | Lý do |
|---|---|
{rows}

### Nhật ký đợt

| Đợt | Mốc dữ liệu | Mở | Đóng | Reset/seed sau đợt |
|---|---|---|---|---|
| | | | | |

### Kết quả chạy

| Ngày | Đợt | TC | Agent | Kết quả | Bằng chứng | Bug |
|---|---|---|---|---|---|---|
| | | | | | | |

### Tổng hợp lượt

| TC trong phạm vi | Đã chạy | PASS | FAIL | BLOCKED | SKIP | Bug mới (S1/S2/S3/S4) |
|---|---|---|---|---|---|---|
| | | | | | | |
"""


def die(msg: str) -> int:
    print(f"✗ {msg}")
    return 1


def git_clean() -> bool | None:
    if not (ROOT / ".git").is_dir():
        return None
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"],
                             capture_output=True, text=True, timeout=30)
        return out.stdout.strip() == ""
    except Exception:
        return None


def write(rel: str, text: str) -> None:
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def edit_state_common(text: str, updates: dict[str, str]) -> str:
    for key, val in updates.items():
        pat = re.compile(rf"^({re.escape(key)}\s*:).*$", re.MULTILINE)
        if pat.search(text):
            text = pat.sub(rf"\1 {val}", text, count=1)
    return text


def insert_after_line(text: str, anchor_key: str, new_line: str) -> str:
    """Chèn new_line ngay sau dòng bắt đầu bằng anchor_key (nếu chưa tồn tại khoá đó)."""
    key = new_line.split(":")[0].strip()
    if re.search(rf"^{re.escape(key)}\s*:", text, re.MULTILINE):
        return re.sub(rf"^{re.escape(key)}\s*:.*$", new_line, text, count=1, flags=re.MULTILINE)
    return re.sub(rf"^({re.escape(anchor_key)}[^\n]*)$", rf"\1\n{new_line}",
                  text, count=1, flags=re.MULTILINE)


def untick(text: str, only_blocks: list[str] | None = None) -> str:
    """Bỏ tick checkbox trong §Gate. only_blocks: chỉ các khối `**X — …**` này."""
    lines = text.splitlines()
    out = []
    in_gate = False
    in_target = only_blocks is None
    for line in lines:
        if line.startswith("## Gate"):
            in_gate = True
        elif line.startswith("## ") and in_gate:
            in_gate = False
        if in_gate and only_blocks is not None:
            m = re.match(r"\*\*([SPEC])\s*—", line.strip())
            if m:
                in_target = m.group(1) in only_blocks
        if in_gate and in_target:
            line = line.replace("- [x]", "- [ ]")
        out.append(line)
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def append_decisions(marker: str) -> None:
    p = ROOT / "context/DECISIONS.md"
    text = C.read(p)
    if not text.endswith("\n"):
        text += "\n"
    text += f"| {marker} | — mốc do release.py ghi, gate chỉ đếm dưới mốc cuối | — | — | — |\n"
    p.write_text(text, encoding="utf-8")


# --- --go --------------------------------------------------------------------

def check_go(st: dict, verbose: bool = True) -> list[str]:
    errs = []
    n, k = st["release"], max(st["ban_giao"], 1)
    concl = C.report_conclusions(n).get(k, {})
    if concl.get("verdict") not in ("PASS", "PASS-có-điều-kiện"):
        errs.append(f"REPORT-r{n} mục `Kết luận — bàn giao {k}` chưa có Verdict PASS "
                    f"(đang: {concl.get('verdict')}). FAIL thì dùng --retest.")
    if not concl.get("ky_qc"):
        errs.append("Chưa có dòng `Ký bởi QC: <ISO>` trong mục kết luận lượt này.")
    clean = git_clean()
    if clean is False:
        errs.append("Working tree chưa sạch — commit trước (`git add -A && git commit`).")
    if (ROOT / "context/archive" / f"release-{n}").exists():
        errs.append(f"context/archive/release-{n}/ đã tồn tại — release {n} đã đóng rồi?")
    return errs


def do_go(st: dict) -> int:
    n = st["release"]
    errs = check_go(st)
    if errs:
        for e in errs:
            print(f"✗ {e}")
        return 1
    arch = ROOT / "context/archive" / f"release-{n}"
    arch.mkdir(parents=True)
    for rel in ARCHIVE_FILES:
        src = ROOT / rel
        if src.is_file():
            shutil.copy2(src, arch / src.name)
    for rel in ARCHIVE_DIRS:
        src = ROOT / rel
        if src.is_dir():
            shutil.copytree(src, arch / src.name, dirs_exist_ok=True)
    print(f"✓ archive snapshot → context/archive/release-{n}/")

    stt = C.read("STATE.md")
    stt = edit_state_common(stt, {
        "Pha hiện tại": "S",
        "Release": str(n + 1),
        "Lần bàn giao": "1",
    })
    stt = insert_after_line(stt, "Lần bàn giao", f"Release mở    : {TODAY}")
    stt = re.sub(r"^Bàn giao mở\s*:.*\n?", "", stt, flags=re.MULTILINE)
    stt = untick(stt)
    write("STATE.md", stt)
    print(f"✓ STATE: release {n + 1} · Release mở {TODAY} · lượt 1 · pha S · bỏ tick §Gate")

    luot_max = C.plan(n).get("luot_max") or 3
    write(C.plan_path(n + 1), PLAN_SCAFFOLD.format(n=n + 1, prev=n, luot_max=luot_max))
    write(C.runlog_path(n + 1), RUNLOG_SCAFFOLD.format(n=n + 1))
    write(C.report_path(n + 1), REPORT_SCAFFOLD.format(n=n + 1))
    (ROOT / "intake/releases" / f"r{n + 1}").mkdir(parents=True, exist_ok=True)
    print(f"✓ scaffold context/releases/r{n + 1}/ + intake/releases/r{n + 1}/ (rỗng — chờ QC thả manifest)")

    append_decisions(f"(release {n + 1})")
    print(f"✓ mốc `(release {n + 1})` vào DECISIONS")

    env_p = ROOT / "context/ENVIRONMENT.md"
    env = C.read(env_p)
    env2 = re.sub(r"- \[x\] (\(mỗi release\))", r"- [ ] \1", env)
    if env2 != env:
        env_p.write_text(env2, encoding="utf-8")
        print("✓ re-arm: bỏ tick mục (mỗi release) trong ENVIRONMENT.md")

    print(f"\nXong. Tiếp theo: git add -A && git commit -m \"đóng release {n}, mở release {n + 1}\"")
    print("Rồi chạy /spec-scope khi QC thả manifest mới.")
    return 0


# --- --retest ----------------------------------------------------------------

def check_retest(st: dict) -> tuple[list[str], dict]:
    errs = []
    n, k = st["release"], max(st["ban_giao"], 1)
    concl = C.report_conclusions(n).get(k, {})
    if concl.get("verdict") != "FAIL":
        errs.append(f"REPORT-r{n} lượt {k} không phải FAIL (đang: {concl.get('verdict')}) "
                    "— retest chỉ dành cho release đang FAIL.")
    luot_max = C.plan(n).get("luot_max") or 0
    if luot_max and k + 1 > luot_max:
        # Chặn TRƯỚC khi rơi vào ngõ cụt: lượt vượt trần thì verdict máy FAIL vĩnh viễn.
        # Đây là quyết định của QC, không phải của agent (SPEC.md — /spec-retest Bước 4).
        errs.append(f"Lượt {k + 1} VƯỢT TRẦN `Lượt bàn giao tối đa: {luot_max}` — escalate "
                    "cho QC: muốn tiếp thì QC TỰ TAY nâng con số đó trong TEST-PLAN "
                    "(hook chỉ chặn agent, không chặn người) + meta ghi 1 dòng DECISIONS "
                    "dẫn lời QC, rồi chạy lại --retest; không nâng thì release đứng ở FAIL.")
    mp = C.manifest_path(n, k + 1)
    mf = C.parse_manifest(mp)
    if mp is None or not mf["ok"]:
        errs.append(f"Thiếu manifest intake/releases/r{n}/RELEASE-{k + 1}.md — QC phải thả "
                    "(team báo qua chat thì meta ghi hộ, trích nguyên văn — "
                    "intake/_RELEASE-TEMPLATE.md).")
    else:
        if mf["ban_giao"] != k + 1:
            errs.append(f"Manifest ghi `Lần bàn giao: {mf['ban_giao']}` — phải là {k + 1}.")
        if not mf["fixed_bugs"]:
            errs.append("Manifest thiếu mục `## Dev đã fix` (liệt kê mã BUG-r…-…).")
    return errs, mf


def do_retest(st: dict) -> int:
    n, k = st["release"], max(st["ban_giao"], 1)
    errs, mf = check_retest(st)
    if errs:
        for e in errs:
            print(f"✗ {e}")
        return 1

    # Phạm vi retest cơ học: TC dính bug chưa đóng của release — cộng bug release TRƯỚC
    # còn mở mà manifest khai đã fix (cam kết PASS-có-điều-kiện được đòi nợ ở đây).
    fixed = set(mf.get("fixed_bugs") or [])
    rows = []
    for b in C.bugs():
        if b["release"] != n and b["id"] not in fixed:
            continue
        if b["status"].startswith("đóng") or b["status"].startswith("không sửa") \
                or b["status"].startswith("deferred"):
            continue
        for tc in re.findall(r"TC-[A-Za-z0-9ĐđÀ-ỹ_-]+-\d+", b["block"]):
            rows.append(f"| {tc} | retest {b['id']} |")
    rows = sorted(set(rows)) or ["| _CHƯA ĐIỀN_ | (không tìm được TC từ BUGS — điền tay) |"]

    rl_p = ROOT / C.runlog_path(n)
    rl = C.read(rl_p)
    rl += RETEST_SECTION.format(k=k + 1, today=TODAY, rows="\n".join(rows))
    rl_p.write_text(rl, encoding="utf-8")
    print(f"✓ RUNLOG: mục `Lượt chạy — bàn giao {k + 1}` + phạm vi retest "
          f"({len(rows)} dòng từ BUGS — bổ sung regression chọn lọc theo TEST-STRATEGY §6)")

    stt = C.read("STATE.md")
    stt = edit_state_common(stt, {"Pha hiện tại": "E", "Lần bàn giao": str(k + 1)})
    anchor = "Release mở" if re.search(r"^Release mở\s*:", stt, re.MULTILINE) else "Lần bàn giao"
    stt = insert_after_line(stt, anchor, f"Bàn giao mở   : {TODAY}")
    stt = untick(stt, only_blocks=["E", "C"])
    write("STATE.md", stt)
    print(f"✓ STATE: lượt bàn giao {k + 1} · Bàn giao mở {TODAY} · pha E · bỏ tick gate E/C (giữ S/P)")

    append_decisions(f"(release {n} — bàn giao {k + 1})")
    print(f"✓ mốc `(release {n} — bàn giao {k + 1})` vào DECISIONS")
    print(f"\nXong. Chạy /spec-retest (hoặc /spec-execute) — ngưỡng KHÔNG đổi, "
          f"verdict mới ghi thành mục `Kết luận — bàn giao {k + 1}` trong cùng REPORT.")
    return 0


# --- main --------------------------------------------------------------------

def preview(st: dict) -> int:
    n, k = st["release"], max(st["ban_giao"], 1)
    print(f"Release hiện tại: {n} · lượt bàn giao {k} · pha {st.get('pha')}")
    concl = C.report_conclusions(n).get(k, {})
    print(f"Verdict lượt {k}: {concl.get('verdict')} · Ký bởi QC: {concl.get('ky_qc')}\n")
    print("— Điều kiện --go:")
    errs = check_go(st)
    print("\n".join(f"  ✗ {e}" for e in errs) if errs else "  ✓ đủ điều kiện đóng release")
    print("— Điều kiện --retest:")
    errs2, _ = check_retest(st)
    print("\n".join(f"  ✗ {e}" for e in errs2) if errs2 else "  ✓ đủ điều kiện mở lượt retest")
    print("\nChưa ghi gì. Chạy lại với --go hoặc --retest để thực thi.")
    return 0


def main(argv: list[str]) -> int:
    st = C.state()
    if not st.get("release"):
        return die("Không đọc được STATE.md (dòng `Release :`).")
    if len(argv) == 1:
        return preview(st)
    if argv[1] == "--go":
        return do_go(st)
    if argv[1] == "--retest":
        return do_retest(st)
    print("Usage: python3 scripts/release.py [--go | --retest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
