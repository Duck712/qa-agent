#!/usr/bin/env python3
"""selftest.py — bộ tự kiểm của TEMPLATE SPEC. Không copy sang dự án.

Bootstrap một dự án SPEC nháp + một repo VIPER giả tối thiểu, rồi đi trọn vòng đời:
    S → P → E (FAIL) → C → --retest → E (PASS) → C → --go
kiểm gate fail-closed đúng chỗ, năm hook chặn đúng, và release.py giữ đúng sổ sách.
Rồi bootstrap dự án thứ hai ở CHẾ ĐỘ TỔNG QUÁT (quy trình dev không phải VIPER, repo nguồn
là thư mục tài liệu, môi trường staging) và kiểm gate S/P + guard_readonly + review_tc.

Chạy sau MỌI lần sửa template:
    python3 scripts/selftest.py            # vài giây, dùng thư mục tạm
    python3 scripts/selftest.py --keep     # giữ lại thư mục nháp để soi

Exit codes: 0 tất cả pass · 1 có phép kiểm fail
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
TODAY = date.today().isoformat()
YESTERDAY = (date.today() - timedelta(days=1)).isoformat()

PASSED: list[str] = []
FAILED: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> bool:
    (PASSED if cond else FAILED).append(label if cond else f"{label} — {detail}")
    print(f"  {'✓' if cond else '✗'} {label}" + (f"  ({detail})" if not cond and detail else ""))
    return cond


def run(cmd: list[str], cwd: Path, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          input=stdin, timeout=120)


def hook(script: str, proj: Path, payload: dict) -> subprocess.CompletedProcess:
    return run([sys.executable, f"scripts/{script}"], proj, json.dumps(payload))


def gate(proj: Path, pha: str) -> subprocess.CompletedProcess:
    return run([sys.executable, "scripts/gate.py", pha], proj)


def gate_fails(proj: Path, pha: str) -> list[str]:
    out = gate(proj, pha).stdout
    return [l.strip() for l in out.splitlines() if l.strip().startswith("✗")]


def compute_verdict_of(proj: Path, n: int = 1, k: int = 2) -> str:
    """Verdict máy tính của release n lượt k — gọi thẳng _counts trong dự án nháp."""
    r = run([sys.executable, "-c",
             "import sys; sys.path.insert(0, 'scripts'); import _counts as C; "
             f"print(C.compute_verdict({n}, {k})[0])"], proj)
    return r.stdout.strip()


# --- dựng repo VIPER giả -----------------------------------------------------

def make_fake_viper(root: Path) -> None:
    (root / "context/archive/vong-2").mkdir(parents=True)
    (root / "intake/loops/l1").mkdir(parents=True)
    (root / "intake/loops/l2").mkdir(parents=True)
    (root / "context/shared").mkdir(parents=True, exist_ok=True)
    (root / "VIPER.md").write_text("# VIPER giả cho selftest\n", encoding="utf-8")
    (root / "context/PRD.md").write_text(
        "# PRD\n## 3. AC\n| # | Làm được gì |\n|---|---|\n| AC-1 | Tạo lịch hẹn |\n",
        encoding="utf-8")
    (root / "context/archive/vong-2/PRD.md").write_text("# PRD vòng 2\n", encoding="utf-8")
    (root / "context/CAPABILITIES-MAP.md").write_text("# CAP\n| CAP-BOOK-01 |\n", encoding="utf-8")
    (root / "context/PERSONAS.md").write_text("# Personas\n", encoding="utf-8")
    (root / "context/ARCHITECTURE.md").write_text("# Arch\n", encoding="utf-8")
    (root / "context/ROADMAP.md").write_text("# Roadmap\n", encoding="utf-8")
    (root / "context/shared/DEPLOY.md").write_text("# Deploy\n", encoding="utf-8")
    for i, phases in ((1, "V, I"), (2, "V, I, P")):
        (root / f"intake/loops/l{i}/_PROPOSAL.md").write_text(
            f"NGUỒN: KẾ HOẠCH VÒNG\nPha vòng này: {phases}\n", encoding="utf-8")


# --- điền dự án SPEC cho tới trước từng gate --------------------------------

def fill_scope(proj: Path, viper: Path) -> None:
    (proj / "intake/releases/r1").mkdir(parents=True, exist_ok=True)
    write_manifest(proj, viper, 1, urls=MULTI_URLS)
    mirror = proj / "intake/releases/r1/viper"
    mirror.mkdir(parents=True, exist_ok=True)
    for name in ("PRD.md", "CAPABILITIES-MAP.md", "PERSONAS.md", "ARCHITECTURE.md",
                 "ROADMAP.md", "DEPLOY.md"):
        (mirror / name).write_text(f"# mirror {name}\n", encoding="utf-8")

    (proj / "context/HANDOVER.md").write_text(f"""---
type: handover
---

# HANDOVER

NGUỒN: VIPER — {viper}

## Truy vết VIPER → context

| Release | Mục context | Nguồn trong mirror | Ghi chú dịch |
|---|---|---|---|
| 1 | TEST-PLAN §1 | viper/PRD.md §3 | AC-1 (l2) |
| 1 | COVERAGE-MAP | viper/CAPABILITIES-MAP.md | CAP-BOOK-01 |
| 1 | PERSONAS | viper/PERSONAS.md | giữ mã P- |
| 1 | ARCHITECTURE | viper/ARCHITECTURE.md | 1 boundary |
| 1 | ENVIRONMENT | viper/DEPLOY.md | URL prod |

## Lỗ hổng & cách xử

| Release | Lỗ hổng | Cách xử |
|---|---|---|
| 1 | Không có hộp thư test | hỏi QC — DECISIONS {TODAY} |
""", encoding="utf-8")

    strategy = (proj / "context/TEST-STRATEGY.md").read_text(encoding="utf-8")
    strategy = strategy.replace("Chốt bởi QC: _CHƯA ĐIỀN_", f"Chốt bởi QC: {YESTERDAY}")
    strategy = re.sub(r"\| r1 \| _CHƯA ĐIỀN_ \| _CHƯA ĐIỀN_ \| _CHƯA ĐIỀN_ \| — \| chưa bàn giao \|",
                      "| r1 | l1–l2 | l2 | Đặt lịch lõi | — | đang test |", strategy)
    strategy = re.sub(r"^\| _CHƯA ĐIỀN_ \|(.*)$",
                      "| app | ✓ | — | ✓ | — | ✓ | — | — | — | — | — | — |",
                      strategy, count=1, flags=re.MULTILINE)
    strategy = strategy.replace(
        "| Số TC regression tối thiểu mỗi release | _CHƯA ĐIỀN_ |",
        "| Số TC regression tối thiểu mỗi release | 1 |")
    strategy = strategy.replace(UNF := "_CHƯA ĐIỀN_", "đã điền")
    (proj / "context/TEST-STRATEGY.md").write_text(strategy, encoding="utf-8")

    (proj / "context/COVERAGE-MAP.md").write_text("""---
type: coverage-map
---

# COVERAGE MAP

| Capability | Loop giao | Release test | TI phủ | Trạng thái |
|---|---|---|---|---|
| CAP-BOOK-01 | l2 | r1 | TI-1, TI-2, TI-3 | đang test (r1) |

## 2. Lát cắt release hiện tại

Release 1 phủ CAP-BOOK-01.
""", encoding="utf-8")

    (proj / "context/releases/r1/TEST-PLAN.md").write_text(f"""---
type: test-plan
release: 1
---

# TEST PLAN — release 1

NGUỒN: intake/releases/r1/ — dịch ngày {YESTERDAY}
Phạm vi loop: l1–l2
Lượt bàn giao tối đa: 3
Rà lại chiến lược (release 1): {YESTERDAY}

## 1. Phạm vi — AC mới

| AC | Loop | Capability | Diễn giải 1 dòng |
|---|---|---|---|
| AC-1 | l2 | CAP-BOOK-01 | Tạo lịch hẹn |

## 2. Hạng mục test (TI)

| TI | Tên | Loại test | Nguồn | Mức |
|---|---|---|---|---|
| TI-1 | Đặt lịch lõi | chức năng | CAP-BOOK-01 · AC-1 | R1 |
| TI-2 | Ma trận phân quyền | phân quyền | PERSONAS §2 | R1 |
| TI-3 | Biên đặt lịch | biên | CAP-BOOK-01 | R2 |

## 3. Out-of-scope của release này

- workflow, tương-thích-ngược, tích-hợp, api, cross-target, hình thức, hiệu năng, mobile — ngoài phạm vi release 1

## 4. Ngưỡng verdict

