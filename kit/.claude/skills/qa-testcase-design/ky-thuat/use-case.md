# Use case & kịch bản (scenario testing)

Tài liệu viết dạng user story / use case / quy trình → mỗi use case sinh ba loại TC:

| Luồng | Là gì | TC |
|---|---|---|
| **Chính** (main success) | Người dùng đi đúng, mọi thứ ổn | 1 TC, `Kiểu: normal`, đi hết từ đầu đến kết quả cuối |
| **Thay thế** (alternate) | Đường khác vẫn tới đích (thanh toán bằng ví thay thẻ, đăng nhập bằng Google) | 1 TC mỗi nhánh, `normal` |
| **Ngoại lệ** (exception) | Đường không tới đích (hết hàng, thẻ bị từ chối, mất mạng giữa chừng, hết phiên, huỷ giữa chừng) | 1 TC mỗi nhánh, `abnormal` — kiểm hệ thống **về trạng thái sạch** (không nửa vời, không trừ tiền, không dữ liệu ma) |

Cách làm:
1. Viết use case dạng bước đánh số (từ tài liệu; thiếu → dựng từ code/giao diện và hỏi xác nhận).
2. Ở **mỗi bước**, hỏi: người dùng làm khác đi được không (thay thế)? hỏng được không (ngoại lệ)? Ghi `2a`, `2b`…
3. Với user story: tiêu chí chấp nhận dạng **Given–When–Then** là luồng chính; mỗi "khi nào không…" là ngoại lệ.
   Story thiếu tiêu chí chấp nhận → dùng example mapping (`qa-knowledge/analysis-review.md` §5) để hỏi.
4. **Kịch bản nghiệp vụ** (scenario): ghép nhiều use case thành một câu chuyện thật của một persona
   (vd "quản lý mở ca → nhận 3 đơn → huỷ 1 → xuất báo cáo cuối ngày") — bắt lỗi ở chỗ nối giữa các tính năng.
   Mỗi persona chính ít nhất một kịch bản. R1 thêm kịch bản "ngày tồi tệ": luồng chính của persona + chèn lần lượt
   ≥ 3 ngoại lệ đã biết (mạng mất ở bước k, hết phiên ở bước k+1, dữ liệu bị người khác sửa ở bước k+2), kiểm hệ thống
   về trạng thái sạch sau mỗi ngoại lệ.

Ghi `Kỹ thuật: use case` (chỉ tên chuẩn); mã luồng (`UC-DATLICH 3a`) ghi ở `Nguồn:` hoặc tiêu đề TC.
