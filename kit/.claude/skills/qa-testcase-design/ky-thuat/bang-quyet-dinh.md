# Bảng quyết định · ma trận phân quyền · ma trận CRUD

## 1. Bảng quyết định
Kết quả phụ thuộc **tổ hợp** điều kiện → mỗi điều kiện một **dòng**, mỗi quy tắc một **cột**, kết quả ở các dòng
dưới; mỗi quy tắc (cột) một TC. Ví dụ (con số minh hoạ — dùng đúng luật trong tài liệu sản phẩm):

| Điều kiện / Quy tắc | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|
| Khách thành viên | Y | Y | N | N |
| Đơn ≥ 500k | Y | N | Y | N |
| **→ Giảm giá** | 10% | 5% | 5% | 0 |
| **→ Miễn phí ship** | có | không | có | không |

- n điều kiện nhị phân → 2ⁿ quy tắc; **gộp** quy tắc có cùng kết quả mà một điều kiện không ảnh hưởng (ghi `–`).
  Kiểm đủ: tổng quy tắc sau gộp (quy tắc có k dấu `–` tính 2^k) = 2ⁿ; tổ hợp không thể xảy ra ghi `N/A` + lý do.
- Điều kiện nhiều giá trị (loại khách: cá nhân / doanh nghiệp / đại lý) → bảng mở rộng (extended-entry): số quy tắc =
  tích số giá trị các điều kiện.
- Quy tắc tài liệu không nói kết quả → điểm hỏi (bảng quyết định là cách nhanh nhất lộ lỗ của tài liệu).
- Cause-effect (nguyên nhân → hệ quả, có ràng buộc "loại trừ nhau", "cần") dùng khi điều kiện phụ thuộc lẫn nhau — cùng tinh thần, vẽ quan hệ trước rồi lập bảng.

## 2. Ghép vào TC
Mỗi cột một TC (hoặc một TC nhiều dòng dữ liệu nếu cùng bước). Ghi `Kỹ thuật: bảng quyết định` (chỉ tên chuẩn); mã quy tắc (`Q3`) ghi ở `Nguồn:` hoặc tiêu đề TC.

## 3. Ma trận phân quyền
Bảng vai × hành động (ANALYSIS §2) là bảng quyết định có hai điều kiện (vai, quan hệ với bản ghi). **Mỗi ô ✗ là
một TC bắt buộc**, chặn phải ở **server** (gọi thẳng API/URL/lệnh), không phải UI giấu nút.
Viết ma trận đúng khuôn `gen_matrix_tc.py` đọc (ANALYSIS §2) — vai là cột, mỗi hành động một dòng, hành động trên bản
ghi của người khác / tenant khác là **dòng riêng** (chiều IDOR):
| Hành động | owner | viewer | chưa đăng nhập |
|---|---|---|---|
| Sửa đơn của mình | ✓ | ✗ | ✗ |
| Sửa đơn của người khác cùng tenant | ✗ | ✗ | ✗ |
| Sửa đơn của tenant khác | ✗ | ✗ | ✗ |
Mỗi ô ✗: bị chặn ở server, không đổi dữ liệu.
Mã cụ thể (401/403/404) lấy từ API doc; tài liệu không nói → hỏi. Lưu ý 403 và 404 khác nhau có thể lộ việc bản ghi tồn tại (bug-patterns #18).
Ma trận lớn → `python3 .claude/qa-scripts/gen_matrix_tc.py <file> --feature QUYEN --target <t> --req <REQ> --muc <mức người dùng chốt> --out qa/testcases/phan-quyen.md` (sinh khung; chỗ `<…>` phải điền trước khi chạy — qa_check chặn TC còn chỗ trống).
Nhớ các hành động phụ: export, download, autocomplete, đếm, thông báo, lịch sử — quyền hay chỉ gắn ở API chính.

## 4. Ma trận CRUD — vòng đời thực thể
Mỗi thực thể (đơn, người dùng, file, cấu hình) × Create / Read / Update / Delete (+ List, Export, Restore):
| Thực thể | C | R | U | D | Ghi chú |
|---|---|---|---|---|---|
| Đơn hàng | khách | khách, admin | khách (khi nháp), admin | admin (xoá mềm) | |
Từ ma trận sinh TC cho:
- mỗi ô có hành động → TC chức năng (bởi vai được phép) + TC phân quyền (vai không được phép);
- **hệ quả chéo**: xoá cha thì con ra sao (cascade/chặn/mồ côi); sửa xong mọi màn hiển thị có cập nhật (list, detail, export, thông báo); đọc sau xoá (404, không lộ trong tìm kiếm/cache);
- **ô trống** (không ai được Update/Delete) → xác nhận thật sự không làm được, kể cả qua API.
