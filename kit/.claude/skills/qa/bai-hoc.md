# Lưu lỗi và bài học — chi tiết của skill `qa` §6

> Khi nào đọc + luật luôn phải nhớ: skill `qa` §6.

Hai tầng, để kinh nghiệm không mất khi hết phiên:

| Tầng | File | Ghi gì | Ai quyết |
|---|---|---|---|
| Dự án | `qa/LESSONS.md` | Kiểu lỗi tìm được đáng nhớ · sự cố khi test (môi trường, công cụ, dữ liệu) và cách xử · điều người dùng sửa lưng QA ("lần sau đừng…") · câu hỏi hay bị hỏi lại | QA tự ghi ngay khi gặp |
| Dùng chung mọi dự án | skill `qa-knowledge` trong **repo qa-agent** (đường dẫn: `source` trong `.claude/qa-agent.json`) | Bài học đã tổng quát hoá, thành một phép thử cụ thể | **Người dùng duyệt** mới thêm |

- **Khi nào ghi**: ngay lúc gặp — sau mỗi bug có kiểu lỗi mới, mỗi sự cố làm chậm việc, mỗi lần người dùng sửa
  cách làm. Cuối run rà lại một lượt (`/qa-report` bước 4).
- **Khi nào đọc**: hook `hook_session` nạp bài học đang hiệu lực vào **mọi phiên** (kể cả chat không gõ lệnh, sau khi
  nén ngữ cảnh). Dự án có `QA.md §Quy trình bắt buộc` → hook nạp toàn văn quy trình đó, bài học **chỉ tiêu đề**: trước
  khi làm việc thuộc phạm vi một bài, chạy `qa_check.py lessons --for <công đoạn / target>` đọc toàn văn. Các lệnh
  `/qa…` cũng chạy `lessons --for` đầu mỗi việc (không đọc cả `LESSONS.md`). Bài học áp dụng được → dùng (vd thêm quan
  điểm/TC cho kiểu lỗi đó, tránh sự cố đó), và nói ra là đang áp bài học nào. Subagent không tự thấy bài học của phiên →
  phiên chính dán `qa_check.py lessons --for …` vào prompt giao việc.
- **Quy trình bắt buộc**: công đoạn lặp lại nhiều lần (mỗi màn, mỗi run, mỗi lô) mà người dùng đã chốt các bước → đề
  xuất gom các bước + luật an toàn môi trường vào `QA.md §Quy trình bắt buộc` (danh sách đánh số theo thứ tự làm, mỗi
  bước kèm nguồn ngắn), người dùng duyệt rồi mới ghi. Bài học gốc giữ lại làm căn cứ + chi tiết. Một luật chỉ viết đầy
  đủ ở **một** chỗ: quy trình ghi việc phải làm, bài học ghi chi tiết / cách xử; không chép lại nhau. Quyết định người
  dùng (DECISIONS) đổi cách làm lâu dài → đưa vào quy trình hoặc bài học, vì DECISIONS không được nạp đầu phiên.
- **Viết bài học**: bài dài mở đầu bằng **tiêu đề in đậm ngắn** (hook hiện tiêu đề này); viết thành việc cần làm, lời
  trích người dùng để ở cột Nguồn. `qa_check.py lessons` / `status` nhắc khi bài dài thiếu tiêu đề, quy trình quá dài,
  hoặc dòng QA.md thành nhật ký.
- **Nhắc ghi**: hook `hook_prompt` thấy tin nhắn giống sửa lưng ("lần sau", "đừng", "sao lại tự…") → nhắc ghi
  `LESSONS.md` ngay trong lượt. Hook chỉ nhắc — tự xét có phải sửa lưng không.
- **Rà bài giống trước khi thêm**: mỗi bài học mới (sửa lưng, sự cố, kiểu lỗi) → `qa_check.py lessons --like "<ý chính>"`.
  Có bài giống / gần giống → **không tự thêm, không tự gộp**: báo người dùng bài định thêm + các bài cũ giống + đề xuất
  (thêm dòng mới · gộp vào bài nào, viết lại thế nào · chỉ là vi phạm bài cũ, không thêm) và chờ quyết. Không có bài
  giống → ghi ngay. Gộp thì giữ đủ ý + nguồn của các dòng cũ.
- **Bug lọt vì thiếu quan điểm**: bug tìm được mà không quan điểm nào phủ → dòng loại `lỗ quan điểm` + đề xuất quan
  điểm mới cho tính năng đó (người dùng duyệt).
- **Giữ gọn**: dòng `đã nâng`/`bỏ` → `qa_check.py lessons --archive` cất sang `LESSONS-archive.md`; bài na ná → gộp;
  `qa_check.py lessons` báo trùng và báo khi đang hiệu lực quá nhiều (đầu phiên nạp tối đa 80 bài mới nhất).
- **Một nơi ghi**: bài học nghề QA của dự án ghi ở `qa/LESSONS.md` — không ghi vào bộ nhớ riêng của Claude (auto-memory),
  để mọi người/phiên/tester cùng thấy và không có hai bản lệch nhau.
- **Nâng lên kho chung**: bài học dùng được cho dự án khác → viết lại cho tổng quát, hỏi người dùng; đồng ý → sửa
  `kit/.claude/skills/qa-knowledge/…` trong repo qa-agent (ghi `(bài học từ dự án)`) và bản trong dự án, đánh dấu dòng
  LESSONS `đã nâng`. Các dự án khác nhận bài học khi chạy `python3 <repo qa-agent>/install.py <dự án> --update`.
  Repo qa-agent là repo khác — sửa xong nhắc người dùng commit + push lên repo chung (thẳng `main` hoặc PR tuỳ đội; commit/push do họ làm);
  bài học chỉ nằm trong bản clone của một người thì dự án người khác không nhận được.
- **Chỉ bài học lên git, tài liệu dự án ở local**: thứ duy nhất được đưa lên repo qa-agent là bài học đã tổng quát hoá —
  không tên dự án/khách, URL, tài khoản, dữ liệu, trích tài liệu, ảnh. Mọi thứ riêng của dự án (`qa/`, tài liệu sản phẩm,
  evidence, `.mcp.json`) chỉ để local, không push, không publish (Artifact, Claude Docs — đã `deny` trong settings),
  không gửi feedback, không ghi vào bộ nhớ Claude. Thư mục dự án nằm trong repo git của sản phẩm → loại `qa/`,
  `.claude/` khỏi commit (vd `.git/info/exclude`) trước khi làm; chưa rõ → hỏi người dùng.
