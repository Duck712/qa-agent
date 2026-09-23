#!/usr/bin/env python3
"""guard_evidence.py — hook PreToolUse: thứ tool MCP ghi ra (ảnh, video, snapshot, log mạng/console, PDF, cookie)
PHẢI rơi vào qa/evidence/, và bằng chứng đã có không bị chép ra ngoài dự án.

Vì sao: `--output-dir` của MCP chỉ là mặc định — từng lời gọi vẫn khai được đường dẫn riêng trỏ ra /tmp hay Desktop;
Playwright MCP tính đường dẫn TƯƠNG ĐỐI theo gốc dự án (không theo --output-dir); mobile-mcp quay màn hình không khai
`output` thì ghi vào thư mục tạm của hệ điều hành. Bằng chứng ngoài qa/evidence/ thì RUNLOG không trỏ được tới, và
dữ liệu môi trường thật (ảnh, token trong log mạng, cookie) nằm rải rác không ai dọn.

Luật:
  · mọi tool mcp__browser…/mcp__mobile… có tham số đường dẫn (filename, path, saveTo, output, outputPath, file):
    đường dẫn (tương đối tính từ gốc dự án) phải nằm dưới qa/evidence/. Không khai → cho qua (dùng --output-dir),
    trừ quay màn hình mobile (bắt buộc khai). browser_run_code_unsafe: soi `path:` trong code (cả template string).
  · Bash: chặn khi chép/nén/đọc-ra thứ ĐANG nằm trong qa/evidence/ tới ngoài qa/ (cp, mv, rsync, scp, tar, zip,
    cat > …), hoặc lệnh chụp/quay màn hình của máy (screencapture, simctl io screenshot/recordVideo, adb exec-out)
    ghi ra ngoài qa/. `adb shell screencap /sdcard/…` (ghi trên thiết bị) đi qua. Việc bình thường của dev đi qua.
Tách lệnh theo ; && || | xuống dòng nằm ngoài nháy. Fail-open khi JSON hỏng. Exit 0 cho qua · 2 chặn.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _root import expand, is_redir, project_root, split_commands, tokens  # noqa: E402

ROOT = project_root()
QA_DIR = ROOT / "qa"
EVIDENCE = QA_DIR / "evidence"
PATH_KEYS = ("filename", "path", "saveTo", "output", "outputPath", "file")
HOW = ("Bằng chứng phải nằm trong qa/evidence/:\n"
       "  · khai đường dẫn TUYỆT ĐỐI dưới qa/evidence/<run-id>/<TC-ID>/ (cách nên dùng — không lẫn với tester khác)\n"
       "  · hoặc bỏ tham số đường dẫn để MCP dùng --output-dir (qa/evidence/_inbox/<vai>/)\n"
       "Đường dẫn tương đối được tính từ GỐC DỰ ÁN, không phải từ --output-dir. Xem skill qa-evidence §1.\n")


def resolve(raw: str, base: Path, env: dict | None = None) -> Path:
    p = Path(expand(raw.strip("\"'"), env or {}))
    return (p if p.is_absolute() else base / p).resolve()


def inside(p: Path, d: Path) -> bool:
    a, b = str(p).casefold(), str(d.resolve()).casefold()   # APFS/NTFS mặc định không phân biệt hoa thường
    return a == b or a.startswith(b.rstrip("/\\") + "/") or a.startswith(b.rstrip("/\\") + "\\")


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


def out_of_qa(raw: str, cwd: Path, env: dict) -> bool:
    if re.match(r"^[\w.-]+@?[\w.-]*:", raw) and not raw.startswith("/"):      # host:path (scp/rsync từ xa)
        return True
    try:
        return not inside(resolve(raw, cwd, env), QA_DIR)
    except (OSError, ValueError):
        return False


def check_bash(command: str) -> tuple[bool, str]:
    cwd, env = Path.cwd(), {}
    for seg in split_commands(command):
        toks = tokens(seg)
        redirs = [toks[i + 1] for i, t in enumerate(toks) if is_redir(t) and i + 1 < len(toks)]
        toks = [t for j, t in enumerate(toks) if not is_redir(t) and not (j > 0 and is_redir(toks[j - 1]))]
        while toks and re.match(r"^\w+=", toks[0]):
            k, v = toks[0].split("=", 1)
            env[k] = expand(v, env)
            toks = toks[1:]
        while toks and toks[0] in ("env", "command", "sudo", "time", "nohup"):
            toks = toks[1:]
        if not toks:
            continue
        head, args = Path(toks[0]).name, toks[1:]
        if head in ("cd", "pushd") and args:
            cwd = resolve(args[0], cwd, env)
            continue
        plain = [a for a in args if not a.startswith("-")]
        ev_args = [a for a in plain if inside(resolve(a, cwd, env), EVIDENCE)]
        dests: list[str] = list(redirs) if ev_args else []
        if head in ("cp", "mv", "rsync", "ditto", "install", "scp") and len(plain) >= 2:
            tdir = [args[k + 1] for k, a in enumerate(args) if a == "-t" and k + 1 < len(args)]
            dest = tdir[0] if tdir else plain[-1]
            srcs = [a for a in plain if a != dest]
            if any(inside(resolve(s, cwd, env), EVIDENCE) for s in srcs):
                dests.append(dest)
        elif head == "tar" and ev_args:
            dests += [args[k + 1] for k, a in enumerate(args) if (a == "-f" or re.fullmatch(r"-?[a-z]*f", a)) and k + 1 < len(args)]
        elif head == "zip" and ev_args and plain:
            dests.append(plain[0])
        for d in dests:
            if out_of_qa(d, cwd, env):
                return False, f"chép/nén bằng chứng ({ev_args[0] if ev_args else ''}) ra ngoài qa/ ({d})"
        shot = head == "screencapture" or (head == "xcrun" and ("screenshot" in args or "recordVideo" in args)) \
            or (head == "adb" and "shell" not in args and any("screencap" in a or "screenrecord" in a for a in args))
        if shot:
            outs = [a for a in plain if re.search(r"\.(png|jpe?g|mp4|mov|gif|webm)$", a, re.I)] + redirs
            for o in outs:
                if out_of_qa(o, cwd, env):
                    return False, f"lệnh chụp/quay màn hình ghi ra {o} (ngoài qa/)"
    return True, ""


def check_code(code: str) -> tuple[bool, str]:
    for m in re.finditer(r"""\b(?:path|filename)\s*:\s*(['"`])([^'"`]+)\1""", code or ""):
        raw = m.group(2).split("${", 1)[0]          # template string: xét phần cố định phía trước
        if not raw:
            continue
        ok, why = verdict(raw if not raw.endswith("/") else raw + "x")
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
        if tool.endswith("__browser_run_code_unsafe"):
            ok, why = check_code(str(ti.get("code") or ti.get("function") or ""))
            return 0 if ok else block(tool, why)
        for k in PATH_KEYS:
            if isinstance(ti.get(k), str):
                ok, why = verdict(ti[k])
                if not ok:
                    return block(tool, why)
        if tool.endswith("__mobile_start_screen_recording") and not ti.get("output"):
            return block(tool, "thiếu `output` — mobile-mcp sẽ ghi vào thư mục tạm ngoài dự án",
                         "Khai `output` tuyệt đối dưới qa/evidence/<run-id>/<TC-ID>/ (video không commit).\n")
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
