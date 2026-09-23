# qa-agent — trợ lý kiểm thử cho mọi quy trình, mọi loại dự án

Bộ skill + agent + lệnh cho Claude Code, cài vào **bất kỳ dự án nào** (repo sản phẩm, hoặc một thư mục QA riêng),
hỗ trợ **mọi việc QA**: phân tích tài liệu, làm rõ yêu cầu, lập kế hoạch/chốt scope, thiết kế và review test case,
chuẩn bị dữ liệu, chạy test, smoke, regression, test lại bug, test khám phá, viết test tự động, bảo mật, hiệu năng,
a11y, ghi bug, báo cáo, rút bài học — cho **web, mobile, API, desktop, CLI, job/pipeline dữ liệu, tính năng AI/LLM,
thư viện/SDK** (loại khác: có hướng dẫn tự lập công thức).

Không ép quy trình. Đội làm Scrum, theo ticket, waterfall, release gate hay hotfix đều được — QA ghép các việc theo
quy trình của đội và ghi lại ở `qa/QA.md` để phiên sau làm tiếp.

## Bốn điều luôn đúng

| | |
|---|---|
| **Không bịa** | Mọi TC, kết luận, bug trỏ về nguồn: tài liệu, code, câu trả lời của người dùng, checklist, hoặc điều tự quan sát. Được đọc cả tài liệu lẫn code để phân tích và biết cách test; code lệch tài liệu → hỏi cái nào đúng |
| **Chưa rõ thì hỏi** | Tài liệu mơ hồ, kết quả không rõ bug hay hiểu sai, bước TC không khớp sản phẩm, thiếu môi trường/tài khoản, muốn làm điều chưa được nhờ → **dừng và hỏi**, kèm điều đã thấy + các cách hiểu + đề xuất. Không tự suy diễn, không tự ý làm |
| **Bằng chứng thật** | PASS/FAIL phải có `qa/evidence/<run>/<TC>/` đúng loại (ảnh + URL, response nguyên văn, stdout + exit code, transcript AI…). Không có → BLOCKED |
| **An toàn môi trường** | Chỉ tài khoản/dữ liệu test mang prefix, không bắn thông báo tới người thật, không tiêu tiền thật, không chạm thẳng DB production, không load test trên môi trường dùng chung |

## Cài

```bash
git clone https://github.com/Duck712/qa-agent ~/qa-agent
python3 ~/qa-agent/install.py <thư-mục-dự-án> --name "Tên sản phẩm"
python3 ~/qa-agent/install.py <thư-mục-dự-án> --dry-run      # xem trước
python3 ~/qa-agent/install.py <thư-mục-dự-án> --update       # nhận bản mới (skill, checklist, bài học chung)
```

`install.py` **gộp**, không ghi đè: giữ `settings.json` / `.mcp.json` / file sẵn có của dự án; không bao giờ đụng dữ liệu
trong `qa/`; `--update` giữ file người dùng đã sửa tay và báo ra. Cần Python 3.9+ và git; Node 18+ cho web/mobile
(Playwright MCP, mobile-mcp); Xcode/Android SDK chỉ khi có app mobile.

## Dùng

```text
/qa phân tích docs/prd-dat-lich.md
/qa sprint 12 test gì, lên plan giúp
/qa viết TC cho màn đăng ký
/qa vừa deploy v2.3 lên staging, smoke giúp
/qa dev báo fix BUG-012 rồi
/qa vọc thử luồng thanh toán 30 phút
/qa viết script Playwright cho TC-DK-001..005
/qa kiểm con bot CSKH trả lời đúng bảng giá không
/qa CLI `ingest` xử lý file CSV hỏng thế nào
/qa release được chưa
```

Lệnh tắt cho việc hay dùng: `/qa-analyze` · `/qa-plan` · `/qa-testcase` · `/qa-run` · `/qa-bug` · `/qa-report` · `/qa-status`.

Lần đầu mở `claude` trong dự án, chấp nhận hộp thoại tin cậy thư mục (trust) — chưa tin cậy thì Claude Code bỏ qua
các quyền `allow` mà bộ cài thêm vào, và server MCP trong `.mcp.json` chưa được bật.

## Đã chạy thử thật

Trên các dự án demo cài sẵn lỗi (CLI Python, REST API, trang web), bằng `claude -p` không giao diện:

