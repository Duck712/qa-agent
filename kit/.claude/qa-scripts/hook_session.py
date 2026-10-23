#!/usr/bin/env python3
"""hook_session.py — hook SessionStart: nạp luật cốt lõi + quy trình bắt buộc (QA.md) + bài học đang hiệu lực + câu hỏi
còn chờ vào đầu mỗi phiên. Dự án có `QA.md §Quy trình bắt buộc` → quy trình nạp toàn văn, bài học chỉ tiêu đề (toàn văn qua
`lessons --for`); chưa có → bài học toàn văn như cũ.

Vì sao: bài học chỉ có ích khi được đọc lại. Slash command có bước đọc `qa/LESSONS.md`, nhưng người dùng chat tự do
(không gõ lệnh) hoặc phiên vừa được nén (compact) thì không — hook này bảo đảm mọi phiên đều thấy.
In ra stdout = thêm vào ngữ cảnh phiên. Không có qa/ → im lặng. Không bao giờ làm hỏng phiên (lỗi → exit 0).
Đầu ra giữ dưới `qa_check.HOOK_BUDGET`: Claude Code cắt stdout hook > 10.000 ký tự, chỉ đưa ~2.000 ký tự đầu vào phiên.
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
           "· Người dùng sửa cách làm → ghi một dòng qa/LESSONS.md (skill qa §6); trước khi ghi chạy `qa_check.py lessons --like` — có bài giống thì báo người dùng quyết thêm mới hay gộp. Bài học nghề QA ghi ở "
           "LESSONS.md, không ghi vào bộ nhớ riêng của Claude."]
    # Thứ tự ưu tiên trong trần q.HOOK_BUDGET: luật → quy trình bắt buộc → câu hỏi chờ → bài học (phần chỗ còn lại).
    used = lambda: sum(len(s) + 1 for s in out)
    qs = q.open_questions()
    clip = lambda s, n=200: s if len(s) <= n else s[:n - 1].rstrip() + "…"
    qline = (f"Câu hỏi còn chờ người dùng trả lời (ANALYSIS §5): {len(qs)} — " + "; ".join(clip(x) for x in qs[:5])
             + (" …" if len(qs) > 5 else "")) if qs else ""
    proc = q.procedure_block()
    if proc:
        out += ["", f"Quy trình bắt buộc của dự án (QA.md §{q.PROC_SECTION}) — làm đủ từng bước, không bỏ bước; tóm tắt / "
                    "bàn giao quy trình cũng nêu đủ:"]
        room = q.HOOK_BUDGET - used() - len(qline) - 2 - 600      # 600: tiêu đề + dòng đếm bài học tối thiểu
        if len(proc) > room:
            cut = proc.rfind("\n", 0, room)
            proc = (proc[:cut if cut > 0 else room] + f"\n⚠ Quy trình dài quá chỗ nạp đầu phiên — phần còn lại: ĐỌC NGAY "
                    f"qa/QA.md §{q.PROC_SECTION} trước khi làm (và rút gọn quy trình, `qa_check.py status` báo độ dài).")
        out.append(proc)
    if qline:
        out += ["", qline]
    b = q.lessons_brief(full=not proc, budget=q.HOOK_BUDGET - used() - 300)   # 300: dòng tiêu đề phần bài học
    if b:
        out += ["", "Bài học đang hiệu lực của dự án (áp dụng khi liên quan, nói ra đang áp bài nào):" if not proc else
                "Bài học đang hiệu lực — chỉ tiêu đề. Trước khi làm việc thuộc phạm vi bài nào: chạy "
                "`python3 .claude/qa-scripts/qa_check.py lessons --for <công đoạn / target>` đọc toàn văn rồi mới làm; "
                "nói ra đang áp bài nào:", b]
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # hook không bao giờ được làm hỏng phiên
        print(f"hook_session.py: {e}", file=sys.stderr)
        sys.exit(0)
