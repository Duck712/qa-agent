# Test case — <Tính năng>

> Một file một tính năng (`qa/testcases/<tinh-nang>.md`), một khối `## TC-…` một test case.
> File bắt đầu bằng `_` bị bỏ qua khi đếm. Khuôn chi tiết: skill `qa-testcase-design`.
> `VP:` = quan điểm test (qa/viewpoints/) đã được người dùng duyệt mà TC này hiện thực hoá — bắt buộc khi dự án có
> quan điểm test (`qa_check.py tc` nhắc; `tc --strict`, bắt buộc sạch trước run all/reg, báo lỗi); TC tái hiện bug
> (`Nguồn: BUG-…`) được miễn.
> `Regression: có` = đưa vào bộ regression · `Tag: smoke` = đưa vào bộ smoke · `Ticket:` = mã Jira/GitHub nếu đội dùng.

## TC-FEAT-001 — <điều được kiểm, viết theo hành vi người dùng>
- REQ: REQ-FEAT-1
- VP: VP-FEAT-001
- Target: <tên target trong QA.md>
- Loại: chức năng
- Kiểu: normal
- Mức: <mức người dùng chốt cho REQ ở SCOPE §2>
- Kỹ thuật: <tên chuẩn, cách nhau dấu phẩy — danh mục ở qa-testcase-design §1, vd: giá trị biên, chuyển trạng thái>
- Nguồn: REQ-FEAT-1
- Regression: không
- Tag: 
- Ticket: 
- Tiền điều kiện: <trạng thái hệ thống, vai đăng nhập>
- Dữ liệu: <giá trị cụ thể, mang prefix QA->
- Bước:
  1. <thao tác cụ thể>
  2. <thao tác cụ thể>
- Kỳ vọng:
  1. <điều quan sát được ở bước 1>
  2. <điều quan sát được ở bước 2>
- Bằng chứng cần: <theo skill qa-evidence, vd "ảnh bước 2 + URL trang (NN-url.txt)">
