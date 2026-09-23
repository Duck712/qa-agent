# Checklist — Form nhập liệu
> Áp dụng cho MỌI form. Mỗi field bắt buộc đi qua nhóm 1-3; cả form đi qua nhóm 4-5.

## 1. Giá trị biên & kiểu dữ liệu
- [ ] Để trống field bắt buộc → submit (phải có message rõ field nào)
- [ ] Chỉ toàn khoảng trắng "   " → có bị coi là hợp lệ không?
- [ ] Khoảng trắng đầu/cuối "  abc  " → hệ thống có trim không, trim ở đâu?
- [ ] Đúng min length, min-1, đúng max length, max+1
- [ ] Field số: 0, số âm, số thập phân, 1e10, chữ trong field số
- [ ] Field ngày: 29/02 năm không nhuận, ngày quá khứ/tương lai, format khác locale

## 2. Ký tự đặc biệt & bảo mật đầu vào
- [ ] Emoji 😀, tiếng Việt có dấu, chữ Hán/Ả Rập (unicode nhiều byte)
- [ ] `<script>alert(1)</script>` → hiển thị lại ở đâu có bị execute không (XSS)
- [ ] `' OR 1=1 --` trong field đi vào query/search (SQLi)
- [ ] Ký tự `% _ * ? / \ " '` trong field search/filter
- [ ] Paste 10.000 ký tự (không gõ tay) → UI + API xử lý sao?

## 3. Hành vi field
- [ ] Copy-paste vào field bị chặn gõ (vd field số có chặn paste chữ không?)
- [ ] Autofill của browser có phá layout/validate không?
- [ ] Error message biến mất khi user sửa lại đúng chưa?

## 4. Submit
- [ ] Double-click nút submit → tạo 2 bản ghi không? (race)
- [ ] Submit → mất mạng giữa chừng → bật mạng lại, trạng thái ra sao?
- [ ] Submit xong bấm Back → form còn data cũ? resubmit được không?
- [ ] Mở 2 tab cùng form, submit cả 2 → conflict xử lý sao?
- [ ] Nút submit có disable + loading indicator trong lúc chờ không?

## 5. Sau khi lưu
- [ ] Data hiển thị lại ĐÚNG như đã nhập (đặc biệt unicode, xuống dòng)
- [ ] Sửa rồi lưu → mở lại xem có đúng bản mới không (cache cũ?)
- [ ] Giá trị nhập ở màn A hiển thị đúng ở màn B, C (list, detail, export)
