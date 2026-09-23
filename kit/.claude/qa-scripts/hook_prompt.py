#!/usr/bin/env python3
"""hook_prompt.py — hook UserPromptSubmit: tin nhắn trông như người dùng SỬA CÁCH LÀM → nhắc ghi bài học ngay.

Vì sao: luật "ghi LESSONS khi bị sửa lưng" nằm trong skill, agent dễ quên giữa lượt dài. Hook chỉ NHẮC (thêm ngữ
cảnh), không chặn, không tự ghi — agent vẫn phải tự xét đây có phải sửa lưng không. Không có qa/ → im lặng.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

PATTERNS = [
    r"lần sau", r"từ (?:giờ|nay|sau)(?: trở đi)?", r"\bđừng\b", r"không được tự", r"sai rồi", r"không phải (?:như )?(?:vậy|thế)",
    r"sao (?:lại|không|cứ)", r"tại sao (?:lại )?tự", r"tự (?:ý|suy diễn|suy ra|nghĩ ra|bịa|đoán|đặt)", r"đã (?:bảo|nói) (?:là|rồi)",
    r"bao nhiêu lần", r"lại quên", r"nhớ (?:là|giùm|giúp|nhé|kỹ)", r"ghi nhớ", r"rút kinh nghiệm", r"\bluôn luôn\b",
    r"không bao giờ", r"phải hỏi",
]


def main() -> int:
    import qa_check as q                          # noqa: E402
    if not (q.QA / "LESSONS.md").is_file():
        return 0
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace"))
    except ValueError:
        return 0
    text = unicodedata.normalize("NFC", str(payload.get("prompt") or "")).casefold()
    hits = [p for p in PATTERNS if re.search(p, text)]
    if not hits:
        return 0
    print("[qa-agent] Tin nhắn này có thể là người dùng sửa cách làm hoặc nhắc luật. Nếu đúng vậy: làm theo, và ngay "
          "trong lượt này thêm một dòng `qa/LESSONS.md` (Loại `cách làm`, Bài học viết thành việc cần làm khác đi, "
          "Nguồn: trích lời người dùng, Phạm vi áp nếu chỉ đúng cho một target/công đoạn, Trạng thái `mới`), rồi nói ra "
          "đã ghi. Trùng bài học có sẵn → không thêm dòng mới, nói bài đó đang bị vi phạm. Không phải sửa lưng → bỏ qua nhắc này.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"hook_prompt.py: {e}", file=sys.stderr)
        sys.exit(0)
