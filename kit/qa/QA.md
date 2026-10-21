# QA — {{PROJECT_NAME}}

> Hồ sơ dự án kiểm thử. `python3 .claude/qa-scripts/qa_check.py` và các hook đọc các dòng `- Khoá: giá trị` ở đây — giữ nguyên tên khoá.

## Quy trình
<!-- Đội đang làm theo quy trình nào và QA ghép việc ra sao (skill qa §3). Phiên sau đọc để biết việc tiếp theo. -->
- Quy trình: 
- Mã ticket ngoài: <!-- vd Jira KAI-123, GitHub #45 — ghi vào trường Ticket: của TC/bug -->
- Việc tiếp theo: 
- Ngôn ngữ bàn giao: vi <!-- vi · en · ja — tiêu đề cột khi `qa_check.py export`; nội dung tài liệu bàn giao agent dịch khi được nhờ (skill qa §1.8). File trong qa/ luôn tiếng Việt -->
- Người chạy TC thủ công: <!-- ai nhận TC `Thực hiện: người` (vai/nhóm), gửi bằng chứng qua đâu — skill qa §7 -->

## Quy trình bắt buộc
<!-- Các bước PHẢI làm mỗi lần của công đoạn lặp lại (vd mỗi màn / mỗi run) + luật an toàn môi trường, người dùng đã chốt.
     Hook nạp TOÀN VĂN phần này đầu mỗi phiên và sau mỗi lần nén; có phần này thì bài học chỉ còn hiện tiêu đề (skill qa §6).
     Danh sách đánh số theo thứ tự làm, mỗi bước ghi nguồn ngắn (LESSONS ngày / DECISIONS #). Chỉ ghi luật hiện hành, gọn
     (qa_check nhắc khi > 8000 ký tự); chi tiết, cách xử sự cố, công cụ → bài học (toàn văn qua `lessons --for`).
     Trạng thái, lịch sử chạy → `Việc tiếp theo` / RUNLOG, không ghi ở đây. Trống = chưa dùng. -->

## Nguồn tài liệu
<!-- Mọi thứ mô tả sản phẩm cần test: PRD, user story, ticket, release note, API doc (OpenAPI), thiết kế, README... -->
<!-- và code của sản phẩm (repo, thư mục route/handler, schema, config, test sẵn có) — đọc để phân tích và biết cách gọi. -->
<!-- Phân tách bằng dấu phẩy: đường dẫn hoặc URL. -->
- Tài liệu: 
- Code: 

## Nguồn chỉ đọc
<!-- Thư mục code / tài liệu của sản phẩm mà QA KHÔNG được ghi vào (hook guard_readonly chặn). -->
<!-- Đường dẫn tuyệt đối hoặc tương đối so với thư mục dự án. Workspace qa/ nằm ngay trong repo sản phẩm thì ghi các thư mục code, ví dụ: src, app, lib -->
- Chỉ đọc: 

## Target
<!-- Mỗi thứ cần kiểm một dòng. Loại: web · mobile · api · desktop · cli · batch · ai · library · khác -->
<!-- Cách vào: URL (web/api) · bundle id + đường dẫn build (mobile) · đường dẫn app (desktop) · lệnh (cli/batch) · endpoint/model (ai) · tên gói + version (library) -->
| Target | Loại | Cách vào | Ghi chú |
|---|---|---|---|
| | | | |

## Môi trường
<!-- local · dev · staging · production (cách ly) · môi trường riêng cho hiệu năng (nếu có) -->
- Môi trường: 
- Bản đang kiểm: 
- Số tester song song / giới hạn worker (quy ước máy/đội): 

## Tài khoản & dữ liệu test
<!-- KHÔNG ghi mật khẩu thật ở đây — ghi tên biến trong qa/.env (không commit). -->
| Vai | Tài khoản | Biến mật khẩu/token | Ghi chú |
|---|---|---|---|
| | | | |

- Prefix dữ liệu test: QA-
- Cách tạo/dọn dữ liệu được phép: <!-- UI / API / lệnh sản phẩm / script qa/scripts — hỏi người dùng nếu chưa rõ -->
- Hộp thư/số điện thoại nhận thông báo test:

## Vùng dữ liệu test
<!-- Cho job/pipeline, kho tài liệu AI, bucket/schema… — thứ không gắn prefix QA- được. Trống → TC đụng tới `BLOCKED`, hỏi. -->
- Nguồn vào test (bucket/thư mục/queue):
- Đích ra test (schema/bảng/thư mục):
- Cách trỏ job/sản phẩm vào vùng test (cờ, biến môi trường, config):
- Kho tài liệu / tenant AI riêng của QA:
