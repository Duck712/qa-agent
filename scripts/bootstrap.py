#!/usr/bin/env python3
"""bootstrap.py — tạo một dự án SPEC mới từ template này.

COPY template ra thư mục mới (template giữ nguyên, dùng lại cho sản phẩm sau),
thay placeholder, git init + first commit.

Usage:
    python3 scripts/bootstrap.py <project-code> [--target PATH] [--name "Tên sản phẩm"]
                                 [--authority "Tên QC <email>"] [--source PATH] [--dry-run]

Ví dụ:
    python3 scripts/bootstrap.py shop-spec --name "Shop — kiểm thử" \\
        --authority "Nguyễn Văn A <qc@example.com>" --source ../shop

<project-code>: chữ thường + số + gạch nối. Mặc định --target là ../<project-code>
--source: đường dẫn repo nguồn (repo code hoặc thư mục tài liệu bàn giao) — chỉ để ghi
          gợi ý vào README của dự án mới; manifest thật vẫn do QC thả vào
          intake/releases/r1/ (dòng `Repo nguồn:`). `--viper` là tên cũ, vẫn nhận.

Dùng cho MỌI dự án: sản phẩm làm bằng VIPER hay quy trình khác đều được — manifest khai
`Quy trình dev:` và SPEC tự chọn chế độ đối chiếu (SPEC.md §1.3).

Windows: dùng `python scripts\\bootstrap.py`.

Exit codes: 0 ok · 1 lỗi tham số · 2 target đã tồn tại · 3 verify thất bại
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
UNFILLED = "_CHƯA ĐIỀN_"

TEXT_SUFFIXES = {".md", ".py", ".sh", ".json", ".yaml", ".yml", ".txt", ".toml"}
TEXT_NAMES = {".gitignore", ".env.example", "Makefile"}
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv",
             # vết chạy của chính template
             ".spec", ".playwright-mcp"}
SKIP_FILES = {".DS_Store", "Thumbs.db"}
# Không copy sang dự án: dự án không sinh dự án khác, không tự kiểm template,
# và nhận một README của riêng nó.
TEMPLATE_ONLY = {"scripts/bootstrap.py", "scripts/selftest.py", "README.md"}

REQUIRED = [
    "SPEC.md", "CLAUDE.md", "STATE.md", "Makefile", ".mcp.json",
    "context/TEST-STRATEGY.md", "context/HANDOVER.md", "context/COVERAGE-MAP.md",
    "context/PERSONAS.md", "context/ARCHITECTURE.md", "context/ENVIRONMENT.md",
    "context/DECISIONS.md", "context/BUGS.md", "context/API-SURFACE.md",
    "context/testcases/_TC-TEMPLATE.md",
    "context/releases/r1/TEST-PLAN.md", "context/releases/r1/RUNLOG.md",
    "context/releases/r1/REPORT.md",
    "context/shared/CONVENTIONS.md", "context/shared/SAFETY.md",
    "intake/README.md", "intake/_RELEASE-TEMPLATE.md",
    "environment/README.md", "environment/.env.example",
    "scripts/_counts.py", "scripts/gate.py", "scripts/release.py",
    "scripts/guard_ask.py", "scripts/guard_readonly.py", "scripts/guard_frozen.py",
    "scripts/guard_verdict.py", "scripts/guard_evidence.py",
    "scripts/reanchor.py", "scripts/compact.py",
    ".claude/settings.json",
    ".claude/commands/spec-scope.md", ".claude/commands/spec-prepare.md",
    ".claude/commands/spec-execute.md", ".claude/commands/spec-certify.md",
    ".claude/commands/spec-retest.md",
    ".claude/agents/_TESTER-TEMPLATE.md", ".claude/agents/spec-evidence-auditor.md",
    ".claude/skills/spec/SKILL.md", ".claude/skills/spec-browse/SKILL.md",
    ".claude/skills/spec-mobile/SKILL.md",
    ".claude/skills/spec-testcase-design/SKILL.md", ".claude/skills/spec-evidence/SKILL.md",
    ".claude/skills/spec-knowledge/SKILL.md", ".claude/agents/spec-tester-security.md",
    "context/LESSONS.md", "scripts/review_tc.py",
]

PROJECT_README = """# {name} — kiểm thử độc lập (SPEC v1.0)

