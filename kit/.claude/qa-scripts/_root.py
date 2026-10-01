"""Dùng chung cho các hook: tìm thư mục dự án, tách lệnh shell, mở rộng biến.

Hook là hàng rào phụ, không phải trình phân tích shell đầy đủ: bắt được các cách viết phổ biến; luật trong skill vẫn
là thứ ràng buộc chính. Giới hạn đã biết: eval, script ngoài tự ghi file, thân `python - <<EOF`, đường dẫn tính lúc chạy.
"""
from __future__ import annotations

import os
import re
import shlex
from pathlib import Path


def project_root() -> Path:
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parents[2]   # <dự án>/.claude/qa-scripts/_root.py


SUB_OPEN, SUB_CLOSE = "\x00(", "\x00)"
SUB_TOKEN, PSUB_TOKEN = "$__SUB__", "$__PSUB__"     # thay cho $(…)/`…` và <(…)/>(…) trong lệnh chứa (lệnh bên trong đã xét riêng)          # đoạn đánh dấu subshell do split_commands trả về
HEREDOC_RE = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][\w-]*)\1")


def strip_heredocs(cmd: str) -> str:
    """Bỏ THÂN heredoc (là dữ liệu, không phải lệnh) — giữ dòng mở `cat > f <<'EOF'`."""
    out, lines, i = [], cmd.split("\n"), 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        delims = [m.group(2) for m in HEREDOC_RE.finditer(line)]
        i += 1
        for d in delims:
            while i < len(lines) and lines[i].strip() != d:
                i += 1
            i += 1                                   # bỏ dòng kết thúc
    return "\n".join(out)


def normalize(cmd: str) -> str:
    cmd = re.sub(r"\d*[<>]&(\d+|-)", " ", cmd)        # 2>&1, >&2, <&0: nhân bản fd, không phải file
    cmd = re.sub(r"&>>?", ">", cmd)                   # &>file = >file
    cmd = re.sub(r"(?<![^\s;&|(])\d+(?=>)", "", cmd)   # 2>/dev/null, 2> err.log: bỏ số fd (shlex tách "2" thành tham số riêng)
    return cmd


def match_paren(cmd: str, j: int) -> int:
    """Vị trí `)` khớp với `(` ở cmd[j] (hiểu nháy, ngoặc lồng); -1 nếu không đóng."""
    depth, q, k = 0, "", j
    while k < len(cmd):
        c = cmd[k]
        if q:
            if c == "\\" and q == '"':
                k += 1
            elif c == q:
                q = ""
        elif c in ("'", '"'):
            q = c
        elif c == "\\":
            k += 1
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return k
        k += 1
    return -1


