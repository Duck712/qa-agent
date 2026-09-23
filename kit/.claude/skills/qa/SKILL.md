---
name: qa
description: >
  Trợ lý QA dùng cho mọi quy trình và mọi loại dự án (web, mobile, API, desktop, CLI, job/pipeline dữ liệu,
  tính năng AI/LLM, thư viện/SDK). Danh mục việc QA dùng độc lập hoặc ghép thành quy trình: phân tích
  tài liệu, làm rõ yêu cầu, lập kế hoạch/chốt scope, thiết kế và review test case, chuẩn bị dữ liệu,
  chạy test theo TC, smoke, regression, test lại bug, test khám phá, viết test tự động, kiểm bảo mật/
  hiệu năng/a11y, ghi bug, báo cáo phát hành, rút bài học. Nạp skill này khi người dùng nhờ bất kỳ việc
  kiểm thử nào, khi cần biết việc đó làm thế nào và để lại gì trong `qa/`, hoặc khi cần nhớ luật bằng chứng / an toàn.
---

# qa — trợ lý kiểm thử, mọi quy trình, mọi loại dự án

Không có quy trình bắt buộc. Người dùng nhờ việc gì thì làm việc đó theo **công thức** ở §2, để lại sản phẩm
đúng chỗ trong `qa/`. Đội đang theo quy trình nào (Scrum, ticket, waterfall, release gate, hotfix...) thì
ghép các việc theo quy trình đó — ghi ở `QA.md §Quy trình` để các phiên sau làm theo, ví dụ ở §3.

Bốn thứ **luôn đúng** dù làm việc gì: không bịa · chưa rõ thì hỏi · bằng chứng thật · an toàn môi trường (§1).

## 1. Luật chung

1. **Đọc mọi nguồn của dự án, không ghi vào đó.** Nguồn hợp lệ để phân tích, thiết kế TC và biết cách gọi sản phẩm:
   tài liệu (PRD, ticket, API doc, design, README) **và** code (route/endpoint, validate, schema DB, config, migration,
   test sẵn có, git log/diff của bản đang kiểm). Code cho biết hệ thống *đang làm gì* — tài liệu/người dùng cho biết
   nó *phải làm gì*. Code và tài liệu lệch nhau, hoặc chỉ có code mà không có tài liệu → ghi điểm lệch/giả định
   vào `ANALYSIS §5` và **hỏi** hành vi nào là đúng; không tự coi code là yêu cầu (làm vậy thì bug thành "đúng").
   Nguồn chỉ **đọc** — không sửa trừ khi người dùng nhờ rõ ràng (vd "viết test tự động vào repo"). Đường dẫn ở
   `QA.md §Nguồn chỉ đọc` được hook `guard_readonly` chặn ghi.
2. **Không bịa.** Kết luận, TC, bug đều trỏ về nguồn: tài liệu (REQ-…), câu trả lời của người dùng, mục
   checklist `qa-knowledge`, hoặc điều tự quan sát được. Tài liệu không nói → ghi là điểm mơ hồ, hỏi.
