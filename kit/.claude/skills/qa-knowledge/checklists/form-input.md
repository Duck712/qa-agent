# Checklist — Form nhập liệu
> Áp dụng cho MỌI form. Mỗi field bắt buộc đi qua nhóm 1-3; cả form đi qua nhóm 4-5.

> **Mục checklist là câu hỏi để thử, không phải kỳ vọng.** Kỳ vọng lấy từ tài liệu; tài liệu không nói → điểm hỏi.
> Không chép từ như "tử tế / rõ ràng / OK" vào Kỳ vọng. Trích nguồn trong TC: `Nguồn: <checklist> <số mục>`, vd `form-input 2.3`.

## 1. Giá trị biên & kiểu dữ liệu
- [ ] 1.1 Để trống field bắt buộc → submit (phải có message rõ field nào)
- [ ] 1.2 Chỉ toàn khoảng trắng "   " → có bị coi là hợp lệ không?
- [ ] 1.3 Khoảng trắng đầu/cuối "  abc  " → hệ thống có trim không, trim ở đâu?
- [ ] 1.4 Đúng min length, min-1, đúng max length, max+1
- [ ] 1.5 Field số: 0, số âm, số thập phân, 1e10, chữ trong field số
- [ ] 1.6 Field ngày: 29/02 năm không nhuận, ngày quá khứ/tương lai, format khác locale

## 2. Ký tự đặc biệt & bảo mật đầu vào
- [ ] 2.1 Emoji 😀, tiếng Việt có dấu, chữ Hán/Ả Rập (unicode nhiều byte)
- [ ] 2.2 `<script>alert(1)</script>` → hiển thị lại ở đâu có bị execute không (XSS)
- [ ] 2.3 `' OR 1=1 --` trong field đi vào query/search (SQLi)
- [ ] 2.4 Ký tự `% _ * ? / \ " '` trong field search/filter
- [ ] 2.5 Paste 10.000 ký tự (không gõ tay) → UI + API xử lý sao?

## 3. Hành vi field
- [ ] 3.1 Copy-paste vào field bị chặn gõ (vd field số có chặn paste chữ không?)
- [ ] 3.2 Autofill của browser có phá layout/validate không?
- [ ] 3.3 Error message biến mất khi user sửa lại đúng chưa?

## 4. Submit
- [ ] 4.1 Double-click nút submit → tạo 2 bản ghi không? (race)
- [ ] 4.2 Submit → mất mạng giữa chừng → bật mạng lại, trạng thái ra sao?
- [ ] 4.3 Submit xong bấm Back → form còn data cũ? resubmit được không?
- [ ] 4.4 Mở 2 tab cùng form, submit cả 2 → conflict xử lý sao?
- [ ] 4.5 Nút submit có disable + loading indicator trong lúc chờ không?

## 5. Sau khi lưu
- [ ] 5.1 Data hiển thị lại ĐÚNG như đã nhập (đặc biệt unicode, xuống dòng)
- [ ] 5.2 Sửa rồi lưu → mở lại xem có đúng bản mới không (cache cũ?)
- [ ] 5.3 Giá trị nhập ở màn A hiển thị đúng ở màn B, C (list, detail, export)

## 6. Bổ sung
- [ ] 6.1 Trường bắt buộc có điều kiện (bắt buộc khi chọn X) → đổi lựa chọn qua lại
- [ ] 6.2 Gửi qua API giá trị dropdown ngoài danh sách → server từ chối
- [ ] 6.3 Rời trang khi có thay đổi chưa lưu → cảnh báo (theo tài liệu)
