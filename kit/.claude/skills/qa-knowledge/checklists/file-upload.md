# Checklist — Upload file / media

## 1. Loại & kích thước
- [ ] Đúng size limit, limit+1 byte → phải trả lỗi RÕ RÀNG (413/400 + message), KHÔNG phải 500
- [ ] File 0 byte, file không có extension
- [ ] Đổi extension giả mạo: file .exe đổi tên thành .jpg → hệ thống check content-type thật hay chỉ tên?
- [ ] File tên tiếng Việt có dấu, tên chứa `../`, tên 255+ ký tự, tên trùng file đã có
- [ ] Định dạng ngoài whitelist (svg chứa script, html) → bị chặn không?

## 2. Quá trình upload
- [ ] Ngắt mạng giữa chừng → retry được không? có file rác trên storage không?
- [ ] Upload đồng thời nhiều file / nhiều tab
- [ ] Cancel giữa chừng → trạng thái sạch không?

## 3. Sau upload
- [ ] URL file trả về mở được từ browser NGOÀI mạng nội bộ không (public vs internal endpoint)?
- [ ] Xóa bản ghi → file trên storage có bị xóa/orphan không?
- [ ] File private có đoán được URL để truy cập không cần quyền không?
- [ ] Ảnh: hiển thị đúng orientation (ảnh chụp dọc từ điện thoại), resize/thumbnail có méo không?