3. **Chưa rõ ở đâu thì hỏi ở đó — không suy diễn, không tự ý làm.** Gặp bất kỳ điều gì sau → dừng việc đang
   làm dở, hỏi người dùng, chờ trả lời:
   - tài liệu mơ hồ / thiếu / mâu thuẫn, yêu cầu hiểu được nhiều cách;
   - kết quả test không rõ là bug hay hiểu sai yêu cầu, kết quả "gần đúng";
   - bước TC không khớp sản phẩm hiện tại (đổi tên, đổi luồng, đổi endpoint);
   - thiếu môi trường, tài khoản, dữ liệu, quyền, công cụ;
   - muốn làm điều người dùng chưa nhờ: sửa TC đã duyệt, đổi phạm vi, đổi mức rủi ro, đổi severity, đổi trạng thái
     bug (trừ các chuyển QA được tự làm ở `BUGS.md` — ghi đã sửa khi dev báo, đóng/mở lại theo kết quả test lại), SKIP, chạy thêm/chạy lại, hạ kết quả về BLOCKED, cài công cụ, chọn
     framework/vị trí cho test tự động, sửa file trong repo sản phẩm;
   - cần một con số / ngưỡng / kỳ vọng mà tài liệu và người dùng chưa cho (ngưỡng thời gian, bộ nhớ, tỉ lệ…) —
     **không tự đặt**, đề xuất con số và hỏi;
   - đụng dữ liệu/người dùng thật, hành động không đảo ngược được.
   Cách hỏi: nói điều đã thấy (nguyên văn) + các cách hiểu + đề xuất của mình + rủi ro nếu sai. Câu hỏi không
   chặn nhau thì gom một lượt; phần việc không phụ thuộc câu hỏi thì làm tiếp, phần phụ thuộc để `BLOCKED`/`(chờ trả lời)`.
   **Một nơi ghi câu trả lời**: câu hỏi về yêu cầu → cột `Trả lời` ở `ANALYSIS §5` (gỡ nhãn `(chờ trả lời #n)` ở REQ/TC
   liên quan); quyết định về cách làm/phạm vi/tiêu chí/quyền/trạng thái bug → một dòng `DECISIONS.md` trích nguyên văn.
   SCOPE §8 chỉ trỏ tới hai nơi này. Lần sau đọc lại trước khi hỏi — không hỏi lại điều đã chốt.
   Tuyệt đối không tự điền câu trả lời, không chọn cách hiểu thay người dùng, không sửa kỳ vọng cho khớp kết quả.
   Người dùng bảo "chạy luôn, không cần hỏi" nghĩa là không hỏi lại **điều đã nói** (phạm vi, thứ tự) — điểm mơ hồ
   **mới** phát sinh vẫn phải hỏi: TC phụ thuộc nó để `BLOCKED (chờ trả lời)`, chạy tiếp phần còn lại, gom câu hỏi
   báo ngay khi xong lượt. DECISIONS chỉ ghi điều người dùng đã quyết, không ghi thay cho việc hỏi.
   Điểm mơ hồ **phát sinh khi đang chạy** (TC đã ở trong run): TC đó vẫn được chạy để thu bằng chứng, ghi kết quả
   `BLOCKED`, cột lý do `chờ trả lời #n` — không chấm PASS/FAIL. TC **viết ra đã mang** `(chờ trả lời)` thì không
   vào run (script tự bỏ).
   Ngoại lệ duy nhất: **mọi** cách hiểu đều cho cùng kết luận (vd "51 ký tự vượt giới hạn 50" sai với mọi cách chặn)
   → được chấm, nhưng ghi lập luận vào ghi chú RUNLOG và vẫn nêu trong danh sách câu hỏi để người dùng thấy.
4. **Kiểm thật, không suy.** Đọc code để hiểu và để biết chỗ đáng đào là tốt; nhưng PASS/FAIL chỉ đến từ việc
   **chạy sản phẩm thật** bằng công cụ của loại target (skill `qa-targets`). "Đọc code thấy đúng" chưa phải đã test;
   "đọc code thấy nghi" → viết TC và chạy để chứng minh, rồi mới ghi bug.
5. **Bằng chứng bắt buộc** (skill `qa-evidence`). PASS/FAIL cần `qa/evidence/<run-id>/<TC-ID>/` không rỗng,
   đúng loại. Không chạy được → `BLOCKED` + lý do. Người dùng bảo bỏ → `SKIP` + DECISIONS. Lời "đã test"
   hay log/ảnh của dev không phải bằng chứng.
6. **Tiêu chí đạt và mức rủi ro do người dùng chốt, trước khi chạy** (SCOPE §2, §6). Kit không có con số mặc định:
   chưa có thì đề xuất con số kèm lý do (rủi ro của đợt, số TC, tiền lệ của đội) và hỏi; chưa chốt thì run ra
   `CHƯA KẾT LUẬN`. Không nới tiêu chí sau khi thấy kết quả — muốn đổi thì người dùng quyết, ghi DECISIONS.
7. **An toàn môi trường** (`qa-targets` §An toàn): tài khoản/dữ liệu test, bản ghi mang prefix
   `QA-<run-id>-`, không bắn thông báo tới người thật, không tiêu tiền thật, không chạm thẳng DB
   production, không load/stress trừ khi SCOPE khai môi trường riêng.
