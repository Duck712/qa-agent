# qa-agent — trợ lý kiểm thử cho mọi quy trình, mọi loại dự án

Bộ skill + agent + lệnh cho Claude Code, cài vào **bất kỳ dự án nào** (repo sản phẩm, hoặc một thư mục QA riêng),
hỗ trợ **mọi việc QA**: phân tích tài liệu, làm rõ yêu cầu, quan điểm test (test viewpoint), lập kế hoạch/chốt scope,
thiết kế và review test case,
chuẩn bị dữ liệu, chạy test, smoke, regression, test lại bug, test khám phá, viết test tự động, bảo mật, hiệu năng,
a11y, ghi bug, báo cáo, rút bài học — cho **web, mobile, API, desktop, CLI, job/pipeline dữ liệu, tính năng AI/LLM,
thư viện/SDK** (loại khác: có hướng dẫn tự lập công thức).

Không ép quy trình. Đội làm Scrum, theo ticket, waterfall, release gate hay hotfix đều được — QA ghép các việc theo
quy trình của đội và ghi lại ở `qa/QA.md` để phiên sau làm tiếp.

## Bốn điều luôn đúng

| | |
|---|---|
| **Không bịa — bám đặc tả** | REQ và quan điểm test ghi nguồn + **trích nguyên văn** câu đặc tả (máy đối chiếu với file, agent `qa-source-check` đối chiếu URL/pdf/docx); TC đi ra từ quan điểm đã duyệt. Gợi ý từ checklist/kinh nghiệm chỉ là `ngoài đặc tả` chờ người dùng duyệt. Code lệch tài liệu → hỏi cái nào đúng |
| **Chưa rõ thì hỏi** | Tài liệu mơ hồ, kết quả không rõ bug hay hiểu sai, bước TC không khớp sản phẩm, thiếu môi trường/tài khoản, muốn làm điều chưa được nhờ → **dừng và hỏi**, kèm điều đã thấy + các cách hiểu + đề xuất. Không tự suy diễn, không tự ý làm |
| **Bằng chứng thật** | PASS/FAIL phải có `qa/evidence/<run>/<TC>/` đúng loại (ảnh + URL, response nguyên văn, stdout + exit code, transcript AI…). Không có → BLOCKED |
| **An toàn môi trường** | Chỉ tài khoản/dữ liệu test mang prefix, không bắn thông báo tới người thật, không tiêu tiền thật, không chạm thẳng DB production, không load test trên môi trường dùng chung |

Nguyên tắc bao trùm: **agent không tự ý làm thay người dùng** — không tự đặt tiêu chí đạt, mức rủi ro, ngưỡng,
số lần chạy; không tự đổi trạng thái/severity bug ngoài các chuyển được phép ghi ở `qa/BUGS.md`, tự chạy lại hay hạ kết quả, tự cài công cụ, tự sửa repo sản phẩm.
Kit không có con số mặc định: thiếu thì đề xuất và hỏi; chưa chốt tiêu chí thì kết luận là `CHƯA KẾT LUẬN`.

## Cài — từng bước (cho người mới bắt đầu)

> **Hình dung trước khi làm**
> - Thư mục **`qa-agent`** là **bộ cài**: tải về một lần, để yên một chỗ, **không làm việc trong đó**.
> - Mỗi dự án cần test có **một thư mục riêng** (vd `Documents\QA\du-an-dat-lich`). Bộ cài chép agent vào thư mục đó.
> - Bạn làm việc bằng cách mở thư mục dự án trong **Orca** (ứng dụng chạy Claude Code) rồi gõ lệnh cho **Claude**.
>
> Hướng dẫn ghi cho **Windows**. Máy Mac: xem dòng *Mac:* ở từng bước.

**Cách mở PowerShell** (nhiều bước dưới cần): bấm phím **Windows** → gõ `PowerShell` → bấm **Windows PowerShell**.
Cửa sổ hiện ra có dòng `PS C:\Users\<tên bạn>>`. Dán lệnh bằng **chuột phải** (hoặc Ctrl+V) rồi bấm **Enter**.
*Mac:* mở **Terminal** (Cmd+Space → gõ `Terminal`).

