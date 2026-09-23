---
description: Tạo quan điểm test (test viewpoint) cho tính năng / REQ — bám đặc tả, trích nguyên văn, người dùng duyệt
argument-hint: <tính năng | REQ-… | "review">
---

Việc: $ARGUMENTS

1. Nạp skill `qa`, `qa-testcase-design` — làm theo **`qa-testcase-design/ky-thuat/quan-diem.md`**; `qa-knowledge`
   (checklist hợp đối tượng — chỉ để gợi ý góc nhìn). Đọc `qa/LESSONS.md` (bài học loại `lỗ quan điểm` của tính năng này).
2. Đọc REQ liên quan ở `qa/ANALYSIS.md` (§3 + mô hình §2/§4 + câu trả lời §5) và **mở lại tài liệu nguồn** của từng REQ
   (cột Nguồn) — quan điểm phải trích từ tài liệu gốc, không trích lại từ Mô tả của REQ. Không mở được nguồn → hỏi
   người dùng, không viết từ trí nhớ. REQ còn `(chờ trả lời #n)` → quan điểm của nó cũng mang nhãn đó.
   Chưa có ANALYSIS → hỏi người dùng: phân tích tài liệu trước (`/qa-analyze`), hay chỉ ra tài liệu để làm thẳng.
3. Viết/bổ sung `qa/viewpoints/<tinh-nang>.md` theo khuôn `qa/viewpoints/_TEMPLATE.md`, mọi dòng `nháp`:
   - mỗi dòng một điều cần kiểm, `Nguồn` + `Trích nguyên văn` câu gốc; không nói nhiều hơn câu trích;
   - mỗi REQ ≥ 1 normal + ≥ 1 abnormal — đặc tả không nói về đường sai → câu hỏi + đề xuất quan điểm `ngoài đặc tả`;
   - gợi ý từ checklist/bug-patterns/yêu cầu ngầm/bài học mà đặc tả không nói → `Nguồn: ngoài đặc tả — <…>`, gom nhóm riêng;
   - điều chưa rõ → `(chờ trả lời #n)` ở cột Quan điểm + một dòng ANALYSIS §5. **Không tự điền kỳ vọng.**
   Việc là "review" → không viết mới: review theo `qa-testcase-design/ky-thuat/quan-diem.md` §3, báo lỗ/trùng/lệch nguồn, sửa khi người dùng đồng ý.
4. `python3 .claude/qa-scripts/qa_check.py vp <tính năng>` → sửa tới khi sạch; `python3 .claude/qa-scripts/qa_check.py src --list`
   → nguồn máy không mở được (URL/pdf/docx) hoặc bộ lớn (≥ 20 dòng) → spawn `qa-source-check` (kèm tính năng + danh sách).
   Lệch nguồn nó trả về → sửa trích dẫn cho đúng hoặc chuyển thành câu hỏi; **không** giữ quan điểm không có căn cứ.
5. Trình theo khuôn `qa-testcase-design/ky-thuat/quan-diem.md` §3 và **hỏi người dùng duyệt** — gom một lượt: quan điểm theo đặc tả (duyệt cả bộ
   hay từng dòng), nhóm ngoài đặc tả (từng dòng: dùng / bỏ), câu hỏi mở. Người dùng đồng ý → đổi `nháp` → `duyệt`
   (ngoài đặc tả: `duyệt (DECISIONS #n)` + một dòng DECISIONS trích nguyên văn), ghi `Duyệt bởi`, `Ngày duyệt`;
   dòng bị bác → `bỏ`. Bước tiếp theo: `/qa-plan` (chưa chốt scope) hoặc `/qa-testcase <tính năng>`.