def split_commands(cmd: str, _norm: bool = True) -> list[str]:
    """Tách theo ; && || | & và xuống dòng NẰM NGOÀI dấu nháy; bỏ thân heredoc.
    Subshell `( … )` ở đầu lệnh (kể cả sau do/then/!/{/time…) → SUB_OPEN … SUB_CLOSE (cd bên trong không lọt ra).
    `$( … )`, `<( … )`, `>( … )` và `…` giữ nguyên trong lệnh chứa nó; lệnh bên trong được tách riêng, bọc
    SUB_OPEN/SUB_CLOSE, đặt ngay trước lệnh chứa nó."""
    if _norm:
        cmd = normalize(strip_heredocs(cmd))
    out, cur, q, i = [], [], "", 0
    opened = 0                                    # số subshell đang mở

    def flush():
        nonlocal cur
        if "".join(cur).strip():
            out.append("".join(cur))
        cur = []

    while i < len(cmd):
        c = cmd[i]
        if q == '"' and (cmd[i:i + 2] == "$(" or c == "`"):     # "$(…)" / "`…`": vẫn là lệnh, phải soi
            if c == "`":
                k = cmd.find("`", i + 1)
                k, body = (len(cmd) - 1 if k < 0 else k), None
                body = cmd[i + 1:k]
            else:
                k = match_paren(cmd, i + 1)
                k = len(cmd) - 1 if k < 0 else k
                body = cmd[i + 2:k]
                if body.startswith("(") and body.endswith(")"):  # "$(( … ))" số học: không phải lệnh
                    body = body[1:-1] if ("$(" in body or "`" in body) else ""   # chỉ soi lệnh lồng trong biểu thức
            out.extend([SUB_OPEN, *split_commands(body, False), SUB_CLOSE])
            cur.append(SUB_TOKEN)
            i = k
        elif q:
            cur.append(c)
            if c == "\\" and q == '"' and i + 1 < len(cmd):
                cur.append(cmd[i + 1])
                i += 1
            elif c == q:
                q = ""
        elif c in ("'", '"'):
            q = c
            cur.append(c)
        elif c == "\\" and i + 1 < len(cmd):
            if cmd[i + 1] != "\n":              # "\\\n" = nối dòng
                cur.append(c)
                cur.append(cmd[i + 1])
            i += 1
        elif c == "(" and cmd[i - 1:i] in ("$", "<", ">") and i > 0:
            k = match_paren(cmd, i)
            k = len(cmd) - 1 if k < 0 else k
            body = cmd[i + 1:k]
            if body.startswith("(") and body.endswith(")"):      # $(( … )) số học: không phải lệnh
                body = body[1:-1] if ("$(" in body or "`" in body) else ""   # chỉ soi lệnh lồng trong biểu thức
            out.extend([SUB_OPEN, *split_commands(body, False), SUB_CLOSE])
            if cmd[i - 1:i] == "$":
                cur.append(SUB_TOKEN[1:])                         # `$` đã nằm trong cur → "$__SUB__"
            else:
                cur.append(PSUB_TOKEN)                            # <( … ) / >( … ): không phải đường dẫn
            i = k
        elif c == "`":
            k = cmd.find("`", i + 1)
            k = len(cmd) - 1 if k < 0 else k
            out.extend([SUB_OPEN, *split_commands(cmd[i + 1:k], False), SUB_CLOSE])
            cur.append(SUB_TOKEN)
            i = k
        elif c == "(" and all(w in KEYWORDS for w in "".join(cur).split()):
            cur = []
            opened += 1
            out.append(SUB_OPEN)
        elif c == "(":                                           # mảng a=(x y), khai báo hàm f()…
            k = match_paren(cmd, i)
            k = len(cmd) - 1 if k < 0 else k
            cur.append(cmd[i:k + 1])
            i = k
        elif c == ")" and opened:
            flush()
            opened -= 1
            out.append(SUB_CLOSE)
        elif c in ";\n" or cmd[i:i + 2] in ("&&", "||") or c == "&" or (c == "|" and cmd[i - 1:i] != ">"):
            flush()
            if cmd[i:i + 2] in ("&&", "||", "|&"):
                i += 1
        else:
            cur.append(c)
        i += 1
    flush()
    return [x.strip() for x in out] + [SUB_CLOSE] * opened      # ngoặc chưa đóng: coi như đóng ở cuối


KEYWORDS = {"do", "then", "else", "elif", "!", "{", "}", "time", "if", "while", "until"}


def drop_inputs(toks: list[str]) -> list[str]:
    """Bỏ `<`, `<<<`, `<<` và toán hạng đi sau — đó là thứ ĐỌC vào, không phải đích ghi (`tee x < src/a`)."""
    out, skip = [], False
    for t in toks:
        if skip:
            skip = False
        elif re.fullmatch(r"\d?<(<<?|<-)?", t):
            skip = True
        else:
            out.append(t)
    return out


