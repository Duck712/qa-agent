#!/usr/bin/env python3
"""guard_evidence.py — hook PreToolUse: ảnh/video chụp được PHẢI rơi vào evidence/.

VÌ SAO CÓ FILE NÀY
    `--output-dir` trong .mcp.json và frontmatter agent chỉ đặt thư mục MẶC ĐỊNH.
    Từng lời gọi vẫn khai được đường dẫn riêng — `filename: "../../../tmp/x.png"`,
    `saveTo: "/Users/…/Desktop/x.png"` — và `mobile_start_screen_recording` KHÔNG khai
    `output` thì ghi thẳng vào thư mục tạm của hệ điều hành. Bằng chứng rơi ra ngoài
    dự án là hỏng hai thứ cùng lúc:

      1. Gate E kiểm đường dẫn evidence TỒN TẠI dưới `evidence/` — ảnh nằm ở /tmp thì
         dòng PASS đó không bao giờ chứng minh được, phát hiện ra thì đã sang pha C.
      2. Ảnh chụp production mang dữ liệu thật; để nó nằm rải rác ngoài repo là rò rỉ
         thầm lặng, không ai dọn vì không ai biết nó ở đâu (lỗi hay gặp).

    Chặn lúc GHI là chỗ rẻ nhất: người thao tác biết ngay, sửa một tham số là xong.

CHẠY NHƯ THẾ NÀO
    Matcher trong .claude/settings.json:
      - các tool MCP ghi file: browser_take_screenshot (`filename`) ·
        mobile_save_screenshot (`saveTo`) · mobile_start_screen_recording (`output`) ·
        browser_run_code_unsafe (soi chuỗi code — heuristic).
      - "Bash": lưới phụ — chặn lệnh ghi/chép file ảnh-video tới đích ngoài repo.

    LUẬT: đường dẫn phải nằm trong `<repo>/evidence/`.
      · Tương đối: cấm mọi `..` (leo ra khỏi --output-dir); phần còn lại rơi trong
        evidence/ vì output-dir đã trỏ vào đó.
      · Tuyệt đối: resolve rồi đòi nằm dưới `<repo>/evidence/`.

    Fail-open có chủ đích: JSON hỏng / không có tham số đường dẫn → cho qua.

Exit codes: 0 cho qua · 2 chặn
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _counts as C  # noqa: E402

ROOT = C.ROOT
EVIDENCE = ROOT / "evidence"

MEDIA_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp",
             ".mp4", ".mov", ".webm", ".pdf"}

# tool → tên tham số mang đường dẫn (đọc từ schema thật của hai MCP server)
PATH_ARG = {
    "mcp__browser__browser_take_screenshot": "filename",
    "mcp__mobile__mobile_save_screenshot": "saveTo",
    "mcp__mobile__mobile_start_screen_recording": "output",
}

HOW = (
    "Bằng chứng phải nằm trong `evidence/` của repo SPEC:\n"
    "  · thô, MCP tự đổ:   evidence/_inbox/<vai>/…\n"
    "  · đã phân loại:     evidence/r<N>/luot-<k>/<TC-ID>/…   ← RUNLOG trỏ vào đây\n"
    "Cách sửa: bỏ tham số đường dẫn để MCP dùng `--output-dir` sẵn có, hoặc khai một "
    "tên tương đối KHÔNG có `..` (ví dụ `01-buoc1.png`).\n"
    "Quy ước đầy đủ: skill `spec-evidence` §1 · SPEC.md §3c.\n"
)


def verdict(raw: str) -> tuple[bool, str]:
    """(ok, lý do). Đường dẫn hợp lệ = nằm trong <repo>/evidence/."""
    raw = (raw or "").strip()
    if not raw:
        return True, ""
    p = Path(raw)
    if not p.is_absolute():
        if ".." in p.parts:
            return False, (f"đường dẫn tương đối `{raw}` có `..` — leo ra khỏi thư mục "
                           "bằng chứng đã cấu hình")
        return True, ""
    try:
        resolved = p.resolve()
        ev = EVIDENCE.resolve()
    except OSError:
        return True, ""
    if resolved == ev or ev in resolved.parents:
        return True, ""
    trong_repo = resolved == ROOT or ROOT in resolved.parents
    return False, (f"`{raw}` nằm {'trong repo nhưng NGOÀI evidence/' if trong_repo else 'NGOÀI repo SPEC'}"
                   f" (resolve → {resolved})")


def block(tool: str, ly_do: str, them: str = "") -> int:
    sys.stderr.write(f"CHẶN {tool} — ảnh/video chụp được đang ghi ra ngoài `evidence/`.\n"
                     f"Lý do: {ly_do}\n\n" + HOW + them)
    return 2


def check_bash(command: str) -> tuple[bool, str]:
    """Lưới phụ: lệnh Bash chép/ghi file ảnh-video tới ĐÍCH ngoài evidence/.
    Chỉ soi vị trí ghi rõ ràng (redirect, đích của cp/mv/rsync/install) — lệnh đọc
    thuần và thao tác trong repo đi qua."""
    for seg in re.split(r"&&|\|\||;", command):
        cands: list[str] = []
        for m in re.finditer(r"(?:>>?|\btee\b(?:\s+-a)?)\s*(\S+)", seg):
            cands.append(m.group(1))
        toks = [t for t in seg.strip().split() if t]
        while toks and ("=" in toks[0] or toks[0] in ("env", "command", "sudo")):
            toks = toks[1:]
        if toks and toks[0] in ("cp", "mv", "rsync", "install", "ditto"):
            plain = [a for a in toks[1:] if not a.startswith("-")]
            if plain:
                cands.append(plain[-1])
        for c in cands:
            c = c.strip("\"'")
            if Path(c).suffix.lower() not in MEDIA_EXT:
                continue
            ok, ly_do = verdict(c)
            if not ok:
                return False, ly_do
    return True, ""


def check_code(code: str) -> tuple[bool, str]:
    """Heuristic cho browser_run_code_unsafe: `page.screenshot({ path: '…' })` và
    họ hàng. Không bắt được mọi cách viết — đây là gờ giảm tốc, luật mới là lưới cuối."""
    for m in re.finditer(r"""\bpath\s*:\s*['"`]([^'"`]+)['"`]""", code or ""):
        ok, ly_do = verdict(m.group(1))
        if not ok:
            return False, ly_do
    return True, ""


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    tool = str(payload.get("tool_name") or "")
    ti = payload.get("tool_input") or {}
    if not isinstance(ti, dict):
        return 0

    if tool in PATH_ARG:
        arg = PATH_ARG[tool]
        raw = ti.get(arg)
        if raw is None:
            # Ghi âm/quay màn hình KHÔNG khai đường dẫn → mobile-mcp ghi vào thư mục
            # TẠM của hệ điều hành, tức ngoài repo. Đòi khai tường minh.
            if tool.endswith("start_screen_recording"):
                return block(tool,
                             f"thiếu `{arg}` — mobile-mcp sẽ ghi vào thư mục tạm ngoài repo",
                             "Khai `output` trỏ vào evidence/, ví dụ "
                             "`evidence/_inbox/mobile/luong-loi.mp4`.\n"
                             "Lưu ý: video KHÔNG commit (.gitignore chặn) — ghi đường dẫn "
                             "vào `ghi-chu.md` của TC.\n")
            return 0
        ok, ly_do = verdict(str(raw))
        return 0 if ok else block(tool, ly_do)

    if tool == "mcp__browser__browser_run_code_unsafe":
        ok, ly_do = check_code(str(ti.get("code") or ""))
        return 0 if ok else block(tool, ly_do)

    if tool == "Bash":
        ok, ly_do = check_bash(str(ti.get("command") or ""))
        return 0 if ok else block(
            "lệnh Bash", ly_do,
            "Lệnh đọc thuần và thao tác bên trong evidence/ không bị chặn.\n")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # hook KHÔNG BAO GIỜ được làm hỏng phiên
        print(f"guard_evidence.py: {e}", file=sys.stderr)
        sys.exit(0)
