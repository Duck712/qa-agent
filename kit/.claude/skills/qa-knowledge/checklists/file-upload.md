# Checklist — Upload file / media

> **Mục checklist là câu hỏi để thử, không phải kỳ vọng.** Kỳ vọng lấy từ tài liệu; tài liệu không nói → điểm hỏi.
> Không chép từ như "tử tế / rõ ràng / OK" vào Kỳ vọng. Trích nguồn trong TC: `Nguồn: <checklist> <số mục>`, vd `form-input 2.3`.

## 1. Loại & kích thước
- [ ] 1.1 Đúng size limit, limit+1 byte → bị từ chối có thông báo chỉ ra giới hạn (mã lỗi theo API doc), KHÔNG phải 500
- [ ] 1.2 File 0 byte, file không có extension
- [ ] 1.3 Đổi extension giả mạo: file .exe đổi tên thành .jpg → hệ thống check content-type thật hay chỉ tên?
- [ ] 1.4 File tên tiếng Việt có dấu, tên chứa `../`, tên 255+ ký tự, tên trùng file đã có
- [ ] 1.5 Định dạng ngoài whitelist (svg chứa script, html) → bị chặn không?

## 2. Quá trình upload
- [ ] 2.1 Ngắt mạng giữa chừng → retry được không? có file rác trên storage không?
- [ ] 2.2 Upload đồng thời nhiều file / nhiều tab
- [ ] 2.3 Cancel giữa chừng → trạng thái sạch không?

## 3. Sau upload
- [ ] 3.1 URL file trả về mở được từ browser NGOÀI mạng nội bộ không (public vs internal endpoint)?
- [ ] 3.2 Xóa bản ghi → file trên storage có bị xóa/orphan không?
- [ ] 3.3 File private có đoán được URL để truy cập không cần quyền không?
- [ ] 3.4 Ảnh: hiển thị đúng orientation (ảnh chụp dọc từ điện thoại), resize/thumbnail có méo không?

## 4. Bổ sung
- [ ] 4.1 Số file tối đa mỗi lần upload; tổng dung lượng nhiều file
- [ ] 4.2 Ảnh "pixel flood" (kích thước pixel khổng lồ, dung lượng nhỏ) và file nén "bom" (zip bomb) → không treo/tràn bộ nhớ (chỉ trên môi trường được phép)
- [ ] 4.3 File HTML/SVG tải lên rồi tải lại → trả `Content-Disposition: attachment` / MIME đúng, trình duyệt không render như trang
- [ ] 4.4 Metadata EXIF/GPS của ảnh bị gỡ nếu tài liệu yêu cầu
- [ ] 4.5 File mẫu EICAR (kiểm có quét virus) — chỉ khi người dùng cho phép