def opt_value(rest: list[str], shorts: str, longs: tuple[str, ...]) -> list[str]:
    """Giá trị của cờ: `-o x`, cờ gộp `-sSo x`, `--output x`, `--output=x`."""
    vals = []
    for k, a in enumerate(rest):
        if a.startswith("--"):
            for lg in longs:
                if a == lg and k + 1 < len(rest):
                    vals.append(rest[k + 1])
                elif a.startswith(lg + "="):
                    vals.append(a.split("=", 1)[1])
        elif re.fullmatch(r"-[A-Za-z]+", a) and a[-1] in shorts and k + 1 < len(rest):
            vals.append(rest[k + 1])
    return vals


def is_redir(t: str) -> bool:
    return bool(re.fullmatch(r"\d?>>?\|?", t))


def tokens(seg: str) -> list[str]:
    """Tách một lệnh thành token (hiểu nháy), tách riêng toán tử chuyển hướng, bỏ ngoặc subshell và từ khoá shell đầu lệnh."""
    try:
        lx = shlex.shlex(seg, posix=True, punctuation_chars="<>()")
        lx.whitespace_split = True
        toks = list(lx)
    except ValueError:
        toks = seg.split()
    out: list[str] = []
    for t in toks:
        if t in ("(", ")"):
            continue
        m = re.match(r"^(\d?>>?\|?)(\S+)$", t)          # >file dính liền
        if m and not is_redir(t):
            out += [m.group(1), m.group(2)]
        elif t == ">|":
            out.append(">")
        elif t.startswith("|") and out and is_redir(out[-1]):   # ">| file" (noclobber) → ">" + file
            if t[1:]:
                out.append(t[1:])
        else:
            out.append(t)
    while out and out[0] in KEYWORDS:
        out = out[1:]
    return out


# ---- PowerShell: chuyển lệnh về dạng bash tương đương để các guard soi chung một đường ----
# Không phải trình phân tích PowerShell đầy đủ: bắt cmdlet/alias ghi-xoá-chép phổ biến, tham số có tên (-Path, -Destination,
# -FilePath, -OutFile, -DestinationPath…, cả viết tắt ≥3 ký tự và -Path:x), redirect (> >> 2> *>), khối { … },
# `cmd /c "…"`, `powershell -Command "…"`, [IO.File]::Write…/Copy/Move/Delete, gán `$x = '…'`.
# Giới hạn đã biết: biến tính lúc chạy, pipeline đưa đường dẫn qua $_, Invoke-Expression, script .ps1 ngoài.
PS_CMD = {
    **dict.fromkeys(("remove-item", "ri", "del", "erase", "rd", "rmdir", "rm"), "rm"),
    **dict.fromkeys(("move-item", "mi", "move", "mv"), "mv"),
    **dict.fromkeys(("rename-item", "rni", "ren"), "ren"),
    **dict.fromkeys(("copy-item", "cpi", "copy", "cp"), "cp"),
    **dict.fromkeys(("set-content", "sc", "add-content", "ac", "clear-content", "clc", "out-file", "tee-object", "tee",
                     "export-csv", "epcsv", "export-clixml", "set-item", "si", "clear-item", "cli"), "write"),
    **dict.fromkeys(("new-item", "ni", "mkdir", "md"), "new"),
    **dict.fromkeys(("invoke-webrequest", "iwr", "invoke-restmethod", "irm", "curl", "wget", "start-bitstransfer"), "web"),
    "expand-archive": "unzip", "compress-archive": "zip",
    **dict.fromkeys(("get-content", "gc", "type"), "cat"),
    **dict.fromkeys(("set-location", "sl", "cd", "chdir", "push-location", "pushd"), "cd"),
    **dict.fromkeys(("pop-location", "popd"), "popd"),
    "cmd": "cmd", "powershell": "ps", "pwsh": "ps",
}
PS_VALUE = ("path", "literalpath", "destination", "filepath", "outfile", "destinationpath", "value", "encoding", "name",
            "itemtype", "type", "target", "include", "exclude", "filter", "newname", "uri", "method", "body", "headers",
            "contenttype", "inputobject", "delimiter", "width", "credential", "erroraction", "warningaction",
            "informationaction", "outvariable", "errorvariable", "stream", "command", "totalcount", "tail", "readcount",
            "depth", "source")
