# qa-agent — template quy trình kiểm thử độc lập SPEC

Quy trình **kiểm thử độc lập** cho **mọi sản phẩm phần mềm**, chạy bằng Claude Code. Một QC quyết tất (solo Authority), agent làm phần còn lại: dịch tài liệu bàn giao, lập chiến lược + kế hoạch test, dựng môi trường, viết test case, chạy test bằng thao tác thật, ra verdict theo ngưỡng đã ghi trước.

Đội dev dùng quy trình gì cũng được — sprint/Scrum, ticket, hay VIPER. Manifest bàn giao khai `Quy trình dev:` và SPEC tự chọn chế độ đối chiếu.

```
S ──► P ──► E ──► C
Scope     Prepare    Execute    Certify
nhận bàn giao,   bootstrap môi     chạy test độc     verdict theo ngưỡng
dịch tài liệu,   trường + viết     lập theo đợt,     ghi TRƯỚC, báo cáo,
test plan +      test case +       bằng chứng bắt    QC ký, rút bài học,
ngưỡng, QC chốt  dry-run           buộc              đóng release
↑ nơi DUY NHẤT được hỏi QC                           (hoặc chờ bàn giao lại)
```

## Vì sao có SPEC

Dev tự kiểm (unit test, demo, dogfood) chỉ nhìn **trong phạm vi việc vừa làm** và do chính người làm tự chấm. Không có gì bảo đảm toàn bộ scope chạy đúng như mô tả, và không ai kiểm bản cũ còn chạy sau khi bản mới đè lên.

SPEC đứng ngoài: dùng sản phẩm như người dùng thật, và **không tin bất cứ kết luận nào của dev cho tới khi tự chứng minh được bằng bằng chứng của mình**.

| | SPEC |
|---|---|
| **Release** | Một bản deploy đội dev bàn giao cho QC kiểm. Release 2 test tính năng mới của bản 2 **và regression** bản 1 |
| **Đầu vào** | Manifest QC thả vào `intake/releases/r<N>/` (phạm vi, bản deploy, môi trường, **bảng URL theo từng target**) + repo nguồn / thư mục tài liệu **chỉ đọc** (meta tự mirror) |
| **Môi trường** | Khai trong manifest: **production** + tenant/tài khoản test cách ly, hoặc **staging**. Mọi bản ghi mang prefix `SPEC-r<N>-` |
| **Bàn giao lại** | Verdict FAIL → dev fix → QC thả `RELEASE-<k>.md` → mở lại pha E **cùng release**, ngưỡng không đổi |
| **Đầu ra** | Báo cáo + verdict trong repo kiểm thử — SPEC không sinh file cho đội dev |

### Hai chế độ đầu vào

| Chế độ | `Quy trình dev:` | Đầu vào | Gate S kiểm thêm |
|---|---|---|---|
| Tổng quát (mặc định) | `khác` | PRD/spec/user story/release note/API doc/thiết kế… trong `Repo nguồn:` | Repo nguồn tồn tại · mirror `nguon/` ≥1 file · truy vết ≥3 dòng |
| VIPER | `VIPER` | Repo VIPER | Mỗi loop có `_PROPOSAL.md` · loop deploy có pha P · mirror `viper/` ≥5 file · truy vết ≥5 dòng |

## Khởi tạo dự án kiểm thử mới

```bash
python3 scripts/bootstrap.py <project-code> \
  --name "Tên sản phẩm — kiểm thử" \
  --authority "Tên QC <email@example.com>" \
  --source ../<repo-code-hoặc-thư-mục-tài-liệu>

# xem trước, không ghi gì:
python3 scripts/bootstrap.py <project-code> --dry-run
```

Script **copy** template ra thư mục mới (template giữ nguyên, dùng lại cho sản phẩm sau), thay placeholder, `git init` + commit đầu. `--source` chỉ là gợi ý ghi vào README dự án; nguồn thật là dòng `Repo nguồn:` trong manifest. (`--viper` là tên cũ, vẫn nhận.)

```bash
cd ../<project-code>
# QC thả manifest vào intake/releases/r1/RELEASE.md (xem intake/_RELEASE-TEMPLATE.md)
claude
/spec-scope
```

