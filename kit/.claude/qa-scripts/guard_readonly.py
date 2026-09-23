#!/usr/bin/env python3
"""guard_readonly.py — hook PreToolUse: không ghi vào các đường dẫn khai ở `qa/QA.md §Nguồn chỉ đọc`.

Dòng `- Chỉ đọc: src, docs, ../product-repo` (phân tách bằng dấu phẩy; tương đối so với thư mục dự án).
Chặn Write/Edit/MultiEdit/NotebookEdit có file_path trong đó, và lệnh Bash có dấu hiệu ghi vào đó (redirect,
tee, sed -i, rm, mv, cp/rsync với đích trong đó, git ghi trong đó). Đọc thuần, cp LẤY từ đó, git chỉ liệt kê
(log, status, branch/tag không đối số, stash list) đi qua. Thư mục qa/ LUÔN ghi được, kể cả khi khai `Chỉ đọc: ..`.
Người dùng nhờ ghi thật (vd viết test tự động vào repo) → họ gỡ đường dẫn khỏi dòng `Chỉ đọc:`, hook không có
ngoại lệ ngầm. Fail-open khi thiếu dữ liệu. Exit 0 cho qua · 2 chặn.
"""
from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _root import project_root  # noqa: E402

ROOT = project_root().resolve()
QA_DIR = ROOT / "qa"


def fold(p: Path) -> str:
    return str(p).casefold()   # APFS/NTFS mặc định không phân biệt hoa thường


def under(p: Path, d: Path) -> bool:
    a, b = fold(p), fold(d)
    return a == b or a.startswith(b.rstrip("/\\") + "/") or a.startswith(b.rstrip("/\\") + "\\")


def protected() -> list[Path]:
    try:
        text = (QA_DIR / "QA.md").read_text(encoding="utf-8-sig")
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
            if fold(p) == fold(ROOT):   # khoá cả dự án thì qa/ vẫn ghi được — xử lý ở hit()
                pass
            out.append(p)
    return out


def hit(path: str, roots: list[Path], cwd: Path) -> Path | None:
    try:
        p = Path(path.strip("\"'")).expanduser()
        p = (p if p.is_absolute() else cwd / p).resolve()
    except (OSError, ValueError):
        return None
    if under(p, QA_DIR):
        return None
    for r in roots:
        if under(p, r):
            return r
    return None


WRITE_CMDS = {"rm", "rmdir", "mv", "touch", "mkdir", "truncate", "chmod", "chown", "ln", "unlink"}
GIT_WRITE = {"commit", "checkout", "switch", "reset", "restore", "clean", "merge", "rebase", "pull", "apply",
             "add", "rm", "mv", "cherry-pick", "revert", "am", "push", "init", "worktree", "gc"}
GIT_WRITE_IF_ARGS = {"branch", "tag"}          # không đối số = chỉ liệt kê
REDIR = {">", ">>", ">|", "&>", "&>>", "1>", "2>", "1>>", "2>>"}


def tokens(seg: str) -> list[str]:
    try:
        lx = shlex.shlex(seg, posix=True, punctuation_chars=True)
        lx.whitespace_split = True
        return [t for t in lx if t not in ("(", ")")]
    except ValueError:
        return seg.split()


def check_bash(cmd: str, roots: list[Path]) -> Path | None:
    cwd = Path.cwd()
    for seg in re.split(r"&&|\|\||;|(?<![>&])\|(?!\|)", cmd):
        toks = tokens(seg)
        # redirect: toán tử nằm ngoài nháy (shlex đã tách), đích là token kế tiếp
        for i, t in enumerate(toks):
            if (t in REDIR or re.fullmatch(r"\d?>>?\|?", t)) and i + 1 < len(toks):
                r = hit(toks[i + 1], roots, cwd)
                if r:
                    return r
        toks = [t for j, t in enumerate(toks) if not (t in REDIR or re.fullmatch(r"\d?>>?\|?", t))
                and not (j > 0 and (toks[j - 1] in REDIR or re.fullmatch(r"\d?>>?\|?", toks[j - 1])))]
        while toks and ("=" in toks[0] or toks[0] in ("env", "command", "sudo", "time")):
            toks = toks[1:]
        if not toks:
            continue
        head, rest = toks[0], toks[1:]
        args = [a for a in rest if not a.startswith("-")]
        if head == "cd" and args:
            cwd = (cwd / args[0]).resolve() if not Path(args[0]).is_absolute() else Path(args[0]).resolve()
            continue
        if head == "git":
            gdir, i, sub, sub_args = cwd, 0, "", []
            while i < len(rest):
                if rest[i] == "-C" and i + 1 < len(rest):
                    gdir = Path(rest[i + 1]).expanduser()
                    gdir = (gdir if gdir.is_absolute() else cwd / gdir).resolve()
                    i += 2
                    continue
                if rest[i].startswith("-") and not sub:
                    i += 1
                    continue
                if not sub:
                    sub = rest[i]
                else:
                    sub_args.append(rest[i])
                i += 1
            writes = sub in GIT_WRITE or (sub in GIT_WRITE_IF_ARGS and [a for a in sub_args if not a.startswith("-l")]) \
                or (sub == "stash" and (not sub_args or sub_args[0] not in ("list", "show")))
            if writes:
                r = hit(str(gdir), roots, cwd)
                if r:
                    return r
            continue
        if head == "tee":
            targets = args
        elif head in WRITE_CMDS:
            targets = args
        elif head in ("cp", "rsync", "install", "ditto"):
            if "-t" in rest and rest.index("-t") + 1 < len(rest):
                targets = [rest[rest.index("-t") + 1]]
            else:
                targets = args[-1:]
        elif head == "sed" and any(t.startswith("-i") for t in rest):
            targets = args[1:]
        else:
            continue
        for t in targets:
            r = hit(t, roots, cwd)
            if r:
                return r
    return None


def main() -> int:
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace"))
    except (json.JSONDecodeError, ValueError):
        return 0
    roots = protected()
    if not roots:
        return 0
    tool = str(payload.get("tool_name") or "")
    ti = payload.get("tool_input") or {}
    r = None
    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        r = hit(str(ti.get("file_path") or ti.get("notebook_path") or ""), roots, ROOT)
    elif tool == "Bash":
        r = check_bash(str(ti.get("command") or ""), roots)
    if r:
        sys.stderr.write(
            f"CHẶN {tool} — `{r}` là nguồn CHỈ ĐỌC (qa/QA.md §Nguồn chỉ đọc).\n"
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