PS_HERESTR = re.compile(r"@(['\"])\r?\n.*?\r?\n\1@", re.S)
PS_FILE_API = re.compile(r"""\[(?:System\.)?IO\.(?:File|Directory)\]::(\w+)\(\s*['"]([^'"]+)['"](?:\s*,\s*['"]([^'"]+)['"])?""", re.I)


def ps_prepare(cmd: str) -> str:
    """Đưa văn bản PowerShell về cú pháp mà split_commands/tokens hiểu."""
    cmd = PS_HERESTR.sub("''", cmd)                        # here-string @'…'@ là dữ liệu
    cmd = re.sub(r"`\r?\n", " ", cmd)                      # ` cuối dòng = nối dòng
    cmd = re.sub(r"`(.)", r"\1", cmd)                      # ` là ký tự thoát của PowerShell (không phải subshell)
    cmd = cmd.replace("\\", "/")                           # \ trong PowerShell là chữ thường — đường dẫn Windows
    cmd = re.sub(r"\$env:(\w+)", r"$\1", cmd, flags=re.I)
    cmd = re.sub(r"\$null\b", "/dev/null", cmd, flags=re.I)
    cmd = re.sub(r"\$home\b", "~", cmd, flags=re.I)
    cmd = re.sub(r"\*>", ">", cmd)                         # *> = mọi luồng
    return re.sub(r"(?<![$@])[{}]", ";", cmd)              # khối { … } (ForEach-Object, if): soi lệnh bên trong


def _ps_params(rest: list[str]) -> tuple[dict, list[str], list[str]]:
    named: dict[str, list[str]] = {}
    pos: list[str] = []
    switches: list[str] = []
    i = 0
    while i < len(rest):
        t = rest[i]
        m = re.fullmatch(r"-([A-Za-z][\w-]*)(?::(.*))?", t)
        if m:
            name = m.group(1).lower()
            full = [k for k in PS_VALUE if k == name] or \
                ([k for k in PS_VALUE if k.startswith(name)] if len(name) >= 3 else [])
            key = full[0] if len(full) == 1 else name
            if m.group(2) is not None:
                named.setdefault(key, []).append(m.group(2))
            elif len(full) == 1 and i + 1 < len(rest):
                named.setdefault(key, []).append(rest[i + 1])
                i += 1
            else:
                switches.append(name)
        elif not re.fullmatch(r"/[A-Za-z?]", t):            # /s /q của cmd là cờ
            pos.append(t)
        i += 1
    return named, pos, switches


