#!/usr/bin/env python3
"""guard_ask.py — hook PreToolUse chặn AskUserQuestion ngoài pha S.

VÌ SAO CÓ FILE NÀY
    Luật #2 (không hỏi QC sau pha S) nếu chỉ cấm bằng văn xuôi thì trôi sau compact.
    File này biến lời dặn thành cơ chế — pha ≠ S thì tool bị chặn hẳn.

CHẠY NHƯ THẾ NÀO
    Claude Code gọi qua hook PreToolUse matcher "AskUserQuestion" (.claude/settings.json).
    Exit 0  → cho qua (pha S, hoặc không đọc được STATE.md — fail-open).
    Exit 2  → CHẶN tool; stderr được đưa lại cho model làm phản hồi.

    Ngoại lệ "hỏi thật" của luật #2 (đụng dữ liệu người dùng thật / phá môi trường không
    đảo được / hướng ra ngoài) KHÔNG đi qua tool này — hỏi bằng lời trong chat.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RULE_REMINDER = (
    "Mơ hồ → tự quyết theo TEST-PLAN/TEST-STRATEGY/HANDOVER, ghi 1 dòng context/DECISIONS.md, đi tiếp.\n"
    "Ngoài scope test → ghi context/BUGS.md trạng thái `deferred`, test tiếp phần còn lại.\n"
    "Chặn cứng sau khi đã tự thử hết cách → STATE.md §Blocker, TC đánh BLOCKED, chuyển việc khác.\n"
    "Ngoại lệ duy nhất (đụng dữ liệu người thật / không đảo ngược được / hướng ra ngoài): "
    "hỏi bằng lời trong chat, không qua tool này.\n"
)


def main() -> int:
    try:
        text = (ROOT / "STATE.md").read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return 0  # không có STATE — fail-open

    # Luật thật của #2 là "sau KHOÁ SCOPE không hỏi" — pha chỉ là proxy. Lỗi thực chiến
    # phổ biến nhất (bài học thực tế): quên đổi `Pha hiện tại : S → P` rồi hỏi suốt pha P.
    if re.search(r"^- \[x\] \*\*Scope khoá\*\*", text, re.MULTILINE):
        sys.stderr.write(
            "LUẬT #2 — scope test ĐÃ KHOÁ (STATE.md §Gate: Scope khoá ✓), không hỏi QC "
            "qua AskUserQuestion nữa, kể cả khi dòng pha còn ghi S.\n"
            "Nếu vừa rời pha S: cập nhật `Pha hiện tại : P` trong STATE.md cho đúng.\n"
            + RULE_REMINDER
        )
        return 2

    m = re.search(r"Pha hiện tại\s*:\s*(S|P|E|C)\b", text)
    if m is None:
        if "Pha hiện tại" in text:
            # Có dòng pha nhưng giá trị lạ — fail-open ở đây là mở lỗ đúng chỗ luật #2
            # cần kín nhất. Chặn kèm hướng dẫn: đang thật sự ở pha S thì sửa một dòng.
            sys.stderr.write(
                "STATE.md có dòng `Pha hiện tại:` nhưng giá trị không phải một mã pha "
                "(S | P | E | C).\n"
                "Sửa dòng đó về đúng một mã (ví dụ `Pha hiện tại : E`) rồi thao tác tiếp — "
                "hook guard_* và gate.py đều đọc đúng dòng này.\n"
            )
            return 2
        return 0  # STATE không theo khung SPEC — fail-open

    if m.group(1) == "S":
        return 0
    sys.stderr.write(
        f"LUẬT #2 — đang ở pha {m.group(1)}, không hỏi QC qua AskUserQuestion.\n"
        + RULE_REMINDER
    )
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # hook KHÔNG BAO GIỜ được làm hỏng phiên
        print(f"guard_ask.py: {e}", file=sys.stderr)
        sys.exit(0)
