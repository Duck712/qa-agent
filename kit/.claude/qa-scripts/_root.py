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


SUB_OPEN, SUB_CLOSE = "\x00(", "\x00)"          # đoạn đánh dấu subshell do split_commands trả về
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
    return cmd


def split_commands(cmd: str) -> list[str]:
    """Tách theo ; && || | & và xuống dòng NẰM NGOÀI dấu nháy; bỏ thân heredoc; lấy thêm lệnh trong $(…) và `…`."""
    cmd = normalize(strip_heredocs(cmd))
    inner = re.findall(r"\$\(([^()]*)\)", cmd) + re.findall(r"`([^`]*)`", cmd)
    out, cur, q, i = [], [], "", 0
    parens: list[bool] = []                       # True = ngoặc subshell ở đầu lệnh; False = $( … ), <( … ), mảng…
    while i < len(cmd):
        c = cmd[i]
        if q:
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
        elif c == "(" and not "".join(cur).strip():
            parens.append(True)
            out.append(SUB_OPEN)
        elif c == "(":
            parens.append(False)
            cur.append(c)
        elif c == ")" and parens:
            if parens.pop():
                if "".join(cur).strip():
                    out.append("".join(cur))
                cur = []
                out.append(SUB_CLOSE)
            else:
                cur.append(c)
        elif c in ";\n" or cmd[i:i + 2] in ("&&", "||") or c == "&" or (c == "|" and cmd[i - 1:i] != ">"):
            if "".join(cur).strip():
                out.append("".join(cur))
            cur = []
            if cmd[i:i + 2] in ("&&", "||", "|&"):
                i += 1
        else:
            cur.append(c)
        i += 1
    if "".join(cur).strip():
        out.append("".join(cur))
    segs = [s.strip() for s in out]
    segs += [SUB_CLOSE] * sum(parens)             # ngoặc chưa đóng: coi như đóng ở cuối
    for x in inner:
        segs += split_commands(x)
    return segs


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


def expand(tok: str, env: dict) -> str:
    """Mở rộng ~, $HOME, ${F:-mặc định} và biến đã gán/export trước đó trong cùng lệnh."""
    def sub(m: re.Match) -> str:
        name, default = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), None)
        v = env.get(name, os.environ.get(name))
        return v if v is not None else (default if default is not None else m.group(0))
    return os.path.expanduser(re.sub(r"\$\{(\w+)(?::?-([^}]*))?\}|\$(\w+)", sub, tok))