def ps_segment(seg: str, depth: int = 0) -> list[str]:
    """Một lệnh PowerShell → danh sách lệnh dạng bash (đã quote) cho guard soi."""
    m = re.fullmatch(r"\s*\$(\w+)\s*=\s*(['\"]?)([^'\"]*)\2\s*", seg)
    if m:                                                  # $D = 'src' → D=src (để $D phía sau mở rộng được)
        return [f"{m.group(1)}={shlex.quote(m.group(3))}"]
    out: list[str] = []
    for fm in PS_FILE_API.finditer(seg):
        op, a, b = fm.group(1).lower(), fm.group(2), fm.group(3)
        if op in ("copy", "move") and b:
            out.append(f"{'cp' if op == 'copy' else 'mv'} {shlex.quote(a)} {shlex.quote(b)}")
        elif op.startswith(("write", "append", "create", "delete", "open")):
            out.append(f"touch {shlex.quote(a)}")
    toks = tokens(seg)
    redirs: list[str] = []
    plain: list[str] = []
    k = 0
    while k < len(toks):
        if is_redir(toks[k]) and k + 1 < len(toks):
            redirs += [toks[k], shlex.quote(toks[k + 1])]
            k += 2
            continue
        plain.append(toks[k])
        k += 1
    while plain and plain[0] in ("&", "."):
        plain = plain[1:]
    if not plain:
        return out + [seg]
    head_raw = Path(plain[0]).name.lower()
    head = re.sub(r"\.(exe|cmd|bat)$", "", head_raw)
    grp = PS_CMD.get(head)
    if grp is None or (head_raw != head and grp in ("web", "write", "rm", "cp", "mv")):   # curl.exe, tee.exe…: bản gốc
        return out + [seg]
    named, pos, sw = _ps_params(plain[1:])
    q = lambda xs: " ".join(shlex.quote(x) for x in xs)
    get = lambda *keys: [v for key in keys for v in named.get(key, [])]
    tail = (" " + " ".join(redirs)) if redirs else ""
    src = get("path", "literalpath", "source")
    if grp == "rm":
        targets = src + pos
        rec = any(s.startswith("r") for s in sw) or head in ("rd", "rmdir")     # rd /s: cờ /s đã bị lọc
        out.append(f"rm {'-r ' if rec else ''}{q(targets)}{tail}")
    elif grp in ("mv", "cp"):
        dest = get("destination")
        if src:
            dest = dest or pos[:1]
        else:
            src, dest = pos[:1], dest or pos[1:2]
        out.append(f"{grp} {q(src)} {q(dest or ['.'])}{tail}")
    elif grp == "ren":
        out.append(f"mv {q(src or pos[:1])}{tail}")
    elif grp == "write":
        out.append(f"touch {q(get('filepath') or src or pos[:1])}{tail}")
    elif grp == "new":
        base = src or pos[:1]
        names = get("name")
        targets = [f"{b.rstrip('/')}/{n}" for b in (base or ["."]) for n in names] if names else base
        out.append(f"touch {q(targets)}{tail}")
    elif grp == "web":
        dest = get("outfile")
        out.append(f"touch {q(dest)}{tail}" if dest else f"true{tail}")
    elif grp == "unzip":
        out.append(f"touch {q(get('destinationpath') or pos[1:2] or ['.'])}{tail}")
    elif grp == "zip":
        dest = get("destinationpath") or (pos[:1] if src else pos[1:2])
        srcs = src or pos[:1]
        out += [f"zip {q(dest)} {q(srcs)}{tail}", f"touch {q(dest)}"]
    elif grp == "cat":
        out.append(f"cat {q(src or pos)}{tail}")
    elif grp == "cd":
        out.append(f"cd {q(src or pos[:1])}" if (src or pos) else "cd")
    elif grp == "popd":
        out.append("popd")
    elif grp in ("cmd", "ps") and depth < 3:
        rest = plain[1:]
        pat = r"/[ck]" if grp == "cmd" else r"[-/]c(?:o(?:m(?:m(?:a(?:n(?:d)?)?)?)?)?)?"
        idx = next((j for j, a in enumerate(rest) if re.fullmatch(pat, a, re.I)), None)
        if idx is None:
            return out + [seg]
        inner = " ".join(rest[idx + 1:])
        out += [SUB_OPEN, *ps_commands(inner, depth + 1), SUB_CLOSE]
    else:
        return out + [seg]
    return out


def ps_commands(cmd: str, depth: int = 0) -> list[str]:
    """Như split_commands nhưng cho PowerShell: mỗi lệnh đã đổi sang dạng bash tương đương."""
    out: list[str] = []
    for seg in split_commands(ps_prepare(cmd)):
        out.extend([seg] if seg in (SUB_OPEN, SUB_CLOSE) else ps_segment(seg, depth))
    return out


def expand(tok: str, env: dict) -> str:
    """Mở rộng ~, $HOME, ${F:-mặc định} và biến đã gán/export trước đó trong cùng lệnh."""
    def sub(m: re.Match) -> str:
        name, default = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), None)
        v = env.get(name, os.environ.get(name))
        return v if v is not None else (default if default is not None else m.group(0))
    return os.path.expanduser(re.sub(r"\$\{(\w+)(?::?-([^}]*))?\}|\$(\w+)", sub, tok))
