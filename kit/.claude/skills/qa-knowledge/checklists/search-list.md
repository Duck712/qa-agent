# Checklist — Tìm kiếm / danh sách / lọc / sắp xếp / export

> **Mục checklist là câu hỏi để thử, không phải kỳ vọng.** Kỳ vọng lấy từ tài liệu; tài liệu không nói → điểm hỏi.
> Không chép từ như "tử tế / rõ ràng / OK" vào Kỳ vọng. Trích nguồn trong TC: `Nguồn: <checklist> <số mục>`, vd `form-input 2.3`.

- [ ] 1.1 Ký tự đặc biệt trong từ khoá: `%`, `_`, `'`, `"`, `\`, `*` → không lỗi, không khớp sai
- [ ] 1.2 Có dấu / không dấu / hoa thường / khoảng trắng đầu cuối → khớp theo tài liệu
- [ ] 1.3 Kết quả rỗng có thông điệp; 1 kết quả; đúng đầy trang; tràn sang trang 2
- [ ] 1.4 Lọc + sắp xếp + phân trang cùng lúc giữ đúng khi chuyển trang và khi tải lại (URL giữ trạng thái?)
- [ ] 1.5 Xoá/thêm bản ghi khi đang ở trang 2 → trang trống hay tự lùi
- [ ] 1.6 Không hiện bản ghi không có quyền xem (kể cả trong đếm tổng, autocomplete, gợi ý)
- [ ] 1.7 Export: đủ dòng (không cắt ở trang hiện tại), đúng quyền, mở được bằng Excel (UTF-8 BOM, dấu phẩy trong ô)
- [ ] 1.8 10.000+ bản ghi: thời gian phản hồi, UI không vỡ

## 2. Bổ sung
- [ ] 2.1 Gõ nhanh: phản hồi của lần tìm cũ về sau không đè kết quả lần tìm mới (race)
- [ ] 2.2 Sắp theo trường có giá trị trùng mà không có khoá phụ → bản ghi bị lặp hoặc lọt giữa các trang
