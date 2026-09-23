"""Dùng chung cho các hook: tìm thư mục dự án, tách lệnh shell, mở rộng biến."""
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


def split_commands(cmd: str) -> list[str]:
    """Tách chuỗi lệnh theo ; && || | và xuống dòng NẰM NGOÀI dấu nháy (không tách `git commit -m "a; b"`)."""
    out, cur, q, i = [], [], "", 0
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
        elif c in ";\n" or cmd[i:i + 2] in ("&&", "||") or (c == "|" and cmd[i - 1:i] != ">"):
            if "".join(cur).strip():
                out.append("".join(cur))
            cur = []
            if cmd[i:i + 2] in ("&&", "||"):
                i += 1
        else:
            cur.append(c)
        i += 1
    if "".join(cur).strip():
        out.append("".join(cur))
    return [s.strip() for s in out]


def is_redir(t: str) -> bool:
    return bool(re.fullmatch(r"\d?>>?\|?|&>>?", t))


def tokens(seg: str) -> list[str]:
    """Tách một lệnh thành token (hiểu nháy), tách riêng toán tử chuyển hướng, bỏ ngoặc subshell."""
    try:
        lx = shlex.shlex(seg, posix=True, punctuation_chars="<>&()")
        lx.whitespace_split = True
        toks = list(lx)
    except ValueError:
        toks = seg.split()
    out: list[str] = []
    for t in toks:
        if t in ("(", ")", "{", "}"):
            continue
        m = re.match(r"^(\d?>>?\|?)(\S+)$", t)          # >file dính liền
        if m and not is_redir(t):
            out += [m.group(1), m.group(2)]
        else:
            out.append(t)
    return out


def expand(tok: str, env: dict) -> str:
    """Mở rộng ~, $HOME và biến đã gán trước đó trong cùng lệnh (F=src/x; echo > $F)."""
    def sub(m: re.Match) -> str:
        name = m.group(1) or m.group(2)
        return env.get(name, os.environ.get(name, m.group(0)))
    return os.path.expanduser(re.sub(r"\$\{(\w+)\}|\$(\w+)", sub, tok))
