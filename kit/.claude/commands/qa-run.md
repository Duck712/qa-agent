---
description: Chạy test — theo bộ TC, smoke, regression, test lại bug, hoặc test khám phá — có bằng chứng, ghi bug
argument-hint: <"all" | "smoke" | "regression" | "retest BUG-012" | "explore <charter>" | danh sách TC-ID | tính năng>
---

Phạm vi: $ARGUMENTS

1. Nạp skill `qa`, `qa-evidence`, `qa-targets` (+ `<loại>.md` của từng target trong phạm vi). Đọc `qa/LESSONS.md`.
2. **Chọn TC** (`python3 .claude/qa-scripts/qa_check.py select <phạm vi>` in danh sách):
   `all` = mọi TC của REQ trong SCOPE · `smoke` = TC có `Tag: smoke` (không có → TC `Mức: R1`) ·
   `regression` = TC `Regression: có` + TC vùng bị ảnh hưởng · `retest BUG-…` = TC của bug + bước tái hiện ·
   `explore` = không có TC, charter + thời lượng (`techniques-judgement §1`), mỗi phát hiện một dòng `EXPLORE-<n>`.
   Trình danh sách + môi trường + tài khoản sẽ dùng → **người dùng xác nhận** rồi mới chạy
   (trừ khi họ đã nói rõ phạm vi và "chạy luôn").
3. **Tạo run**: `python3 .claude/qa-scripts/qa_check.py new-run <loại> <TC…>` → `qa/runs/<run-id>/RUNLOG.md`
   với mọi dòng `CHƯA CHẠY`; script chép sẵn tiêu chí đạt từ SCOPE §6 vào đầu RUNLOG (đóng băng cho run này —
   không sửa sau khi đã chạy). Điền bản đang kiểm, môi trường. SCOPE chưa `CHỐT` → nói rõ với người dùng run này
   dùng tiêu chí nào trước khi chạy.
4. **Kiểm môi trường sống** trước (URL trả lời, đăng nhập được, build đúng bản, lệnh chạy được). Chết/lệch → dừng,
   báo người dùng, hỏi chờ hay đánh `BLOCKED`.
5. **Chạy**: ≤ 5 TC hoặc một target → tự làm. Nhiều hơn → chia nhóm theo target × góc nhìn, spawn `qa-tester`
   (≤ 3 song song; mobile/desktop native tuần tự; nhóm phá-đầu-vào/phân-quyền/bảo-mật chạy cuối, dọn dữ liệu sau).
   Bảo mật → `qa-security`, chỉ khi SCOPE §7 cho phép. Mỗi prompt tester gửi đủ: target + loại + cách vào, góc
   nhìn, TC-ID + file, run-id, tài khoản, prefix, môi trường.
6. **Gặp vấn đề thì hỏi, không tự xử**: kết quả không rõ là bug hay hiểu sai yêu cầu · bước TC không khớp sản phẩm
   hiện tại (đổi tên, đổi luồng) · thiếu dữ liệu/tài khoản/quyền · kết quả "gần đúng" · tester trả về câu hỏi →
   TC để `BLOCKED` tạm, **dừng và hỏi người dùng** (gom các câu cùng lúc nếu chúng không chặn nhau), kèm điều đã
   thấy + các cách hiểu + đề xuất. Không sửa TC, không đổi kỳ vọng, không chọn cách hiểu thay người dùng.
   Trả lời xong → cập nhật TC/kết quả theo đúng câu trả lời, ghi `DECISIONS.md`.
7. **Ghi kết quả** vào RUNLOG ngay sau mỗi nhóm (kết quả, ngày, đường dẫn bằng chứng, BUG/lý do). FAIL → `/qa-bug`
   (retest: cập nhật trạng thái + `Lịch sử` của bug cũ).
8. Hết phạm vi: `qa_check.py run <run-id>` phải sạch → spawn `qa-evidence-check` → xử lý lệch (chạy lại/hạ
   BLOCKED) → ghi bài học mới vào `qa/LESSONS.md` → đề xuất `/qa-report <run-id>`. Đóng trình duyệt/simulator/tiến trình nền.
