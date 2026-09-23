# Checklist — Job / ETL / pipeline dữ liệu

- [ ] Số dòng vào = ra + bị loại (có lý do, có log); tổng cột tiền khớp
- [ ] Null, chuỗi rỗng, số 0/âm/cực lớn, ngày biên, múi giờ quanh 0h, unicode
- [ ] Dòng hỏng không làm chết cả job; vào dead-letter/báo lỗi, không lọt âm thầm
- [ ] Chạy lại cùng input không nhân đôi; chết giữa chừng chạy lại tiếp đúng
- [ ] Hai instance cùng lúc; message trùng; message sai thứ tự
- [ ] Nguồn chết/chậm, đích đầy/không quyền → retry có giới hạn, cảnh báo
- [ ] Schema nguồn đổi (thêm/bớt/đổi kiểu cột) → báo lỗi rõ
- [ ] Lịch chạy theo múi giờ, cuối tháng, job trước chưa xong
- [ ] Dữ liệu tenant/khách hàng không trộn lẫn giữa các lần chạy
- [ ] Log có run id, số dòng, thời gian; thời gian chạy theo kích thước dữ liệu
