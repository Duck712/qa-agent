# Target `batch` — job, ETL, pipeline dữ liệu, worker, báo cáo sinh file

## Chạy bằng gì
Kích job bằng đúng đường chính thức: lệnh, API trigger, lịch (cron/Airflow/scheduler UI), đẩy message vào
queue test. Dữ liệu vào là **bộ dữ liệu mẫu của QA** (prefix `QA-<run-id>-`) đặt trong vùng test (thư mục/
bucket/schema test ở `QA.md`). Kiểm kết quả bằng đọc output (file, bảng test, API) — đọc bảng production
chỉ khi được cho phép, không ghi.

Job cần container / chạy lâu → chạy ở nơi người dùng quy định (quy ước máy/đội), không tự dựng hạ tầng.

## Chuẩn bị dữ liệu mẫu
Mỗi TC một bộ nhỏ có đáp án biết trước ở `qa/testdata/<TC-ID>/input/` + `expected/` (chép vào sandbox khi chạy):
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
- **Hiệu năng**: thời gian theo vài kích thước dữ liệu (đề xuất và hỏi; xem có tuyến tính không); tải lớn chỉ trên môi trường riêng (SCOPE §7).

## Bằng chứng tối thiểu
Checksum/mẫu dữ liệu vào · lệnh/cách kích + thời điểm · log job (trích đoạn có run id) · output hoặc truy vấn
đọc output + kết quả · diff so `expected/`.

## Cách ly, dữ liệu cố định, ngày chạy (bắt buộc)
- **Job tổng hợp** (output là dòng tổng theo ngày/cửa hàng, không mang prefix được): chỉ chạy khi **cả** nguồn vào và
  đích ra là vùng riêng của QA (`QA.md §Vùng dữ liệu test`). Không trỏ được → mọi TC `BLOCKED`, hỏi. Không bao giờ thả
  file test vào nguồn dùng chung của job thật; `cleanup` theo prefix không dọn được dòng tổng hợp.
- **Bộ dữ liệu cố định** của TC ở `qa/testdata/<TC-ID>/input/` + `expected/` (commit, không chứa dữ liệu thật) — dùng
  lại được cho regression. Khi chạy: chép vào `qa/sandbox/<run>/<TC>/`. Bằng chứng ở `qa/evidence/<run>/<TC>/`:
  `sha256sum` (macOS: `shasum -a 256`) input/expected, lệnh kích + thời điểm, log có run id, output, diff.
- **Ngày chạy**: tìm trong code tham số ngày (`--date`, biến môi trường, tham số DAG) để chạy cho ngày biên (29/2,
  31/12, quanh 0h, đổi giờ mùa hè). Không có → hỏi. Không tự đổi giờ máy/container, không sửa lịch cron dùng chung.
- **Đọc output trong DB**: là oracle bắt buộc → hỏi quyền đọc đúng bảng đích test ở bước chốt scope (SCOPE §7).
- **Không tài liệu, không ai biết luật đúng** → đề xuất chốt hành vi hiện tại làm mốc (`qa-testcase-design/ky-thuat/oracle.md` §6).