Manifest tối thiểu cho dự án không dùng VIPER:

```markdown
NGUỒN: BÀN GIAO RELEASE — từ đội app đặt lịch
Quy trình dev: khác
Repo nguồn: ../booking-docs
Release: 1
Phạm vi: Đặt lịch hẹn + nhắc lịch qua SMS (sprint 1–3)
Bản deploy: v1.0.0 (2026-09-20)
Môi trường: staging
Điểm vào chính: https://staging.booking.example.com
Lần bàn giao: 1

## URL theo target
| Target | Loại | URL / bundle id | Health check | Ghi chú |
|---|---|---|---|---|
| booking-web | web-experience | https://staging.booking.example.com | / | |
```

Yêu cầu:

| Cần | Để làm gì | Bắt buộc? |
|---|---|---|
| **Python 3.9+** · git | `gate.py`, `release.py`, `review_tc.py`, 5 hook — Python thuần, thư viện chuẩn | Có |
| **Node.js 18+** | Playwright MCP (`spec-browse`) và mobile-mcp (`spec-mobile`), tải khi chạy lần đầu | Có — luật #5 bắt kiểm bằng thao tác thật |
| Xcode / Android SDK | Simulator/emulator cho `spec-mobile` | Chỉ khi sản phẩm có experience mobile |
| Staging, hoặc quyền production + tenant test cách ly được | Nơi chạy test | Có |
| Bản build mobile bàn giao (.app/.apk) | SPEC **không build code sản phẩm** | Chỉ khi có mobile |
| `gitleaks` · `trufflehog` · `syft`/`grype` (hoặc `npm audit`/`pip-audit`) · `testssl.sh` | Loại test `bảo-mật` | Chỉ khi tick `bảo-mật` |

Máy dùng chung: Playwright chạy tối đa 4 worker, đóng trình duyệt khi xong; không chạy load/stress. Trên Windows dùng `python` thay `python3`; `bootstrap.py` tự đổi lệnh trong hook.

## Sửa template thì chạy cái này

```bash
python3 scripts/selftest.py            # vài giây
python3 scripts/selftest.py --keep     # giữ thư mục nháp để soi
```

Nó bootstrap một dự án nháp + repo nguồn giả (cả chế độ tổng quát lẫn VIPER), rồi đi trọn **S → P → E (FAIL) → C → `--retest` → E (PASS) → C → `--go`**, kiểm 5 hook chặn đúng chỗ, gate fail-closed đúng chỗ, và `release.py` giữ đúng sổ sách (archive, re-arm, mốc, không reset).

## Điểm cốt lõi

**Hỏi dồn ở pha S, sau đó toàn quyền — và mọi kết luận phải chứng minh được.**

Cài bằng năm thứ, không phải bằng lời khuyên:

1. **Ngưỡng verdict ghi TRƯỚC** khi chạy test (`TEST-PLAN §4`, chốt ở pha S) — hook `guard_frozen` chặn sửa ngoài pha S, gate C so ngày chốt với ngày chạy sớm nhất. Ngưỡng viết sau khi nhìn kết quả thì đọc kết quả nào cũng thấy "đạt".
2. **Bằng chứng bắt buộc** theo loại test (`TEST-STRATEGY §9`): ảnh thấy URL đúng môi trường · computed style kèm selector · response nguyên văn · cặp bằng chứng hai phía cho cross-target · PoC hoặc output tool uy tín cho bảo mật. Gate E kiểm đường dẫn evidence **tồn tại trên đĩa và không nằm trong repo nguồn**; `spec-evidence-auditor` bốc mẫu đối chiếu trước khi QC ký.
3. **Năm hook chặn cứng**: `guard_ask` (hỏi QC ngoài pha S) · `guard_readonly` (ghi vào repo nguồn) · `guard_frozen` (sửa ngưỡng/chiến lược — cả Write/Edit lẫn Bash) · `guard_verdict` (ghi REPORT khi test chưa đủ — dùng chung module đếm với `gate.py`) · `guard_evidence` (ảnh/video chụp được ghi ra ngoài `evidence/`).
4. **Đếm theo release, không reset**: mốc `(release N)` trong DECISIONS · challenge tính từ `Release mở`/`Bàn giao mở` · mỗi lượt bàn giao một mục RUNLOG · manifest từng lượt fail-closed · re-arm mục `(mỗi release)` của ENVIRONMENT.
5. **Kinh nghiệm tích luỹ**: skill `spec-knowledge` (checklist theo đối tượng + bug-patterns) đối chiếu khi viết TC; mỗi AC ≥1 TC normal + ≥1 TC abnormal (`scripts/review_tc.py` đếm); pha C rút bài học vào `context/LESSONS.md`, QC duyệt mới đưa vào kho.

