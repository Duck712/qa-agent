# Kỹ thuật phi chức năng

Yêu cầu phi chức năng hay **không được viết ra** — khi phân tích, duyệt ISO 25010 (`qa-knowledge/analysis-review.md` §4)
để hỏi; khi viết TC, dùng kỹ thuật dưới. Mọi ngưỡng (thời gian, bộ nhớ, tỉ lệ) phải do tài liệu/người dùng cho —
không tự đặt.

| Đặc tính | Kỹ thuật / cách kiểm | Bằng chứng |
|---|---|---|
| Hiệu năng | Đo thưa n ≤ 20, giãn ≥ 1s, p50/p95 so ngưỡng; theo 3 kích thước dữ liệu để thấy xu hướng; bộ nhớ ở 2 kích thước | từng lần đo + cách đo + giờ |
| Tải / stress | Chỉ trên môi trường riêng đã khai ở SCOPE §7 (k6, locust) | kịch bản + kết quả công cụ |
| Khả dụng (usability) | **10 heuristic Nielsen**: trạng thái hệ thống hiển thị · khớp ngôn ngữ người dùng · kiểm soát & thoát · nhất quán · phòng lỗi · nhận ra hơn nhớ · linh hoạt · tối giản · giúp nhận ra & sửa lỗi · trợ giúp. Mỗi vi phạm = phát hiện có ảnh + heuristic | ảnh + heuristic số mấy |
| Tiếp cận (a11y) | **WCAG 2.2 mức A/AA** (mức theo tài liệu, mặc định hỏi): tương phản ≥ 4.5:1 (chữ thường) / 3:1 (chữ lớn, thành phần UI) · đi hết bằng bàn phím, focus thấy được, không bẫy focus · ảnh có alt · ô nhập có nhãn · lỗi được đọc lên · không chỉ dùng màu để truyền tin · vùng chạm ≥ 24×24 (AA) · phóng 200% không vỡ · hộp thoại có role và tên | số đo tương phản, cây accessibility, ảnh |
| Tương thích | Pairwise trình duyệt/OS/thiết bị (`to-hop.md`) · bản cũ → mới giữ dữ liệu · API version cũ | cấu hình + ảnh/response |
| Tin cậy / khôi phục | Ngắt giữa chừng (đóng tab, kill, mất mạng, Ctrl-C) rồi tiếp tục: mất/trùng/dở? · retry · chạy lại idempotent | trạng thái trước/sau |
| Bảo mật | Agent `qa-security`, chỉ khi được phép | request/response |
| Bản địa hoá (i18n/l10n) | Chuỗi dài hơn (tiếng Đức, tiếng Việt có dấu) không vỡ layout · định dạng ngày/số/tiền theo locale · múi giờ · RTL nếu hỗ trợ · chuỗi chưa dịch / key lộ ra (`label.submit`) · sắp xếp theo bảng chữ cái có dấu | ảnh từng locale |
| Khả năng cài đặt / vận hành | Cài mới, nâng cấp, gỡ, rollback · cấu hình sai báo gì · log đủ để điều tra | lệnh + output |
