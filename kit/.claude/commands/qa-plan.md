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
   xác nhận mức) + loại test (gồm cả phi chức năng từ ANALYSIS §7) · regression (từ phân tích ảnh hưởng ANALYSIS §8) ·
   cấu hình tương thích (bộ pairwise `pairwise.py` nếu nhiều trình duyệt/OS/thiết bị/vai) · §3 ngoài phạm vi có
   lý do · §4 loại test theo từng target · §5 môi trường, bản, tài khoản, cách tạo/dọn dữ liệu · §6 tiêu chí đạt
   (giữ đúng định dạng ba dòng, đề xuất con số hợp mức rủi ro) · §7 quyền đặc biệt (bảo mật, tải — mặc định `không`).
4. **Hỏi người dùng**, gom một lượt: điểm mơ hồ còn mở ở `ANALYSIS §5`, phạm vi đề xuất, mức rủi ro, tiêu chí đạt,
   môi trường/tài khoản còn thiếu, quyền bảo mật/tải. Mỗi câu kèm đề xuất + rủi ro. Ghi trả lời vào `SCOPE §8`.
5. Người dùng đồng ý → `Trạng thái: CHỐT`, `Chốt bởi`, `Ngày chốt`; quyền đặc biệt → một dòng `DECISIONS.md`
   trích nguyên văn lời cho phép. Chưa đồng ý → giữ `NHÁP`, sửa theo góp ý, hỏi lại.
