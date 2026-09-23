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
     Định dạng: `Bug mở không được phép: S1, S2` (hoặc `S1–S3`, `S2 trở lên`, `không`) · `Tỉ lệ PASS tối thiểu: <số>%` ·
     `Tỉ lệ BLOCKED tối đa: <số>%` — mỗi dòng đúng MỘT số có %. Tiêu chí theo mức → thêm dòng riêng
     `- Tỉ lệ PASS tối thiểu R1: <số>%` (tính trên TC thuộc REQ có mức R1 ở SCOPE §2; `Mức:` của TC chỉ dùng khi REQ chưa có mức). Tiêu chí không vừa khuôn → ghi DECISIONS, báo người
     dùng máy không tính được (run ra CHƯA KẾT LUẬN). -->
- Bug mở không được phép: 
- Tỉ lệ PASS tối thiểu: 
- Tỉ lệ BLOCKED tối đa: 
- Soi bằng chứng — tỉ lệ bốc mẫu PASS: <!-- vd 30% — mọi FAIL luôn soi; nhóm ưu tiên (qa-evidence §5) được bốc trước trong tỉ lệ này -->

## 7. Quyền đặc biệt
<!-- "có" chỉ khi người dùng cho phép rõ ràng — trích nguyên văn vào DECISIONS. -->
- Kiểm thử bảo mật: không
- Kiểm thử tải: không
- Môi trường riêng cho kiểm thử tải: 
- Đọc/ghi DB trực tiếp (môi trường nào, bảng nào, đọc hay ghi): không
- Test AI — N mỗi ca: <!-- một số, hoặc theo mức: R1: …, R2: …, R3: … -->
- Test AI — số cách diễn đạt mỗi ca (kiểm ổn định): <!-- số, kèm lý do; không ghi vào dòng N -->
- Test AI — ngưỡng đạt mỗi ca: <!-- vd 4/5 lượt thoả mọi tiêu chí; tiêu chí an toàn: … -->

## 8. Câu hỏi đã chốt
<!-- Không chép lại câu trả lời ở đây: câu hỏi về yêu cầu → cột Trả lời ANALYSIS §5; quyết định → DECISIONS.md.
     Ghi số tham chiếu để người đọc SCOPE biết phạm vi dựa trên câu trả lời nào. -->
- ANALYSIS §5: #
- DECISIONS: #

## 9. Tiêu chí vào / ra
<!-- Vào: điều kiện để BẮT ĐẦU chạy (bản đã deploy đúng, smoke xanh, dữ liệu seed xong, quan điểm + TC đã duyệt…).
     Ra: điều kiện để KẾT THÚC đợt — tiêu chí đạt §6 là phần máy tính được; ghi thêm điều kiện khác người dùng muốn. -->
- Tiêu chí vào: 
- Tiêu chí ra (ngoài §6): 
- Điều kiện tạm dừng / tiếp tục: 

## 10. Lịch & nguồn lực
| Việc | Người | Bắt đầu | Hạn | Ghi chú |
|---|---|---|---|---|
| | | | | |

## 11. Sản phẩm bàn giao
<!-- Mặc định: qa/viewpoints/, qa/testcases/, TRACE.md, runs/<run-id>/RUNLOG.md + REPORT.md, BUGS.md. Đội cần định dạng
     khác (Excel) → `qa_check.py export tc|vp`. -->
- 

## 12. Giả định · phụ thuộc · rủi ro dự án
<!-- Rủi ro của VIỆC TEST (không phải của sản phẩm — cái đó ở ANALYSIS §6): môi trường chập chờn, thiếu tài khoản, bản
     giao trễ, người trả lời câu hỏi vắng… mỗi dòng một cách giảm. Chỉ ghi điều người dùng xác nhận hoặc đã quan sát. -->
| Loại | Nội dung | Ảnh hưởng | Cách giảm / ai lo |
|---|---|---|---|
| | | | |