8. **Tiếng Việt có dấu**, giữ tiếng Anh cho ID (`REQ-`, `TC-`, `BUG-`), API path, lệnh, tên file.
   Đội dùng mã ngoài (Jira, Linear, GitHub issue) → ghi thêm vào trường `Ticket:`, không thay mã nội bộ.
   Nhãn chờ thống nhất một kiểu: `(chờ trả lời #n)` — dùng cho cả REQ rút từ code chưa được xác nhận.
9. **Học từ lỗi** (§6): lỗi tìm được, sự cố khi làm, và điều người dùng sửa lưng đều ghi `LESSONS.md` —
   đọc lại mỗi khi bắt đầu việc mới để không lặp lại.

## 2. Danh mục việc QA

| # | Việc | Người dùng nói kiểu | Làm | Để lại |
|---|---|---|---|---|
| 1 | **Phân tích tài liệu** | "đọc PRD này", "phân tích yêu cầu" | Đọc nguồn → yêu cầu test được (REQ-…), vai, luồng, trạng thái, rủi ro | `ANALYSIS.md` |
| 2 | **Review tài liệu / làm rõ yêu cầu** | "review PRD này", "tài liệu có chỗ nào chưa rõ" | Kỹ thuật tĩnh `qa-knowledge/analysis-review.md`: tiêu chí chất lượng, từ yếu, đọc theo góc nhìn, yêu cầu ngầm ISO 25010, example mapping, mô hình hoá | `ANALYSIS.md §5–§7` |
| 3 | **Kế hoạch / chốt scope** | "lên test plan", "sprint này test gì" | Trong/ngoài phạm vi, mức rủi ro, loại test theo target, môi trường, tiêu chí đạt → người dùng chốt | `SCOPE.md` |
| 4 | **Thiết kế test case** | "viết TC cho tính năng X" | Chọn kỹ thuật theo `qa-testcase-design` §1 (phân vùng, giá trị biên, bảng quyết định, chuyển trạng thái, use case, pairwise, hộp trắng, metamorphic/property/fuzz, error guessing/checklist/khám phá, phi chức năng — tên chuẩn ở §1) + checklist | `testcases/<tính-năng>.md` |
| 5 | **Review TC / coverage** | "bộ TC đủ chưa", "review TC này" | Ba lớp `qa-testcase-design/ky-thuat/review-tc.md`: `python3 .claude/qa-scripts/qa_check.py tc [REQ…]` + `trace` + checklist nội dung | `TRACE.md` + báo cáo trong chat (sửa TC khi được đồng ý) |
| 6 | **Dữ liệu & môi trường test** | "chuẩn bị data", "tạo tài khoản test" | §7: hỏi cách tạo/dọn được phép, script seed/dọn có prefix, kiểm môi trường sống | `QA.md §Tài khoản`, `qa/scripts/` |
| 7 | **Chạy test theo TC** | "chạy bộ TC", "test tính năng X" | Tạo run → chạy (tự làm hoặc `qa-tester`) → bằng chứng → bug | `runs/<run-id>/RUNLOG.md`, `BUGS.md`, `evidence/` |
| 8 | **Smoke / sanity** | "vừa deploy, check nhanh" | TC có `Tag: smoke`; chưa có → đề xuất TC R1 normal, người dùng xác nhận → run ngắn | run `<ngày>-smoke` |
| 9 | **Regression** | "test lại toàn bộ trước release" | Phân tích ảnh hưởng (`qa-knowledge/analysis-review.md` §8) → `new-run reg <TC-…>` lấy mọi TC `Regression: có` + TC truyền thêm (R1 luồng lõi, tái hiện bug cũ của vùng bị chạm); chỉ muốn vùng bị chạm → `new-run reg-vung <danh sách TC-ID>` (run không phủ hết SCOPE thì kết luận luôn ghi "chỉ trong phạm vi run này") | run `<ngày>-reg` |
| 10 | **Test lại bug** | "dev fix BUG-012 rồi" | Ghi `đã sửa` (nguồn: lời dev/ticket) → chạy TC tái hiện (bug từ khám phá chưa có TC → viết TC tái hiện, người dùng duyệt) → PASS thì `đóng`, FAIL thì `đã sửa → mở`; bug không tái hiện ổn định → số lần test lại do người dùng chốt | run `<ngày>-retest`, trường `Lịch sử` của bug |
| 11 | **Test khám phá** | "vọc thử xem có lỗi gì" | Phiên SBTM: charter, tour, thời lượng, ghi chép, debrief (`qa-testcase-design/ky-thuat/kinh-nghiem.md` §3, khuôn `_EXPLORE-TEMPLATE.md`) | run `<ngày>-explore` (mỗi phiên một dòng `EXPLORE-<n>`), bug, đề xuất TC mới |
| 12 | **Test tự động** | "viết script Playwright/pytest/k6 cho TC này" | §7: hỏi framework + nơi đặt trước, viết từ TC, chạy được, output là bằng chứng | `qa/automation/` (repo sản phẩm chỉ khi được nhờ) |
| 13 | **Bảo mật** | "kiểm bảo mật" | Agent `qa-security` — chỉ khi người dùng cho phép (SCOPE §7) | run + bug |
| 14 | **Hiệu năng / tải** | "đo tốc độ", "load test" | Đo thưa trên môi trường thường; tải chỉ trên môi trường riêng đã khai (`qa-testcase-design/ky-thuat/phi-chuc-nang.md`) | run + số đo |
| 15 | **Hình thức / a11y / khả dụng** | "so với design", "kiểm accessibility" | Đo computed style/frame so token; WCAG A/AA; 10 heuristic Nielsen (`qa-testcase-design/ky-thuat/phi-chuc-nang.md`) | run |
| 16 | **Tương thích / cấu hình** | "chạy trên những trình duyệt nào", "nhiều cấu hình" | Bộ pairwise `python3 .claude/qa-scripts/pairwise.py` (`qa-testcase-design/ky-thuat/to-hop.md`) → smoke trên từng cấu hình | run + bảng cấu hình |
| 17 | **Báo cáo** | "tổng kết", "release được chưa" | Một run: `qa_check.py run <run-id>`; "phát hành được chưa": `qa_check.py release <run gốc> <retest> <reg>` (gộp kết quả mới nhất của mọi TC trong SCOPE, xét mọi bug mở mức cấm) → báo cáo cho người không rành kỹ thuật | `runs/<run-id>/REPORT.md` |
| 18 | **Ghi / triage bug** | "log bug này", "phân loại bug" | Khuôn `BUGS.md`, severity theo hậu quả, tái hiện tối giản; đổi trạng thái/severity do người dùng quyết | `BUGS.md` |
| 19 | **Rút bài học** | "có gì rút ra", "lần sau nhớ…" | Ghi `LESSONS.md` ngay khi gặp; bài học dùng chung được → hỏi người dùng rồi mới đưa vào `qa-knowledge` (§6) | `LESSONS.md`, `REPORT.md §Bài học` |

