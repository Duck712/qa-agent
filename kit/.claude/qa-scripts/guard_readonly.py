#!/usr/bin/env python3
"""guard_readonly.py — hook PreToolUse: không ghi vào các đường dẫn khai ở `qa/QA.md §Nguồn chỉ đọc`.

Dòng `- Chỉ đọc: src, docs, ../product-repo` (phân tách `,` hoặc `;`; chú thích trong ngoặc được bỏ; tương đối so với
thư mục dự án). Chặn Write/Edit/MultiEdit/NotebookEdit có file_path trong đó, và lệnh Bash có dấu hiệu ghi vào đó:
chuyển hướng, tee, sed/perl -i (cả cờ gộp), rm/mv/touch/…, cp/rsync/install (-t, --target-directory), dd of=,
curl -o/--output, wget -O, unzip -d, tar -x -C, find -delete/-exec, xargs với lệnh ghi, git làm đổi cây thư mục (cả
-C, -c, --work-tree, pathspec, chạy ở gốc repo khi thư mục chỉ đọc nằm bên trong), `bash -c`/`sh -lc`, `python -c` mở
file để ghi, `$(…)`/`…`, biến gán/export trước, glob. Tiền tố env/sudo/timeout/nice/nohup, từ khoá do/then/!, lệnh nền
`&`, thân heredoc (bỏ qua — là dữ liệu). Đọc thuần, cp LẤY từ đó, git chỉ liệt kê đi qua. Thư mục qa/ LUÔN ghi được.
Lệnh PowerShell (Windows) được đổi về dạng bash tương đương trước khi soi — xem `_root.ps_commands`.

Giới hạn đã biết (hàng rào phụ — luật trong skill qa vẫn áp): eval, script ngoài tự ghi, thân `python - <<EOF`,
vòng lặp dùng biến chạy lúc thực thi, đường dẫn tính lúc chạy (`$(pwd)`). Người dùng nhờ ghi thật → gỡ đường dẫn
khỏi dòng `Chỉ đọc:`. Fail-open khi thiếu dữ liệu. Exit 0 cho qua · 2 chặn.
"""
from __future__ import annotations

import glob
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _root import (SUB_CLOSE, SUB_OPEN, drop_inputs, expand, is_redir, opt_value, project_root,  # noqa: E402
                   ps_commands, split_commands, tokens)

ROOT = project_root().resolve()
QA_DIR = ROOT / "qa"
PARTIAL = "\x01partial"                              # tên giả cho phần đường dẫn tính lúc chạy


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
            if s:
                p = Path(s).expanduser()
                out.append((p if p.is_absolute() else ROOT / p).resolve())
    return out


def resolve(path: str, cwd: Path, env: dict) -> list[Path]:
    raw = expand(path.strip("\"'"), env)
    if raw and "$" in raw:                              # src/`date`.log, src/$(date).log: phần thư mục cố định phía trước
        fixed = raw.split("$", 1)[0]
        if not fixed:                                   # bắt đầu bằng giá trị tính lúc chạy ("$D/x"): không biết thư mục
            return []
        d = fixed if fixed.endswith("/") else fixed.rsplit("/", 1)[0] + "/" if "/" in fixed else "./"
        raw = d + PARTIAL
    if not raw:
        return []
    base = raw if Path(raw).is_absolute() else str(cwd / raw)
    if re.search(r"[*?\[]", raw):                       # glob: xét các file khớp + phần thư mục cố định phía trước
        found = [Path(x) for x in glob.glob(base)]
        fixed = re.split(r"[*?\[]", base)[0]
        return [p.resolve() for p in found] + ([Path(fixed).resolve()] if fixed else [])
    try:
        return [Path(base).resolve()]
    except (OSError, ValueError):
        return []


def hit(path: str, roots: list[Path], cwd: Path, env: dict, ancestor: bool = False) -> Path | None:
    """Đường dẫn nằm trong vùng chỉ đọc? ancestor=True: cả khi vùng chỉ đọc nằm BÊN TRONG đường dẫn (rm -r ., find .)."""
    for p in resolve(path, cwd, env):
        if p.name == PARTIAL:                              # chỉ biết thư mục: xét "nằm trong", không xét "chứa vùng chỉ đọc"
            p = p.parent
            if not under(p, QA_DIR) and any(under(p, r) for r in roots):
                return next(r for r in roots if under(p, r))
            continue
        if under(p, QA_DIR) and not ancestor:
            continue
        for r in roots:
            if under(p, r) or (ancestor and under(r, p) and not under(p, QA_DIR)):
                return r
    return None