| Công đoạn | Kết quả |
|---|---|
| Phân tích tài liệu | Ra REQ + 8 điểm mơ hồ kèm đề xuất; **không tự điền câu trả lời nào**, dừng lại hỏi |
| Chốt scope → viết TC → chạy → bug → báo cáo | CLI: 32 TC, tìm đủ 3 lỗi cài sẵn + 4 lỗi thật khác; bằng chứng là file lệnh/stdout/stderr/exit; code sản phẩm không bị đụng |
| Test lại bug | Xác nhận 2 bug đã sửa, bắt thêm lỗi trước đó bị che; hỏi có chạy regression không thay vì tự chạy |
| Smoke khi chưa có scope | Đề xuất phạm vi + tiêu chí + 4 điểm mơ hồ, **chờ duyệt** rồi mới chạy |
| Web qua Playwright MCP | 16 TC, tìm đúng lỗi cài sẵn, đo màu bằng computed style, ảnh nằm đúng `qa/evidence/` |

Chưa chạy thử thật: mobile, desktop, batch, AI, thư viện, bảo mật, viết test tự động, test khám phá — công thức đã có
trong `qa-targets`, cần một dự án thật để kiểm.

## Kỹ thuật được hỗ trợ

| Nhóm | Kỹ thuật | Ở đâu |
|---|---|---|
| Phân tích & review tài liệu (tĩnh) | Quy trình review 8 bước · tiêu chí chất lượng yêu cầu (kiểm được, rõ, đủ, nhất quán, khả thi, truy vết) · INVEST + Given–When–Then · danh sách từ yếu · đọc theo góc nhìn (người dùng, tester, dev, vận hành, bảo mật, nghiệp vụ) · yêu cầu ngầm ISO 25010 · example mapping · mô hình hoá (use case, trạng thái, CRUD, luồng dữ liệu) · đối chiếu tài liệu ↔ code · rủi ro xác suất × thiệt hại · phân tích ảnh hưởng chọn regression | `qa-knowledge/analysis-review.md` |
| Thiết kế TC hộp đen | Phân vùng tương đương · giá trị biên 2/3 giá trị · biên nhiều chiều (domain analysis) · syntax testing · bảng quyết định / cause-effect · ma trận phân quyền · ma trận CRUD · chuyển trạng thái (bảng trạng thái × sự kiện, 0/1-switch) · use case & kịch bản (luồng chính/thay thế/ngoại lệ) · pairwise & classification tree | `qa-testcase-design/ky-thuat/` |
| Hộp trắng nhẹ | Rút nhánh, validate, mã lỗi, điểm kiểm quyền, truy vấn tenant, vùng vừa đổi từ code → mỗi thứ có TC hộp đen chạm tới | `ky-thuat/hop-trang.md` |
| Không có đáp án chắc | Chọn oracle · metamorphic testing · property · fuzz có seed | `ky-thuat/oracle.md` |
| Dựa trên kinh nghiệm | Error guessing có hệ thống · fault attacks · checklist-based · khám phá theo phiên (SBTM, charter, tour, debrief) | `ky-thuat/kinh-nghiem.md` |
| Phi chức năng | Hiệu năng/tải · 10 heuristic Nielsen · WCAG 2.2 A/AA · tương thích · tin cậy/khôi phục · i18n/l10n · cài đặt/vận hành | `ky-thuat/phi-chuc-nang.md` |
| Review TC | Ba lớp: hình thức (`qa_check.py tc`) · truy vết (`qa_check.py trace` → `qa/TRACE.md`) · checklist nội dung theo từng kỹ thuật | `ky-thuat/review-tc.md` |

Mật độ theo rủi ro: R1 ≥ 2 kỹ thuật + biên 3 giá trị + mọi ô cấm + luồng ngoại lệ · R2 phân vùng + biên + luồng
chính/thay thế · R3 happy path + 1 ca abnormal — mọi REQ luôn có cả ca đúng lẫn ca sai. Công cụ: `pairwise.py`
(sinh bộ tổ hợp có ràng buộc), `gen_matrix_tc.py` (TC phân quyền từ ma trận), `qa_check.py trace` (ma trận truy vết).

## Học từ lỗi

