# Bảng quyết định · ma trận phân quyền · ma trận CRUD

## 1. Bảng quyết định
Kết quả phụ thuộc **tổ hợp** điều kiện → liệt kê điều kiện (cột), hành động/kết quả (dòng dưới), mỗi quy tắc một TC.

| Điều kiện / Quy tắc | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|
| Khách thành viên | Y | Y | N | N |
| Đơn ≥ 500k | Y | N | Y | N |
| **→ Giảm giá** | 10% | 5% | 5% | 0 |
| **→ Miễn phí ship** | có | không | có | không |

- n điều kiện nhị phân → 2ⁿ quy tắc; **gộp** quy tắc có cùng kết quả mà một điều kiện không ảnh hưởng (ghi `–`).
- Quy tắc tài liệu không nói kết quả → điểm hỏi (bảng quyết định là cách nhanh nhất lộ lỗ của tài liệu).
- Cause-effect (nguyên nhân → hệ quả, có ràng buộc "loại trừ nhau", "cần") dùng khi điều kiện phụ thuộc lẫn nhau — cùng tinh thần, vẽ quan hệ trước rồi lập bảng.

## 2. Ghép vào TC
Mỗi cột một TC (hoặc một TC nhiều dòng dữ liệu nếu cùng bước). Ghi `Kỹ thuật: bảng quyết định` + mã quy tắc (`Q3`).

## 3. Ma trận phân quyền
Bảng vai × hành động (ANALYSIS §2) là bảng quyết định có hai điều kiện (vai, quan hệ với bản ghi). **Mỗi ô ✗ là
một TC bắt buộc**, chặn phải ở **server** (gọi thẳng API/URL/lệnh), không phải UI giấu nút.
| Hành động | Vai | Chủ bản ghi | Kỳ vọng |
|---|---|---|---|
| Sửa đơn | owner | của mình | cho |
| Sửa đơn | owner | tenant khác | chặn 403/404 |
| Sửa đơn | viewer | bất kỳ | chặn 403 |
| Sửa đơn | chưa đăng nhập | — | chặn 401 |
Ma trận lớn → `python3 .claude/qa-scripts/gen_matrix_tc.py <file> --feature QUYEN --target <t> --out qa/testcases/phan-quyen.md`.
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
