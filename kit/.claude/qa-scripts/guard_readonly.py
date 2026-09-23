#!/usr/bin/env python3
"""guard_readonly.py — hook PreToolUse: không ghi vào các đường dẫn khai ở `qa/QA.md §Nguồn chỉ đọc`.

Dòng `- Chỉ đọc: src, docs, ../product-repo` (phân tách bằng `,` hoặc `;`; chú thích trong ngoặc được bỏ; tương đối so
với thư mục dự án). Chặn Write/Edit/MultiEdit/NotebookEdit có file_path trong đó, và lệnh Bash có dấu hiệu ghi vào đó:
chuyển hướng, tee, sed/perl -i, rm/mv/touch/…, cp/rsync/install (cả -t/--target-directory), dd of=, curl -o, wget -O,
unzip -d, tar -x -C, find -delete/-exec, xargs với lệnh ghi, git ghi (cả -C, -c, --work-tree, đường dẫn sau --),
`bash -c "…"`, `python -c` mở file để ghi, biến gán trước trong cùng lệnh. Tách lệnh theo ; && || | xuống dòng nằm
ngoài dấu nháy. Đọc thuần, cp LẤY từ đó, git chỉ liệt kê đi qua. Thư mục qa/ LUÔN ghi được.

Giới hạn đã biết (không bắt được — luật trong skill qa vẫn áp): lệnh sinh động phức tạp (eval, script ngoài tự ghi),
đường dẫn tính lúc chạy (`$(pwd)`, `cd -`). Người dùng nhờ ghi thật → họ gỡ đường dẫn khỏi dòng `Chỉ đọc:`.
Fail-open khi thiếu dữ liệu. Exit 0 cho qua · 2 chặn.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _root import expand, is_redir, project_root, split_commands, tokens  # noqa: E402

ROOT = project_root().resolve()
QA_DIR = ROOT / "qa"


def fold(p: Path) -> str:
    return str(p).casefold()   # APFS/NTFS mặc định không phân biệt hoa thường


def under(p: Path, d: Path) -> bool:
    a, b = fold(p), fold(d)
    return a == b or a.startswith(b.rstrip("/\\") + "/") or a.startswith(b.rstrip("/\\") + "\\")


def protected() -> list[Path]:
    try:
        text = unicodedata.normalize("NFC", (QA_DIR / "QA.md").read_text(encoding="utf-8-sig", errors="replace"))
    except OSError:
        return []
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    out = []
    for m in re.finditer(r"^[ \t]*-[ \t]*\*{0,2}Chỉ đọc\*{0,2}[ \t]*:\*{0,2}[ \t]*(.+)$", text, re.M):
        for part in re.split(r"[,;]", re.sub(r"\([^()]*\)", "", m.group(1))):
            s = part.strip().strip("`*").strip()
            if not s:
                continue
            p = Path(s).expanduser()
            out.append((p if p.is_absolute() else ROOT / p).resolve())
    return out


def hit(path: str, roots: list[Path], cwd: Path, env: dict) -> Path | None:
    raw = expand(path.strip("\"'").lstrip("|"), env)
    if not raw or "$" in raw:
        return None
    try:
        p = Path(raw)
        p = (p if p.is_absolute() else cwd / p).resolve()
    except (OSError, ValueError):
        return None
    if under(p, QA_DIR):
        return None
    for r in roots:
        if under(p, r):
            return r
    return None


WRITE_CMDS = {"rm", "rmdir", "mv", "touch", "mkdir", "truncate", "chmod", "chown", "ln", "unlink", "shred"}
GIT_WRITE = {"commit", "checkout", "switch", "reset", "restore", "clean", "merge", "rebase", "pull", "apply", "add",
             "rm", "mv", "cherry-pick", "revert", "am", "push", "init", "gc", "stash", "branch", "tag", "worktree"}
PY_WRITE = re.compile(r"""open\(\s*['"]([^'"]+)['"]\s*,\s*['"][wax+]""")


def git_hit(rest: list[str], roots, cwd, env) -> Path | None:
    gdir, i, sub, sub_args = cwd, 0, "", []
    while i < len(rest):
        t = rest[i]
        if t in ("-C", "--work-tree", "--git-dir") and i + 1 < len(rest):
            gdir = Path(expand(rest[i + 1], env))
            gdir = (gdir if gdir.is_absolute() else cwd / gdir).resolve()
            i += 2
            continue
        if t.startswith(("--work-tree=", "--git-dir=")):
            v = Path(expand(t.split("=", 1)[1], env))
            gdir = (v if v.is_absolute() else cwd / v).resolve()
            i += 1
            continue
        if t == "-c" and not sub:
            i += 2
            continue
        if t.startswith("-") and not sub:
            i += 1
            continue
        if not sub:
            sub = t
        else:
            sub_args.append(t)
        i += 1
    if sub not in GIT_WRITE:
        return None
    pos = [a for a in sub_args if not a.startswith("-")]
    listing = {
        "branch": not pos or any(a in ("-l", "--list", "-a", "-r", "--show-current", "-v", "-vv", "--contains", "--merged")
                                  for a in sub_args),
        "tag": not pos or any(a in ("-l", "--list", "-n") for a in sub_args),
        "stash": bool(sub_args) and sub_args[0] in ("list", "show"),
        "worktree": bool(sub_args) and sub_args[0] == "list",
        "clean": any(a in ("-n", "--dry-run") for a in sub_args),
    }
    if listing.get(sub):
        return None
    if "--" in sub_args:                      # git checkout -- src/a.js
        for p in sub_args[sub_args.index("--") + 1:]:
            r = hit(p, roots, cwd, env)
            if r:
                return r
    return hit(str(gdir), roots, cwd, env)


def check_bash(cmd: str, roots: list[Path], depth: int = 0) -> Path | None:
    cwd = Path.cwd()
    env: dict = {}
    for seg in split_commands(cmd):
        toks = tokens(seg)
        for i, t in enumerate(toks):
            if is_redir(t) and i + 1 < len(toks):
                r = hit(toks[i + 1], roots, cwd, env)
                if r:
                    return r
        toks = [t for j, t in enumerate(toks) if not is_redir(t) and not (j > 0 and is_redir(toks[j - 1]))]
        while toks and re.match(r"^\w+=", toks[0]):
            k, v = toks[0].split("=", 1)
            env[k] = expand(v, env)
            toks = toks[1:]
        while toks and toks[0] in ("env", "command", "sudo", "time", "nohup", "exec"):
            toks = toks[1:]
        if not toks:
            continue
        head, rest = Path(toks[0]).name, toks[1:]
        args = [a for a in rest if not a.startswith("-")]
        if head in ("cd", "pushd") and args:
            nxt = Path(expand(args[0], env))
            cwd = (nxt if nxt.is_absolute() else cwd / nxt).resolve()
            continue
        if head in ("bash", "sh", "zsh") and "-c" in rest and rest.index("-c") + 1 < len(rest) and depth < 3:
            r = check_bash(rest[rest.index("-c") + 1], roots, depth + 1)
            if r:
                return r
            continue
        if head == "git":
            r = git_hit(rest, roots, cwd, env)
            if r:
                return r
            continue
        targets: list[str] = []
        if head in ("tee",) or head in WRITE_CMDS:
            targets = args
        elif head in ("cp", "rsync", "install", "ditto"):
            tdir = [rest[k + 1] for k, a in enumerate(rest) if a == "-t" and k + 1 < len(rest)]
            tdir += [a.split("=", 1)[1] for a in rest if a.startswith("--target-directory=")]
            targets = tdir or args[-1:]
        elif head in ("sed", "perl") and any(t.startswith("-i") for t in rest):
            targets = [a for a in args if "/" in a or "." in a][-1:] if head == "sed" else args
        elif head == "dd":
            targets = [a[3:] for a in rest if a.startswith("of=")]
        elif head == "curl":
            targets = [rest[k + 1] for k, a in enumerate(rest) if a in ("-o", "--output") and k + 1 < len(rest)]
        elif head == "wget":
            targets = [rest[k + 1] for k, a in enumerate(rest) if a in ("-O", "-P") and k + 1 < len(rest)]
        elif head == "unzip":
            targets = [rest[k + 1] for k, a in enumerate(rest) if a == "-d" and k + 1 < len(rest)]
        elif head == "tar" and any("x" in a.lstrip("-") for a in rest[:1]) or (head == "tar" and "-x" in rest):
            targets = [rest[k + 1] for k, a in enumerate(rest) if a in ("-C", "--directory") and k + 1 < len(rest)]
            targets = targets or ["."]
        elif head == "find" and any(a in ("-delete", "-exec", "-execdir", "-ok") for a in rest):
            dangerous = "-delete" in rest or any(x in rest for x in ("rm", "mv", "sed", "truncate", "shred"))
            targets = [a for a in rest if not a.startswith("-") and a not in ("{}", ";", "+")][:1] if dangerous else []
        elif head == "xargs" and any(Path(a).name in WRITE_CMDS | {"sed", "tee", "cp", "mv"} for a in rest):
            targets = [t for s in split_commands(cmd) for t in tokens(s)]      # đích đến từ stdin → xét mọi token của lệnh
        elif head.startswith("python") and "-c" in rest and rest.index("-c") + 1 < len(rest):
            targets = PY_WRITE.findall(rest[rest.index("-c") + 1])
        for t in targets:
            r = hit(t, roots, cwd, env)
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
        r = hit(str(ti.get("file_path") or ti.get("notebook_path") or ""), roots, ROOT, {})
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
