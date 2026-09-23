---
description: Lập kế hoạch / chốt scope test — phạm vi, rủi ro, loại test theo target, môi trường, tiêu chí đạt
argument-hint: [tên đợt, vd "sprint 12" | "release 2.3"]
---

Đợt: $ARGUMENTS. `qa/SCOPE.md` luôn là scope của đợt hiện tại; sang đợt mới mà SCOPE cũ đã CHỐT → chép nó thành
`qa/SCOPE-<đợt cũ>.md` để lưu, rồi soạn SCOPE.md mới (hỏi người dùng giữ lại gì từ đợt trước).

1. Nạp skill `qa`, `qa-targets` (bảng loại test §2, an toàn §3), `qa-knowledge/analysis-review.md` (§7 rủi ro,
   §8 ảnh hưởng), `qa-knowledge/techniques-judgement.md §4`.
   Đọc `qa/LESSONS.md` — bài học cũ có ảnh hưởng phạm vi/rủi ro thì nêu ra.
2. Đọc `qa/ANALYSIS.md` (chưa có → hỏi người dùng: phân tích tài liệu trước, hay lập scope từ mô tả của họ).
3. Soạn SCOPE (khuôn `qa/SCOPE.md`): §2 REQ trong phạm vi + mức R1/R2/R3 (từ bảng rủi ro ANALYSIS §6 — người dùng
   xác nhận mức — chưa xác nhận thì để trống cột Mức) + loại test (gồm cả phi chức năng từ ANALYSIS §7) · regression (từ phân tích ảnh hưởng ANALYSIS §8) ·
   cấu hình tương thích (bộ pairwise `python3 .claude/qa-scripts/pairwise.py` nếu nhiều trình duyệt/OS/thiết bị/vai) · §3 ngoài phạm vi có
   lý do · §4 loại test theo từng target · §5 môi trường, bản, tài khoản, cách tạo/dọn dữ liệu · §6 tiêu chí đạt
   (để trống cho tới khi người dùng chốt — chỉ **đề xuất** con số trong câu hỏi) · §7 quyền đặc biệt (bảo mật, tải, chạm
   DB staging — mặc định `không`; test AI: đề xuất N lần chạy và ngưỡng đạt, cả chi phí gọi model, rồi hỏi).
4. **Hỏi người dùng**, gom một lượt: điểm mơ hồ còn mở ở `ANALYSIS §5`, phạm vi đề xuất, mức rủi ro từng REQ, tiêu
   chí đạt, tỉ lệ bốc mẫu soi bằng chứng (SCOPE §6), môi trường/tài khoản/cách tạo-dọn dữ liệu còn thiếu, quyền bảo mật/tải/DB. Mỗi câu kèm đề xuất + rủi ro.
   Ghi trả lời đúng một nơi: yêu cầu → cột `Trả lời` ANALYSIS §5 (gỡ `(chờ trả lời #n)` ở REQ/TC liên quan); quyết định
   → DECISIONS.md. SCOPE §8 chỉ trỏ số tham chiếu.
5. Người dùng đồng ý → điền mức R + ba dòng tiêu chí đúng con số họ chốt, `Trạng thái: CHỐT`, `Chốt bởi`, `Ngày
   chốt`; quyền đặc biệt → một dòng `DECISIONS.md` trích nguyên văn lời cho phép. Chưa đồng ý → giữ `NHÁP`, sửa theo góp ý, hỏi lại.