| Điều kiện | Ngưỡng release này |
|---|---|
| Bug S1 mở | 0 |
| Bug S2 mở | 0 (PASS) / ≤ 2 có cam kết (PASS-có-điều-kiện) |
| AC mới có ≥1 TC PASS | 100% |
| Regression khu vực R1 | 100% PASS |
| Tổng TC PASS | ≥ 90 % |

## 5. Regression scope

| TC | Lý do chọn |
|---|---|
| — (release đầu) | |

## 6. Phân công đợt

| Đợt | Mốc dữ liệu | Agent (≤3) | Phủ TI |
|---|---|---|---|
| 0 | B1 | meta tự tay | — |
| 1 | B0 | spec-tester-edge | TI-3 |
| 2 | B1 | spec-tester-flow · spec-tester-authz | TI-1, TI-2 |

## 7. Rủi ro release này

| Rủi ro | Ứng phó |
|---|---|
| Tenant test chưa có | tạo qua đăng ký công khai |

## 8. Truy vết TEST-STRATEGY

| Mục STRATEGY | Áp vào release này |
|---|---|
| §2 dòng r1 | l1–l2, loop deploy l2 |

---

Chốt bởi QC: {YESTERDAY}
""", encoding="utf-8")

    dec = (proj / "context/DECISIONS.md").read_text(encoding="utf-8")
    dec += (f"| {YESTERDAY} | Cách ly bằng tài khoản + prefix | Sản phẩm không đa tenant | Prefix đủ phân biệt | Có |\n"
            f"| {YESTERDAY} | Không load test trên production | SAFETY mục 4 | Ngưỡng p95 đủ để phát hiện chậm | Có |\n")
    (proj / "context/DECISIONS.md").write_text(dec, encoding="utf-8")

    add_challenge(proj, YESTERDAY, "S", "Phạm vi test đã đủ chưa?", "đủ 3 TI")


def make_fake_source(root: Path) -> None:
    """Repo nguồn tổng quát: chỉ là thư mục tài liệu bàn giao (không VIPER.md, không loop)."""
    (root / "docs").mkdir(parents=True)
    (root / "docs/PRD-dat-lich.md").write_text(
        "# PRD đặt lịch\n## 3. AC\n| AC | Làm được gì |\n|---|---|\n| AC-1 | Tạo lịch hẹn |\n",
        encoding="utf-8")
    (root / "docs/api.md").write_text("# API\nPOST /api/bookings\n", encoding="utf-8")


STAGING_URLS = [
    "| booking-api | boundary | https://api.staging.vi-du.test/booking | /healthz | |",
    "| notify-worker | boundary | — | — | nội bộ, chạm qua booking-api |",
    "| web | web-experience | https://staging.vi-du.test | / | |",
]


def write_manifest_tong_quat(proj: Path, src: Path, luot: int = 1, urls: list[str] | None = None,
                             ban_deploy: str = "v1.4.0 (build 2026-09-20)",
                             moi_truong: str = "staging", fixed: str = "") -> Path:
    name = "RELEASE.md" if luot == 1 else f"RELEASE-{luot}.md"
    p = proj / "intake/releases/r1" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    body = f"""NGUỒN: BÀN GIAO RELEASE — từ đội Shop
Quy trình dev: Scrum
Repo nguồn: {src}
Release: 1
Phạm vi: Sprint 12 — đặt lịch
Bản deploy: {ban_deploy}
Môi trường: {moi_truong}
Điểm vào chính: https://staging.vi-du.test
Lần bàn giao: {luot}

## URL theo target

| Target | Loại | URL / bundle id | Health check | Ghi chú |
|---|---|---|---|---|
""" + "\n".join(urls if urls is not None else STAGING_URLS) + "\n"
    if fixed:
        body += f"\n## Dev đã fix\n- {fixed}\n"
    p.write_text(body, encoding="utf-8")
    return p


def fill_scope_tong_quat(proj: Path, src: Path) -> None:
    """Như fill_scope nhưng đầu vào là thư mục tài liệu — mirror nguon/, marker chung,
    TEST-PLAN `Phạm vi:` + bảng AC cột `Nguồn`."""
    fill_scope(proj, src)          # dựng phần dùng chung (strategy, coverage, decisions…)
    shutil.rmtree(proj / "intake/releases/r1/viper", ignore_errors=True)
    write_manifest_tong_quat(proj, src)
    mirror = proj / "intake/releases/r1/nguon"
    mirror.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src / "docs/PRD-dat-lich.md", mirror / "PRD-dat-lich.md")
    (proj / "context/HANDOVER.md").write_text(f"""---
type: handover
---

# HANDOVER

NGUỒN: Tài liệu bàn giao đội Shop — {src}

## Truy vết nguồn → context

| Release | Mục context | Nguồn trong mirror | Ghi chú dịch |
|---|---|---|---|
| 1 | TEST-PLAN §1 | nguon/PRD-dat-lich.md §3 | AC-1 |
| 1 | PERSONAS | nguon/PRD-dat-lich.md §1 | 2 vai |
| 1 | ARCHITECTURE | nguon/PRD-dat-lich.md §4 | 1 boundary + web |

## Lỗ hổng & cách xử

| Release | Lỗ hổng | Đề xuất của meta / rủi ro nếu sai | Cách xử |
|---|---|---|---|
| 1 | Tài liệu không nói hộp thư test | dùng alias +spec — rủi ro: mail thật lọt | hỏi QC — DECISIONS {TODAY} |
""", encoding="utf-8")
    tp = proj / "context/releases/r1/TEST-PLAN.md"
    text = tp.read_text(encoding="utf-8")
    text = text.replace("Phạm vi loop: l1–l2", "Phạm vi: Sprint 12 — đặt lịch")
    text = text.replace("| AC | Loop | Capability | Diễn giải 1 dòng |",
                        "| AC | Nguồn | Capability | Diễn giải 1 dòng |")
    text = text.replace("| AC-1 | l2 | CAP-BOOK-01 | Tạo lịch hẹn |",
                        "| AC-1 | PRD-dat-lich §3 | CAP-BOOK-01 | Tạo lịch hẹn |")
    tp.write_text(text, encoding="utf-8")


# Hệ nhiều microservice: 2 boundary (một cái nội bộ) + 1 web experience
MULTI_URLS = [
    "| booking-api | boundary | https://api.vi-du.test/booking | /healthz | |",
    "| notify-worker | boundary | — | — | nội bộ, chạm qua booking-api |",
    "| web | web-experience | https://vi-du.test | / | |",
]


def write_manifest(proj: Path, viper: Path, luot: int, urls: list[str],
                   fixed: str = "") -> Path:
    name = "RELEASE.md" if luot == 1 else f"RELEASE-{luot}.md"
    p = proj / "intake/releases/r1" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    body = f"""NGUỒN: BÀN GIAO RELEASE — từ VIPER
Repo VIPER: {viper}
Release: 1
Phạm vi loop: l1–l2
Loop deploy: l2
Điểm vào chính: https://vi-du.test
Lần bàn giao: {luot}

## URL theo target

| Target | Loại | URL / bundle id | Health check | Ghi chú |
|---|---|---|---|---|
""" + "\n".join(urls) + "\n"
    if fixed:
        body += f"\n## VIPER đã fix\n- {fixed}\n"
    p.write_text(body, encoding="utf-8")
    return p


def add_challenge(proj: Path, ngay: str, pha: str, cau: str, ghi_chu: str) -> None:
    """Chèn một dòng vào ĐÚNG bảng §Challenge log (không đụng bảng Blocker cùng số cột)."""
    p = proj / "STATE.md"
    text = p.read_text(encoding="utf-8")
    head, sep, rest = text.partition("## Challenge log")
    # chỉ thao tác TRONG mục Challenge log — bảng Blocker phía dưới cũng 5 cột
    cut = rest.find("\n## ")
    body, after = (rest[:cut], rest[cut:]) if cut > 0 else (rest, "")
    row = f"| {ngay} | {pha} | {cau} | PASS | {ghi_chu} |"
    if "| | | | | |" in body:
        body = body.replace("| | | | | |", row, 1)
    else:
        lines = body.splitlines()
        last = max(i for i, l in enumerate(lines) if l.startswith("|"))
        lines.insert(last + 1, row)
        body = "\n".join(lines)
    p.write_text(head + sep + body + after, encoding="utf-8")


def tick_scope_locked(proj: Path) -> None:
    st = (proj / "STATE.md").read_text(encoding="utf-8")
    st = st.replace("- [ ] **Scope khoá**", "- [x] **Scope khoá**")
    (proj / "STATE.md").write_text(st, encoding="utf-8")


def set_phase(proj: Path, pha: str) -> None:
    st = (proj / "STATE.md").read_text(encoding="utf-8")
    st = re.sub(r"^(Pha hiện tại\s*:).*$", rf"\1 {pha}", st, count=1, flags=re.MULTILINE)
    (proj / "STATE.md").write_text(st, encoding="utf-8")


def fill_dich(proj: Path) -> None:
    """Pha S — dịch PERSONAS + ARCHITECTURE từ mirror (gate S đọc ARCHITECTURE để biết
    target nào trong phạm vi)."""
    (proj / "context/PERSONAS.md").write_text("""---
