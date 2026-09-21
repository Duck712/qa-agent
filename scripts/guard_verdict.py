#!/usr/bin/env python3
"""guard_verdict.py — hook PreToolUse (Write|Edit|MultiEdit): chưa test đủ thì chưa có verdict.

VÌ SAO CÓ FILE NÀY
    Verdict đã ký là hành động hướng ra ngoài không thu hồi được — dev sẽ hành động
    theo nó (fix, hay mở release kế). Viết REPORT khi còn TC chưa chạy / FAIL chưa có bug
    / PASS chưa có bằng chứng là báo cáo trên nền cát. Gate E bắt được nhưng gate chỉ BÁO
    — chỗ này chặn cứng lúc ghi, cùng triết lý "chặn deploy khi còn nợ" của các quy trình dev (vd guard_bc của VIPER).

CHẠY NHƯ THẾ NÀO
    Hai matcher cùng trỏ script này:
      - "Write|Edit|MultiEdit": soi tool_input.file_path là context/releases/r<N>/REPORT.md.
      - "Bash": soi lệnh VỪA nhắc REPORT.md VỪA mang token ghi (>>, sed -i, tee… —
        C.bash_writes_into). Số release lấy từ đường dẫn trong lệnh, không thấy thì
        lấy release hiện tại của STATE. Lệnh đọc thuần cho qua ngay.
    Chạy lại ĐÚNG các phép đếm của gate E qua module chung scripts/_counts.py
    (gate_e_missing) — gate và hook không bao giờ lệch nhau.

    Fail-open có chủ đích: không có STATE / RUNLOG / TEST-PLAN (release chưa tới pha E,
    hoặc release.py đang scaffold REPORT rỗng) → cho qua. Chưa có gì để mà theo thì không chặn.

Exit codes: 0 cho qua · 2 chặn
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _counts as C  # noqa: E402


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    tool = str(payload.get("tool_name") or "")
    ti = payload.get("tool_input") or {}

    if tool == "Bash":
        command = str(ti.get("command") or "")
        if not command or not C.bash_writes_into(command, "REPORT.md"):
            return 0
        m = re.search(r"context/releases/r(\d+)/REPORT\.md", command.replace("\\", "/"))
        n = int(m.group(1)) if m else 0
    else:
        fp = str(ti.get("file_path") or "")
        m = re.search(r"context/releases/r(\d+)/REPORT\.md$", fp.replace("\\", "/"))
        if not m:
            return 0
        n = int(m.group(1))

    st = C.state()
    if not st.get("release"):
        return 0  # không có STATE — fail-open
    if not n:
        n = st["release"]  # lệnh Bash không nêu rõ đường dẫn — coi là REPORT hiện tại
    if st["release"] != n:
        return 0  # sửa REPORT của release khác (vd bổ chú lịch sử) — gate không canh chỗ đó
    k = max(st.get("ban_giao") or 1, 1)

    # release.py scaffold REPORT khi RUNLOG chưa có lượt chạy — cho qua lúc đó
    rl = C.runlog(n)
    if not rl["exists"] or k not in rl["sections"]:
        if (C.ROOT / C.report_path(n)).exists() and rl["exists"]:
            sys.stderr.write(
                f"CHẶN ghi REPORT — RUNLOG chưa có mục `## Lượt chạy — bàn giao {k}`.\n"
                "Lượt ≥2 mở bằng `python3 scripts/release.py --retest` (đòi manifest "
                f"RELEASE-{k}.md). Chạy test xong mới viết báo cáo.\n"
            )
            return 2
        return 0

    problems = C.gate_e_missing(n, k)
    if not problems:
        return 0

    head = "\n".join(f"  ✗ {p}" for p in problems[:10])
    more = f"\n  … và {len(problems) - 10} mục nữa (python3 scripts/gate.py E)" \
        if len(problems) > 10 else ""
    sys.stderr.write(
        f"CHẶN ghi REPORT-r{n} — gate E còn {len(problems)} mục chưa xong "
        f"(lượt bàn giao {k}):\n{head}{more}\n\n"
        "Verdict đã ký là hành động không thu hồi được — chạy đủ TC, đủ bằng chứng, đủ "
        "severity rồi mới viết báo cáo (luật #8) — cùng tinh thần chặn deploy khi còn nợ "
        "tương thích ngược.\n"
    )
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # hook KHÔNG BAO GIỜ được làm hỏng phiên
        print(f"guard_verdict.py: {e}", file=sys.stderr)
        sys.exit(0)