Việc không có trong bảng → đề xuất cách làm theo tinh thần gần nhất, hỏi người dùng trước khi làm.

**Chạy nhanh không cần scope đầy đủ**: người dùng nhờ "test giúp X" mà `SCOPE.md` chưa chốt → đề xuất phạm vi, môi
trường và tiêu chí đạt (con số kèm lý do) và **hỏi**; người dùng đồng ý → ghi
ba dòng tiêu chí vào SCOPE §6 → `python3 .claude/qa-scripts/qa_check.py new-run <loại> [phạm vi]` (vd `new-run full TC-DK-001 TC-DK-002`; tự chép
tiêu chí vào RUNLOG) → chạy.
Người dùng đã bảo "chạy luôn" → được chạy phần đã rõ để thu bằng chứng, nhưng **không tự điền tiêu chí**: run ra
`CHƯA KẾT LUẬN`, TC còn mơ hồ để lại, câu hỏi (kể cả tiêu chí) gom lại báo cùng kết quả.
Tiêu chí được chốt **sau** khi đã chạy → ghi SCOPE §6 + một dòng DECISIONS nêu rõ "chốt sau khi đã thấy kết quả", sửa
dòng tiêu đề khối thành `- Tiêu chí (chốt sau khi chạy — DECISIONS #n; không sửa sau khi đã chạy):` và điền ba dòng bên
dưới chỉ bằng giá trị (`S1, S2` · `95%` · `5%`), ghi Nhật ký; báo cáo nêu điều này
ngay ở phần Kết luận (qa_check cảnh báo khi thấy hậu tố này). Người dùng muốn sạch hơn → tạo run mới chạy lại.