Vá lỗ hổng compact bằng hook `SessionStart`: [scripts/reanchor.py](scripts/reanchor.py) đọc lại 8 luật + STATE + **ngưỡng đã khoá** từ file rồi nhồi vào context. Đo hiệu quả: `python3 scripts/reanchor.py --audit`.

## Roster tester — mở theo ma trận loại test

Từ điển loại test ở `TEST-STRATEGY §3`; **mỗi loại một agent**. Thiếu góc nhìn → thêm cột vào ma trận + tạo agent theo [`.claude/agents/_TESTER-TEMPLATE.md`](.claude/agents/_TESTER-TEMPLATE.md); gate P bắt loại tick trong ma trận mà không có TC.

| Agent | Phủ |
|---|---|
| `spec-tester-flow` · `-workflow` | chức năng theo AC · kịch bản end-to-end xuyên vai/trạng thái |
| `spec-tester-edge` · `-breaker` | rỗng/lỗi/mạng/nhiều dữ liệu · injection, chuỗi dài, double-submit, rate limit |
| `spec-tester-authz` · `-compat` | ma trận vai × hành động + cross-tenant · API/dữ liệu di sản release trước |
| `spec-tester-integration` · `-api` | email/SMS/payment/webhook + phụ thuộc giữa boundary · hành vi server qua API |
| `spec-tester-cross` · `-visual` | hành động ở A hiện ở B · computed style so token + a11y |
| `spec-tester-perf` · `-mobile` | p95 gọi thưa (cấm stress) · app native trên simulator |
| `spec-tester-security` | OWASP Top 10 chứng minh bằng thao tác + secrets + SBOM/CVE — chỉ khi QC xác nhận quyền kiểm thử bảo mật |
| `spec-evidence-auditor` | đối kháng nội bộ — soi bằng chứng trước khi ký |

Chạy **theo đợt ≤3 vai**, nhóm theo nhu cầu dữ liệu (B0 rỗng → đọc/đo → ghi → phá), reset giữa đợt: trình duyệt riêng từng vai nhưng **tenant test dùng chung**. Mobile chạy tuần tự. Bảo mật nằm trong đợt phá cuối cùng.

## Cấu trúc