### Phần A — Chuẩn bị máy (chỉ làm một lần)

#### A1. Tài khoản Claude
Claude Code cần tài khoản Claude trả phí: **Pro, Max, Team hoặc Enterprise** (gói Free không dùng được Claude Code).
Đăng ký / đăng nhập ở <https://claude.ai>. Công ty cấp tài khoản Team/Enterprise thì dùng tài khoản đó.

#### A2. Cài Python (để chạy bộ cài)
1. Vào <https://www.python.org/downloads/> → bấm nút **Download Python 3.x** (bản 3.9 trở lên đều được).
2. Mở file vừa tải. Ở màn hình đầu tiên **tích ô `Add python.exe to PATH`** (quan trọng — quên tích thì lệnh
   `python` không chạy) → bấm **Install Now** → chờ xong → **Close**.
3. Kiểm tra: mở **PowerShell mới**, gõ `python --version` → thấy `Python 3.x.x` là được.
   Nếu Windows mở Microsoft Store thay vì in số phiên bản: cài lại Python và nhớ tích ô ở bước 2.

*Mac:* tải bản macOS ở cùng trang, cài như phần mềm thường; kiểm tra bằng `python3 --version`.

#### A3. Cài Git
Orca làm việc với thư mục dạng "repo git"; Claude Code trên Windows cũng nên có Git.
1. Vào <https://git-scm.com/downloads/win> → tải **Git for Windows** (bản 64-bit).
2. Mở file cài → bấm **Next** liên tục, giữ mọi lựa chọn mặc định → **Install** → **Finish**.
3. Kiểm tra: mở PowerShell mới, gõ `git --version` → thấy `git version …` là được.

*Mac:* gõ `git --version` trong Terminal; máy hỏi cài "command line developer tools" thì bấm **Install**.

#### A4. Cài GitHub Desktop và tải bộ cài `qa-agent`
1. Vào <https://desktop.github.com> → **Download** → mở file cài (cài tự động, không cần bấm gì thêm).
2. Mở GitHub Desktop. Đăng nhập GitHub hoặc bấm **Skip this step** — tải bộ cài không cần tài khoản.
3. Menu **File → Clone repository…** → chọn tab **URL** → ô *Repository URL* dán:
   `https://github.com/Duck712/qa-agent`
4. Ô **Local path** để mặc định (`C:\Users\<tên bạn>\Documents\GitHub\qa-agent`) → bấm **Clone**.
5. Xong: máy bạn có thư mục `Documents\GitHub\qa-agent`. Đây là bộ cài — không sửa gì trong đó.

#### A5. Cài Claude Code và đăng nhập
1. Mở PowerShell, dán lệnh sau rồi Enter (lệnh chạy im lặng một lúc, chờ đến khi hiện lại dòng `PS C:\…>`):
   ```powershell
   irm https://claude.ai/install.ps1 | iex
   ```
2. **Đóng PowerShell, mở cửa sổ mới**, gõ `claude --version` → thấy số phiên bản (vd `2.x.x (Claude Code)`) là được.
   Báo `claude is not recognized`: khởi động lại máy rồi thử lại.
3. Đăng nhập: gõ `claude` → Enter → chọn đăng nhập bằng tài khoản Claude → trình duyệt mở ra → đăng nhập và bấm
   cho phép → quay lại PowerShell thấy Claude sẵn sàng là xong. Gõ `/exit` để thoát.
   Chỉ cần đăng nhập một lần — Orca dùng lại phiên đăng nhập này.

*Mac:* lệnh cài là `curl -fsSL https://claude.ai/install.sh | bash`, các bước còn lại giống hệt.

