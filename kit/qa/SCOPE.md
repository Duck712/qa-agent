# SCOPE — {{PROJECT_NAME}}

> `/qa-plan`. Người dùng chốt file này trước khi chạy test. Mọi con số (mức R, tiêu chí đạt) do **người dùng** xác nhận
> — QA chỉ đề xuất. Sau khi CHỐT, tiêu chí đạt (§6) không sửa theo kết quả — muốn đổi thì chốt lại và ghi DECISIONS.

- Trạng thái: NHÁP
- Chốt bởi: 
- Ngày chốt: 

## 1. Mục tiêu
<!-- Một câu: lượt test này trả lời câu hỏi gì (vd "bản 2.3 có đủ điều kiện phát hành không") -->

## 2. Trong phạm vi
<!-- Mỗi REQ một dòng (có thể nhiều REQ một ô, cách nhau dấu phẩy). Mức R1/R2/R3: đề xuất từ bảng rủi ro ANALYSIS §6,
     NGƯỜI DÙNG xác nhận — chưa xác nhận thì để trống, qa_check sẽ nhắc. -->
| REQ | Mô tả ngắn | Target | Mức | Loại test |
|---|---|---|---|---|
| | | | | |

## 3. Ngoài phạm vi
| Hạng mục | Lý do |
|---|---|
| | |

## 4. Loại test theo target
<!-- Đánh dấu loại áp dụng. Danh mục loại + công cụ: skill qa-targets. Loại "khác": thêm cách điều khiển, bằng chứng
     tối thiểu, vùng an toàn (qa-targets/khac.md) — người dùng duyệt. -->
| Target | Loại | Loại test áp dụng | Bằng chứng tối thiểu / vùng an toàn (loại khác) |
|---|---|---|---|
| | | | |

## 5. Môi trường & dữ liệu
<!-- Môi trường, bản đang kiểm, tài khoản từng vai (tham chiếu QA.md), cách tạo/dọn dữ liệu test -->

## 6. Tiêu chí đạt
<!-- NGƯỜI DÙNG chốt ba dòng dưới (qa_check.py đọc đúng định dạng này). Để trống = chưa chốt → run ra CHƯA KẾT LUẬN.
     Đề xuất thường dùng: "Bug mở không được phép: S1, S2" · "Tỉ lệ PASS tối thiểu: 95%" · "Tỉ lệ BLOCKED tối đa: 5%". -->
- Bug mở không được phép: 
- Tỉ lệ PASS tối thiểu: 
- Tỉ lệ BLOCKED tối đa: 

## 7. Quyền đặc biệt
<!-- "có" chỉ khi người dùng cho phép rõ ràng — trích nguyên văn vào DECISIONS. -->
- Kiểm thử bảo mật: không
- Kiểm thử tải: không
- Môi trường riêng cho kiểm thử tải: 
- Chạm DB staging trực tiếp (seed/đọc): không
- Test AI — số lần chạy mỗi ca (N) và ngưỡng đạt: 

## 8. Câu hỏi đã chốt
<!-- Không chép lại câu trả lời ở đây: câu hỏi về yêu cầu → cột Trả lời ANALYSIS §5; quyết định → DECISIONS.md.
     Ghi số tham chiếu để người đọc SCOPE biết phạm vi dựa trên câu trả lời nào. -->
- ANALYSIS §5: #
- DECISIONS: #