WRITE_CMDS = {"rm", "rmdir", "mv", "touch", "mkdir", "truncate", "chmod", "chown", "ln", "unlink", "shred"}
PREFIX = {"env", "command", "sudo", "time", "nohup", "exec", "nice", "timeout", "stdbuf", "ionice", "caffeinate"}
GIT_TREE = {"checkout", "switch", "reset", "restore", "clean", "merge", "rebase", "pull", "apply", "am", "stash",
            "cherry-pick", "revert", "rm", "mv"}
GIT_META = {"commit", "add", "push", "tag", "branch", "worktree", "init", "gc", "config"}
PY_WRITE = re.compile(r"""open\(\s*['"]([^'"]+)['"]\s*,\s*['"][wax+]|Path\(\s*['"]([^'"]+)['"]\s*\)\.write_(?:text|bytes)""")


def short_flag(tok: str, letter: str) -> bool:
    return bool(re.fullmatch(rf"-[A-Za-z]*{letter}[A-Za-z]*", tok))


def git_hit(rest: list[str], roots, cwd, env) -> Path | None:
    gdir, i, sub, sub_args = cwd, 0, "", []
    while i < len(rest):
        t = rest[i]
        if t in ("-C", "--work-tree", "--git-dir") and i + 1 < len(rest):
            v = Path(expand(rest[i + 1], env))
            gdir = (v if v.is_absolute() else cwd / v).resolve()
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
    pos = [a for a in sub_args if not a.startswith("-")]
    new_branch = len(pos) <= 1 and (
        (sub == "checkout" and any(a in ("-b", "-B", "--orphan") for a in sub_args)) or
        (sub == "switch" and any(a in ("-c", "-C", "--create", "--force-create", "--orphan") for a in sub_args)))
    read_only = {
        "branch": not pos or any(a in ("-l", "--list", "-a", "-r", "--show-current", "-v", "-vv", "--contains",
                                        "--merged", "--no-merged", "--points-at", "--sort", "--format") for a in sub_args),
        "tag": not pos or any(a in ("-l", "--list", "-n", "--contains", "--points-at", "--merged", "--sort") for a in sub_args),
        "stash": bool(sub_args) and sub_args[0] in ("list", "show"),
        "worktree": bool(sub_args) and sub_args[0] == "list",
        "clean": any(a in ("--dry-run",) or short_flag(a, "n") for a in sub_args),
        "config": any(a in ("--get", "--list", "-l", "--get-all", "--get-regexp") for a in sub_args) or len(pos) <= 1,
    }
    if sub not in GIT_TREE | GIT_META or read_only.get(sub):
        return None
    if "--" in sub_args:                                   # git checkout -- src/a.js
        paths = sub_args[sub_args.index("--") + 1:]
    elif sub in ("restore", "rm", "mv"):
        paths = pos                                         # checkout/switch không có `--` = đổi nhánh → cả cây
    else:
        paths = []
    for p in paths:
        r = hit(p, roots, gdir, env, ancestor=True)
        if r:
            return r
    r = hit(str(gdir), roots, cwd, env)
    if r:
        return r
    if new_branch:                                         # tạo nhánh từ HEAD ở repo ngoài: không đổi file trong cây
        return None
    if sub in GIT_TREE and not paths:                      # chạy ở gốc repo, không pathspec → đổi cả cây, gồm vùng chỉ đọc
        inner = [r for r in roots if not (r / ".git").exists()]   # vùng chỉ đọc là repo git RIÊNG lồng bên trong:
        return hit(str(gdir), inner, cwd, env, ancestor=True)     # lệnh của repo ngoài không đụng tới nó
    return None


