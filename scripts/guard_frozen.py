#!/usr/bin/env python3
"""guard_frozen.py — hook PreToolUse: ngưỡng ghi TRƯỚC là bất khả xâm phạm.

VÌ SAO CÓ FILE NÀY
    Ngưỡng verdict (TEST-PLAN §4) và chiến lược (TEST-STRATEGY) chốt ở pha S — sửa chúng
    sau khi đã nhìn kết quả test là cách tự lừa mình lịch sự nhất: đọc kết quả nào cũng
    thấy sản phẩm "đạt". Gate C so ngày làm backstop, nhưng backstop chỉ báo; chỗ này
    cần chặn cứng ngay lúc ghi — cùng triết lý guard_ask.

CHẠY NHƯ THẾ NÀO
    Hai matcher cùng trỏ script này:
      - "Write|Edit|MultiEdit": chặn khi tool_input.file_path là context/TEST-STRATEGY.md
        hoặc context/releases/r*/TEST-PLAN.md. File khác exit 0 ngay.
      - "Bash": chặn khi lệnh VỪA nhắc TEST-PLAN.md/TEST-STRATEGY.md VỪA mang token ghi
        (sed -i, >>, tee, mv/cp đích… — C.bash_writes_into, cùng con mắt guard_readonly).
        Lệnh đọc thuần (cat/grep/git log) cho qua ngay — workflow này hay append file
        bằng shell, thiếu nhánh Bash là "bất khả xâm phạm" chỉ đúng với tool Write/Edit.
    Pha S → cho qua. Pha P/E/C → exit 2. Dòng pha sai định dạng → chặn kèm hướng dẫn
    (đây là hàng rào cần kín nhất — fail-open ở đây là mở lỗ đúng chỗ luật #8 đứng).

    Fail-open: không có STATE / file đích chưa tồn tại (dự án mới scaffold) → cho qua.

Exit codes: 0 cho qua · 2 chặn
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _counts as C  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

TARGET = re.compile(r"(context/TEST-STRATEGY\.md|context/releases/r\d+/TEST-PLAN\.md)$")

FROZEN_MSG = (
    "LUẬT #8 — đang ở pha {pha}: TEST-PLAN và TEST-STRATEGY đã KHOÁ "
    "(ngưỡng ghi TRƯỚC khi nhìn kết quả, SPEC.md §1.1).\n"
    "· Phạm vi retest của lượt bàn giao mới → ghi vào RUNLOG mục lượt (release.py --retest tạo), "
    "không sửa TEST-PLAN.\n"
    "· Thấy ngưỡng/chiến lược sai → ghi 1 dòng DECISIONS + STATE §Blocker, đề xuất trong "
    "REPORT, sửa ở pha S của release sau.\n"
    "· Nâng `Lượt bàn giao tối đa` là chữ ký tay của QC — QC tự sửa, agent không sửa hộ.\n"
)


def block_unless_phase_s(extra: str = "") -> int:
    """0 nếu đang pha S (hoặc STATE không có/không theo khung — fail-open); 2 nếu khoá."""
    try:
        text = (ROOT / "STATE.md").read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return 0  # không có STATE — fail-open

    m = re.search(r"Pha hiện tại\s*:\s*(S|P|E|C)\b", text)
    if m is None:
        if "Pha hiện tại" in text:
            sys.stderr.write(
                "STATE.md có dòng `Pha hiện tại:` nhưng giá trị không phải S|P|E|C — "
                "sửa về đúng một mã rồi thao tác tiếp. TEST-PLAN/TEST-STRATEGY chỉ sửa "
                "được ở pha S.\n"
            )
            return 2
        return 0
    if m.group(1) == "S":
        return 0
    sys.stderr.write(FROZEN_MSG.format(pha=m.group(1)) + extra)
    return 2


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    tool = str(payload.get("tool_name") or "")
    ti = payload.get("tool_input") or {}

    if tool == "Bash":
        command = str(ti.get("command") or "")
        if not command or not C.bash_writes_into(command, "TEST-PLAN.md",
                                                 ("TEST-STRATEGY.md",)):
            return 0
        return block_unless_phase_s(
            "· Lệnh Bash này mang dấu hiệu GHI vào TEST-PLAN/TEST-STRATEGY — lệnh đọc "
            "thuần không bị chặn, tách phần ghi ra nếu đây là báo nhầm.\n")

    fp = str(ti.get("file_path") or "")
    if not fp:
        return 0
    norm = fp.replace("\\", "/")
    if not TARGET.search(norm):
        return 0
    try:
        target = Path(fp)
        if not target.is_absolute():
            target = ROOT / fp
        if not target.exists():
            return 0  # scaffold lần đầu (release.py / pha S dựng file) — cho qua
    except OSError:
        return 0

    return block_unless_phase_s()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # hook KHÔNG BAO GIỜ được làm hỏng phiên
        print(f"guard_frozen.py: {e}", file=sys.stderr)
        sys.exit(0)
