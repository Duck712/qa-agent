# Kỹ thuật phi chức năng

Yêu cầu phi chức năng hay **không được viết ra** — khi phân tích, duyệt ISO 25010 (`qa-knowledge/analysis-review.md` §4)
để hỏi; khi viết TC, dùng kỹ thuật dưới. Mọi ngưỡng (thời gian, bộ nhớ, tỉ lệ) phải do tài liệu/người dùng cho —
không tự đặt.

| Đặc tính | Kỹ thuật / cách kiểm | Bằng chứng |
|---|---|---|
| Hiệu năng | Đo thưa theo nhịp đã chốt (`qa-targets` §3 mục 4); báo **median + max kèm n**; nhiều kích thước dữ liệu để thấy xu hướng (số kích thước đề xuất và hỏi); ngưỡng do tài liệu/người dùng cho | từng lần đo + cách đo + giờ |
| Tải / stress | Chỉ trên môi trường riêng đã khai ở SCOPE §7 (k6, locust) | kịch bản + kết quả công cụ |
| Khả dụng (usability) | **10 heuristic Nielsen**: trạng thái hệ thống hiển thị · khớp ngôn ngữ người dùng · kiểm soát & thoát · nhất quán · phòng lỗi · nhận ra hơn nhớ · linh hoạt · tối giản · giúp nhận ra & sửa lỗi · trợ giúp. Kết quả là **phát hiện/đề xuất** kèm mức nghiêm trọng Nielsen 0–4 (0 không phải vấn đề … 4 thảm hoạ), **không phải FAIL** — trừ khi tài liệu có tiêu chí cụ thể | ảnh + heuristic số mấy + mức 0–4 |
| Tiếp cận (a11y) | **WCAG 2.2** — mức A/AA theo tài liệu, mặc định hỏi. Checklist đầy đủ theo tiêu chí: `qa-knowledge/checklists/a11y.md` (tương phản, bàn phím, focus không bị che, thao tác kéo có thay thế, vùng chạm 24×24, reflow 320px, giãn chữ, thông báo trạng thái, không bắt nhập lại…) | số đo tương phản, cây accessibility, ảnh |
| Tương thích | Pairwise trình duyệt/OS/thiết bị (`to-hop.md`) · bản cũ → mới giữ dữ liệu · API version cũ | cấu hình + ảnh/response |
| Tin cậy / khôi phục | Ngắt giữa chừng (đóng tab, kill, mất mạng, Ctrl-C) rồi tiếp tục: mất/trùng/dở? · retry · chạy lại idempotent | trạng thái trước/sau |
| Bảo mật | Agent `qa-security`, chỉ khi được phép | request/response |
| Bản địa hoá (i18n/l10n) | Chuỗi dài hơn (tiếng Đức, tiếng Việt có dấu) không vỡ layout · định dạng ngày/số/tiền theo locale · múi giờ · RTL nếu hỗ trợ · chuỗi chưa dịch / key lộ ra (`label.submit`) · sắp xếp theo bảng chữ cái có dấu | ảnh từng locale |
| Khả năng cài đặt / vận hành | Cài mới, nâng cấp, gỡ, rollback · cấu hình sai báo gì · log đủ để điều tra | lệnh + output |
