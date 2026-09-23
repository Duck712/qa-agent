#!/usr/bin/env python3
"""guard_evidence.py — hook PreToolUse: ảnh/video chụp được PHẢI rơi vào qa/evidence/.

Vì sao: `--output-dir` của MCP chỉ là mặc định — từng lời gọi vẫn khai được `filename`/`saveTo`/`output`
trỏ ra /tmp hay Desktop, và `mobile_start_screen_recording` không khai `output` thì ghi vào thư mục tạm của
hệ điều hành. Bằng chứng ngoài qa/evidence/ thì RUNLOG không trỏ được tới, và ảnh môi trường thật mang dữ
liệu thật nằm rải rác không ai dọn.

Luật: đường dẫn tương đối không được có `..`; đường dẫn tuyệt đối phải nằm dưới <dự án>/qa/evidence/.
Fail-open khi JSON hỏng / không có tham số đường dẫn. Exit 0 cho qua · 2 chặn.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _root import project_root  # noqa: E402

ROOT = project_root()
EVIDENCE = ROOT / "qa" / "evidence"
QA_DIR = ROOT / "qa"
MEDIA_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".mp4", ".mov", ".webm", ".pdf"}
PATH_ARG = {
    "mcp__browser__browser_take_screenshot": "filename",
    "mcp__mobile__mobile_save_screenshot": "saveTo",
    "mcp__mobile__mobile_start_screen_recording": "output",
}
HOW = ("Bằng chứng phải nằm trong qa/evidence/:\n"
       "  · thô, MCP tự đổ:  qa/evidence/_inbox/<vai>/…\n"
       "  · đã phân loại:    qa/evidence/<run-id>/<TC-ID>/…   ← RUNLOG trỏ vào đây\n"
       "Cách sửa: bỏ tham số đường dẫn để MCP dùng --output-dir, hoặc khai tên tương đối không có `..`\n"
       "(vd `01-buoc1.png`), hoặc đường dẫn tuyệt đối dưới qa/evidence/. Xem skill qa-evidence §1.\n")


def verdict(raw: str, allow: Path | None = None) -> tuple[bool, str]:
    """allow: thư mục được phép (mặc định qa/evidence/)."""
    raw = (raw or "").strip()
    if not raw:
        return True, ""
    p = Path(raw).expanduser()
    if not p.is_absolute():
        if ".." in p.parts:
            return False, f"đường dẫn tương đối `{raw}` có `..`"
        return True, ""
    try:
        resolved, ev = p.resolve(), (allow or EVIDENCE).resolve()
    except OSError:
        return True, ""
    if resolved == ev or ev in resolved.parents:
        return True, ""
    return False, f"`{raw}` nằm ngoài {'qa/' if allow else 'qa/evidence/'} (→ {resolved})"


def block(tool: str, why: str, extra: str = "") -> int:
    sys.stderr.write(f"CHẶN {tool} — ảnh/video đang ghi ra ngoài qa/evidence/.\nLý do: {why}\n\n{HOW}{extra}")
    return 2


def check_bash(command: str) -> tuple[bool, str]:
    for seg in re.split(r"&&|\|\||;|\|", command):
        cands = [m.group(1) for m in re.finditer(r"(?:>>?|\btee\b(?:\s+-a)?)\s*(\S+)", seg)]
        toks = seg.strip().split()
        while toks and ("=" in toks[0] or toks[0] in ("env", "command")):
            toks = toks[1:]
        if toks and toks[0] in ("cp", "mv", "rsync", "install", "ditto", "screencapture"):
            plain = [a for a in toks[1:] if not a.startswith("-")]
            if plain:
                cands.append(plain[-1])
        for c in cands:
            c = c.strip("\"'")
            if Path(c).suffix.lower() in MEDIA_EXT:
                # Bash: đích trong qa/ được (ảnh mẫu cho test upload ở qa/sandbox, qa/automation) — chỉ chặn ra ngoài dự án QA
                ok, why = verdict(c if Path(c).expanduser().is_absolute() else str((Path.cwd() / c)), QA_DIR)
                if not ok:
                    return False, why
    return True, ""


def check_code(code: str) -> tuple[bool, str]:
    for m in re.finditer(r"""\bpath\s*:\s*['"`]([^'"`$]+)['"`]""", code or ""):
        ok, why = verdict(m.group(1))
        if not ok:
            return False, why
    return True, ""


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    tool = str(payload.get("tool_name") or "")
    ti = payload.get("tool_input") or {}
    if not isinstance(ti, dict):
        return 0
    if tool in PATH_ARG:
        raw = ti.get(PATH_ARG[tool])
        if raw is None:
            if tool.endswith("start_screen_recording"):
                return block(tool, "thiếu `output` — mobile-mcp sẽ ghi vào thư mục tạm ngoài dự án",
                             "Khai `output`, vd qa/evidence/_inbox/mobile/luong.mp4 (video không commit).\n")
            return 0
        ok, why = verdict(str(raw))
        return 0 if ok else block(tool, why)
    if tool == "mcp__browser__browser_run_code_unsafe":
        ok, why = check_code(str(ti.get("code") or ""))
        return 0 if ok else block(tool, why)
    if tool == "Bash":
        ok, why = check_bash(str(ti.get("command") or ""))
        return 0 if ok else block("lệnh Bash", why)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # hook không bao giờ được làm hỏng phiên
        print(f"guard_evidence.py: {e}", file=sys.stderr)
        sys.exit(0)
