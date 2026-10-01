---
description: Chạy test — theo bộ TC, smoke, regression, test lại bug, hoặc test khám phá — có bằng chứng, ghi bug
argument-hint: <"all" | "smoke" | "regression" | "retest BUG-012" | "explore <charter>" | danh sách TC-ID | tính năng>
---

Phạm vi: $ARGUMENTS

1. Nạp skill `qa`, `qa-evidence`, `qa-targets` (+ `<loại>.md` của từng target trong phạm vi). Đọc `qa/LESSONS.md`.
2. **Chọn TC** (`python3 .claude/qa-scripts/qa_check.py select <phạm vi>` in danh sách):
   `all` = mọi TC của REQ trong SCOPE · `smoke` = TC có `Tag: smoke` (không có → script đề xuất TC R1 normal, người
   dùng xác nhận) · `regression` = TC `Regression: có` + TC vùng bị ảnh hưởng (truyền rõ: `new-run reg TC-… TC-…`) ·
   `retest BUG-…` = TC tái hiện ghi ở trường `TC:` của bug (bug từ khám phá chưa có TC → viết TC tái hiện với
   `Nguồn: BUG-…`, người dùng duyệt, rồi mới retest) ·
   `explore` = không có TC, phiên theo khuôn `qa/runs/_EXPLORE-TEMPLATE.md` (charter, thời lượng, ghi chép, debrief —
   `qa-testcase-design/ky-thuat/kinh-nghiem.md` §3), mỗi **phiên** một dòng `EXPLORE-<n>` (phát hiện liệt kê trong `ghi-chep.md` của phiên) ·
   `regression` chọn theo phân tích ảnh hưởng (`qa-knowledge/analysis-review.md` §8) chứ không chỉ theo tag.
   Trình danh sách + môi trường + tài khoản sẽ dùng → **người dùng xác nhận** rồi mới chạy
   (trừ khi họ đã nói rõ phạm vi và "chạy luôn").
3. **Tạo run**: `python3 .claude/qa-scripts/qa_check.py new-run <loại> [phạm vi]` (`new-run retest BUG-012` · `new-run reg TC-…`
   (thêm TC ngoài `Regression: có`) · `new-run smoke` · `new-run explore` · `new-run full TC-… TC-…`) → `qa/runs/<run-id>/RUNLOG.md`
   với mọi dòng `CHƯA CHẠY`; script chép tiêu chí đạt từ SCOPE §6 vào đầu RUNLOG (đóng băng cho run này — không sửa
   sau khi đã chạy). Điền bản đang kiểm, môi trường. SCOPE §6 còn trống → **không tự điền**: nếu người dùng
   đã nhờ chạy ngay thì chạy để thu bằng chứng (run ra `CHƯA KẾT LUẬN`), đề xuất tiêu chí và hỏi khi báo kết quả; nếu
   chưa nhờ chạy ngay thì hỏi tiêu chí trước. Tiêu chí chốt sau khi đã chạy → làm theo skill `qa` §2 (sửa dòng tiêu đề
   khối thành `- Tiêu chí (chốt sau khi chạy — DECISIONS #n; …):`, hoặc tạo run mới chạy lại — người dùng chọn). Trước run `all`/`reg`:
   `python3 .claude/qa-scripts/qa_check.py tc --strict` phải sạch. Cần dữ liệu test → seed theo skill `qa` §7 và ghi Nhật ký.
4. **Kiểm môi trường sống** trước (URL trả lời, đăng nhập được, build đúng bản, lệnh chạy được). Chết/lệch → dừng,
   báo người dùng, hỏi chờ hay đánh `BLOCKED`.
5. **Chạy**: việc nhỏ (vài TC trên một target — người dùng thấy tự làm được) → tự làm. TC `Loại: cross-target` hoặc workflow xuyên target → phiên chính tự
   chạy, hoặc giao **một** qa-tester đủ các target (mỗi target một cách vào trong prompt) — không tách hai nửa.
   Bản đang kiểm đổi giữa run (dev deploy lại) → dừng, hỏi người dùng: chạy lại TC đã xong trên bản mới hay mở run mới;
   TC đã chạy trên bản cũ ghi bản vào cột Lý do và Nhật ký. Nhiều hơn → chia nhóm theo target × góc nhìn, spawn `qa-tester`
   (số tester song song theo `QA.md §Môi trường` — chưa có thì hỏi; mobile/desktop native tuần tự; nhóm phá-đầu-vào/phân-quyền/bảo-mật chạy cuối, dọn dữ liệu sau).
   TC `Thực hiện: người` (new-run in danh sách) → giao cho người ở `QA.md §Người chạy TC thủ công` theo skill `qa` §7,
   chạy phần còn lại song song; nhận kết quả về thì chép bằng chứng + `nguoi-thuc-hien.md`, ghi RUNLOG đúng lời người làm.
   Bảo mật → `qa-security`, chỉ khi SCOPE §7 cho phép (kết quả `INCONCLUSIVE` ghi RUNLOG thành
   `BLOCKED (inconclusive: …)` + câu hỏi). Mỗi prompt tester gửi đủ: target + loại + cách vào, góc nhìn, TC-ID + file,
   run-id, **đường dẫn tuyệt đối** thư mục bằng chứng `qa/evidence/<run-id>/`, tài khoản, prefix, môi trường, và
   **bài học liên quan**: dán nguyên đầu ra `python3 .claude/qa-scripts/qa_check.py lessons --for <target> <tính năng> <góc nhìn>`.
6. **Gặp vấn đề thì hỏi, không tự xử**: kết quả không rõ là bug hay hiểu sai yêu cầu · bước TC không khớp sản phẩm
   hiện tại (đổi tên, đổi luồng) · thiếu dữ liệu/tài khoản/quyền · kết quả "gần đúng" · tester trả về câu hỏi →
   TC để `BLOCKED` tạm, **dừng và hỏi người dùng** (gom các câu cùng lúc nếu chúng không chặn nhau), kèm điều đã
   thấy + các cách hiểu + đề xuất. Không sửa TC, không đổi kỳ vọng, không chọn cách hiểu thay người dùng.
   Trả lời xong → câu trả lời về yêu cầu ghi cột `Trả lời` ở ANALYSIS §5 (gỡ `(chờ trả lời #n)`); quyết định cách làm/
   phạm vi/trạng thái → một dòng DECISIONS trích nguyên văn; rồi chạy lại TC đó theo câu trả lời.
7. **Ghi kết quả** vào RUNLOG ngay sau mỗi nhóm (kết quả, ngày, đường dẫn bằng chứng, BUG/lý do). FAIL → `/qa-bug`
   (retest: cập nhật trạng thái + `Lịch sử` của bug cũ).
8. Hết phạm vi: `python3 .claude/qa-scripts/qa_check.py run <run-id>` phải sạch → spawn `qa-evidence-check` kèm run-id và tỉ lệ ở SCOPE §6 `Soi bằng chứng — tỉ lệ bốc mẫu PASS` (chưa có thì hỏi
   người dùng trước khi spawn) → ghi
   `Đã soi bằng chứng <ngày> — <x> lệch` vào Nhật ký → **trình danh sách lệch cho người dùng**, người dùng quyết chạy
   lại hay hạ BLOCKED (ghi DECISIONS) → hỏi có dọn dữ liệu test không → ghi bài học mới vào `qa/LESSONS.md` → đề xuất
   `/qa-report <run-id>`. Đóng trình duyệt/simulator/tiến trình nền.
