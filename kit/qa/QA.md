# QA — {{PROJECT_NAME}}

> Hồ sơ dự án kiểm thử. `python3 .claude/qa-scripts/qa_check.py` và các hook đọc các dòng `- Khoá: giá trị` ở đây — giữ nguyên tên khoá.

## Quy trình
<!-- Đội đang làm theo quy trình nào và QA ghép việc ra sao (skill qa §3). Phiên sau đọc để biết việc tiếp theo. -->
- Quy trình: 
- Mã ticket ngoài: <!-- vd Jira KAI-123, GitHub #45 — ghi vào trường Ticket: của TC/bug -->
- Việc tiếp theo: 

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