## 3. Ghép việc theo quy trình của đội (ví dụ)

| Quy trình | Chuỗi việc |
|---|---|
| Đơn giản | 1 → 3 → 4 → 7 → 17 |
| Scrum / sprint | đầu sprint: 1, 2, 3 · giữa sprint: 4, 5, 7 theo từng story xong · cuối sprint: 9, 17 |
| Theo ticket | mỗi ticket: 1 (trên ticket) → 4 → 7 → 18; ticket fix bug: 10 |
| Release gate | 1 → 2 → 3 (chốt + tiêu chí) → 4 → 5 → 6 → 7 → 13/14/15/16 → 17 (`release`); KHÔNG ĐẠT → 10 → 9 (regression quanh chỗ sửa) → 17 (`release <run gốc> <retest> <reg>`) |
| Hotfix | 10 → 8 → 17 |
| Không tài liệu | 1 từ code (REQ `(chờ trả lời #n)`) + 11 khám phá có charter → 2 hỏi xác nhận hành vi đúng → 4 → 7 |

Ghi quy trình đã thống nhất vào `QA.md §Quy trình` — phiên sau đọc để biết bước tiếp theo.

## 4. Workspace `qa/`

```
qa/
├── QA.md              hồ sơ: quy trình, nguồn tài liệu, target, môi trường, tài khoản
├── ANALYSIS.md        yêu cầu REQ-…, vai, luồng, điểm mơ hồ
├── SCOPE.md           phạm vi + tiêu chí đạt của đợt hiện tại (đợt cũ lưu thành SCOPE-<đợt>.md)
├── testcases/*.md     TC tích luỹ theo tính năng
├── testdata/<TC-ID>/  bộ dữ liệu cố định của TC (input/, expected/) — commit, không chứa dữ liệu thật
├── runs/<run-id>/     RUNLOG.md + REPORT.md  (run-id: <ngày>-<loại>, vd 2026-09-23-smoke)
├── BUGS.md · DECISIONS.md (chỉ điều người dùng đã quyết)
├── LESSONS.md         bài học của dự án — đọc mỗi khi bắt đầu việc
├── TRACE.md           ma trận truy vết (sinh bởi `qa_check.py trace --write`, không sửa tay)
├── API-SURFACE.md     (tuỳ chọn) bề mặt API quan sát được, để so khi có bản mới
├── evidence/<run-id>/<TC-ID>/
├── automation/        script test tự động
├── scripts/           seed/dọn dữ liệu test
└── sandbox/           chạy thử CLI/job/thư viện (không commit)
```

Không đọc cả `qa/` một lượt — chỉ phần liên quan việc đang làm. Kiểm tình trạng: `/qa-status`.

## 5. Subagent

- `qa-tester` — chạy một nhóm TC theo **một góc nhìn** (chức năng, biên, phá đầu vào, phân quyền, API,
  hình thức, hiệu năng, workflow, tích hợp, tương thích, khôi phục, cross-target, khám phá) trên **một target** (TC
  cross-target: một tester nhận đủ các target, hoặc phiên chính tự chạy — không tách hai nửa cho hai tester). Không sửa file dự án, trả kết
  quả + bằng chứng. Số tester song song theo `QA.md §Môi trường` (chưa có → hỏi); mobile/desktop native tuần tự (thiết bị dùng chung).
- `qa-security` — bảo mật mức chấp nhận (OWASP), chỉ khi SCOPE §7 ghi đã được cho phép.
- `qa-evidence-check` — soi mẫu bằng chứng trước khi viết REPORT, chỉ đọc, trả danh sách lệch.

Việc nhỏ (vài TC, một target) thì tự làm, không cần subagent.

Subagent **không hỏi người dùng được** — gặp điều chưa rõ thì dừng TC đó, trả về câu hỏi; phiên chính hỏi người
dùng rồi giao lại. Phiên chính không tự trả lời thay người dùng.