| Tầng | Ở đâu | Ghi khi nào |
|---|---|---|
| Dự án | `qa/LESSONS.md` | Ngay khi gặp: kiểu lỗi đáng nhớ, sự cố môi trường/công cụ, điều người dùng sửa lưng ("lần sau đừng…"), câu hỏi đã chốt. Đọc lại đầu mỗi việc |
| Dùng chung | `kit/.claude/skills/qa-knowledge/` trong repo này | Bài học dùng được cho dự án khác → hỏi người dùng → thêm vào checklist/bug-patterns → các dự án nhận qua `install.py --update` |

Kho chung đã có 13 checklist (form, đăng nhập/phân quyền, upload, API, ca bất thường, thanh toán, thông báo, realtime,
tìm kiếm/danh sách, ngày giờ/lịch, CLI, job/dữ liệu, AI/LLM) và 24 kiểu lỗi dev hay mắc.

## Cấu trúc

```
install.py                  cài / cập nhật vào dự án
tests/selftest.py           cài vào dự án nháp, kiểm từng mảnh (chạy sau mỗi lần sửa)
kit/
├── .claude/
│   ├── commands/           /qa (nhận mọi việc) + 7 lệnh tắt
│   ├── agents/             qa-tester (1 target × 1 góc nhìn) · qa-security · qa-evidence-check
│   ├── skills/
│   │   ├── qa/                  danh mục 18 việc QA, luật chung, ghép theo quy trình, lưu bài học
│   │   ├── qa-targets/          web · mobile · api · desktop · cli · batch · ai · library · khác + an toàn
│   │   ├── qa-testcase-design/  chọn kỹ thuật, mật độ theo rủi ro, khuôn TC + ky-thuat/ (10 file kỹ thuật, review TC)
│   │   ├── qa-evidence/         bằng chứng theo loại test × loại target, chống test giả
│   │   └── qa-knowledge/        checklist + bug-patterns + phân tích/review tài liệu + mẹo nghề (kho chung)
│   ├── qa-scripts/         qa_check.py (status · tc · trace · select · new-run · run) · pairwise.py · gen_matrix_tc.py · 2 hook
│   └── settings.qa.json    phần gộp vào settings.json của dự án
├── .mcp.qa.json            Playwright MCP + mobile-mcp, version khoá cứng
└── qa/                     workspace mẫu: QA.md · ANALYSIS · SCOPE · testcases/ · runs/ · BUGS · DECISIONS · LESSONS
```

`qa_check.py` chỉ **báo** (không chặn): TC thiếu trường, REQ thiếu ca normal/abnormal, kỳ vọng mơ hồ, PASS không có
bằng chứng, FAIL không có bug, và tính **kết luận ĐẠT / KHÔNG ĐẠT** theo tiêu chí ghi trước trong `SCOPE.md §6`.
Hai hook nhẹ chặn thật: `guard_evidence` (ảnh/video phải nằm trong `qa/evidence/`) và `guard_readonly` (không ghi vào
đường dẫn khai ở `qa/QA.md §Nguồn chỉ đọc`).

## Lấy gì từ SPEC (v2)

v3 bỏ bộ máy pha S-P-E-C, gate, release/lượt bàn giao; giữ phần prompt và cấu trúc agent đã chứng minh hiệu quả:
ngưỡng ghi trước khi chạy · bằng chứng bắt buộc theo loại + checklist chống test giả · auditor soi bằng chứng trước
khi báo cáo · 4 kỹ thuật thiết kế TC + luật normal/abnormal · tester theo góc nhìn (gộp 13 agent thành một
`qa-tester` nhận góc nhìn làm tham số) · luật an toàn khi test trên môi trường thật · hook giữ bằng chứng trong dự án.
Thêm: đường dẫn bằng chứng tuyệt đối (v2 để tương đối nên ảnh lạc thư mục khi mở phiên chỗ khác), MCP khoá version,
công cụ sinh TC phân quyền từ ma trận, 6 loại target mới, cơ chế lưu bài học hai tầng. Bản v2 vẫn ở lịch sử git
(commit `11b5a85`).

## Giới hạn

- Kiểm từ bên ngoài như người dùng — không viết unit test trong code sản phẩm (trừ khi được nhờ viết test tự động).
- Load/stress chỉ khi khai môi trường riêng; không bao giờ trên production hay máy dùng chung.
- Native Windows cần máy Windows; firmware/phần cứng không có emulator → QA viết TC, người dùng thực hiện và gửi bằng chứng.
- Tính năng AI chấm theo tiêu chí quan sát được × N lần chạy — tiêu chí chủ quan cần người dùng duyệt mẫu.
