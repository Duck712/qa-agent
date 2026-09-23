#!/usr/bin/env python3
"""guard_evidence.py — hook PreToolUse: bằng chứng chụp/ghi bằng tool MCP PHẢI rơi vào qa/evidence/, và bằng chứng
đã có không bị chép ra ngoài dự án.

Vì sao: `--output-dir` của MCP chỉ là mặc định — từng lời gọi vẫn khai được `filename`/`saveTo`/`output` trỏ ra
/tmp hay Desktop; Playwright MCP tính đường dẫn TƯƠNG ĐỐI theo gốc dự án (không theo --output-dir); mobile-mcp
quay màn hình không khai `output` thì ghi vào thư mục tạm của hệ điều hành. Bằng chứng ngoài qa/evidence/ thì
RUNLOG không trỏ được tới, và ảnh môi trường thật mang dữ liệu thật nằm rải rác không ai dọn.

Luật:
  · tool MCP ghi file (browser_take_screenshot / browser_snapshot / browser_evaluate `filename`,
    browser_run_code_unsafe `path:` trong code, mobile_save_screenshot `saveTo`, mobile_start_screen_recording
    `output`): đường dẫn (tương đối tính từ gốc dự án) phải nằm dưới qa/evidence/. Không khai → cho qua (dùng
    --output-dir), trừ quay màn hình mobile (bắt buộc khai).
  · Bash: chỉ chặn khi chép/chuyển thứ ĐANG nằm trong qa/evidence/ ra ngoài qa/, hoặc lệnh chụp màn hình
    (screencapture, simctl io screenshot, adb screencap/screenrecord) ghi ra ngoài qa/. Việc bình thường của dev
    (cp ảnh vào src/assets…) không bị đụng.
Tên server khớp theo tiền tố (mcp__browser…, mcp__mobile…) để phủ cả server riêng của agent tester.
Fail-open khi JSON hỏng. Exit 0 cho qua · 2 chặn.
"""
from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _root import project_root  # noqa: E402

ROOT = project_root()
QA_DIR = ROOT / "qa"
EVIDENCE = QA_DIR / "evidence"
PATH_ARG = {  # hậu tố tên tool → tham số đường dẫn
    "__browser_take_screenshot": "filename",
    "__browser_snapshot": "filename",
    "__browser_evaluate": "filename",
    "__mobile_save_screenshot": "saveTo",
    "__mobile_start_screen_recording": "output",
}
HOW = ("Bằng chứng phải nằm trong qa/evidence/:\n"
       "  · khai đường dẫn TUYỆT ĐỐI dưới qa/evidence/<run-id>/<TC-ID>/ (cách nên dùng — không lẫn với tester khác)\n"
       "  · hoặc bỏ tham số đường dẫn để MCP dùng --output-dir (qa/evidence/_inbox/<vai>/)\n"
       "Đường dẫn tương đối được tính từ GỐC DỰ ÁN, không phải từ --output-dir. Xem skill qa-evidence §1.\n")


def resolve(raw: str, base: Path) -> Path:
    p = Path(raw).expanduser()
    return (p if p.is_absolute() else base / p).resolve()


def inside(p: Path, d: Path) -> bool:
    a, b = str(p).casefold(), str(d.resolve()).casefold()   # APFS/NTFS mặc định không phân biệt hoa thường
    return a == b or a.startswith(b.rstrip("/\\") + ("\\" if "\\" in b and "/" not in b else "/"))


def verdict(raw: str) -> tuple[bool, str]:
    raw = (raw or "").strip()
    if not raw:
        return True, ""
    try:
        p = resolve(raw, ROOT)
    except (OSError, ValueError):
        return True, ""
    if inside(p, EVIDENCE):
        return True, ""
    return False, f"`{raw}` → {p} nằm ngoài qa/evidence/"


def block(tool: str, why: str, extra: str = "") -> int:
    sys.stderr.write(f"CHẶN {tool} — bằng chứng đang ghi/chép ra ngoài qa/evidence/.\nLý do: {why}\n\n{HOW}{extra}")
    return 2


def check_bash(command: str) -> tuple[bool, str]:
    cwd = Path.cwd()
    for seg in re.split(r"&&|\|\||;|\|", command):
        seg = seg.strip().lstrip("(").rstrip(")").strip()
        try:
            toks = shlex.split(seg)
        except ValueError:
            toks = seg.split()
        while toks and ("=" in toks[0] or toks[0] in ("env", "command", "sudo")):
            toks = toks[1:]
        if not toks:
            continue
        head, args = toks[0], toks[1:]
        if head == "cd" and args:
            cwd = resolve(args[0], cwd)
            continue
        plain = [a for a in args if not a.startswith("-")]
        if head in ("cp", "mv", "rsync", "ditto", "install", "scp") and len(plain) >= 2:
            if "-t" in args and args.index("-t") + 1 < len(args):
                dest = args[args.index("-t") + 1]
                srcs = [a for a in plain if a != dest]
            else:
                dest, srcs = plain[-1], plain[:-1]
            src_ev = [s for s in srcs if inside(resolve(s, cwd), EVIDENCE)]
            remote = ":" in dest and not dest.startswith("/")
            if src_ev and (remote or not inside(resolve(dest, cwd), QA_DIR)):
                return False, f"chép bằng chứng {src_ev[0]} ra ngoài qa/ ({dest})"
        shot = head == "screencapture" or (head == "xcrun" and "screenshot" in args) or \
            (head == "adb" and any("screencap" in a or "screenrecord" in a for a in args))
        if shot:
            outs = [a for a in plain if re.search(r"\.(png|jpe?g|mp4|mov)$", a, re.I)]
            outs += [m.group(1) for m in re.finditer(r">\s*(\S+)", seg)]
            for o in outs:
                if not inside(resolve(o.strip("\"'"), cwd), QA_DIR):
                    return False, f"lệnh chụp màn hình ghi ra {o} (ngoài qa/)"
    return True, ""


def check_code(code: str) -> tuple[bool, str]:
    for m in re.finditer(r"""\bpath\s*:\s*['"`]([^'"`$]+)['"`]""", code or ""):
        ok, why = verdict(m.group(1))
        if not ok:
            return False, why
    return True, ""


def main() -> int:
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace"))
    except (json.JSONDecodeError, ValueError):
        return 0
    tool = str(payload.get("tool_name") or "")
    ti = payload.get("tool_input") or {}
    if not isinstance(ti, dict):
        return 0
    if tool.startswith(("mcp__browser", "mcp__mobile")):
        for suffix, arg in PATH_ARG.items():
            if tool.endswith(suffix):
                raw = ti.get(arg)
                if raw is None:
                    if suffix == "__mobile_start_screen_recording":
                        return block(tool, "thiếu `output` — mobile-mcp sẽ ghi vào thư mục tạm ngoài dự án",
                                     "Khai `output` tuyệt đối dưới qa/evidence/<run-id>/<TC-ID>/ (video không commit).\n")
                    return 0
                ok, why = verdict(str(raw))
                return 0 if ok else block(tool, why)
        if tool.endswith("__browser_run_code_unsafe"):
            ok, why = check_code(str(ti.get("code") or ""))
            return 0 if ok else block(tool, why)
        return 0
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
