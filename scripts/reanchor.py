#!/usr/bin/env python3
"""reanchor.py — nhồi lại luật SPEC vào context sau khi compact.

VÌ SAO CÓ FILE NÀY
    Compact giữ được "đang làm gì" nhưng làm phẳng "đang bị cấm gì". SPEC sống bằng ràng
    buộc thủ tục (không hỏi QC sau pha S, repo nguồn chỉ đọc, ngưỡng khoá, bằng chứng
    bắt buộc) — đúng loại thứ biến mất đầu tiên trong bản tóm tắt. Hook này chạy ngay
    sau compact, đọc lại luật + trạng thái sống TỪ FILE — meta không phải nhớ.

CHẠY NHƯ THẾ NÀO
    Hook SessionStart matcher "compact" (.claude/settings.json).
    stdout: JSON có hookSpecificOutput.additionalContext — chỉ được xử lý khi exit 0.
    Mỗi lần chạy ghi một dòng vào .spec/reanchor.log để sau còn đo (--audit).

Exit codes: 0 luôn luôn (trừ --audit) — hook lỗi không được phép chặn phiên.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / ".spec" / "reanchor.log"

VIOLATION_TOOLS = {"AskUserQuestion": "luật #2 — hỏi QC sau pha S"}


def read(rel: str) -> str:
    try:
        return (ROOT / rel).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def phase() -> str:
    m = re.search(r"Pha hiện tại\s*:\s*(S|P|E|C)\b", read("STATE.md"))
    return m.group(1) if m else "?"


def release_luot() -> str:
    text = read("STATE.md")
    n = re.search(r"Release\s*:\s*(\d+)", text)
    k = re.search(r"Lần bàn giao\s*:\s*(\d+)", text)
    return f"release {n.group(1) if n else '?'} · lượt bàn giao {k.group(1) if k else '?'}"


COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def section(text: str, header: str, stop: str = "\n## ") -> str:
    i = text.find(header)
    if i < 0:
        return ""
    j = text.find(stop, i + len(header))
    body = text[i: j if j > 0 else len(text)]
    return re.sub(r"\n{3,}", "\n\n", COMMENT.sub("", body)).strip()


SEPARATOR = re.compile(r"^\|[\s|:-]+\|$")


def table_rows(block: str) -> list[str]:
    lines = [l for l in block.splitlines() if l.startswith("|")]
    lines = [l for l in lines if not SEPARATOR.match(l)]
    return [r for r in lines[1:] if r.strip("| ").strip()]


def live_state() -> str:
    state = read("STATE.md")
    out = []
    head = state[: state.find("---")] if "---" in state else state[:400]
    head = "\n".join(l for l in head.splitlines()
                     if not l.startswith(("# ", "> "))).strip()
    if head:
        out.append(head)
    try:  # môi trường + chế độ nguồn từ manifest — hỏng thì bỏ qua, hook không được gãy
        sys.path.insert(0, str(ROOT / "scripts"))
        import _counts as C  # noqa: E402
        mf = C.current_manifest()
        if mf.get("text"):
            out.append(f"**Môi trường test: {mf.get('moi_truong') or 'production'}** · "
                       f"quy trình dev: {mf.get('quy_trinh') or '?'} · "
                       f"repo nguồn CHỈ ĐỌC: `{mf.get('repo') or '?'}`")
    except Exception:
        pass
    rows = table_rows(section(state, "## Blocker"))
    if rows:
        out.append(f"**Blocker đang mở ({len(rows)}):**\n" + "\n".join(rows))
    n = re.search(r"Release\s*:\s*(\d+)", state)
    if n:
        plan = read(f"context/releases/r{n.group(1)}/TEST-PLAN.md")
        nguong = section(plan, "## 4.")
        if nguong:
            out.append("**Ngưỡng verdict đã khoá (TEST-PLAN §4 — KHÔNG sửa):**\n" + nguong)
    return "\n\n".join(out)


def rules() -> str:
    """Luật đọc THẲNG từ CLAUDE.md — chép cứng vào đây là tạo bản sao thứ tư của luật."""
    claude = read("CLAUDE.md")
    blocks = [b for b in (section(claude, "## 1. TÁM LUẬT"),
                          section(claude, "## 3. LUẬT #2")) if b]
    if blocks:
        return "\n\n".join(blocks)
    return "_Không đọc được `CLAUDE.md` — mở file đó ra đọc §1 và §3 trước khi làm tiếp._"


def build_context(source: str) -> str:
    p = phase()
    return "\n".join([
        f"# SPEC — nhồi lại sau `{source}`",
        "",
        f"Context vừa bị nén. Bản tóm tắt giữ được *đang làm gì* nhưng thường đánh rơi "
        f"*đang bị cấm gì*. Dưới đây là luật đọc thẳng từ `CLAUDE.md`. "
        f"Pha hiện tại: **{p}** ({release_luot()}).",
        "",
        rules(),
        "",
        "## Trạng thái sống",
        "",
        live_state() or "_(chưa đọc được STATE.md)_",
        "",
        "## Trước khi làm tiếp",
        "",
        f"Chạy `python3 scripts/gate.py` để biết gate pha {p} còn thiếu gì. "
        "Nếu không chắc đang dở việc gì: đọc `STATE.md` + RUNLOG của release, làm nốt "
        "TC/đợt gần nhất — đừng mở việc mới.",
    ])


def log_fire(payload: dict) -> None:
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "source": payload.get("source", "?"),
                "session_id": payload.get("session_id", "?"),
                "transcript": payload.get("transcript_path", ""),
                "phase": phase(),
            }, ensure_ascii=False) + "\n")
    except OSError:
        pass


def run_hook() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}
    log_fire(payload)
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": build_context(payload.get("source", "compact")),
        }
    }, ensure_ascii=False))
    return 0


# --- đo hiệu quả -------------------------------------------------------------

def iter_records(path: Path):
    try:
        with path.open(encoding="utf-8") as f:
            for line in f:
                try:
                    yield json.loads(line)
                except (json.JSONDecodeError, ValueError):
                    continue
    except OSError:
        return


def parse_ts(s: str):
    try:
        d = datetime.fromisoformat((s or "").replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def tools_after(transcript: Path, after_iso: str) -> list[tuple[str, str]]:
    mark = parse_ts(after_iso)
    if mark is None:
        return []
    found = []
    for rec in iter_records(transcript):
        if rec.get("type") != "assistant":
            continue
        ts = rec.get("timestamp", "")
        t = parse_ts(ts)
        if t is None or t <= mark:
            continue
        for block in (rec.get("message") or {}).get("content") or []:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                found.append((ts, block.get("name", "?")))
    return found


def audit() -> int:
    if not LOG.exists():
        print("Chưa có .spec/reanchor.log — hook chưa chạy lần nào.")
        print("Kiểm nối hook: grep -A6 SessionStart .claude/settings.json")
        return 0
    fires = [json.loads(l) for l in LOG.read_text(encoding="utf-8").splitlines() if l.strip()]
    print(f"\n=== Đã compact {len(fires)} lần ===\n")
    total = 0
    for i, fire in enumerate(fires, 1):
        print(f"[{i}] {fire['at']}  ·  pha {fire['phase']}  ·  {fire['source']}")
        tp = Path(fire.get("transcript") or "")
        if not tp.is_file():
            print("    (không đọc được transcript — bỏ qua)\n")
            continue
        after = tools_after(tp, fire["at"])
        print(f"    {len(after)} lượt gọi tool sau mốc này")
        if fire["phase"] == "S":
            print("    · pha S — hỏi QC là đúng luật, không soi AskUserQuestion\n")
            continue
        viol = [(ts, nm) for ts, nm in after if nm in VIOLATION_TOOLS]
        total += len(viol)
        for ts, nm in viol:
            print(f"    ✗ {ts}  {nm} — {VIOLATION_TOOLS[nm]}")
        if not viol:
            print("    ✓ không có dấu hiệu phá luật đo được bằng máy")
        print()
    print("=" * 60)
    print(f"Tổng vi phạm đo được bằng máy: {total}")
    print("""
Máy chỉ soi được AskUserQuestion. Ba thứ nặng hơn phải đọc tay:
  - PASS ghi vào RUNLOG mà thiếu bằng chứng (guard_verdict bắt lúc viết REPORT)
  - sửa ngưỡng sau khi nhìn kết quả (guard_frozen bắt lúc ghi)
  - lặng lẽ nới scope test đã khoá
""")
    return 0


if __name__ == "__main__":
    if "--audit" in sys.argv:
        sys.exit(audit())
    try:
        sys.exit(run_hook())
    except Exception as e:  # hook KHÔNG BAO GIỜ được làm hỏng phiên
        print(f"reanchor.py: {e}", file=sys.stderr)
        sys.exit(0)
