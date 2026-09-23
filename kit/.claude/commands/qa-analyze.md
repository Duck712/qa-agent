---
description: Phân tích tài liệu → yêu cầu test được (REQ-…), vai, luồng, điểm mơ hồ
argument-hint: [đường dẫn/URL tài liệu hoặc tính năng cần phân tích]
---

Nguồn: $ARGUMENTS (trống → dùng `qa/QA.md §Nguồn tài liệu`) — tài liệu và/hoặc code của dự án.

1. Nạp skill `qa` và `qa-knowledge` (`bug-patterns.md`, `techniques-judgement.md §3`). Đọc `qa/LESSONS.md`.
2. Đọc nguồn — chỉ phần liên quan; lớn thì đọc mục lục/cấu trúc trước. Nguồn chỉ đọc: không sửa.
   - **Tài liệu** cho biết sản phẩm *phải* làm gì → nguồn chính của REQ.
   - **Code** (route/endpoint, handler, validate, model/schema, config, quyền, test sẵn có, git diff của bản đang kiểm)
     cho biết hệ thống *đang* làm gì → dùng để: tìm bề mặt cần test (endpoint, lệnh, màn), dữ liệu và vai cần có,
     chỗ tài liệu bỏ sót, vùng vừa thay đổi (rủi ro cao), và cách gọi sản phẩm khi chạy test.
   - Code lệch tài liệu → mỗi chỗ lệch một dòng `ANALYSIS §5` (trích cả hai phía). Không có tài liệu → viết REQ từ
     code nhưng đánh dấu `(từ code — chờ xác nhận)` và hỏi người dùng đó có phải hành vi mong muốn không.
   - Không tìm thấy/không mở được nguồn nào → hỏi người dùng, không phân tích từ trí nhớ.
3. Điền/cập nhật `qa/ANALYSIS.md`:
   - §2 vai và ma trận được/không được làm; §3 mỗi yêu cầu một `REQ-<TÍNH-NĂNG>-<n>` viết thành **hành vi
     quan sát được**, ghi target và nguồn (file + mục, hoặc `file:dòng` với code); §4 luồng chính và vòng đời trạng thái; §6 rủi ro.
   - §5 mọi điểm mơ hồ / thiếu / mâu thuẫn — mỗi điểm một đề xuất + rủi ro nếu hiểu sai. **Không** tự đoán
     thành yêu cầu; REQ nào phụ thuộc điểm chưa rõ thì đánh dấu `(chờ trả lời #n)`.
4. **Hỏi người dùng** các điểm §5 (gom một lượt, mỗi câu kèm đề xuất + rủi ro). Ghi câu trả lời vào cột `Trả lời`,
   gỡ dấu `(chờ trả lời)`. Câu nào người dùng chưa trả lời → giữ nguyên, không tự điền.
5. Trình: số REQ theo tính năng, điểm còn chờ trả lời, đề xuất bước tiếp theo (thường `/qa-plan`).