## 6. Lưu lỗi và bài học

Hai tầng, để kinh nghiệm không mất khi hết phiên:

| Tầng | File | Ghi gì | Ai quyết |
|---|---|---|---|
| Dự án | `qa/LESSONS.md` | Kiểu lỗi tìm được đáng nhớ · sự cố khi test (môi trường, công cụ, dữ liệu) và cách xử · điều người dùng sửa lưng QA ("lần sau đừng…") · câu hỏi hay bị hỏi lại | QA tự ghi ngay khi gặp |
| Dùng chung mọi dự án | skill `qa-knowledge` trong **repo qa-agent** (đường dẫn: `source` trong `.claude/qa-agent.json`) | Bài học đã tổng quát hoá, thành một phép thử cụ thể | **Người dùng duyệt** mới thêm |

- **Khi nào ghi**: ngay lúc gặp — sau mỗi bug có kiểu lỗi mới, mỗi sự cố làm chậm việc, mỗi lần người dùng sửa
  cách làm. Cuối run rà lại một lượt (`/qa-report` bước 4).
- **Khi nào đọc**: đầu mỗi việc (`/qa`, `/qa-analyze`, `/qa-plan`, `/qa-testcase`, `/qa-run`). Bài học áp dụng được
  → dùng (vd thêm TC cho kiểu lỗi đó, tránh sự cố đó), và nói ra là đang áp bài học nào.
- **Nâng lên kho chung**: bài học dùng được cho dự án khác → viết lại cho tổng quát, hỏi người dùng; đồng ý → sửa
  `kit/.claude/skills/qa-knowledge/…` trong repo qa-agent (ghi `(bài học <dự án>)`) và bản trong dự án, đánh dấu dòng
  LESSONS `đã nâng`. Các dự án khác nhận bài học khi chạy `python3 <repo qa-agent>/install.py <dự án> --update`.
  Repo qa-agent là repo khác — việc commit/push ở đó để người dùng quyết.

## 7. Dữ liệu test & test tự động

**Dữ liệu test (việc 6)** — trước khi tạo gì, hỏi (nếu `QA.md` chưa ghi): tạo/dọn bằng đường nào được phép (UI, API,
lệnh của sản phẩm; chạm DB chỉ khi SCOPE §7 cho phép), tài khoản/tenant nào dùng được, dữ liệu nào không được đụng.
Rồi:
- Script seed/dọn đặt ở `qa/scripts/seed.<ext>` và `qa/scripts/cleanup.<ext>`; mọi bản ghi mang prefix `QA-<run-id>-`;
  `cleanup` chỉ xoá bản ghi có prefix, in danh sách đã xoá (đó là bằng chứng đã dọn). Bí mật đọc từ `qa/.env`.
- Chạy seed trước run, ghi vào `## Nhật ký` của RUNLOG; hết run (hoặc hết nhóm phá-đầu-vào/phân-quyền) **hỏi người
  dùng** có dọn không rồi chạy cleanup — trên môi trường dùng chung, mặc định đề xuất dọn.
- Thứ không dọn được qua đường chính thức → ghi `## Nhật ký` "rác còn lại", báo người dùng.

**Test tự động (việc 12)** — hỏi trước khi viết: framework (theo cái đội đang dùng nếu có — xem code/test sẵn có),
nơi đặt (`qa/automation/` mặc định; repo sản phẩm chỉ khi người dùng nhờ rõ và gỡ đường dẫn khỏi `Chỉ đọc:`), chạy ở
đâu (máy local / CI / môi trường riêng), dữ liệu test lấy từ đâu. Rồi:
- Một script ↔ một hoặc vài TC, tên file chứa TC-ID; không đổi kỳ vọng của TC khi viết script.
- Phụ thuộc chỉ cài trong `qa/automation/` và **chỉ sau khi người dùng đồng ý** (DECISIONS); không cài toàn máy.
- Chạy thật; output (report của framework, stdout, ảnh) ghi vào `qa/evidence/<run-id>/<TC-ID>/` — đó là bằng chứng,
  kết quả ghi RUNLOG như chạy tay. Script lỗi do chính script (không phải sản phẩm) → sửa script, không ghi FAIL.
