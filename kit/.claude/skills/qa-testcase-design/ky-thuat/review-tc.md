# Review bộ test case · ma trận truy vết

## 1. Ba lớp review
1. **Hình thức** — `python3 .claude/qa-scripts/qa_check.py tc`: trường bắt buộc, ID, normal+abnormal mỗi REQ, kỳ vọng mơ hồ, R1 < 2 kỹ thuật.
2. **Truy vết** — `python3 .claude/qa-scripts/qa_check.py trace` (thêm `--write` để ghi `qa/TRACE.md`): REQ × TC normal/abnormal × kỹ thuật × kết quả run gần nhất × bug. Đọc cột trống.
3. **Nội dung** — checklist §2, do người review (agent hoặc tester) đọc từng TC.

## 2. Checklist nội dung
**Phủ yêu cầu**
- [ ] Mọi REQ trong SCOPE có TC; mọi tiêu chí chấp nhận của story có TC riêng.
- [ ] Mỗi REQ có cả đường đúng và đường sai; R1 có kỹ thuật thuộc ≥ 2 họ.
- [ ] Mọi điểm mơ hồ đã trả lời được phản ánh vào TC (ANALYSIS §5, cột Trả lời).
- [ ] Yêu cầu phi chức năng trong phạm vi có TC (không chỉ chức năng).

**Phủ kỹ thuật** (theo kỹ thuật đã chọn cho REQ)
- [ ] Phân vùng: mỗi lớp không hợp lệ một TC riêng, có lớp rỗng và khoảng trắng.
- [ ] Biên: đủ hai phía mỗi mép; R1 đủ 3 giá trị; biên nhiều chiều cho ràng buộc chéo.
- [ ] Bảng quyết định: mọi quy tắc (sau gộp) có TC.
- [ ] Phân quyền: mọi ô ✗ có TC gọi thẳng server; có hành động phụ (export, đếm, autocomplete).
- [ ] Trạng thái: mọi chuyển hợp lệ; mọi ô ✗ R1; 1-switch cho R1.
- [ ] Use case: luồng chính + mọi luồng thay thế/ngoại lệ đã biết; ngoại lệ kiểm trạng thái sạch.
- [ ] Tổ hợp: bộ pairwise đã sinh, ràng buộc đúng, cặp R1 dùng tích đầy đủ.
- [ ] Có code: mọi nhánh/validate/mã lỗi/điểm kiểm quyền quan trọng có TC chạm tới.
- [ ] Không có oracle: đã chọn oracle và ghi `Kỹ thuật: metamorphic` / `property` / `rubric` / `mốc hành vi` (tên chuẩn).

**Chất lượng từng TC**
- [ ] Bắt được một kiểu hỏng nêu được thành lời; không trùng TC khác (cùng lớp, cùng bước, cùng kỳ vọng → gộp).
- [ ] Bước cụ thể, người lạ chạy được; dữ liệu cụ thể có prefix; tiền điều kiện dựng được.
- [ ] Kỳ vọng quan sát được ở **từng bước**; không "hoạt động đúng"; không lấy hành vi hiện tại của code làm kỳ vọng khi tài liệu nói khác.
- [ ] `Bằng chứng cần` đúng loại (skill `qa-evidence`).
- [ ] Mọi giá trị cụ thể trong Kỳ vọng (con số, thông điệp, mã trạng thái) có nguồn; không nguồn → điểm hỏi, không phải kỳ vọng; không có kỳ vọng hai đáp án "A hoặc B".
- [ ] Mỗi kỳ vọng ứng với một bước có thật; TC nhiều dòng dữ liệu ghi rõ kỳ vọng từng dòng.
- [ ] `Mức:` khớp mức người dùng chốt ở SCOPE §2; `Kỹ thuật:` dùng tên chuẩn; REQ R1 có ≥ 2 họ kỹ thuật.
- [ ] `Mức:` lệch rõ với bảng rủi ro ANALYSIS §6 → nêu thành câu hỏi cho người dùng, không tự đổi; `Regression`/`Tag` đặt có chủ đích.
- [ ] TC tái hiện cho mọi bug S1/S2 đã đóng.

## 3. Kết quả review — trình người dùng
```
Bộ TC <tính năng>: <n> TC · REQ phủ <x>/<y> · normal/abnormal <a>/<b>
Lỗ phủ: <REQ/kỹ thuật/ô ma trận chưa có TC>
TC thừa/trùng: <danh sách + đề xuất gộp>
Kỳ vọng mơ hồ / sai nguồn: <danh sách>
Chủ động bỏ: <mục checklist + lý do>
Đề xuất: <thêm/sửa/bỏ> — chờ người dùng đồng ý mới sửa TC người khác viết
```
