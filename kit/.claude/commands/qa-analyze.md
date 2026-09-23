---
description: Phân tích tài liệu → yêu cầu test được (REQ-…), vai, luồng, điểm mơ hồ
argument-hint: [đường dẫn/URL tài liệu hoặc tính năng cần phân tích]
---

Nguồn: $ARGUMENTS (trống → dùng `qa/QA.md §Nguồn tài liệu`) — tài liệu và/hoặc code của dự án.

1. Nạp skill `qa` và `qa-knowledge` — làm theo **`qa-knowledge/analysis-review.md`** (quy trình §1: đọc lướt → đọc theo góc
   nhìn → chấm tiêu chí chất lượng từng yêu cầu → yêu cầu ngầm ISO 25010 → mô hình hoá → đối chiếu code → rủi ro).
   Cộng `qa-knowledge/bug-patterns.md`. Đọc `qa/LESSONS.md`.
2. Đọc nguồn — chỉ phần liên quan; lớn thì đọc mục lục/cấu trúc trước. Nguồn chỉ đọc: không sửa.
   - **Tài liệu** cho biết sản phẩm *phải* làm gì → nguồn chính của REQ.
   - **Code** (route/endpoint, handler, validate, model/schema, config, quyền, test sẵn có, git diff của bản đang kiểm)
     cho biết hệ thống *đang* làm gì → dùng để: tìm bề mặt cần test (endpoint, lệnh, màn), dữ liệu và vai cần có,
     chỗ tài liệu bỏ sót, vùng vừa thay đổi (rủi ro cao), và cách gọi sản phẩm khi chạy test.
   - Code lệch tài liệu → mỗi chỗ lệch một dòng `ANALYSIS §5` (trích cả hai phía). Không có tài liệu → viết REQ từ
     code nhưng đánh dấu `(chờ trả lời #n)` + một dòng ANALYSIS §5 "đây có phải hành vi mong muốn không" — TC dựa
     trên REQ đó không được đưa vào run cho tới khi người dùng xác nhận.
   - Không tìm thấy/không mở được nguồn nào → hỏi người dùng, không phân tích từ trí nhớ.
3. Điền/cập nhật `qa/ANALYSIS.md`:
   - §2 vai và ma trận được/không được làm; §3 mỗi yêu cầu một `REQ-<TÍNH-NĂNG>-<n>` viết thành **hành vi
     quan sát được**, ghi target và nguồn (file + mục, hoặc `file:dòng` với code); §4 mô hình (use case luồng
     chính/thay thế/ngoại lệ, bảng trạng thái × sự kiện, CRUD); §6 bảng rủi ro xác suất × thiệt hại; §7 yêu cầu
     ngầm/phi chức năng; §8 thay đổi & ảnh hưởng (khi có bản trước).
   - §5 mọi điểm mơ hồ / thiếu / mâu thuẫn — mỗi điểm một đề xuất + rủi ro nếu hiểu sai. **Không** tự đoán
     thành yêu cầu; REQ nào phụ thuộc điểm chưa rõ thì đánh dấu `(chờ trả lời #n)`.
4. **Hỏi người dùng** các điểm §5 (gom một lượt, xếp theo mức chặn, mỗi câu kèm đề xuất + rủi ro). Luật nghiệp vụ
   khó nói rõ → hỏi bằng ví dụ cụ thể (example mapping, `qa-knowledge/analysis-review.md` §5). Ghi câu trả lời vào cột `Trả lời`,
   gỡ dấu `(chờ trả lời #n)`. Câu nào người dùng chưa trả lời → giữ nguyên, không tự điền.
5. Trình theo khuôn `qa-knowledge/analysis-review.md` §9: REQ theo tính năng, yêu cầu ngầm, điểm còn chờ trả lời, lệch tài liệu ↔
   code, rủi ro đề xuất; bước tiếp theo (thường `/qa-plan`).