Repo này kiểm thử độc lập một sản phẩm — do bất kỳ đội/quy trình dev nào làm ra. Authority = **QC**.
Quy trình đầy đủ: [SPEC.md](SPEC.md) · Trạng thái: [STATE.md](STATE.md)

## Bắt đầu một release

1. **QC thả manifest** vào `intake/releases/r1/RELEASE.md` — theo
   [intake/_RELEASE-TEMPLATE.md](intake/_RELEASE-TEMPLATE.md). Khai: quy trình dev
   (VIPER hay khác), repo nguồn (repo code hoặc thư mục tài liệu bàn giao — chỉ đọc),
   phạm vi, bản deploy, môi trường test (production cách ly hoặc staging), URL từng target,
   lần bàn giao.{source_hint}
2. Mở Claude Code trong thư mục này rồi chạy:

```
/spec-scope       # dịch tài liệu bàn giao, TEST-STRATEGY (release 1), TEST-PLAN + ngưỡng, QC chốt
/spec-prepare     # bootstrap môi trường test + viết test case + dry-run
/spec-execute     # chạy test độc lập theo đợt, bằng chứng bắt buộc
/spec-certify     # verdict theo ngưỡng đã ghi trước, QC ký
```

Verdict FAIL → dev fix → QC thả `RELEASE-2.md` → `/spec-retest` (cùng release, ngưỡng không đổi).
Verdict PASS → `python3 scripts/release.py --go` mở release kế tiếp.

## Lệnh hay dùng

```bash
python3 scripts/gate.py         # gate của pha hiện tại — thiếu gì
python3 scripts/review_tc.py    # pha P: máy soát bộ TC (normal/abnormal mỗi AC, meta, bằng chứng)
make doctor                     # môi trường test còn sống không
python3 scripts/release.py      # xem trước điều kiện đóng release / mở lượt retest
```

## Yêu cầu