type: personas
---

# PERSONAS

## 1. Persona

### Persona 1 — Chủ gara (role: owner, mã P-OWNER) ← persona chính

| Mục | Nội dung |
|---|---|
| Chân dung + bối cảnh | Quản 3–10 thợ |
| Thiết bị chính | Điện thoại |
| Năng lực được cấp | Tạo/sửa/huỷ lịch |
| KHÔNG được làm | Thấy dữ liệu gara khác |
| Luồng chính | Mở app → chốt hẹn |

## 2. Ma trận vai × hành động

| Hành động | owner | mechanic | chưa đăng nhập |
|---|---|---|---|
| Tạo lịch hẹn | ✓ | ✗ | ✗ |

## 3. Tài khoản test theo vai

| Vai (role) | Persona | Tài khoản | Biến env mật khẩu | Tạo bằng | Đăng nhập ✓? |
|---|---|---|---|---|---|
| owner | P-OWNER | spec+owner@vi-du.test | SPEC_PW_OWNER | đăng ký | ✓ |
| mechanic | P-OWNER | spec+mechanic@vi-du.test | SPEC_PW_MECHANIC | mời | ✓ |
| (chưa đăng nhập) | — | — | — | — | — |
""", encoding="utf-8")

    (proj / "context/ARCHITECTURE.md").write_text("""---
type: architecture
---

# ARCHITECTURE

## 1. Backend boundaries

| Boundary | Nhiệm vụ (1 dòng) | Loop giao | Trong phạm vi release hiện tại? |
|---|---|---|---|
| booking-api | Đặt lịch | l1–l2 | có |
| notify-worker | Gửi nhắc lịch | l2 | có |
| billing-api | Thu tiền | l4 | không |

## 2. Frontend experiences — web

| Experience | Persona | Loop giao | Design system | Trong phạm vi? |
|---|---|---|---|---|
| web | P-OWNER | l2 | — | có |

## 3. Frontend experiences — mobile

| Experience | Nền tảng | Persona | Loop giao | Trong phạm vi? |
|---|---|---|---|---|
| — | | | | |

## 4. Contract giữa các target

| Contract | Bên cung cấp | Bên dùng | Kiểu | Ghi chú test |
|---|---|---|---|---|
| booking.created | booking-api | notify-worker | event | notify nội bộ — kiểm qua booking-api |

## 5. Luồng lõi

Mở app → chọn giờ trống → tạo hẹn → thấy hẹn trong danh sách.

## 6. Ca biên VIPER đã quyết

| Tình huống | VIPER hứa xử thế nào | TC kiểm |
|---|---|---|
| Gửi hai lần | Ràng buộc unique | TC-BOOK-01-003 |

## 7. Dịch vụ ngoài

| Dịch vụ | Sản phẩm dùng để | Kiểm bằng |
|---|---|---|
| — | | |
""", encoding="utf-8")


def fill_prepare(proj: Path) -> None:
    (proj / "context/ENVIRONMENT.md").write_text(f"""---
type: environment
---

# ENVIRONMENT

## 1. Boundary / microservice

| Boundary | URL production | Health check | Chạm từ ngoài? | Kiểm lần cuối |
|---|---|---|---|---|
| booking-api | https://api.vi-du.test/booking | /healthz → 200 | có | {TODAY} ✓ |
| notify-worker | — | — | không — qua booking-api | {TODAY} ✓ |

## 2. Web / mobile experience

| Experience | Loại | URL / bundle id | Persona chính |
|---|---|---|---|
| web | web | https://vi-du.test | P-OWNER |

## 3. Tài khoản test theo vai

| Vai | Tài khoản | Tenant | Biến env mật khẩu | Tạo bằng | Đăng nhập ✓? |
|---|---|---|---|---|---|
| owner | spec+owner@vi-du.test | SPEC-TEST | SPEC_PW_OWNER | đăng ký | ✓ |
| mechanic | spec+mechanic@vi-du.test | SPEC-TEST | SPEC_PW_MECHANIC | mời | ✓ |
| (chưa đăng nhập) | — | — | — | — | — |

## 4. Tenant test + cách ly

| Mục | Giá trị |
|---|---|
| Tenant | SPEC-TEST |
| Sản phẩm đa tenant? | không — cách ly bằng tài khoản + prefix |
| Prefix dữ liệu | SPEC-r1- |

## 5. Seed / reset — hai mốc dữ liệu

| Mốc | Nghĩa là | Lệnh | Thời gian chạy |
|---|---|---|---|
| B0 | Tenant sạch | `make reset` | 30s |
| B1 | B0 + dữ liệu mẫu | `make seed` | 90s |

Đường seed: API công khai — environment/local/seed.py

## 6. Thiết bị mobile

| Thiết bị | Nền tảng | Vì sao chọn | Build cài | Checksum khớp? |
|---|---|---|---|---|
| — | | | | |

## 7. Rác còn lại

| Ngày | Bản ghi | Vì sao không xoá được |
|---|---|---|
| | | |

## 8. Kiểm lại mỗi release

- [x] (mỗi release) URL từng target còn sống
- [x] (mỗi release) Từng tài khoản còn đăng nhập được
- [x] (mỗi release) `make seed` còn chạy đúng
- [x] (mỗi release) Cách ly còn đúng
""", encoding="utf-8")

    mk = (proj / "Makefile").read_text(encoding="utf-8")
    for t in ("doctor", "seed", "reset", "accounts", "devices", "smoke"):
        mk = mk.replace(f"{t}:\n\t$(NOT_IMPLEMENTED)", f"{t}:\n\t@echo '{t} ok'")
    (proj / "Makefile").write_text(mk, encoding="utf-8")

    (proj / "context/testcases/CAP-BOOK-01.md").write_text("""---
type: testcases
capability: CAP-BOOK-01
---

# Test case — CAP-BOOK-01

### TC-BOOK-01-001 — Tạo lịch hẹn thành công
AC: AC-1 (l2) · Loại: chức năng · Tầng: web · Mức: R1 · Regression: có · Release vào: 1

| Mục | Nội dung |
|---|---|
| Vai / tài khoản | owner |
| Mốc dữ liệu | B1 |
| Bằng chứng cần | Screenshot có URL bar |

| Bước | Thao tác | Dữ liệu | Kỳ vọng |
|---|---|---|---|
| 1 | Chọn giờ trống, lưu | SPEC-r1-Khách A | Hẹn hiện trong danh sách |

### TC-BOOK-01-002 — Mechanic không tạo được lịch hẹn
AC: AC-1 (l2) · Loại: phân quyền · Tầng: web · Mức: R1 · Regression: có · Release vào: 1 · Ô ma trận: Tạo lịch hẹn × mechanic = ✗

| Mục | Nội dung |
|---|---|
| Vai / tài khoản | mechanic |
| Mốc dữ liệu | B1 |
| Bằng chứng cần | Response nguyên văn |

| Bước | Thao tác | Dữ liệu | Kỳ vọng |
|---|---|---|---|
| 1 | POST /api/bookings bằng token mechanic | — | 403 |

### TC-BOOK-01-003 — Gửi hai lần không tạo bản ghi trùng
AC: AC-1 (l2) · Loại: biên · Tầng: web · Mức: R2 · Regression: có · Release vào: 1

| Mục | Nội dung |
|---|---|
| Vai / tài khoản | owner |
| Mốc dữ liệu | B1 |
| Bằng chứng cần | Screenshot danh sách |

| Bước | Thao tác | Dữ liệu | Kỳ vọng |
|---|---|---|---|
| 1 | Bấm lưu hai lần nhanh | SPEC-r1-Khách B | Chỉ một bản ghi |

### TC-BOOK-01-004 — Chưa đăng nhập không tạo được lịch hẹn
AC: AC-1 (l2) · Loại: phân quyền · Tầng: web · Mức: R1 · Regression: có · Release vào: 1 · Ô ma trận: Tạo lịch hẹn × chưa đăng nhập = ✗

| Mục | Nội dung |
|---|---|
| Vai / tài khoản | (chưa đăng nhập) |
| Mốc dữ liệu | B0 |
| Bằng chứng cần | Response nguyên văn |

