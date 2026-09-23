#!/usr/bin/env python3
"""guard_readonly.py — hook PreToolUse: không ghi vào các đường dẫn khai ở `qa/QA.md §Nguồn chỉ đọc`.

Dòng `- Chỉ đọc: src, docs, ../product-repo` (phân tách bằng dấu phẩy; tương đối so với thư mục dự án).
Chặn Write/Edit/MultiEdit/NotebookEdit có file_path trong đó, và lệnh Bash có dấu hiệu ghi vào đó
(redirect, tee, sed -i, rm, mv, cp/rsync với đích trong đó, git commit/checkout/reset trong đó).
Đọc thuần và cp LẤY từ đó đi qua. Người dùng nhờ ghi thật (vd viết test tự động vào repo) → họ gỡ đường dẫn
khỏi dòng `Chỉ đọc:`, hook không có ngoại lệ ngầm. Fail-open khi thiếu dữ liệu. Exit 0 cho qua · 2 chặn.
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


def protected() -> list[Path]:
    try:
        text = (ROOT / "qa" / "QA.md").read_text(encoding="utf-8")
    except OSError:
        return []
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    out = []
    for m in re.finditer(r"^[ \t]*-[ \t]*Chỉ đọc[ \t]*:[ \t]*(.+)$", text, re.M):
        for part in m.group(1).split(","):
            s = part.strip().strip("`")
            if not s:
                continue
            p = Path(s).expanduser()
            p = (p if p.is_absolute() else ROOT / p).resolve()
            if p == ROOT.resolve():      # không cho khoá cả dự án — qa/ phải ghi được
                continue
            out.append(p)
    return out


def inside(path: str, roots: list[Path], cwd: Path) -> Path | None:
    try:
        p = Path(path.strip("\"'")).expanduser()
        p = (p if p.is_absolute() else cwd / p).resolve()
    except (OSError, ValueError):
        return None
    for r in roots:
        if p == r or r in p.parents:
            return r
    return None


WRITE_CMDS = {"rm", "rmdir", "mv", "touch", "mkdir", "truncate", "chmod", "chown", "ln", "unlink"}
GIT_WRITE = {"commit", "checkout", "switch", "reset", "restore", "clean", "stash", "merge", "rebase", "pull",
             "apply", "add", "rm", "mv", "cherry-pick", "revert", "am", "push", "tag", "branch"}


def check_bash(cmd: str, roots: list[Path]) -> Path | None:
    cwd = Path.cwd()
    for seg in re.split(r"&&|\|\||;|\|", cmd):
        for m in re.finditer(r"(?:>>?|\btee\b(?:\s+-a)?)\s*(\S+)", seg):
            r = inside(m.group(1), roots, cwd)
            if r:
                return r
        try:
            toks = shlex.split(seg)
        except ValueError:
            toks = seg.split()
        while toks and ("=" in toks[0] or toks[0] in ("env", "command", "sudo")):
            toks = toks[1:]
        if not toks:
            continue
        head, args = toks[0], [a for a in toks[1:] if not a.startswith("-")]
        if head == "git":
            gdir, i, sub = cwd, 1, ""
            while i < len(toks):
                if toks[i] == "-C" and i + 1 < len(toks):
                    gdir = Path(toks[i + 1]).expanduser()
                    gdir = (gdir if gdir.is_absolute() else cwd / gdir).resolve()
                    i += 2
                    continue
                if toks[i].startswith("-"):
                    i += 1
                    continue
                sub = toks[i]
                break
            if sub in GIT_WRITE:
                r = inside(str(gdir), roots, cwd)
                if r:
                    return r
            continue
        if head == "cd" and args:
            cwd = (cwd / args[0]).resolve() if not Path(args[0]).is_absolute() else Path(args[0])
            continue
        if head in WRITE_CMDS:
            targets = args
        elif head in ("cp", "rsync", "install", "ditto") and args:
            targets = args[-1:]
        elif head == "sed" and any(t.startswith("-i") for t in toks[1:]):
            targets = args[1:]
        else:
            continue
        for t in targets:
            r = inside(t, roots, cwd)
            if r:
                return r
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    roots = protected()
    if not roots:
        return 0
    tool = str(payload.get("tool_name") or "")
    ti = payload.get("tool_input") or {}
    hit = None
    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        hit = inside(str(ti.get("file_path") or ti.get("notebook_path") or ""), roots, ROOT)
    elif tool == "Bash":
        hit = check_bash(str(ti.get("command") or ""), roots)
    if hit:
        sys.stderr.write(
            f"CHẶN {tool} — `{hit}` là nguồn CHỈ ĐỌC (qa/QA.md §Nguồn chỉ đọc).\n"
            "QA không sửa tài liệu/code sản phẩm. Cần ghi thật (vd người dùng nhờ viết test tự động vào repo)\n"
            "→ hỏi người dùng; họ đồng ý thì gỡ đường dẫn khỏi dòng `Chỉ đọc:` rồi làm.\n")
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"guard_readonly.py: {e}", file=sys.stderr)
        sys.exit(0)
