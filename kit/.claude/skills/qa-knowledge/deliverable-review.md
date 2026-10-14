# Review file kết quả test + evidence trước khi báo

> **Bắt buộc** (skill `qa` §1 luật 10): mỗi lần chạy xong / sửa xong một file giao (checklist kết quả, RUNLOG,
> REPORT, bảng tổng hợp, file Excel / tài liệu gửi khách) phải review **toàn bộ file + evidence** theo các mục dưới
> đây rồi mới báo xong. Lỗi lặt vặt (sai số đếm, công thức hỏng, chữ lệch, ảnh không khớp) làm người đọc mất niềm tin
> vào cả kết quả test — người dùng không phải người bắt lỗi này. (bài học từ dự án)

## 1. Trước khi review — độ phủ đã đủ chưa
- [ ] **Mọi item trong phạm vi có case normal + abnormal** đã chạy thật — ô nhập, ô chọn, nút, phím tắt, tìm kiếm,
      điều kiện lọc / in / xuất, danh sách. Normal: giá trị đúng, biên, trống, ≥ 2 bộ có dữ liệu + 1 bộ không dữ liệu.
      Abnormal: sai định dạng, ký tự lạ (toàn giác, khoảng trắng đầu/cuối, emoji, thẻ HTML, chuỗi kiểu SQL), thiếu một
      nửa điều kiện (chỉ có "từ" hoặc "đến"), giá trị ngoài miền (`checklists/form-input.md`, `checklists/abnormal.md`).
      Kể cả khi đội không viết TC mà chạy theo checklist có sẵn. Ca nào ngoài đặc tả → vẫn theo skill `qa` §1 luật 2.
- [ ] Kết quả ghi trong file nói được cả hai phía: normal ra sao, abnormal ra sao (thông báo lỗi, chặn nhập, cắt
      chữ…) — không chỉ "OK".

## 2. Tiêu chí review file
1. **Máy soát trước.** Dự án có script kiểm file (vd lệnh `check`) → chạy, phải sạch. Chưa có mà file giao lặp lại
   nhiều lần → đề xuất viết; mỗi lỗi người dùng bắt được lần đầu → thêm thành luật của script để không lặp lại.
2. **Thông tin đầu file**: người làm, ngày (đúng quy ước của đội: ngày chạy hay ngày kế hoạch), tên file đúng khuôn;
   không còn placeholder / dòng mẫu / tên mẫu ("Tester 1", "〇〇", "TBD").
3. **Số đếm và tổng**: đếm lại từ các dòng chi tiết — số mục, số đã kiểm, số đạt / lỗi, tỉ lệ — khớp ô tổng và khớp
   điều báo trong chat.
4. **Từng câu kết quả** đối chiếu với kết quả thật (log, ảnh, phản hồi): không viết quá điều đã test, nêu rõ tên đối
   tượng khi có ≥ 2, có kết quả normal + abnormal, mã bug / ticket đúng.
5. **Công thức** (file bảng tính):
   - so với file mẫu: mọi ô công thức của mẫu **còn đủ, không đổi**; công thức thêm chỉ khi quy ước của đội cho phép;
   - không ô nào hiện lỗi `#DIV/0!` `#REF!` `#NAME?` `#VALUE!` `#N/A` `#NUM!` (trừ `NA()` cố ý để biểu đồ bỏ trống điểm);
   - ô chữ không bắt đầu bằng `=` (Excel hiểu là công thức → `#NAME?`);
   - **giá trị lưu sẵn** của ô công thức = số tính lại từ dữ liệu (file ghi bằng script thường không được tính lại —
     trình xem không tính lại sẽ hiện số cũ); vùng cộng (SUM, COUNTIF) phủ hết các dòng có dữ liệu;
   - phép chia cho ô có thể bằng 0 trong tình huống thật (vd thực tế chạy sớm hơn kế hoạch → "số kế hoạch" = 0) →
     báo người dùng; công thức của mẫu khách thì **không tự sửa**.
6. **Evidence** — mở **từng** ảnh / file bằng chứng (đúng ảnh đã nhúng trong file giao, không chỉ ảnh tạm):
   **đúng** (khớp mô tả và mục nó làm bằng chứng, đúng bên trước / sau hoặc cũ / mới, đúng màn, đúng dữ liệu),
   **đủ** (mục nào có đối tượng cũng có bằng chứng; thấy được kết quả: thông báo lỗi, giá trị tự hiện, nội dung file
   xuất), **rõ đạt / lỗi** (chỗ cần nhìn được khoanh hoặc nêu trong mô tả, chữ đọc được) — `qa-evidence`.
7. **Trình bày**: phông / cỡ / định dạng ô như mẫu; định dạng số đúng loại (ô giờ / số không mang định dạng ngày);
   khoảng trắng và cách ghi đồng bộ trong file **và giữa các file cùng loại**; chữ không bị cắt (dòng đủ cao —
   Excel tự giãn tối đa 409.5pt, chữ dài hơn phải rút gọn).
8. **Quét ngang**: lỗi tìm thấy ở một file → quét mọi file cùng loại đã làm, sửa cùng một cách.

## 3. Báo
- Báo kết quả review **cùng lúc** với kết quả test: đã soát gì, sửa gì, còn gì chờ người dùng quyết.
- Thiếu một mục ở §1 hoặc §2 → chưa được báo việc đó là xong.