| Bước | Thao tác | Dữ liệu | Kỳ vọng |
|---|---|---|---|
| 1 | POST /api/bookings không token | — | 401 |
""", encoding="utf-8")

    add_challenge(proj, TODAY, "P", "TC nào phủ ca gửi hai lần?", "TC-BOOK-01-003")


def evidence_for(proj: Path, luot: int, tc: str) -> str:
    d = proj / "evidence" / "r1" / f"luot-{luot}" / tc
    d.mkdir(parents=True, exist_ok=True)
    (d / "01.png").write_text("fake", encoding="utf-8")
    return f"evidence/r1/luot-{luot}/{tc}/"


def fill_execute_fail(proj: Path) -> None:
    """Lượt 1: 3 PASS + 1 FAIL (bug S2) → verdict FAIL."""
    for tc in ("TC-BOOK-01-001", "TC-BOOK-01-002", "TC-BOOK-01-003", "TC-BOOK-01-004"):
        evidence_for(proj, 1, tc)
    rl = (proj / "context/releases/r1/RUNLOG.md").read_text(encoding="utf-8")
    rows = "\n".join([
        f"| {TODAY} | 2 | TC-BOOK-01-001 | spec-tester-flow | PASS | evidence/r1/luot-1/TC-BOOK-01-001/ | — |",
        f"| {TODAY} | 2 | TC-BOOK-01-002 | spec-tester-authz | FAIL | evidence/r1/luot-1/TC-BOOK-01-002/ | BUG-r1-001 |",
        f"| {TODAY} | 1 | TC-BOOK-01-003 | spec-tester-edge | PASS | evidence/r1/luot-1/TC-BOOK-01-003/ | — |",
        f"| {TODAY} | 2 | TC-BOOK-01-004 | spec-tester-authz | PASS | evidence/r1/luot-1/TC-BOOK-01-004/ | — |",
    ])
    rl = rl.replace("| | | | | | | |", rows, 1)
    rl = rl.replace("## Lượt chạy — bàn giao 1 (mở _CHƯA ĐIỀN_)",
                    f"## Lượt chạy — bàn giao 1 (mở {TODAY})")
    (proj / "context/releases/r1/RUNLOG.md").write_text(rl, encoding="utf-8")

    bugs = (proj / "context/BUGS.md").read_text(encoding="utf-8")
    bugs += f"""
### BUG-r1-001 — Thợ tạo được lịch hẹn dù bị cấm

| Mục | Nội dung |
|---|---|
| Severity | S2 |
| AC / TC | AC-1 (l2) · TC-BOOK-01-002 |
| Lượt phát hiện | bàn giao 1 · đợt 2 · spec-tester-authz |
| Bước tái hiện | POST /api/bookings bằng token mechanic |
| Kỳ vọng | 403 |
| Bằng chứng | evidence/r1/luot-1/TC-BOOK-01-002/ |
| Trạng thái | mở |
"""
    # bảng Tổng hợp phải khớp các khối — gate C đối chiếu
    bugs = bugs.replace("| S2 | 0 | 0 | 0 | 0 | 0 |", "| S2 | 1 | 0 | 0 | 0 | 0 |")
    (proj / "context/BUGS.md").write_text(bugs, encoding="utf-8")


def write_report(proj: Path, luot: int, verdict: str) -> None:
    p = proj / "context/releases/r1/REPORT.md"
    text = p.read_text(encoding="utf-8")
    filled = f"""## 1. Executive summary

Release 1 lượt {luot}: kết quả {verdict}.

## 2. Số liệu

| Chỉ số | Giá trị |
|---|---|
| TC trong phạm vi / đã chạy / PASS lượt cuối | 3 / 3 / {2 if verdict == 'FAIL' else 3} |

## 3. So ngưỡng (TEST-PLAN §4 — đã khoá trước khi chạy)

| Điều kiện | Ngưỡng | Thực tế | Đạt? |
|---|---|---|---|
| Bug S1 mở | 0 | 0 | ✓ |

## 4. Kết quả theo hạng mục (TI)

| TI | TC pass/tổng | Bug liên quan | Ghi chú |
|---|---|---|---|
| TI-1 | 1/1 | — | |

## 5. Bàn giao lại cho VIPER

| Bug | Severity | Một câu | Bằng chứng |
|---|---|---|---|
| {'BUG-r1-001 | S2 | Thợ tạo được lịch hẹn | evidence/r1/luot-1/TC-BOOK-01-002/' if verdict == 'FAIL' else '— | — | — | —'} |
"""
    if luot == 1:
        # thay thân báo cáo mẫu bằng bản đã điền
        head, _sep, tail = text.partition("## 1. Executive summary")
        tail_concl = tail[tail.find("---\n\n## Kết luận"):]
        text = head + filled + "\n" + tail_concl
        text = text.replace("Verdict: _CHƯA ĐIỀN_", f"Verdict: {verdict}")
        text = text.replace("Ký bởi QC: _CHƯA ĐIỀN_", f"Ký bởi QC: {TODAY}")
    else:
        text += f"""

## Kết luận — bàn giao {luot}

Verdict: {verdict}

Điều kiện kèm theo (PASS-có-điều-kiện): —

