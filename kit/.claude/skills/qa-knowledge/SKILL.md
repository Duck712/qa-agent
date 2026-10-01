---
name: qa-knowledge
description: >
  Kinh nghiệm kiểm thử tích luỹ qua nhiều dự án — kỹ thuật phân tích & review tài liệu (tiêu chí chất lượng yêu
  cầu, INVEST, Given–When–Then, từ yếu, đọc theo góc nhìn, yêu cầu ngầm ISO 25010, example mapping, rủi ro, phân
  tích ảnh hưởng), checklist theo đối tượng (form, đăng nhập/phân quyền/MFA/SSO, dữ liệu cá nhân, a11y WCAG 2.2,
  upload, API, ca bất thường, thanh toán, thông báo, realtime/chat/gọi, tìm kiếm/danh sách/export, ngày giờ/
  lịch), checklist theo loại target (CLI, job/pipeline dữ liệu, AI/LLM), danh sách lỗi dev hay mắc
  (bug-patterns) và mẹo nghề (khám phá có kỷ luật, viết bug, soi yêu cầu mơ hồ, cắt phạm vi, viết báo cáo).
  Nạp skill này khi phân tích tài liệu tìm lỗ hổng, khi viết/review test case, khi đóng vai qa-tester để
  biết chỗ nào đáng đào, và khi rút bài học sau một lượt test (chỉ sửa skill khi người dùng đã duyệt).
---

# qa-knowledge — kinh nghiệm dùng lại được

> `qa-testcase-design` trả lời **cách** nghĩ ra đủ ca. Skill này trả lời **chỗ nào** dev hay sai — thứ tài
> liệu gần như không bao giờ nhắc. Đối chiếu, không chép máy móc: mục không áp dụng thì bỏ **chủ động**.

## Mục lục

| File | Mở khi |
|---|---|
| `bug-patterns.md` | **Luôn** — soi trước khi viết TC cho mọi tính năng |
| `checklists/form-input.md` | Có form nhập liệu |
| `checklists/auth-login.md` | Đăng nhập / phiên / phân quyền / đa tenant (§3 thường đề xuất R1 — người dùng xác nhận) |
| `checklists/file-upload.md` | Upload file, ảnh, media |
| `checklists/api-common.md` | Bất kỳ API nào |
| `checklists/abnormal.md` | Luồng xuyên nhiều màn/hạ tầng: mạng, race, múi giờ, trình duyệt, mobile, cache, dữ liệu lớn, i18n, phục hồi |
| `checklists/payment.md` | Có tiền: giá, giảm giá, thanh toán, hoàn tiền |
| `checklists/notification.md` | Email / SMS / push / thông báo trong app, link trong thông báo |
| `checklists/realtime.md` | Chat, cộng tác nhiều người, gọi thoại/video, trạng thái online |
| `checklists/search-list.md` | Tìm kiếm, danh sách, lọc, sắp xếp, phân trang, export |
| `checklists/datetime.md` | Ngày giờ, lịch, sự kiện lặp, múi giờ, nhắc nhở |
| `checklists/privacy-pii.md` | Có dữ liệu cá nhân: che/ẩn, xoá tài khoản, tải dữ liệu, đồng ý |
| `checklists/a11y.md` | Tiếp cận theo WCAG 2.2 (mức A/AA do người dùng chốt) |
| `checklists/cli.md` | Target `cli` |
| `checklists/batch-data.md` | Target `batch` — job, ETL, pipeline |
| `checklists/ai-llm.md` | Target `ai` — chatbot, tóm tắt, phân loại, agent |
| `analysis-review.md` | **Phân tích & review tài liệu**: tiêu chí chất lượng yêu cầu, INVEST, Given–When–Then, từ yếu, đọc theo góc nhìn, yêu cầu ngầm ISO 25010, example mapping, mô hình hoá, rủi ro, phân tích ảnh hưởng |
| `scope-review.md` | **Review kế hoạch / SCOPE** — phạm vi, chạy được, kết luận được |
| `techniques-judgement.md` | Khám phá có kỷ luật · viết bug · soi yêu cầu mơ hồ · cắt phạm vi · viết báo cáo |

Bảo mật chuyên sâu (OWASP, CVE, secret) thuộc agent `qa-security`. Ở đây chỉ giữ ca bảo mật cơ bản ai cũng
phải thử (`auth-login §3`, `form-input §2`, `api-common`).

## Dùng thế nào
- **Phân tích tài liệu** — theo `analysis-review.md` (quy trình §1) + `bug-patterns`: điều tài liệu không nói → `ANALYSIS §5` kèm đề xuất.
- **Quan điểm test / TC** — mỗi đối tượng trong phạm vi mở checklist tương ứng. Mục checklist mà **đặc tả có nói tới** → quan
  điểm bám câu đặc tả đó (checklist chỉ là gợi ý góc nhìn). Mục đặc tả **không nói** → quan điểm `Nguồn: ngoài đặc tả —
  <checklist> <số mục>` (vd `form-input 2.3`, `bug-patterns #11`), để `nháp`, người dùng duyệt mới viết TC
  (`qa-testcase-design/ky-thuat/quan-diem.md` §1). Không trình mục checklist như thể đặc tả yêu cầu.
- **Chạy test** — tester nạp checklist của loại mình để biết chỗ đáng đào, nhưng chỉ chạy TC được giao; thấy chỗ đáng ngờ ngoài danh sách → báo thành phát hiện.
- **Sau một lượt** — kiểu lỗi mới ghi `REPORT §Bài học`; đề xuất thành một dòng ở đây → người dùng duyệt rõ ràng mới sửa.

## Luật sửa skill này
- Mỗi dòng thêm vào là **một phép thử cụ thể** (thao tác + điều quan sát), không phải lời khuyên chung.
- Ghi nguồn cuối dòng: `(bài học từ dự án)` — **không** ghi tên dự án/khách, URL, tài khoản, dữ liệu (skill `qa` §6:
  repo này là kho chung, chỉ chứa bài học đã tổng quát hoá).
- Không xoá dòng vì "dự án này không dùng" — dự án khác vẫn dùng. Dòng sai thật → đề xuất sửa, người dùng duyệt mới sửa (ghi DECISIONS trích lời duyệt).
- Kho này dùng chung nhiều dự án: bài học riêng của một sản phẩm (tên màn, tên API) → viết lại cho tổng quát trước khi thêm.
- Sửa ở **repo qa-agent** (đường dẫn: `source` trong `.claude/qa-agent.json`), rồi nhắc người dùng commit + push lên repo
  chung (thẳng `main` hoặc qua PR, tuỳ đội) — bài học nằm trong bản clone riêng của một người thì dự án của người khác không nhận được.
  Máy dùng chung nhiều người: nên dùng một bản clone chung cho cả nhóm, hoặc luôn đi qua PR.