```
SPEC.md                     policy T0 — 4 pha, 8 luật, bảng gate chuẩn, 2 chế độ đầu vào
CLAUDE.md · STATE.md        router đọc mỗi phiên · trạng thái sống (pha, release, lượt bàn giao)
Makefile                    hợp đồng lệnh môi trường test: doctor/seed/reset/accounts/devices/smoke

intake/                     cửa nhận bàn giao — đầu vào đóng băng
├── _RELEASE-TEMPLATE.md    đặc tả manifest (dòng máy đọc + bảng URL)
└── releases/r<N>/          RELEASE.md · RELEASE-<k>.md · nguon/ (mirror; VIPER: viper/)

context/                    nguồn sự thật
├── TEST-STRATEGY.md        chiến lược cả sản phẩm — lập MỘT lần ở release 1, QC chốt
├── HANDOVER.md             sổ dịch: marker + truy vết + lỗ hổng (kèm đề xuất + rủi ro)
├── COVERAGE-MAP.md         capability × release × TI × trạng thái
├── PERSONAS.md             persona + ma trận vai × hành động + tài khoản test
├── ARCHITECTURE.md         target · contract · luồng lõi · ca biên · dịch vụ ngoài
├── ENVIRONMENT.md          URL · tài khoản · tenant · seed B0/B1 · thiết bị · rác còn lại
├── API-SURFACE.md          surface do SPEC tự quan sát — baseline cho test tương thích
├── BUGS.md                 sổ bug append-only, severity S1–S4 (kiêm backlog: deferred)
├── DECISIONS.md            append-only, mốc (release N) / (release N — bàn giao k)
├── LESSONS.md              bài học sau mỗi release — QC duyệt mới vào spec-knowledge
├── testcases/              TC sống, tích luỹ qua release — regression = tag `Regression: có`
├── releases/r<N>/          TEST-PLAN (ngưỡng!) · RUNLOG · REPORT
├── archive/                release-N/ (snapshot) · ledger/ (gấp tay)
└── shared/                 CONVENTIONS · SAFETY (production + staging)

environment/                artifact chạy môi trường test (.env.example · local/seed)
evidence/r<N>/luot-<k>/     bằng chứng — RUNLOG trỏ vào, gate E kiểm tồn tại

.claude/
├── settings.json           Bash trần allow · ask cho DB/reset/hướng-ra-ngoài · 5 hook + reanchor
├── commands/               9 slash command
├── agents/                 13 tester + auditor + _TESTER-TEMPLATE
└── skills/                 spec · spec-browse · spec-mobile · spec-testcase-design · spec-evidence · spec-knowledge

scripts/
├── bootstrap.py            tạo dự án kiểm thử mới                  ← template only
├── _counts.py              module đếm dùng chung (gate ↔ hook không lệch nhau)
├── gate.py                 kiểm gate S/P/E/C — chỉ báo
├── release.py              --go đóng release · --retest mở lượt bàn giao
├── review_tc.py            pha P: máy soát bộ TC (normal/abnormal mỗi AC, meta, bằng chứng, kỳ vọng rỗng nghĩa)
├── guard_ask.py · guard_readonly.py · guard_frozen.py · guard_verdict.py · guard_evidence.py
├── reanchor.py · compact.py
└── selftest.py             chạy trọn vòng đời trên dự án nháp      ← template only
```

**`← template only`** = không copy sang dự án: `bootstrap.py`, `selftest.py`, và `README.md` này — dự án nhận một README riêng.

## Slash command

| Lệnh | Pha | Việc |
|---|---|---|
| `/spec-scope` | S | Manifest → mirror → dịch → *(r1)* TEST-STRATEGY → TEST-PLAN + **ngưỡng** → challenge → QC chốt → khoá scope · **nơi duy nhất được hỏi** |
| `/spec-prepare` | P | Bootstrap môi trường (**URL từng service/experience** đã curl xác nhận · tenant · tài khoản từng vai · seed B0/B1 · thiết bị) + viết test case (đối chiếu `spec-knowledge`, soát bằng `review_tc.py`) + dry-run |
| `/spec-execute` | E | Chạy test theo đợt — meta tự tay + agent tester, bằng chứng bắt buộc, bug đúng khuôn |
| `/spec-certify` | C | Máy tính verdict vs ngưỡng → REPORT → QC ký → LESSONS → PASS: `release.py --go` · FAIL: điều kiện bàn giao lại |
| `/spec-retest` | E | Bàn giao lại: manifest `RELEASE-<k>` → `--retest` → chạy phạm vi retest → certify lại |
| `/spec-status` · `/spec-decide` · `/spec-bug` | mọi pha | Đang ở đâu · ghi quyết định · ghi bug đúng khuôn |
| `/spec-compact` | ngoài pha | Vệ sinh tài liệu, gấp tay vào `archive/ledger/` — từ release ≥3 |

## An toàn — production hay staging

Phanh thật là **cách ly**, không phải permission rule ([context/shared/SAFETY.md](context/shared/SAFETY.md)):

