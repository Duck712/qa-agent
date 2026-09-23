# Dựa trên kinh nghiệm: error guessing · checklist · khám phá theo phiên

## 1. Error guessing có hệ thống
Không đoán bừa — đi từ danh sách kiểu lỗi: `qa-knowledge/bug-patterns.md` + checklist theo đối tượng + `qa/LESSONS.md`
của dự án + bug cũ trong `qa/BUGS.md` (lỗi hay tái phát ở chỗ cũ và chỗ tương tự). Mỗi kiểu lỗi áp được → một TC,
`Kỹ thuật: error guessing`, `Nguồn: bug-patterns #n`.

Tấn công lỗi (fault attacks) theo tầng: đầu vào (ký tự lạ, quá dài, sai kiểu, rỗng) · đầu ra (buộc hiện mọi thông
báo lỗi, tràn màn hình) · dữ liệu lưu (dữ liệu đã bị sửa từ nơi khác, dữ liệu cũ) · tính toán (tràn số, chia 0, làm
tròn) · môi trường (mạng, quyền file, đầy đĩa, giờ hệ thống).

## 2. Checklist-based
Checklist trong `qa-knowledge` là "những điều ai cũng phải thử". Với mỗi đối tượng trong phạm vi: duyệt checklist,
mục áp dụng được mà chưa có TC → viết TC; mục không áp dụng → ghi lý do bỏ trong bảng trình người dùng.

## 3. Khám phá theo phiên (session-based, SBTM)
Mỗi phiên là một đơn vị có kiểm soát — khuôn `qa/runs/_EXPLORE-TEMPLATE.md`:
- **Charter**: *Khám phá* <vùng> *với* <tài nguyên/kỹ thuật> *để tìm* <loại rủi ro>.
  Vd: "Khám phá luồng thanh toán với mã giảm giá và đổi số lượng giữa chừng để tìm sai tiền".
- **Thời lượng**: do người dùng chốt (tham khảo SBTM: ngắn ~60, thường ~90, dài ~120 phút). Hết giờ thì dừng.
- **Ghi chép liên tục**: đã đi đâu, dữ liệu gì, thấy gì; lỗi → bug có bằng chứng; câu hỏi → danh sách hỏi.
- **Tỉ lệ thời gian**: dựng môi trường / test / điều tra bug — để biết phiên bị nghẽn ở đâu.
- **Tỉ lệ đúng charter**: bao nhiêu thời gian đi đúng charter / đi lệch (cơ hội) — lệch nhiều thì charter chưa hợp.
- **Debrief** cuối phiên (theo PROOF: Past — đã làm gì · Results — tìm thấy gì · Obstacles — vướng gì · Outlook — còn
  lại gì, charter tiếp theo · Feelings — cảm nhận rủi ro): đã phủ / chưa phủ, rủi ro mới, TC mới đề xuất.
  Debrief trình người dùng; bug/câu hỏi trong phiên đi theo luật chung (hỏi, không tự quyết).

**Tour** gợi ý charter khi chưa biết bắt đầu từ đâu:
| Tour | Đi thế nào |
|---|---|
| Tính năng | Chạm mọi nút, menu, cài đặt ít nhất một lần |
| Tiền | Đi đúng những gì quảng cáo/khách trả tiền cho |
| Dữ liệu xấu | Đưa dữ liệu tồi tệ nhất vào mọi ô nhập |
| Người dùng mới | Lần đầu, không dữ liệu, không biết gì — màn rỗng, hướng dẫn |
| Người dùng lâu năm | Dữ liệu nhiều, lịch sử dài, cấu hình lạ |
| Ngược chiều | Làm mọi thứ theo thứ tự ngược, huỷ giữa chừng, bấm Back |
| Hạ tầng | Mạng chập chờn, tab ngủ, nhiều thiết bị cùng lúc |
| Chỗ vừa sửa | Quanh vùng code/tính năng mới đổi (git diff) |
Phát hiện đáng giữ → đề xuất TC mới (khám phá là nguồn TC, không thay TC).
