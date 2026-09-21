#!/usr/bin/env python3
"""guard_readonly.py — hook PreToolUse: repo nguồn là đầu vào CHỈ ĐỌC (luật #4).

VÌ SAO CÓ FILE NÀY
    SPEC kiểm thử độc lập — giá trị của nó nằm ở chỗ KHÔNG đụng vào sản phẩm. Ghi một
    byte vào repo nguồn (dù là "sửa hộ cho nhanh" hay "thả bug vào repo của dev") là
    phá cả tính độc lập lẫn hợp đồng "SPEC chỉ báo cáo trong repo SPEC". Cấm bằng văn
    xuôi không giữ được luật, nhất là sau compact — nên chặn cứng lúc ghi.

CHẠY NHƯ THẾ NÀO
    Hai matcher cùng trỏ script này (.claude/settings.json):
      - "Write|Edit|MultiEdit": chặn khi tool_input.file_path nằm dưới repo nguồn.
      - "Bash": chỉ chặn khi lệnh VỪA chứa đường dẫn repo nguồn VỪA mang token ghi
        (>, >>, tee, rm/mv/cp có đích trong đó, sed -i, git -C <repo> subcommand ghi).
        Lệnh đọc thuần (cat/grep/ls/git log/diff/show) cho qua ngay.

    Đường dẫn đọc từ manifest của lượt hiện tại: dòng `Repo nguồn:` (repo code hoặc thư
    mục tài liệu bàn giao) — định dạng VIPER cũ `Repo VIPER:` vẫn đọc.
    Fail-open có chủ đích: không có STATE/manifest/JSON hỏng → cho qua — gate S sẽ bắt
    manifest thiếu; hook an toàn không được chặn nhầm phiên.

Exit codes: 0 cho qua · 2 chặn
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _counts as C  # noqa: E402

# Phép dò "lệnh Bash có ghi vào đường dẫn này không" nằm ở C.bash_writes_into —
# dùng chung với guard_frozen/guard_verdict (cùng một con mắt, không lệch nhau).

MSG = (
    "LUẬT #4 — repo nguồn là ĐẦU VÀO CHỈ ĐỌC.\n"
    "SPEC không sửa sản phẩm, không sinh file cho dev. Phát hiện/bug ghi vào "
    "context/BUGS.md và REPORT của repo SPEC — QC chuyển cho dev theo kênh của họ.\n"
    "Cần bản chụp tài liệu thì COPY vào intake/releases/r<N>/nguon/ (VIPER: viper/) — "
    "mirror, không đụng bản gốc.\n"
)


def source_str() -> str | None:
    vr = C.source_root()
    return str(vr) if vr else None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # fail-open
    repo = source_str()
    if not repo:
        return 0  # chưa có manifest — gate S sẽ nhắc
    # Dạng viết trong manifest (có thể chưa resolve symlink / tương đối) cũng phải bắt,
    # vì lệnh Bash thường chép nguyên chuỗi đó.
    raw = str(C.current_manifest().get("repo") or "")
    aliases = (raw,) if raw and raw != repo else ()

    tool = str(payload.get("tool_name") or "")
    ti = payload.get("tool_input") or {}

    if tool in ("Write", "Edit", "MultiEdit"):
        fp = str(ti.get("file_path") or "")
        if not fp:
            return 0
        try:
            p = Path(fp)
            if not p.is_absolute():
                p = C.ROOT / fp
            resolved = str(p.resolve())
        except OSError:
            return 0
        if resolved.startswith(repo) or (raw and str(Path(fp)).startswith(raw)):
            sys.stderr.write(f"CHẶN ghi `{fp}` — nằm trong repo nguồn ({repo}).\n" + MSG)
            return 2
        return 0

    if tool == "Bash":
        command = str(ti.get("command") or "")
        if C.bash_writes_into(command, repo, aliases):
            sys.stderr.write(
                f"CHẶN lệnh Bash có dấu hiệu GHI vào repo nguồn ({repo}).\n" + MSG
                + "Lệnh đọc thuần (cat/grep/ls/git log|diff|show) không bị chặn — "
                "tách phần ghi ra khỏi lệnh nếu đây là báo nhầm.\n"
            )
            return 2
        return 0

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # hook KHÔNG BAO GIỜ được làm hỏng phiên
        print(f"guard_readonly.py: {e}", file=sys.stderr)
        sys.exit(0)