| Cần | Để làm gì |
|---|---|
| Python 3.9+ · git | `gate.py`, `release.py`, hook — thư viện chuẩn |
| Node.js 18+ | Playwright MCP (`spec-browse`) và mobile-mcp (`spec-mobile`) — tải khi chạy lần đầu |
| Xcode / Android SDK | Chỉ khi sản phẩm có experience mobile |
| Quyền truy cập môi trường test + tài khoản/tenant test | Production cách ly hoặc staging — theo `Môi trường:` của manifest ([context/shared/SAFETY.md](context/shared/SAFETY.md)) |
"""


def is_text(p: Path) -> bool:
    return p.suffix in TEXT_SUFFIXES or p.name in TEXT_NAMES


def substitute(text: str, subs: dict[str, str]) -> str:
    for k, v in subs.items():
        text = text.replace(k, v)
    return text


def copy_tree(src: Path, dst: Path, subs: dict[str, str], dry: bool) -> int:
    count = 0
    for item in sorted(src.rglob("*")):
        rel = item.relative_to(src)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if item.name in SKIP_FILES:
            continue
        if str(rel).replace("\\", "/") in TEMPLATE_ONLY:
            continue
        target = dst / rel
        if item.is_dir():
            if not dry:
                target.mkdir(parents=True, exist_ok=True)
            continue
        if not dry:
            target.parent.mkdir(parents=True, exist_ok=True)
            if is_text(item):
                try:
                    text = item.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    shutil.copy2(item, target)
                    count += 1
                    continue
                target.write_text(substitute(text, subs), encoding="utf-8")
            else:
                shutil.copy2(item, target)
        count += 1
    return count


def fix_windows_python(dst: Path) -> None:
    """Windows không có lệnh `python3` — hook trong settings.json phải đổi."""
    if sys.platform != "win32":
        return
    p = dst / ".claude" / "settings.json"
    if p.is_file():
        p.write_text(p.read_text(encoding="utf-8").replace('"python3"', '"python"'),
                     encoding="utf-8")


def verify(dst: Path) -> list[str]:
    missing = [rel for rel in REQUIRED if not (dst / rel).is_file()]
    leftovers = []
    for rel in ("SPEC.md", "CLAUDE.md", "STATE.md", "Makefile"):
        p = dst / rel
        if p.is_file() and re.search(r"\{\{[A-Z_-]+\}\}", p.read_text(encoding="utf-8")):
            leftovers.append(rel)
    errs = []
    if missing:
        errs.append(f"thiếu file: {missing}")
    if leftovers:
        errs.append(f"còn placeholder chưa thay: {leftovers}")
    return errs


def git_init(dst: Path, name: str) -> None:
    try:
        subprocess.run(["git", "init", "-q"], cwd=dst, check=True, timeout=60)
        subprocess.run(["git", "add", "-A"], cwd=dst, check=True, timeout=60)
        subprocess.run(["git", "commit", "-q", "-m",
                        f"khởi tạo repo kiểm thử SPEC cho {name}"],
                       cwd=dst, check=True, timeout=60)
    except Exception as e:
        print(f"  (git init/commit bỏ qua: {e})")


def main() -> int:
    ap = argparse.ArgumentParser(description="Tạo dự án SPEC mới từ template")
    ap.add_argument("project_code")
    ap.add_argument("--target")
    ap.add_argument("--name")
    ap.add_argument("--authority", default="")
    ap.add_argument("--source", default="")
    ap.add_argument("--viper", default="", help="tên cũ của --source")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", a.project_code):
        print("✗ project-code chỉ gồm chữ thường, số, gạch nối")
        return 1

    dst = Path(a.target).resolve() if a.target else (SRC.parent / a.project_code).resolve()
    if dst.exists() and any(dst.iterdir()):
        print(f"✗ {dst} đã tồn tại và không rỗng")
        return 2

    name = a.name or a.project_code
    m = re.match(r"^(.*?)\s*<([^>]+)>$", a.authority.strip()) if a.authority else None
    subs = {
        "{{PROJECT_NAME}}": name,
        "{{PROJECT-CODE}}": a.project_code,
        "{{AUTHORITY_NAME}}": (m.group(1) if m else a.authority) or "QC",
        "{{AUTHORITY_EMAIL}}": (m.group(2) if m else "") or "",
        "{{DATE}}": date.today().isoformat(),
    }

    print(f"{'[dry-run] ' if a.dry_run else ''}Tạo dự án SPEC: {name}")
    print(f"  nguồn : {SRC}")
    print(f"  đích  : {dst}")
    n = copy_tree(SRC, dst, subs, a.dry_run)
    print(f"  {'sẽ copy' if a.dry_run else 'đã copy'} {n} file "
          f"(bỏ qua template-only: {sorted(TEMPLATE_ONLY)})")

    if a.dry_run:
        print("\n[dry-run] không ghi gì.")
        return 0

    # Thư mục rỗng git không giữ, nhưng dự án cần chúng tồn tại ngay: chỗ QC thả manifest,
    # chỗ pha P viết seed, chỗ pha E đổ bằng chứng.
    for d, note in (
        ("intake/releases/r1", "QC thả RELEASE.md vào đây — xem intake/_RELEASE-TEMPLATE.md\n"),
        ("environment/local", "Pha P viết seed script + plan-B1.yaml + .env (không commit) vào đây.\n"),
        ("evidence", "Bằng chứng: _inbox/<vai>/ (thô) · r<N>/luot-<k>/<TC-ID>/ (đã phân loại).\n"),
        ("context/archive/ledger", "Nơi gấp sổ đã hết hiệu lực — xem /spec-compact.\n"),
    ):
        p = dst / d
        p.mkdir(parents=True, exist_ok=True)
        (p / ".gitkeep").write_text(f"# {note}", encoding="utf-8")

    hint = ""
    source = a.source or a.viper
    if source:
        hint = (f"\n   Repo nguồn của sản phẩm này (gợi ý lúc khởi tạo): `{source}` — "
                "manifest vẫn phải khai lại dòng `Repo nguồn:`.")
    (dst / "README.md").write_text(PROJECT_README.format(name=name, source_hint=hint),
                                   encoding="utf-8")
    fix_windows_python(dst)

    errs = verify(dst)
    if errs:
        print("\n✗ verify thất bại:")
        for e in errs:
            print(f"  - {e}")
        return 3
    print("  ✓ verify: đủ file, hết placeholder")

    git_init(dst, name)
    print(f"""
Xong. Tiếp theo:

  cd {dst}
  # QC thả manifest vào intake/releases/r1/RELEASE.md (xem intake/_RELEASE-TEMPLATE.md)
  claude
  /spec-scope
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