#### A6. Cài Orca
Orca (<https://github.com/stablyai/orca>) là ứng dụng chạy Claude Code trong một cửa sổ có danh sách dự án,
terminal và trình duyệt.
1. Tải bản Windows: <https://github.com/stablyai/orca/releases/latest/download/orca-windows-setup.exe>
   (hoặc vào <https://onorca.dev/download>).
2. Mở file `orca-windows-setup.exe` để cài. Nếu Windows hiện cảnh báo "Windows protected your PC" thì bấm
   **More info → Run anyway**.
3. Mở Orca lần đầu:
   - Orca xin quyền truy cập thư mục người dùng (home) → **cho phép** (để Orca mở được thư mục dự án).
   - Orca hỏi nhập cài đặt có sẵn (`~/.claude` …) → **đồng ý** (dùng lại đăng nhập Claude ở bước A5).

*Mac:* ở trang <https://github.com/stablyai/orca/releases/latest> tải `orca-macos-arm64.dmg` (máy chip Apple M1/M2/M3…)
hoặc `orca-macos-x64.dmg` (máy chip Intel), kéo Orca vào **Applications**; lần đầu mở nếu máy hỏi thì bấm **Open**.

#### A7. (Chỉ khi test web hoặc app mobile) Cài Node.js
Agent điều khiển trình duyệt / điện thoại qua Node.js. Chỉ phân tích tài liệu, viết quan điểm / test case thì **bỏ qua**.
Vào <https://nodejs.org> → tải bản **LTS** → cài mặc định (Next liên tục). Kiểm tra: `node --version` (cần 18 trở lên).
Test app mobile cần thêm Android Studio (Android) hoặc Xcode (iOS, chỉ trên Mac).

### Phần B — Mỗi dự án mới (làm lại cho từng dự án)

#### B1. Cài agent vào thư mục dự án
Mở PowerShell, dán lệnh dưới — **đổi `du-an-dat-lich`** (tên thư mục, viết liền không dấu) và **`"Đặt lịch"`**
(tên sản phẩm) theo dự án của bạn:
```powershell
python $HOME\Documents\GitHub\qa-agent\install.py $HOME\Documents\QA\du-an-dat-lich --name "Đặt lịch"
```
Thư mục chưa có thì bộ cài **tự tạo**. Cài xong thấy các dòng `✓` và mục **Tiếp theo**. Trong thư mục dự án giờ có:
`.claude\` (agent), `qa\` (nơi agent ghi phân tích, quan điểm test, test case, bài học) và `docs\` (để tài liệu).

*Mac:* `python3 ~/Documents/GitHub/qa-agent/install.py ~/Documents/QA/du-an-dat-lich --name "Đặt lịch"`

#### B2. Bỏ tài liệu đặc tả vào `docs\`
Tài liệu trên Google Drive / Sheets / Excel → tải về thư mục `docs\` của dự án (agent không tự mở link Drive):

| Tài liệu | Tải về dạng | Agent đối chiếu trích dẫn tự động? |
|---|---|---|
| Google Docs | File → Download → **Plain text (.txt)** hoặc **Markdown (.md)** | ✅ |
| Google Sheets / Excel | File → Download → **CSV** (mỗi sheet một file) | ✅ |
| PDF | giữ nguyên | ⚠️ agent đọc được, đối chiếu do `qa-source-check` |
| Word (.docx) | nên lưu thành .txt | ❌ chưa đọc thẳng |

Đặt tên kèm ngày tải (vd `docs\prd-dat-lich-2026-09-23.txt`) và ghi link gốc vào `qa\QA.md` mục **Tài liệu** —
tài liệu trên Drive hay bị sửa, cần biết test đang bám bản nào. Có bản mới thì tải lại.

#### B3. Biến thư mục dự án thành repo git (để Orca mở được)
Orca chỉ thêm được thư mục là repo git. Làm bằng GitHub Desktop, **chỉ lưu trên máy bạn**:
1. GitHub Desktop → menu **File → Add local repository…** → **Choose…** → chọn thư mục dự án
   (`Documents\QA\du-an-dat-lich`).
2. Hiện dòng *"This directory does not appear to be a Git repository…"* → bấm chữ **create a repository**.
3. Giữ nguyên **Name** và **Local path** → bấm **Create repository**.
4. Nếu tab **Changes** bên trái còn liệt kê file: ô **Summary** gõ `bắt đầu` → bấm **Commit to main**.

> ⚠️ **Không bấm "Publish repository"**. Thư mục dự án chứa tài liệu và kết quả test của khách — chỉ để trên máy,
> không đưa lên GitHub. (File mật khẩu `qa\.env` đã được bộ cài loại khỏi git sẵn.)

#### B4. Mở dự án trong Orca và chạy Claude
1. Mở Orca → bấm **Add Repo** (thanh bên trái) → chọn thư mục dự án (`Documents\QA\du-an-dat-lich`).
   **Không** chọn thư mục `qa-agent`.
2. Dưới tên dự án ở thanh bên trái, bấm **dòng thư mục chính** (dòng nhánh `main`).
   > ⚠️ **Không bấm dấu `+`** cạnh tên dự án. Dấu `+` tạo một **bản sao** thư mục (worktree) — agent sẽ ghi kết quả
   > vào bản sao, còn ảnh bằng chứng vẫn đổ về thư mục chính → kết quả bị tách hai nơi.
3. Mở terminal ở dòng đó, chọn **Claude Code** trong ô chọn agent. Nếu chỉ thấy terminal trống thì gõ `claude` rồi Enter.
4. Lần đầu Claude hỏi hai câu, **cả hai chọn đồng ý**:
   - **Tin cậy thư mục** (trust) — không đồng ý thì luật và quyền của agent không chạy.
   - **Bật MCP `browser` / `mobile`** — công cụ điều khiển trình duyệt / điện thoại.

Không dùng Orca cũng được: mở PowerShell, gõ `cd $HOME\Documents\QA\du-an-dat-lich` rồi `claude` (khi đó bỏ qua B3).

#### B5. Dùng agent
Gõ vào ô chat của Claude:
1. `/qa-status` → Claude in ra tình trạng dự án = agent đã cài đúng.
2. Lần lượt các việc chính (mỗi lệnh xong, Claude hỏi lại những chỗ chưa rõ — bạn trả lời rồi làm lệnh tiếp):
   ```text
   /qa-analyze docs           phân tích tài liệu → yêu cầu (REQ) + câu hỏi cho bạn
   /qa-viewpoint <tính-năng>  quan điểm test → bạn duyệt
   /qa-plan <tên đợt>         chốt scope + tiêu chí đạt
   /qa-testcase <tính-năng>   viết test case từ quan điểm đã duyệt
   /qa-review all             review quan điểm + test case + scope
   ```
3. Việc khác thì nói bằng lời thường sau `/qa`, vd `/qa vừa deploy lên staging, smoke giúp` (xem mục **Dùng** bên dưới).

Mẹo:
- Cần giao test case/quan điểm dưới dạng Excel: nói *"xuất test case ra Excel"* (agent tạo CSV trong `qa\export\`, mở bằng
  Excel hoặc import vào Google Sheets). TC người khác viết trên Sheets: tải CSV rồi nói *"review file tc.csv"*.
- Bàn giao bằng tiếng Anh/Nhật: ghi `- Ngôn ngữ bàn giao: en` (hoặc `ja`) trong `qa\QA.md` — file xuất có tiêu đề cột theo
  ngôn ngữ đó; nhờ agent dịch nội dung thì bản dịch nằm riêng trong `qa\export\`, file trong `qa\` vẫn tiếng Việt.
- TC agent không tự chạy được (thiết bị thật, máy in…) hoặc đội muốn người chạy: ghi `- Thực hiện: người` trong TC —
  agent giao cho người, nhận kết quả + bằng chứng họ gửi về và ghi vào run.
- Lần sau mở lại: Orca → bấm dòng thư mục chính của dự án → mở terminal Claude Code → làm tiếp (agent tự nạp bài học
  và câu hỏi đang chờ).

**Dự án tiếp theo**: làm lại Phần B (B1 → B5) với thư mục mới. Phần A không cần làm lại.

### Gặp lỗi thường gặp

| Hiện tượng | Cách xử lý |
|---|---|
| `python` mở Microsoft Store / báo không tìm thấy | Cài lại Python, tích ô **Add python.exe to PATH** (A2), mở PowerShell mới |
| `claude is not recognized` | Mở PowerShell mới; vẫn lỗi thì khởi động lại máy (A5) |
| Claude báo cần đăng nhập / gói không hỗ trợ | Gõ `claude` trong PowerShell để đăng nhập lại; kiểm tra tài khoản là Pro/Max/Team/Enterprise (A1) |
| Orca không thêm được thư mục | Thư mục chưa là repo git → làm B3 |
| Orca không chạy được Claude Code | Gõ `claude` trong PowerShell thường xem có chạy không; có chạy thì trong Orca vào **Settings → Agents** kiểm tra đường dẫn Claude Code |
| Gõ `/qa-status` không thấy lệnh | Đang mở nhầm thư mục (vd `qa-agent`) hoặc chưa đồng ý **tin cậy thư mục** → mở đúng thư mục dự án, mở lại Claude |
| Test web báo lỗi `npm` / không mở được trình duyệt | Chưa cài Node.js (A7) |

### Nhận bản mới của bộ cài
1. GitHub Desktop → chọn repo `qa-agent` (ô **Current repository** góc trên trái) → bấm **Fetch origin**, có bản mới thì
   bấm **Pull origin**.
2. Với **từng** dự án, chạy trong PowerShell:
   ```powershell
   python $HOME\Documents\GitHub\qa-agent\install.py $HOME\Documents\QA\du-an-dat-lich --update
   ```
Dữ liệu trong `qa\` không bị ghi đè; file mẫu cũ cần gộp tay thì bộ cài báo ra.

### Tuỳ chọn nâng cao
```bash
python install.py <dự án> --dry-run          # xem trước sẽ đổi gì, không ghi
python install.py <dự án> --settings-local   # cài vào REPO CODE mà dev khác cũng dùng Claude Code
```
`install.py` **gộp**, không ghi đè: giữ `settings.json` / `.mcp.json` / file sẵn có của dự án (server MCP đã chỉnh tay
được giữ nguyên và báo ra); không bao giờ đụng dữ liệu trong `qa/`; `--update` giữ file người dùng đã sửa tay và báo ra.
- `--settings-local`: quyền + hook ghi vào `.claude/settings.local.json` (không commit) — dev khác không bị hook của QA chặn.
- Thư mục bằng chứng trong `.mcp.json` và agent là **đường dẫn tuyệt đối** của máy cài → chép dự án sang máy/account
  khác thì chạy lại `install.py <dự án> --update` trên máy đó.

## Dùng

```text
/qa phân tích docs/prd-dat-lich.md
/qa tạo quan điểm test cho tính năng đặt lịch
/qa review bộ TC trong file tc-dat-lich.csv
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

Lệnh tắt cho việc hay dùng: `/qa-analyze` · `/qa-viewpoint` · `/qa-plan` · `/qa-testcase` · `/qa-review` · `/qa-run` · `/qa-bug` ·
`/qa-report` · `/qa-status`.

Chuỗi tài liệu test: **phân tích** (`ANALYSIS.md`, REQ + trích nguyên văn) → **quan điểm test** (`viewpoints/`, người dùng
duyệt) → **chốt scope** (`SCOPE.md`: phạm vi, mức rủi ro, tiêu chí đạt, vào/ra, lịch, bàn giao) → **test case**
(`testcases/`, mỗi TC trỏ `VP:`) → **review** (`/qa-review`: máy soát + checklist + đối chiếu nguồn). Truy vết
REQ → quan điểm → TC ở `qa_check.py trace`. Đội dùng Excel: `qa_check.py export tc|vp` / `import tc|vp <file.csv>`.

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
| Quan điểm test | Rút theo góc (luồng, dữ liệu, luật, trạng thái, quyền, hiển thị, tích hợp, phi chức năng) từ câu đặc tả · normal + abnormal mỗi REQ · tách nhóm ngoài đặc tả · checklist review | `ky-thuat/quan-diem.md` |
| Review tài liệu test | Quan điểm (`qa_check.py vp`) · TC ba lớp: hình thức (`qa_check.py tc`) · truy vết (`qa_check.py trace` → `qa/TRACE.md`) · checklist nội dung · nguồn (`qa_check.py src` + `qa-source-check`) · kế hoạch (`qa-knowledge/scope-review.md`) | `ky-thuat/review-tc.md` |

Mật độ theo rủi ro: R1 kỹ thuật thuộc ≥ 2 họ + biên 3 giá trị + mọi ô cấm + luồng ngoại lệ · R2 phân vùng + biên + luồng
chính/thay thế · R3 happy path + 1 ca abnormal — mọi REQ luôn có cả ca đúng lẫn ca sai. Công cụ: `pairwise.py`
(sinh bộ tổ hợp có ràng buộc), `gen_matrix_tc.py` (TC phân quyền từ ma trận), `qa_check.py trace` (ma trận truy vết).

## Học từ lỗi

| Tầng | Ở đâu | Ghi khi nào |
|---|---|---|
| Dự án | `qa/LESSONS.md` | Ngay khi gặp: kiểu lỗi đáng nhớ, lỗ quan điểm, sự cố môi trường/công cụ, điều người dùng sửa lưng ("lần sau đừng…"), câu hỏi đã chốt. Hook `hook_session` nạp bài học đang hiệu lực vào **mọi phiên**; hook `hook_prompt` thấy câu sửa lưng thì nhắc ghi ngay; subagent nhận bài học liên quan qua `qa_check.py lessons --for …`; dòng xong cất bằng `lessons --archive` |
| Dùng chung | `kit/.claude/skills/qa-knowledge/` trong repo này | Bài học dùng được cho dự án khác → hỏi người dùng → thêm vào checklist/bug-patterns → người dùng commit + push lên repo chung (thẳng `main` hoặc qua PR, tuỳ đội) → các dự án nhận qua `install.py --update` |

**Đưa bài học lên kho chung, từng bước:**
1. Làm việc bình thường — agent tự ghi bài học vào `qa/LESSONS.md` của dự án (bug đáng nhớ, sự cố, lần bạn sửa lưng).
2. Cuối đợt (`/qa-report`) agent hỏi bài học nào dùng được cho dự án khác. Bạn đồng ý → agent viết lại cho tổng quát
   (bỏ tên màn/API riêng) và thêm vào checklist chung trong thư mục **`qa-agent`** (bộ cài).
3. GitHub Desktop → repo `qa-agent` → thấy file checklist vừa đổi → ghi mô tả → **Commit to main** → **Push origin**.
4. Mọi người: **Pull** repo `qa-agent`, rồi `install.py <dự án> --update` cho từng dự án — từ đó gặp tính năng tương tự
   (thanh toán, form, đăng nhập, lịch…) agent tự kiểm luôn điểm này.

Agent chỉ đưa bài học vào kho chung khi **bạn đồng ý** — kho chung không lẫn bài sai hoặc chỉ đúng cho một dự án.

Kho chung đã có 15 checklist (form, đăng nhập/phân quyền/MFA/SSO, upload, API, ca bất thường, thanh toán, thông báo, realtime,
tìm kiếm/danh sách, ngày giờ/lịch, dữ liệu cá nhân, a11y WCAG 2.2, CLI, job/dữ liệu, AI/LLM), đánh số từng mục để TC trích nguồn và 24 kiểu lỗi dev hay mắc.

## Cấu trúc

```
install.py                  cài / cập nhật vào dự án
tests/selftest.py           cài vào dự án nháp, kiểm từng mảnh (chạy sau mỗi lần sửa)
tests/refcheck.py           kiểm mọi tham chiếu file/skill/lệnh/§ trong bản đã cài
kit/
├── .claude/
│   ├── commands/           /qa (nhận mọi việc) + 9 lệnh tắt
│   ├── agents/             qa-tester (1 target × 1 góc nhìn) · qa-security · qa-evidence-check · qa-source-check
│   ├── skills/
│   │   ├── qa/                  danh mục 19 việc QA, luật chung, ghép theo quy trình, lưu bài học
│   │   ├── qa-targets/          web · mobile · api · desktop · cli · batch · ai · library · khác + an toàn
│   │   ├── qa-testcase-design/  chọn kỹ thuật, mật độ theo rủi ro, khuôn TC + ky-thuat/ (9 file kỹ thuật + review-tc)
│   │   ├── qa-evidence/         bằng chứng theo loại test × loại target, chống test giả
│   │   └── qa-knowledge/        checklist + bug-patterns + phân tích/review tài liệu + mẹo nghề (kho chung)
│   ├── qa-scripts/         qa_check.py (status · vp · tc · src · trace · select · new-run · run · release · export · import · lessons)
│   │                       · pairwise.py · gen_matrix_tc.py · 4 hook (guard_evidence · guard_readonly · hook_session · hook_prompt)
│   └── settings.qa.json    phần gộp vào settings.json của dự án
├── .mcp.qa.json            Playwright MCP + mobile-mcp, version khoá cứng
└── qa/                     workspace mẫu: QA.md · ANALYSIS · viewpoints/ · SCOPE · testcases/ · runs/ · BUGS · DECISIONS · LESSONS
```

`qa_check.py` chỉ **báo** (không chặn): TC thiếu trường, REQ thiếu ca normal/abnormal, kỳ vọng mơ hồ, PASS không có
bằng chứng, FAIL không có bug, và tính **kết luận ĐẠT / KHÔNG ĐẠT** theo tiêu chí ghi trước (chép từ `SCOPE.md §6` vào RUNLOG lúc tạo run; chưa chốt → CHƯA KẾT LUẬN); `release` trả lời "phát hành được chưa" trên nhiều run.
Hai hook nhẹ chặn thật: `guard_evidence` (ảnh/video phải nằm trong `qa/evidence/`) và `guard_readonly` (không ghi vào
đường dẫn khai ở `qa/QA.md §Nguồn chỉ đọc`). Hai hook nhắc (không chặn): `hook_session` (đầu phiên nạp luật + bài học +
câu hỏi chờ; dự án có `QA.md §Quy trình bắt buộc` → nạp toàn văn quy trình đó, bài học chỉ hiện tiêu đề, toàn văn lấy
bằng `qa_check.py lessons --for <công đoạn>`) và `hook_prompt` (người dùng sửa lưng → nhắc ghi `LESSONS.md`).
`qa_check.py` cũng báo: REQ/quan điểm thiếu nguồn hoặc trích dẫn không có trong file nguồn, quan điểm ngoài đặc tả chưa
được duyệt, TC trỏ quan điểm chưa duyệt (run tự bỏ TC đó).

## Giới hạn

- Kiểm từ bên ngoài như người dùng — không viết unit test trong code sản phẩm (trừ khi được nhờ viết test tự động).
- Load/stress chỉ khi khai môi trường riêng; không bao giờ trên production hay máy dùng chung.
- Native Windows cần máy Windows (UI Automation có sẵn — `qa-targets/windows.md`); app cũ không lộ phần tử UI, firmware/
  phần cứng không có emulator → TC `Thực hiện: người`: QA viết TC, người thực hiện và gửi bằng chứng.
- Trên Windows agent không gửi được Ctrl-C thật cho tiến trình — ca "ngắt bằng Ctrl-C" cần người bấm tay.
- Tính năng AI chấm theo tiêu chí quan sát được × N lần chạy — tiêu chí chủ quan cần người dùng duyệt mẫu.