Ký bởi QC: {TODAY}
"""
    p.write_text(text, encoding="utf-8")


def fill_retest_pass(proj: Path) -> None:
    """Lượt 2: TC-BOOK-01-002 retest PASS, bug đóng."""
    evidence_for(proj, 2, "TC-BOOK-01-002")
    p = proj / "context/releases/r1/RUNLOG.md"
    rl = p.read_text(encoding="utf-8")
    marker = "## Lượt chạy — bàn giao 2"
    head, sep, tail = rl.partition(marker)
    row = (f"| {TODAY} | 1 | TC-BOOK-01-002 | spec-tester-authz | PASS | "
           f"evidence/r1/luot-2/TC-BOOK-01-002/ | BUG-r1-001 |")
    tail = tail.replace("| | | | | | | |", row, 1)
    p.write_text(head + sep + tail, encoding="utf-8")

    bugs = (proj / "context/BUGS.md").read_text(encoding="utf-8")
    bugs = bugs.replace("| Trạng thái | mở |",
                        f"| Trạng thái | đóng (retest PASS lượt 2, {TODAY}) |")
    bugs = bugs.replace("| S2 | 1 | 0 | 0 | 0 | 0 |", "| S2 | 0 | 0 | 1 | 0 | 0 |")
    (proj / "context/BUGS.md").write_text(bugs, encoding="utf-8")


UNF = "_CHƯA ĐIỀN_"


def scenario_tong_quat(tmp: Path) -> None:
    """Dự án thứ hai: quy trình dev KHÔNG phải VIPER, repo nguồn = thư mục tài liệu,
    môi trường staging. Không đòi VIPER.md / _PROPOSAL.md / loop có P."""
    proj = tmp / "nhap-tong-quat"
    src = tmp / "nhap-nguon"
    make_fake_source(src)

    print("\n[17] chế độ tổng quát — bootstrap --source")
    r = run([sys.executable, "scripts/bootstrap.py", "nhap-tong-quat", "--target", str(proj),
             "--name", "Shop nháp", "--authority", "QC Nháp <qc@vi-du.test>",
             "--source", str(src)], SRC)
    check(r.returncode == 0, "bootstrap.py --source chạy xong", (r.stdout + r.stderr)[-300:])
    if r.returncode != 0:
        return
    readme = (proj / "README.md").read_text(encoding="utf-8")
    check("Repo nguồn" in readme and str(src) in readme, "README dự án ghi gợi ý repo nguồn")
    check("VIPER." not in readme.replace("VIPER hay khác", ""),
          "README dự án không mặc định sản phẩm làm bằng VIPER")
    for d in ("intake/releases/r1", "evidence"):
        check((proj / d).is_dir(), f"tạo sẵn thư mục {d}/")

    print("\n[18] chế độ tổng quát — gate S")
    fill_scope_tong_quat(proj, src)
    fill_dich(proj)
    tick_scope_locked(proj)
    out = gate(proj, "S").stdout
    fails = [l.strip() for l in out.splitlines() if l.strip().startswith("✗")]
    check(not fails, "gate S xanh — không đòi VIPER.md / _PROPOSAL.md / loop P", "; ".join(fails[:4]))
    check("_PROPOSAL" not in out and "VIPER.md" not in out,
          "gate S tổng quát không nhắc kiểm tra riêng của VIPER")
    check("CẢNH BÁO" not in out, "URL staging hợp lệ → không cảnh báo production")

    write_manifest_tong_quat(proj, src, ban_deploy="_CHƯA ĐIỀN_")
    fails = gate_fails(proj, "S")
    check(any("Bản deploy" in f for f in fails), "gate S đỏ khi `Bản deploy:` chưa điền",
          "; ".join(fails[:3]))
    write_manifest_tong_quat(proj, src, moi_truong="prod")
    fails = gate_fails(proj, "S")
    check(any("Môi trường" in f for f in fails), "gate S đỏ khi `Môi trường:` không hợp lệ",
          "; ".join(fails[:3]))
    write_manifest_tong_quat(proj, src, urls=[
        "| booking-api | boundary | https://api.vi-du.vn/booking | /healthz | |",
        STAGING_URLS[1], STAGING_URLS[2]])
    out = gate(proj, "S").stdout
    check("CẢNH BÁO" in out and "api.vi-du.vn" in out,
          "staging mà URL trông như production → gate S cảnh báo", out[-300:])
    write_manifest_tong_quat(proj, src)

    mirror = proj / "intake/releases/r1/nguon"
    backup = tmp / "nguon-backup"
    shutil.move(str(mirror), str(backup))
    fails = gate_fails(proj, "S")
    check(any("nguon" in f for f in fails), "gate S đỏ khi chưa đóng băng mirror nguon/",
          "; ".join(fails[:3]))
    shutil.move(str(backup), str(mirror))

    shutil.rmtree(src)
    fails = gate_fails(proj, "S")
    check(any("Repo nguồn" in f for f in fails), "gate S đỏ khi repo nguồn không tồn tại",
          "; ".join(fails[:3]))
    make_fake_source(src)
    check(not gate_fails(proj, "S"), "gate S xanh lại")

    print("\n[19] chế độ tổng quát — guard_readonly bảo vệ repo nguồn")
    r = hook("guard_readonly.py", proj, {"tool_name": "Edit",
             "tool_input": {"file_path": str(src / "docs/PRD-dat-lich.md")}})
    check(r.returncode == 2 and "repo nguồn" in r.stderr, "chặn Edit vào repo nguồn", f"exit={r.returncode}")
    r = hook("guard_readonly.py", proj, {"tool_name": "Bash",
             "tool_input": {"command": f"echo x >> {src}/docs/api.md"}})
    check(r.returncode == 2, "chặn Bash append vào repo nguồn")
    r = hook("guard_readonly.py", proj, {"tool_name": "Bash",
             "tool_input": {"command": f"cp -r {src}/docs intake/releases/r1/nguon/"}})
    check(r.returncode == 0, "cho qua cp mirror (nguồn → SPEC)")

    print("\n[20] chế độ tổng quát — gate P + review_tc")
    set_phase(proj, "P")
    fill_prepare(proj)
    tc_file = proj / "context/testcases/CAP-BOOK-01.md"
    tc_file.write_text(tc_file.read_text(encoding="utf-8").replace("AC: AC-1 (l2)", "AC: AC-1"),
                       encoding="utf-8")
    out = gate(proj, "P").stdout
    fails = [l.strip() for l in out.splitlines() if l.strip().startswith("✗")]
    check(not fails, "gate P xanh — AC mã trần (cột Nguồn không phải loop)", "; ".join(fails[:4]))
    check("trên staging" in out, "gate P nhắc dry-run trên đúng môi trường staging")

    r = run([sys.executable, "scripts/review_tc.py"], proj)
    check(r.returncode == 1 and "Kiểu" in r.stdout,
          "review_tc ĐỎ khi TC thiếu nhãn `Kiểu:`", r.stdout[-300:])
    text = tc_file.read_text(encoding="utf-8")
    text = text.replace("AC: AC-1 · Loại: chức năng", "AC: AC-1 · Kiểu: normal · Loại: chức năng")
    text = re.sub(r"AC: AC-1 · Loại: (phân quyền|biên)", r"AC: AC-1 · Kiểu: abnormal · Loại: \1", text)
    tc_file.write_text(text, encoding="utf-8")
    r = run([sys.executable, "scripts/review_tc.py"], proj)
    check(r.returncode == 0, "review_tc XANH khi mỗi AC có normal + abnormal, meta đủ",
          r.stdout[-400:])
    check(not gate_fails(proj, "P"), "thêm nhãn `Kiểu:` không làm gãy gate P")
    tc_file.write_text(text.replace(" · Kiểu: normal", ""), encoding="utf-8")
    r = run([sys.executable, "scripts/review_tc.py"], proj)
    check(r.returncode == 1 and "AC thiếu TC normal: 1" in r.stdout,
          "review_tc chỉ ra AC thiếu ca normal", r.stdout[-300:])
    tc_file.write_text(text.replace("hiện trong danh sách", "hoạt động đúng"), encoding="utf-8")
    r = run([sys.executable, "scripts/review_tc.py"], proj)
    check(r.returncode == 1 and "rỗng nghĩa: 1" in r.stdout,
          "review_tc bắt kỳ vọng rỗng nghĩa (\"hoạt động đúng\")", r.stdout[-300:])
    tc_file.write_text(text, encoding="utf-8")

    print("\n[21] chế độ tổng quát — manifest lượt 2 đọc `## Dev đã fix`")
    mp = write_manifest_tong_quat(proj, src, luot=2, fixed="BUG-r1-001: thêm kiểm quyền")
    r = run([sys.executable, "-c",
             "import sys; sys.path.insert(0, 'scripts'); import _counts as C; from pathlib import Path; "
             f"m = C.parse_manifest(Path({str(mp)!r})); print(m['mode'], m['fixed_bugs'], m['moi_truong'])"],
            proj)
    check(r.stdout.strip() == "tong-quat ['BUG-r1-001'] staging",
          "parse_manifest: chế độ tổng quát + bug đã fix + môi trường", r.stdout.strip() + r.stderr[-200:])
    mp.unlink()

    print("\n[22] tương thích ngược — manifest VIPER định dạng cũ vẫn là chế độ VIPER")
    r = run([sys.executable, "-c",
             "import sys; sys.path.insert(0, 'scripts'); import _counts as C; from pathlib import Path; "
             "import tempfile; p = Path(tempfile.mkstemp(suffix='.md')[1]); "
             "p.write_text('Repo VIPER: /x\\nRelease: 1\\nPhạm vi loop: l3–l5\\nLoop deploy: l5\\n"
             "## VIPER đã fix\\n- BUG-r1-002: x\\n', encoding='utf-8'); m = C.parse_manifest(p); "
             "print(m['mode'], m['loop_a'], m['loop_b'], m['loop_deploy'], m['fixed_bugs'], m['moi_truong']); p.unlink()"],
            proj)
    check(r.stdout.strip() == "viper 3 5 5 ['BUG-r1-002'] production",
          "`Repo VIPER:` + `Phạm vi loop:` + `## VIPER đã fix` → VIPER, mặc định production",
          r.stdout.strip() + r.stderr[-200:])


# --- kịch bản chính ----------------------------------------------------------

def main() -> int:
    keep = "--keep" in sys.argv
    tmp = Path(tempfile.mkdtemp(prefix="spec-selftest-"))
    proj = tmp / "nhap-spec"
    viper = tmp / "nhap-viper"
    print(f"\n=== SPEC selftest — {tmp} ===\n")

    try:
        print("[1] bootstrap")
        r = run([sys.executable, "scripts/bootstrap.py", "nhap-spec", "--target", str(proj),
                 "--name", "Dự án nháp", "--authority", "QC Nháp <qc@vi-du.test>"], SRC)
        check(r.returncode == 0, "bootstrap.py chạy xong", r.stderr[-300:])
        check((proj / "SPEC.md").is_file(), "dự án có SPEC.md")
        check(not (proj / "scripts/bootstrap.py").exists(), "bootstrap.py KHÔNG copy sang dự án")
        check(not (proj / "scripts/selftest.py").exists(), "selftest.py KHÔNG copy sang dự án")
        check("{{PROJECT_NAME}}" not in (proj / "CLAUDE.md").read_text(encoding="utf-8"),
              "placeholder đã thay")
        for d in ("intake/releases/r1", "environment/local", "evidence", "context/archive/ledger"):
            check((proj / d).is_dir(), f"tạo sẵn thư mục {d}/")
        make_fake_viper(viper)

        print("\n[2] gate S fail-closed khi chưa có manifest")
        fails = gate_fails(proj, "S")
        check(any("Manifest" in f for f in fails), "gate S đỏ vì thiếu manifest")
        check(gate(proj, "S").returncode == 1, "gate S exit 1")

        print("\n[3] pha S — điền đủ rồi gate S xanh")
        fill_scope(proj, viper)
        fill_dich(proj)
        tick_scope_locked(proj)
        fails = gate_fails(proj, "S")
        check(not fails, "gate S xanh sau khi điền", "; ".join(fails[:4]))

        print("\n[3b] hệ nhiều microservice — manifest phải phủ mọi target trong phạm vi")
        write_manifest(proj, viper, 1, urls=[MULTI_URLS[0], MULTI_URLS[2]])  # bỏ notify-worker
        fails = gate_fails(proj, "S")
        check(any("notify-worker" in f for f in fails),
              "gate S đỏ khi thiếu URL của một microservice trong phạm vi", "; ".join(fails[:3]))
        check(not any("billing-api" in f for f in fails),
              "target NGOÀI phạm vi không bị đòi URL")
        ho = proj / "context/HANDOVER.md"
        ho.write_text(ho.read_text(encoding="utf-8").replace(
            "| 1 | Không có hộp thư test | hỏi QC — DECISIONS",
            "| 1 | notify-worker chưa biết URL — QC chưa cấp, dò ở pha P | hỏi QC — DECISIONS"), encoding="utf-8")
        fails = gate_fails(proj, "S")
        check(not any("notify-worker" in f for f in fails),
              "ghi vào HANDOVER §Lỗ hổng thì gate S cho qua (có vết)", "; ".join(fails[:3]))
        write_manifest(proj, viper, 1, urls=MULTI_URLS)  # khôi phục bản đủ
        check(not gate_fails(proj, "S"), "gate S xanh lại với manifest đủ URL")

        print("\n[4] hook guard_ask")
        set_phase(proj, "S")
        r = hook("guard_ask.py", proj, {"tool_name": "AskUserQuestion"})
        check(r.returncode == 2, "chặn khi Scope khoá đã tick (dù pha S)", f"exit={r.returncode}")
        st = (proj / "STATE.md").read_text(encoding="utf-8").replace("- [x] **Scope khoá**",
                                                                     "- [ ] **Scope khoá**")
        (proj / "STATE.md").write_text(st, encoding="utf-8")
        r = hook("guard_ask.py", proj, {"tool_name": "AskUserQuestion"})
        check(r.returncode == 0, "cho qua ở pha S khi chưa khoá scope", f"exit={r.returncode}")
        set_phase(proj, "E")
        r = hook("guard_ask.py", proj, {"tool_name": "AskUserQuestion"})
        check(r.returncode == 2, "chặn ở pha E", f"exit={r.returncode}")
        set_phase(proj, "S")
        tick_scope_locked(proj)

        print("\n[5] hook guard_readonly")
        r = hook("guard_readonly.py", proj, {"tool_name": "Write",
                                             "tool_input": {"file_path": str(viper / "context/PRD.md")}})
        check(r.returncode == 2, "chặn Write vào repo VIPER", f"exit={r.returncode}")
        r = hook("guard_readonly.py", proj, {"tool_name": "Write",
                                             "tool_input": {"file_path": str(proj / "context/BUGS.md")}})
        check(r.returncode == 0, "cho qua Write trong repo SPEC")
        r = hook("guard_readonly.py", proj, {"tool_name": "Bash",
                                             "tool_input": {"command": f"rm -rf {viper}/context"}})
        check(r.returncode == 2, "chặn Bash xoá trong repo VIPER")
        r = hook("guard_readonly.py", proj, {"tool_name": "Bash",
                                             "tool_input": {"command": f"cat {viper}/context/PRD.md"}})
        check(r.returncode == 0, "cho qua Bash đọc repo VIPER")
        r = hook("guard_readonly.py", proj, {
            "tool_name": "Bash",
            "tool_input": {"command": f"cp -r {viper}/context intake/releases/r1/viper/"}})
        check(r.returncode == 0, "cho qua cp mirror (VIPER là NGUỒN, đích là SPEC)")

        print("\n[6] hook guard_frozen")
        plan_p = str(proj / "context/releases/r1/TEST-PLAN.md")
        r = hook("guard_frozen.py", proj, {"tool_name": "Edit", "tool_input": {"file_path": plan_p}})
        check(r.returncode == 0, "cho sửa TEST-PLAN ở pha S")
        set_phase(proj, "E")
        r = hook("guard_frozen.py", proj, {"tool_name": "Edit", "tool_input": {"file_path": plan_p}})
        check(r.returncode == 2, "chặn sửa TEST-PLAN ở pha E", f"exit={r.returncode}")
        r = hook("guard_frozen.py", proj, {
            "tool_name": "Edit",
            "tool_input": {"file_path": str(proj / "context/TEST-STRATEGY.md")}})
        check(r.returncode == 2, "chặn sửa TEST-STRATEGY ở pha E")
        r = hook("guard_frozen.py", proj, {"tool_name": "Edit",
                                           "tool_input": {"file_path": str(proj / "context/BUGS.md")}})
        check(r.returncode == 0, "không soi file khác")
        r = hook("guard_frozen.py", proj, {"tool_name": "Bash",
                 "tool_input": {"command": f"sed -i '' 's/90/50/' {plan_p}"}})
        check(r.returncode == 2, "chặn Bash sed -i vào TEST-PLAN ở pha E", f"exit={r.returncode}")
        r = hook("guard_frozen.py", proj, {"tool_name": "Bash",
                 "tool_input": {"command": f"echo x >> {proj / 'context/TEST-STRATEGY.md'}"}})
        check(r.returncode == 2, "chặn Bash append vào TEST-STRATEGY ở pha E")
        r = hook("guard_frozen.py", proj, {"tool_name": "Bash",
                 "tool_input": {"command": f"cat {plan_p} | grep 'Ngưỡng'"}})
        check(r.returncode == 0, "cho qua Bash đọc thuần TEST-PLAN")

        print("\n[6b] hook guard_evidence — ảnh/video phải rơi vào evidence/")
        SHOT = "mcp__browser__browser_take_screenshot"
        SAVE = "mcp__mobile__mobile_save_screenshot"
        REC = "mcp__mobile__mobile_start_screen_recording"
        CODE = "mcp__browser__browser_run_code_unsafe"
        for label, payload, want in (
            ("chặn filename tuyệt đối ra /tmp",
             {"tool_name": SHOT, "tool_input": {"filename": "/tmp/x.png"}}, 2),
            ("chặn filename leo `..` ra khỏi output-dir",
             {"tool_name": SHOT, "tool_input": {"filename": "../../../../tmp/x.png"}}, 2),
            ("chặn ảnh ghi vào root repo (ngoài evidence/)",
             {"tool_name": SHOT, "tool_input": {"filename": str(proj / "shot.png")}}, 2),
            ("chặn mobile saveTo ra ngoài repo",
             {"tool_name": SAVE, "tool_input": {"device": "i", "saveTo": "/tmp/a.png"}}, 2),
            ("chặn quay màn hình THIẾU `output` (mobile-mcp ghi vào thư mục tạm)",
             {"tool_name": REC, "tool_input": {"device": "i"}}, 2),
            ("chặn page.screenshot({path}) ra ngoài trong run_code_unsafe",
             {"tool_name": CODE, "tool_input": {"code": "await page.screenshot({ path: '/tmp/y.png' })"}}, 2),
            ("chặn Bash chép ảnh ra ngoài repo",
             {"tool_name": "Bash", "tool_input": {"command": "cp evidence/r1/a.png /tmp/leak.png"}}, 2),
            ("cho qua filename tương đối trần",
             {"tool_name": SHOT, "tool_input": {"filename": "01-buoc1.png"}}, 0),
            ("cho qua khi không khai filename (dùng --output-dir)",
             {"tool_name": SHOT, "tool_input": {"scale": "css"}}, 0),
            ("cho qua saveTo tuyệt đối TRONG evidence/",
             {"tool_name": SAVE, "tool_input": {"device": "i",
                                                "saveTo": str(proj / "evidence/_inbox/mobile/a.png")}}, 0),
            ("cho qua recording có `output` trong evidence/",
             {"tool_name": REC, "tool_input": {"device": "i",
                                               "output": "evidence/_inbox/mobile/v.mp4"}}, 0),
            ("cho qua Bash chép ảnh TRONG evidence/",
             {"tool_name": "Bash",
              "tool_input": {"command": "cp evidence/_inbox/flow/01.png evidence/r1/luot-1/TC-1/01.png"}}, 0),
            ("cho qua Bash đọc thuần",
             {"tool_name": "Bash", "tool_input": {"command": "ls -la evidence/r1/"}}, 0),
        ):
            r = hook("guard_evidence.py", proj, payload)
            check(r.returncode == want, label, f"exit={r.returncode}, mong đợi {want}")

        print("\n[6c] mọi --output-dir khai sẵn đều trỏ vào evidence/")
        bad_out = []
        for f in sorted((proj / ".claude/agents").glob("*.md")) + [proj / ".mcp.json"]:
            for m in re.finditer(r'--output-dir"?\s*,?\s*"([^"]+)"', f.read_text(encoding="utf-8")):
                if not m.group(1).startswith("evidence/"):
                    bad_out.append(f"{f.name}: {m.group(1)}")
        check(not bad_out, "--output-dir của .mcp.json + mọi agent nằm trong evidence/", str(bad_out))

        print("\n[7] pha P")
        set_phase(proj, "P")
        fill_prepare(proj)
        fails = gate_fails(proj, "P")
        check(not fails, "gate P xanh sau khi bootstrap môi trường + viết TC", "; ".join(fails[:4]))
        env_p = proj / "context/ENVIRONMENT.md"
        env_full = env_p.read_text(encoding="utf-8")
        env_p.write_text("\n".join(l for l in env_full.splitlines()
                                   if not l.startswith("| notify-worker")), encoding="utf-8")
        fails = gate_fails(proj, "P")
        check(any("notify-worker" in f for f in fails),
              "gate P đỏ khi ENVIRONMENT thiếu một microservice trong phạm vi", "; ".join(fails[:3]))
        env_p.write_text(env_full, encoding="utf-8")
        check(not gate_fails(proj, "P"), "gate P xanh lại khi ENVIRONMENT đủ target")

        print("\n[7b] out-of-scope so theo TÊN loại khai tường minh, không substring")
        stg_p = proj / "context/TEST-STRATEGY.md"
        stg_orig = stg_p.read_text(encoding="utf-8")
        stg_p.write_text(stg_orig.replace("| app | ✓ | — | ✓ | — | ✓ |",
                                          "| app | ✓ | ✓ | ✓ | — | ✓ |"), encoding="utf-8")
        check(not gate_fails(proj, "P"),
              "tick thêm `workflow` nhưng tên ĐÃ khai ở §3 → gate P vẫn xanh")
        tp_p = proj / "context/releases/r1/TEST-PLAN.md"
        tp_orig = tp_p.read_text(encoding="utf-8")
        tp_p.write_text(tp_orig.replace(
            "- workflow, tương-thích-ngược,",
            "- đường /workflow/export chưa kiểm — tương-thích-ngược,"), encoding="utf-8")
        fails = gate_fails(proj, "P")
        check(any("workflow" in f for f in fails),
              "nhắc 'workflow' trong văn xuôi/URL KHÔNG tính là khai out-of-scope",
              "; ".join(fails[:3]))
        tp_p.write_text(tp_orig, encoding="utf-8")
        stg_p.write_text(stg_orig, encoding="utf-8")
        check(not gate_fails(proj, "P"), "khôi phục → gate P xanh lại")

        print("\n[7c] ô ✗ ma trận đối chiếu TỪNG Ô, không đếm tổng")
        tc_file = proj / "context/testcases/CAP-BOOK-01.md"
        tc_orig = tc_file.read_text(encoding="utf-8")
        tc_file.write_text(tc_orig.replace(
            " · Ô ma trận: Tạo lịch hẹn × chưa đăng nhập = ✗", ""), encoding="utf-8")
        fails = gate_fails(proj, "P")
        check(any("chưa đăng nhập" in f for f in fails),
              "mất nhãn một ô → gate P nêu đích danh ô thiếu", "; ".join(fails[:3]))
        tc_file.write_text(tc_orig, encoding="utf-8")
        check(not gate_fails(proj, "P"), "khôi phục nhãn ô → gate P xanh lại")

        print("\n[8] pha E — lượt 1 (có FAIL)")
        set_phase(proj, "E")
        report_p = str(proj / "context/releases/r1/REPORT.md")
        r = hook("guard_verdict.py", proj, {"tool_name": "Write", "tool_input": {"file_path": report_p}})
        check(r.returncode == 2, "guard_verdict chặn ghi REPORT khi chưa chạy test", f"exit={r.returncode}")
        r = hook("guard_verdict.py", proj, {"tool_name": "Bash",
                 "tool_input": {"command": f"echo 'Verdict: PASS' >> {report_p}"}})
        check(r.returncode == 2, "guard_verdict chặn cả Bash append REPORT khi chưa chạy test")
        fill_execute_fail(proj)
        fails = gate_fails(proj, "E")
        check(not fails, "gate E xanh sau lượt 1", "; ".join(fails[:4]))
        r = hook("guard_verdict.py", proj, {"tool_name": "Write", "tool_input": {"file_path": report_p}})
        check(r.returncode == 0, "guard_verdict cho qua khi gate E xanh")
        r = hook("guard_verdict.py", proj, {"tool_name": "Bash",
                 "tool_input": {"command": f"echo x >> {report_p}"}})
        check(r.returncode == 0, "guard_verdict cho qua Bash khi gate E xanh")

        print("\n[9] pha C — verdict FAIL")
        set_phase(proj, "C")
        write_report(proj, 1, "FAIL")
        rc = gate(proj, "C")
        out = rc.stdout
        check("verdict máy tính (`FAIL`)" in out,
              "gate C tính đúng verdict FAIL (S2 mở không cam kết + dưới ngưỡng tổng "
              "→ không lọt PASS-có-điều-kiện)", out[-300:])
        check(rc.returncode == 0,
              "gate C xanh toàn phần ở lượt 1 (kể cả REPORT đủ mục + Tổng hợp BUGS)",
              "; ".join(l for l in out.splitlines() if l.strip().startswith("✗")))
        r = run([sys.executable, "scripts/release.py", "--go"], proj)
        check(r.returncode == 1, "release.py --go TỪ CHỐI khi verdict FAIL")

        print("\n[10] bàn giao lại — release.py --retest")
        tp_p = proj / "context/releases/r1/TEST-PLAN.md"
        tp_orig = tp_p.read_text(encoding="utf-8")
        tp_p.write_text(tp_orig.replace("Lượt bàn giao tối đa: 3",
                                        "Lượt bàn giao tối đa: 1"), encoding="utf-8")
        r = run([sys.executable, "scripts/release.py", "--retest"], proj)
        check(r.returncode == 1 and "VƯỢT TRẦN" in r.stdout,
              "--retest từ chối MỞ lượt vượt trần (escalate QC, không rơi vào ngõ cụt)",
              r.stdout[-300:])
        tp_p.write_text(tp_orig, encoding="utf-8")
        r = run([sys.executable, "scripts/release.py", "--retest"], proj)
        check(r.returncode == 1, "--retest từ chối khi thiếu manifest RELEASE-2.md")
        write_manifest(proj, viper, 2, urls=MULTI_URLS,
                       fixed="BUG-r1-001: thêm kiểm quyền ở server, đã deploy")
        r = run([sys.executable, "scripts/release.py", "--retest"], proj)
        check(r.returncode == 0, "--retest chạy khi có manifest", r.stdout[-300:] + r.stderr[-200:])
        st = (proj / "STATE.md").read_text(encoding="utf-8")
        check("Lần bàn giao  : 2" in st or re.search(r"Lần bàn giao\s*:\s*2", st) is not None,
              "STATE: lượt bàn giao = 2")
        check(re.search(r"Bàn giao mở\s*:\s*\d{4}-\d{2}-\d{2}", st) is not None,
              "STATE: có dòng Bàn giao mở")
        check(re.search(r"Pha hiện tại\s*:\s*E", st) is not None, "STATE: pha về E")
        check("- [x] **Scope khoá**" in st, "STATE: giữ tick gate S/P")
        rl = (proj / "context/releases/r1/RUNLOG.md").read_text(encoding="utf-8")
        check("## Lượt chạy — bàn giao 2" in rl, "RUNLOG: có mục lượt 2")
        check("### Phạm vi retest" in rl and "TC-BOOK-01-002" in rl.split("bàn giao 2")[1],
              "RUNLOG: phạm vi retest sinh từ BUGS")
        dec = (proj / "context/DECISIONS.md").read_text(encoding="utf-8")
        check("(release 1 — bàn giao 2)" in dec, "DECISIONS: có mốc bàn giao 2")

        print("\n[11] gate E lượt 2 + verdict PASS")
        fails = gate_fails(proj, "E")
        check(any("TC-BOOK-01-002" in f for f in fails),
              "gate E lượt 2 fail-closed khi chưa chạy retest", "; ".join(fails[:3]))
        fill_retest_pass(proj)
        fails = gate_fails(proj, "E")
        check(not fails, "gate E xanh sau retest", "; ".join(fails[:4]))
        set_phase(proj, "C")
        write_report(proj, 2, "PASS")
        rc = gate(proj, "C")
        out = rc.stdout
        check("`PASS`" in out, "gate C tính verdict PASS ở lượt 2", out[-200:])
        check(rc.returncode == 0, "gate C xanh toàn phần ở lượt 2",
              "; ".join(l for l in out.splitlines() if l.strip().startswith("✗")))

        print("\n[11b] verdict không bị lừa bởi AC tiền tố (AC-1 vs AC-10)")
        tc_file = proj / "context/testcases/CAP-BOOK-01.md"
        tc_orig = tc_file.read_text(encoding="utf-8")
        tc_file.write_text(tc_orig.replace("AC: AC-1 (l2)", "AC: AC-10 (l2)"),
                           encoding="utf-8")
        check(compute_verdict_of(proj) == "FAIL",
              "AC-1 không TC nào phủ (mọi TC gắn AC-10) → verdict FAIL",
              compute_verdict_of(proj))
        tc_file.write_text(tc_orig, encoding="utf-8")
        check(compute_verdict_of(proj) == "PASS", "khôi phục meta AC → verdict PASS lại")

        print("\n[11c] PASS-có-điều-kiện không phải cửa thoát ngưỡng tổng TC PASS")
        rl_p = proj / "context/releases/r1/RUNLOG.md"
        rl_orig = rl_p.read_text(encoding="utf-8")
        rl_p.write_text(rl_orig
            + f"| {TODAY} | 1 | TC-BOOK-01-003 | spec-tester-edge | BLOCKED |  |  |\n"
            + f"| {TODAY} | 1 | TC-BOOK-01-004 | spec-tester-authz | BLOCKED |  |  |\n",
            encoding="utf-8")
        check(compute_verdict_of(proj) == "FAIL",
              "50% TC PASS (< ngưỡng 90%), 0 S1/S2 mở → FAIL chứ không PASS-có-điều-kiện",
              compute_verdict_of(proj))
        rl_p.write_text(rl_orig, encoding="utf-8")

        print("\n[11d] bug mở của release trước vẫn được release sau đếm")
        b_p = proj / "context/BUGS.md"
        b_orig = b_p.read_text(encoding="utf-8")
        b_p.write_text(b_orig.replace("| Trạng thái | đóng (retest PASS lượt 2",
                                      "| Trạng thái | mở (thí nghiệm"), encoding="utf-8")
        r = run([sys.executable, "-c",
                 "import sys; sys.path.insert(0, 'scripts'); import _counts as C; "
                 "print(C.open_bugs_by_sev(2)['S2'])"], proj)
        check(r.stdout.strip() == "1",
              "open_bugs_by_sev(release 2) đếm S2 còn mở của r1", r.stdout.strip())
        b_p.write_text(b_orig, encoding="utf-8")

        print("\n[12] release.py --go")
        r = run([sys.executable, "scripts/release.py", "--go"], proj)
        check(r.returncode == 1, "--go TỪ CHỐI khi working tree bẩn (chưa commit)")
        run(["git", "add", "-A"], proj)
        run(["git", "commit", "-q", "-m", "certify release 1 — PASS"], proj)
        r = run([sys.executable, "scripts/release.py", "--go"], proj)
        check(r.returncode == 0, "--go chạy khi verdict PASS + QC ký", r.stdout[-300:] + r.stderr[-200:])
        check((proj / "context/archive/release-1/TEST-STRATEGY.md").is_file(),
              "archive snapshot release-1")
        check((proj / "context/archive/release-1/testcases").is_dir(), "archive cả testcases/")
        check((proj / "context/releases/r2/TEST-PLAN.md").is_file(), "scaffold releases/r2/")
        check((proj / "intake/releases/r2").is_dir(), "tạo intake/releases/r2/ (rỗng)")
        st = (proj / "STATE.md").read_text(encoding="utf-8")
        check(re.search(r"Release\s*:\s*2", st) is not None, "STATE: release = 2")
        check(re.search(r"Release mở\s*:\s*\d{4}-\d{2}-\d{2}", st) is not None, "STATE: có Release mở")
        check(re.search(r"Lần bàn giao\s*:\s*1", st) is not None, "STATE: lượt về 1")
        check(re.search(r"^Bàn giao mở\s*:", st, re.MULTILINE) is None,
              "STATE: xoá dòng Bàn giao mở")
        check(re.search(r"Pha hiện tại\s*:\s*S", st) is not None, "STATE: pha về S")
        check("- [x]" not in st.split("## Gate")[1].split("## Challenge")[0],
              "STATE: bỏ tick toàn bộ §Gate")
        env = (proj / "context/ENVIRONMENT.md").read_text(encoding="utf-8")
        check("- [ ] (mỗi release)" in env, "ENVIRONMENT: re-arm mục (mỗi release)")
        dec = (proj / "context/DECISIONS.md").read_text(encoding="utf-8")
        check("(release 2)" in dec, "DECISIONS: có mốc release 2")
        check((proj / "context/testcases/CAP-BOOK-01.md").is_file(), "testcases sống KHÔNG bị xoá")
        check("BUG-r1-001" in (proj / "context/BUGS.md").read_text(encoding="utf-8"),
              "BUGS giữ nguyên (append-only)")

        print("\n[13] release 2 — đếm theo release (fail-closed)")
        fails = gate_fails(proj, "S")
        check(any("Manifest" in f for f in fails), "gate S release 2 đỏ vì chưa có manifest r2")
        check(any("quyết định" in f.lower() for f in fails),
              "gate S release 2 đòi ≥2 DECISIONS dưới mốc mới", "; ".join(fails[:3]))
        check(any("Challenge" in f for f in fails),
              "gate S release 2 đòi challenge mới (ngày ≥ Release mở)")

        print("\n[14] compact + reanchor")
        r = run([sys.executable, "scripts/compact.py"], proj)
        check(r.returncode == 0 and "DÒNG NEO" in r.stdout, "compact.py chạy, in phần dòng neo")
        r = run([sys.executable, "scripts/reanchor.py"], proj,
                stdin=json.dumps({"source": "compact", "session_id": "test"}))
        ok = r.returncode == 0 and "additionalContext" in r.stdout
        check(ok, "reanchor.py trả JSON hookSpecificOutput", r.stderr[-200:])
        if ok:
            ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
            check("TÁM LUẬT" in ctx, "reanchor nhồi 8 luật đọc từ CLAUDE.md")

        print("\n[15] frontmatter agent + settings")
        agents = sorted((proj / ".claude/agents").glob("spec-tester-*.md"))
        check(len(agents) >= 12, f"đủ roster tester ({len(agents)} agent)")
        bad = [a.name for a in agents
               if not re.match(r"^---\nname: spec-tester-",
                               a.read_text(encoding="utf-8"))]
        check(not bad, "mọi agent tester có frontmatter name đúng", str(bad))
        no_guard = [a.name for a in agents
                    if "disallowedTools" not in a.read_text(encoding="utf-8")]
        check(not no_guard, "mọi agent tester bị chặn Write/Edit", str(no_guard))
        settings = json.loads((proj / ".claude/settings.json").read_text(encoding="utf-8"))
        hooks = settings["hooks"]["PreToolUse"]
        names = {h["args"][0].rsplit("/", 1)[-1] for e in hooks for h in e["hooks"]}
        check({"guard_ask.py", "guard_readonly.py", "guard_frozen.py",
               "guard_verdict.py", "guard_evidence.py"} <= names,
              "settings.json nối đủ 5 hook", str(names))
        bash_names = {h["args"][0].rsplit("/", 1)[-1]
                      for e in hooks if e.get("matcher") == "Bash" for h in e["hooks"]}
        check({"guard_readonly.py", "guard_frozen.py", "guard_verdict.py",
               "guard_evidence.py"} <= bash_names,
              "matcher Bash nối đủ 4 guard", str(bash_names))
        mcp_matchers = [e for e in hooks if e.get("matcher", "").startswith("mcp__")]
        mcp_covered = " ".join(e["matcher"] for e in mcp_matchers)
        check(all(t in mcp_covered for t in
                  ("browser_take_screenshot", "mobile_save_screenshot",
                   "mobile_start_screen_recording", "browser_run_code_unsafe")),
              "matcher MCP phủ đủ 4 tool ghi file", mcp_covered or "(không có matcher mcp__)")
        check("Bash" in settings["permissions"]["allow"], "Bash trần trong allow")
        check(any("psql" in x for x in settings["permissions"]["ask"]),
              "lệnh chạm DB nằm ở lớp ask")

        print("\n[16] .gitignore")
        gi = (proj / ".gitignore").read_text(encoding="utf-8")
        check(".env" in gi and "!environment/.env.example" in gi,
              ".gitignore chặn .env, chừa .env.example")
        check("evidence/_inbox/" in gi, ".gitignore chặn evidence/_inbox")

        scenario_tong_quat(tmp)

    finally:
        print("\n" + "=" * 60)
        print(f"  {len(PASSED)} ✓ · {len(FAILED)} ✗")
        for f in FAILED:
            print(f"  ✗ {f}")
        if keep:
            print(f"\nGiữ lại: {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