def check_bash(cmd: str, roots: list[Path], depth: int = 0, ps: bool = False) -> Path | None:
    cwd0 = Path.cwd()
    cwd = cwd0
    env: dict = {}
    prev: list[str] = []
    stack: list[Path] = []
    for seg in (ps_commands(cmd) if ps else split_commands(cmd)):
        if seg == SUB_OPEN:                                # ( cd src && … ): cd không ra khỏi subshell
            stack.append(cwd)
            continue
        if seg == SUB_CLOSE:
            cwd = stack.pop() if stack else cwd0
            continue
        toks = drop_inputs(tokens(seg))
        for i, t in enumerate(toks):
            if is_redir(t) and i + 1 < len(toks) and toks[i + 1] != "/dev/null":
                r = hit(toks[i + 1], roots, cwd, env)
                if r:
                    return r
        toks = [t for j, t in enumerate(toks) if not is_redir(t) and not (j > 0 and is_redir(toks[j - 1]))]
        if toks and toks[0] in ("export", "declare", "local", "readonly"):
            toks = toks[1:]
        while toks and re.match(r"^\w+=", toks[0]):
            k, v = toks[0].split("=", 1)
            env[k] = expand(v, env)
            toks = toks[1:]
        while toks and Path(toks[0]).name in PREFIX:
            head0 = Path(toks[0]).name
            toks = toks[1:]
            while toks and (toks[0].startswith("-") or re.match(r"^\w+=", toks[0])
                            or (head0 == "timeout" and re.fullmatch(r"\d+[smhd]?", toks[0]))):
                if head0 == "sudo" and toks[0] in ("-u", "-g") and len(toks) > 1:
                    toks = toks[1:]
                if head0 == "nice" and toks[0] == "-n" and len(toks) > 1:
                    toks = toks[1:]
                toks = toks[1:]
        if not toks:
            prev = []
            continue
        head, rest = Path(toks[0]).name, toks[1:]
        args = [a for a in rest if not a.startswith("-")]
        if head in ("cd", "pushd") and args:
            nxt = Path(expand(args[0], env))
            cwd = (nxt if nxt.is_absolute() else cwd / nxt).resolve()
            prev = toks
            continue
        if head == "popd" or (head == "cd" and not args):
            cwd = cwd0
            continue
        if head in ("bash", "sh", "zsh", "dash") and depth < 3:
            ci = [k for k, a in enumerate(rest) if re.fullmatch(r"-[A-Za-z]*c[A-Za-z]*", a)]
            if ci and ci[0] + 1 < len(rest):
                r = check_bash(rest[ci[0] + 1], roots, depth + 1)
                if r:
                    return r
                continue
        if head == "git":
            r = git_hit(rest, roots, cwd, env)
            if r:
                return r
            prev = toks
            continue
        targets: list[str] = []
        anc: list[str] = []
        if head == "tee":
            targets = args
        elif head in WRITE_CMDS:
            targets = args
            if head in ("rm", "chmod", "chown") and any(short_flag(a, "r") or short_flag(a, "R") or a == "--recursive" for a in rest):
                anc = args
        elif head in ("cp", "rsync", "install", "ditto"):
            tdir = opt_value(rest, "t", ("--target-directory",))
            targets = tdir or args[-1:]
        elif head == "sed" and any(a.startswith("--in-place") or short_flag(a, "i") or re.fullmatch(r"-[A-Za-z]*i\S*", a) for a in rest):
            has_e = any(a in ("-e", "--expression") or short_flag(a, "e") or a == "-f" for a in rest)
            files = args if has_e else args[1:]
            targets = [a for a in files if a not in ("''", '""', "")]
        elif head == "perl" and any(re.fullmatch(r"-[A-Za-z]*i\S*", a) for a in rest):
            targets = args[1:] if any(short_flag(a, "e") for a in rest) else args
        elif head == "dd":
            targets = [a[3:] for a in rest if a.startswith("of=")]
        elif head == "curl":
            targets = opt_value(rest, "o", ("--output",))
        elif head == "wget":
            targets = opt_value(rest, "OP", ("--output-document", "--directory-prefix"))
        elif head == "unzip":
            targets = opt_value(rest, "d", ())
        elif head == "tar" and (any(short_flag(a, "x") or a == "--extract" for a in rest) or (rest and re.fullmatch(r"[a-z]*x[a-z]*", rest[0]))):
            targets = opt_value(rest, "C", ("--directory",)) or ["."]
        elif head == "find" and ("-delete" in rest or any(x in rest for x in ("rm", "mv", "shred", "truncate"))
                                 or any(a in ("-exec", "-execdir") and k + 1 < len(rest) and rest[k + 1] in ("sed", "perl")
                                        for k, a in enumerate(rest))):
            anc = [a for a in rest if not a.startswith("-") and a not in ("{}", ";", "+")][:1] or ["."]
        elif head == "xargs":
            sub = [a for a in rest if not a.startswith("-") and a != "{}"]
            wcmd = Path(sub[0]).name if sub else ""
            if wcmd in ("cp", "mv", "rsync", "install"):
                targets = sub[-1:]
            elif wcmd in WRITE_CMDS | {"sed", "tee", "perl", "truncate"}:
                targets = [t for t in prev[1:] if not t.startswith("-")]      # đích đến từ lệnh trước trong pipe
                anc = targets if wcmd == "rm" else []
        elif head.startswith("python") and rest:
            ci = [k for k, a in enumerate(rest) if a == "-c"]
            if ci and ci[0] + 1 < len(rest):
                targets = [a or b for a, b in PY_WRITE.findall(rest[ci[0] + 1])]
        for t in targets:
            r = hit(t, roots, cwd, env)
            if r:
                return r
        for t in anc:
            r = hit(t, roots, cwd, env, ancestor=True)
            if r:
                return r
        prev = toks
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
    elif tool in ("Bash", "PowerShell"):
        r = check_bash(str(ti.get("command") or ""), roots, ps=tool == "PowerShell")
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
