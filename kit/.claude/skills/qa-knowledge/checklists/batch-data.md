# Checklist — Job / ETL / pipeline dữ liệu

> **Mục checklist là câu hỏi để thử, không phải kỳ vọng.** Kỳ vọng lấy từ tài liệu; tài liệu không nói → điểm hỏi.
> Không chép từ như "tử tế / rõ ràng / OK" vào Kỳ vọng. Trích nguồn trong TC: `Nguồn: <checklist> <số mục>`, vd `form-input 2.3`.

- [ ] 1.1 Số dòng vào = ra + bị loại (có lý do, có log); tổng cột tiền khớp
- [ ] 1.2 Null, chuỗi rỗng, số 0/âm/cực lớn, ngày biên, múi giờ quanh 0h, unicode
- [ ] 1.3 Dòng hỏng không làm chết cả job; vào dead-letter/báo lỗi, không lọt âm thầm
- [ ] 1.4 Chạy lại cùng input không nhân đôi; chết giữa chừng chạy lại tiếp đúng
- [ ] 1.5 Hai instance cùng lúc; message trùng; message sai thứ tự
- [ ] 1.6 Nguồn chết/chậm, đích đầy/không quyền → retry có giới hạn, cảnh báo
- [ ] 1.7 Schema nguồn đổi (thêm/bớt/đổi kiểu cột) → báo lỗi rõ
- [ ] 1.8 Lịch chạy theo múi giờ, cuối tháng, job trước chưa xong
- [ ] 1.9 Dữ liệu tenant/khách hàng không trộn lẫn giữa các lần chạy
- [ ] 1.10 Log có run id, số dòng, thời gian; thời gian chạy theo kích thước dữ liệu

## 2. Bổ sung
- [ ] 2.1 Dữ liệu đến muộn / chạy bù (backfill) cho ngày cũ → không trùng, không ghi đè sai
- [ ] 2.2 Đích ghi dở bị đọc giữa chừng → ghi có tính nguyên tử (file tạm rồi đổi tên / transaction)
- [ ] 2.3 CSV có BOM, dấu phân cách nằm trong ô có nháy, xuống dòng trong ô
