# Target `batch` — job, ETL, pipeline dữ liệu, worker, báo cáo sinh file

## Chạy bằng gì
Kích job bằng đúng đường chính thức: lệnh, API trigger, lịch (cron/Airflow/scheduler UI), đẩy message vào
queue test. Dữ liệu vào là **bộ dữ liệu mẫu của QA** (prefix `QA-<run-id>-`) đặt trong vùng test (thư mục/
bucket/schema test ở `QA.md`). Kiểm kết quả bằng đọc output (file, bảng test, API) — đọc bảng production
chỉ khi được cho phép, không ghi.

Job cần container / chạy lâu → chạy ở nơi người dùng quy định (CLAUDE.md toàn cục của máy), không tự dựng hạ tầng.

## Chuẩn bị dữ liệu mẫu
Mỗi TC một bộ nhỏ có đáp án biết trước (`qa/sandbox/<run>/<TC>/input/` + `expected/`):
dòng hợp lệ điển hình · dòng biên (null, chuỗi rỗng, số 0/âm/rất lớn, ngày 29/2, múi giờ quanh 0h) ·
dòng hỏng (sai kiểu, thiếu cột, trùng khoá, encoding lạ) · bộ lớn để đo (sinh bằng script, ghi seed).

## Công thức
- **Đúng dữ liệu**: số dòng vào = ra + bị loại (có lý do) · tổng/checksum cột tiền khớp · mẫu từng dòng biên đúng như `expected/`.
- **Dòng hỏng**: bị loại/đưa vào dead-letter có log, **không** làm chết cả job, không lọt âm thầm.
- **Idempotent / chạy lại**: chạy 2 lần cùng input → không nhân đôi · chạy lại sau khi chết giữa chừng → tiếp tục đúng, không mất/trùng.
- **Thứ tự & đồng thời**: 2 instance cùng lúc (khoá?) · message đến sai thứ tự · message trùng.
- **Phụ thuộc lỗi**: nguồn dữ liệu chết/chậm giữa job, đích đầy/không có quyền → retry có giới hạn, báo lỗi rõ.
- **Lịch chạy**: đúng giờ theo múi giờ cấu hình, đổi giờ mùa hè, cuối tháng, job trước chưa xong thì job sau làm gì.
- **Schema thay đổi**: thêm/bớt cột ở nguồn → job báo lỗi rõ hay âm thầm sai.
- **Giám sát**: log có run id, số dòng, thời gian; lỗi có cảnh báo tới kênh test.
- **Hiệu năng**: thời gian theo 3 kích thước dữ liệu (tuyến tính?); tải lớn chỉ trên môi trường riêng (SCOPE §7).

## Bằng chứng tối thiểu
Checksum/mẫu dữ liệu vào · lệnh/cách kích + thời điểm · log job (trích đoạn có run id) · output hoặc truy vấn
đọc output + kết quả · diff so `expected/`.
