#!/usr/bin/env python3
"""hook_session.py — hook SessionStart: nạp luật cốt lõi + bài học đang hiệu lực + câu hỏi còn chờ vào đầu mỗi phiên.

Vì sao: bài học chỉ có ích khi được đọc lại. Slash command có bước đọc `qa/LESSONS.md`, nhưng người dùng chat tự do
(không gõ lệnh) hoặc phiên vừa được nén (compact) thì không — hook này bảo đảm mọi phiên đều thấy.
In ra stdout = thêm vào ngữ cảnh phiên. Không có qa/ → im lặng. Không bao giờ làm hỏng phiên (lỗi → exit 0).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def main() -> int:
    import qa_check as q                          # noqa: E402 — tìm workspace theo CLAUDE_PROJECT_DIR
    if not (q.QA / "QA.md").is_file():
        return 0
    out = ["[qa-agent] Nhắc đầu phiên — luật không đổi:",
           "· Không bịa, không tự suy diễn: chỗ chưa rõ → hỏi người dùng (kèm điều đã thấy + cách hiểu + đề xuất), "
           "ghi nhãn `(chờ trả lời #n)`.",
           "· Tài liệu test (quan điểm test, test case) bám đặc tả: mỗi REQ/quan điểm trích NGUYÊN VĂN câu nguồn; "
           "điều đặc tả không nói → điểm hỏi hoặc `ngoài đặc tả` chờ người dùng duyệt.",
           "· Người dùng sửa cách làm → ghi ngay một dòng qa/LESSONS.md (skill qa §6). Bài học nghề QA ghi ở "
           "LESSONS.md, không ghi vào bộ nhớ riêng của Claude."]
    b = q.lessons_brief()
    if b:
        out += ["", "Bài học đang hiệu lực của dự án (áp dụng khi liên quan, nói ra đang áp bài nào):", b]
    qs = q.open_questions()
    if qs:
        out += ["", f"Câu hỏi còn chờ người dùng trả lời (ANALYSIS §5): {len(qs)} — " + "; ".join(qs[:5])
                + (" …" if len(qs) > 5 else "")]
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # hook không bao giờ được làm hỏng phiên
        print(f"hook_session.py: {e}", file=sys.stderr)
        sys.exit(0)