- Chỉ tenant/tài khoản test; mọi bản ghi mang prefix `SPEC-r<N>-`; không đụng bản ghi thiếu prefix (staging dùng chung: đó là dữ liệu của người khác).
- Seed/dọn **qua API** — **cấm chạm thẳng DB production**; staging chỉ khi `TEST-STRATEGY §8` cho phép (lớp `ask` chặn `psql`/`mysql`/… như gờ giảm tốc).
- Không gửi notification tới người thật; thanh toán/SMS chỉ sandbox — staging chưa xác nhận sandbox thì TC chạm vào là `BLOCKED`; **cấm stress/load** (n ≤ 20, giãn cách ≥1s).
- Bảo mật: chỉ chứng minh lỗ, không phá; active scan chỉ khi QC xác nhận quyền kiểm thử (dẫn nguyên văn vào DECISIONS).
- `make reset` chỉ xoá prefix release hiện tại — **dữ liệu di sản** release cũ giữ lại cho test tương thích ngược.

## Chuyển từ qa-agent v1

v1 là một agent đơn (`qa-agent.md` + `qa-security-agent.md` + `qa-knowledge/`) làm việc trong thư mục `qa/` của dự án, hỏi duyệt ở từng stage. v2 là **template dự án kiểm thử riêng** theo quy trình SPEC. Mọi ý của v1 đều còn, chỉ đổi chỗ:

| v1 | v2 |
|---|---|
| Stage SETUP → DOCS_READY → TC_DRAFTED → TC_APPROVED → ROUND_OPEN → EXECUTED → REPORTED, duyệt từng stage | 4 pha S → P → E → C. Hỏi và duyệt dồn ở pha S (+ QC ký ở pha C); pha P/E tự quyết, ghi `DECISIONS.md` |
| Workspace `qa/` trong repo sản phẩm | Repo kiểm thử riêng (`bootstrap.py`), repo sản phẩm chỉ đọc |
| `qa/docs/` | Mirror `intake/releases/r<N>/nguon/` |
| `QUAN-DIEM-<feature>.md` (quan điểm test) | `TEST-STRATEGY.md` (cả sản phẩm) + `TEST-PLAN.md §2` hạng mục TI (từng release) |
| `QA-<feature>.md` (hỏi–đáp làm rõ tài liệu) | `HANDOVER.md §Lỗ hổng & cách xử` (cột đề xuất của meta + rủi ro nếu sai) + hỏi QC ở pha S |
| `TC-<PREFIX>-<feature>.md`, priority P1–P4 | `context/testcases/CAP-….md`, mức rủi ro R1–R3, nhãn `Kiểu: normal/abnormal` |
| `coverage-review.md` | `COVERAGE-MAP.md` + gate P đếm AC/TI/ô ma trận |
| Round `R<N>` + `scope.md` | Release `r<N>` + lượt bàn giao `k` (`RUNLOG.md`) |
| Bug `BUG-<PREFIX>-NNN` trong `rounds/R<N>/bugs/`, severity P/S | `context/BUGS.md` khối `BUG-r<N>-<số>`, severity S1–S4 |
| Report GO / CONDITIONAL GO / NO-GO | Verdict PASS / PASS-có-điều-kiện / FAIL, máy tính từ ngưỡng ghi trước |
| `tracking/decisions.md` | `context/DECISIONS.md` (cột giả định + đảo ngược được) |
| `qa-knowledge/checklists/*`, `bug-patterns.md` | Skill `.claude/skills/spec-knowledge/` |
| `qa-knowledge/lessons/` | `context/LESSONS.md` |
| `qa-security-agent` (stage-gate riêng) | Loại test `bảo-mật` + agent `spec-tester-security` trong đợt phá |
| Evidence `rounds/R<N>/evidence/` | `evidence/r<N>/luot-<k>/<TC-ID>/`, hook `guard_evidence` giữ ảnh trong repo |

Dự án đang chạy dở với v1: chốt round hiện tại bằng v1, rồi bootstrap dự án v2 — chép TC còn dùng vào `context/testcases/` (thêm dòng meta), bug còn mở vào `BUGS.md`, knowledge riêng của dự án vào `spec-knowledge`.

## Khi nào KHÔNG dùng SPEC

| Hợp | Không hợp |
|---|---|
| Một QC quyết tất | Nhiều bên sign-off chéo |
| Có tài liệu bàn giao (dù sơ sài) + biết bản deploy nào đang được kiểm | Không có tài liệu nào để biết release cắt ở đâu |
| Có staging, hoặc production cách ly được dữ liệu test | Chỉ có production mà không cách ly nổi dữ liệu test |
