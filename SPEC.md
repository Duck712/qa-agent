---
type: spec-policy
version: 1.1
tier: T0
owner: Authority (QC, solo)
last_reviewed: "{{DATE}}"
---

# SPEC v1.1 — quy trình kiểm thử độc lập cho mọi sản phẩm phần mềm

> **Đây là tài liệu T0.** Mọi tài liệu khác trong repo phải nhất quán với file này. Conflict → file này thắng.

---

## 0. SPEC dùng cho việc gì

SPEC kiểm thử **độc lập** một sản phẩm phần mềm do một đội dev (người hoặc agent) làm ra — bất kể đội đó dùng quy trình gì. Dev tự kiểm (unit test, dogfood, demo) chỉ nhìn trong phạm vi việc họ vừa làm và do chính người làm tự chấm — không có gì bảo đảm toàn bộ scope hoạt động đúng như mô tả. SPEC đứng ngoài, dùng sản phẩm như người dùng thật, và **không tin bất cứ kết luận nào của dev cho tới khi tự chứng minh được bằng bằng chứng của mình**.

Hai chế độ đầu vào, chọn bằng dòng `Quy trình dev:` của manifest (§1.3):

| Chế độ | Khi nào | Đầu vào | Release cắt ở đâu |
|---|---|---|---|
| **khác** (mặc định) | Mọi dự án: tài liệu bàn giao là PRD/spec/ticket/Figma/README/wiki xuất ra… | `Repo nguồn:` = repo code **hoặc** thư mục tài liệu bàn giao — chỉ đọc | Mỗi lần đội dev deploy một bản cho QC kiểm (`Bản deploy:` = version/tag/commit/ngày) |
| **VIPER** | Sản phẩm làm bằng quy trình VIPER (có `VIPER.md`, `intake/loops/l<i>/_PROPOSAL.md`) | `Repo nguồn:` = repo VIPER — gate đối chiếu thêm loop/_PROPOSAL/pha P | Loop có pha P (deploy) |

| | SPEC |
|---|---|
| Authority | **QC** — một người quyết tất (solo), chốt scope test, ký verdict |
| Đường vào | **Chỉ intake** — không có đường phỏng vấn. Đầu vào là manifest bàn giao + repo nguồn (chỉ đọc) |
| Đơn vị lặp | **Release** — một bản deploy mà đội dev bàn giao cho QC kiểm, gồm các tính năng mới của đợt đó. VD: sprint 1–3 deploy v1.0, sprint 4–5 deploy v1.1 → release 1 = v1.0 · release 2 = v1.1 (kèm regression v1.0). Chế độ VIPER: một khối loop kết thúc bằng loop có pha P |
| Môi trường | Khai ở manifest (`Môi trường:`): **production** + tenant/tài khoản test cách ly, hoặc **staging** — luật an toàn §7 áp cho cả hai |
| Đầu ra | Báo cáo release + verdict **trong repo SPEC** — SPEC không sinh file cho đội dev |
| Người dùng quy trình | QA engineer — mọi tài liệu là bảng tiếng Việt đơn giản, đọc/sửa tay được không cần biết code |

| Hợp | Không hợp |
|---|---|
| Một QC quyết tất | Nhiều bên sign-off chéo |
| Có tài liệu bàn giao (dù sơ sài) + biết bản deploy nào đang được kiểm | Không có tài liệu nào, không biết release cắt ở đâu |
| Có staging riêng, hoặc test trên production với tenant test cách ly được | Chỉ có production mà không cách ly nổi dữ liệu test |

SPEC đứng trên năm nguyên tắc: **context là nguồn sự thật · quyết định phải có vết · gate trước khi đi tiếp · gate chỉ báo, hook mới chặn · không reset, đếm theo đơn vị lặp**. Năm hook chặn cứng: hỏi QC ngoài pha S · ghi vào repo nguồn · sửa ngưỡng/chiến lược ngoài pha S · ghi verdict khi test chưa chạy đủ · ghi ảnh/video chụp được ra ngoài `evidence/` (§3c).

---

## 1. Bốn pha

```
S ──► P ──► E ──► C
Scope     Prepare    Execute    Certify

nhận bàn giao,   bootstrap môi     chạy test mới +    verdict theo ngưỡng
dịch tài liệu,   trường + thiết    regression, bằng    ghi TRƯỚC, báo cáo,
test plan +      kế test case,     chứng bắt buộc      QC ký, đóng release
ngưỡng, QC chốt, dry-run                               (hoặc chờ bàn giao lại)
khoá scope
↑ nơi DUY NHẤT được hỏi QC
```

| Pha | Việc |
|---|---|
| **S — Scope** | Nhận manifest bàn giao → mirror + dịch tài liệu nguồn sang `context/` → *(release 1)* lập `TEST-STRATEGY.md` cho cả sản phẩm, QC chốt → viết `TEST-PLAN.md` của release: phạm vi AC, hạng mục test, out-of-scope, **ngưỡng verdict ghi trước**, regression scope → challenge → QC chốt plan → **khoá scope** |
| **P — Prepare** | Bootstrap môi trường test (production cách ly hoặc staging, theo manifest): URL từng target, tenant + tài khoản theo vai, seed/reset hai mốc dữ liệu, thiết bị mobile → viết test case phủ đủ hạng mục → chọn regression → `make doctor` xanh → dry-run một luồng lõi |
| **E — Execute** | Chạy test **độc lập, thao tác thật**: meta tự tay + spawn agent tester theo đợt → mọi TC có kết quả + bằng chứng → FAIL thành bug có severity |
| **C — Certify** | Máy tính verdict từ kết quả so **ngưỡng đã ghi trước** → báo cáo → QC ký → PASS: đóng release, mở release mới · FAIL: chờ dev fix, bàn giao lại, quay lại pha E (**cùng release**, lượt bàn giao +1) |

Cả 4 pha bắt buộc ở mọi release — kiểm thử không có pha "tuỳ chọn". Không có stage machine; gate chỉ báo: `python3 scripts/gate.py <pha>`. Năm hook ở §3c mới chặn.

### 1.1 Gate rời pha — bản chuẩn

> **Đây là định nghĩa gate DUY NHẤT.** `CLAUDE.md §2`, `STATE.md §Gate` và `scripts/gate.py` là bản sao thao tác của bảng này. Lệch nhau → bảng này thắng, sửa ba chỗ kia cho khớp (luật #4).
>
> Mốc đếm: release 1 tính hết; release ≥2 tính ngày ≥ `Release mở`; lượt bàn giao k ≥2 tính ngày ≥ `Bàn giao mở`. Phép so ngày luôn dùng **max(`Release mở`, `Bàn giao mở`)** — mốc nào không tồn tại thì bỏ qua. Thiếu mốc khi bắt buộc phải có (không mở bằng `release.py`) → **fail-closed**. Mốc có độ phân giải **NGÀY**: đóng release rồi mở release mới trong cùng ngày làm vết cùng-ngày của release cũ (challenge, DECISIONS) đếm được cho release mới — khi có thể, đừng đóng/mở trong cùng một ngày.

| Gate | Điều kiện | Máy kiểm được? |
|---|---|---|
| **S** | Manifest bàn giao là bản thật: `intake/releases/r<N>/RELEASE.md` (lượt k ≥2: `RELEASE-<k>.md` với k lớn nhất) không rỗng, hết `{{…}}` | ✓ |
| | Manifest đủ dòng máy đọc: `Quy trình dev:` · `Repo nguồn:` (thư mục tồn tại; chế độ VIPER: có `VIPER.md` + `context/`) · `Release:` khớp STATE · `Phạm vi:` (VIPER: `l<a>–l<b>`) · `Bản deploy:` (VIPER: `l<b>`) · `Môi trường:` (`production`\|`staging` — thiếu thì coi là production) · `Điểm vào chính:` · `Lần bàn giao:` khớp STATE. Có mobile-experience trong phạm vi → thêm `Bản build mobile:`. Nhãn cũ `Repo VIPER:` / `Phạm vi loop:` / `Loop deploy:` vẫn đọc được (và bật chế độ VIPER) | ✓ |
| | **Bảng `## URL theo target` ≥1 dòng thật**, và mọi target khai `Trong phạm vi` = có ở `ARCHITECTURE §1–§3` xuất hiện trong bảng — hoặc được ghi ở `HANDOVER §Lỗ hổng` (QC chưa biết URL → meta dò ở pha P, có vết). Hệ nhiều microservice khai từng service ở đây, boundary nội bộ ghi `—` kèm gateway chạm vào | ✓ |
| | *(chế độ VIPER)* Bàn giao khớp thực tế repo VIPER (đọc chỉ-đọc): mỗi loop trong phạm vi có `intake/loops/l<i>/_PROPOSAL.md`; loop khai ở `Bản deploy` có `P` trong dòng `Pha vòng này` | ✓ |
| | Mirror đã đóng băng — mọi phép dịch từ mirror, không từ nguồn sống: chế độ khác `intake/releases/r<N>/nguon/` có ≥1 file tài liệu (`.md`/`.pdf`/`.docx`/ảnh…) · chế độ VIPER `intake/releases/r<N>/viper/` có ≥5 file `.md` (PRD/CAPABILITIES-MAP/PERSONAS/ARCHITECTURE + tài liệu vòng) | ✓ |
| | `context/HANDOVER.md`: dòng đầu ngoài comment mang marker `NGUỒN: <tên nguồn> — <path>` khớp manifest (VIPER: `NGUỒN: VIPER — <path>`) + bảng `## Truy vết nguồn → context` ≥3 dòng (VIPER ≥5) + `## Lỗ hổng & cách xử` không rỗng | ✓ |
| | *(release 1)* `context/TEST-STRATEGY.md` đủ §1–§10, hết `_CHƯA ĐIỀN_`, có dòng `Chốt bởi QC:` — bảng §2 (chuỗi release dự kiến) ≥1 dòng; chế độ VIPER: số dòng §2 **≥** số loop đã khai `P` trong các `_PROPOSAL.md` hiện có | ✓ |
| | *(release ≥2 — thay dòng trên)* `TEST-PLAN.md` có dòng `Rà lại chiến lược (release N): <ISO>` ngày ≥ `Release mở`; `Phạm vi` của manifest lệch dòng release N ở `TEST-STRATEGY §2` (so chuỗi, bỏ khoảng trắng) → phải có dòng change log `TEST-STRATEGY §11` ngày ≥ `Release mở` | ✓ |
| | `context/releases/r<N>/TEST-PLAN.md` đủ: 4 dòng đầu máy đọc · §1 bảng AC mới (mã `AC-n` giữ nguyên như tài liệu nguồn, kèm nguồn nếu mã trùng giữa các tài liệu — VIPER: `AC-n (l<i>)` — + capability) · §2 ≥3 hạng mục `TI-n`, mỗi TI có Nguồn (CAP/AC) và `Loại test` thuộc ma trận `TEST-STRATEGY §3` · §3 out-of-scope tường minh · §4 **bảng ngưỡng verdict có số** · §5 regression scope | ✓ |
| | Mọi `TI-n` của TEST-PLAN §2 có mặt ở `COVERAGE-MAP.md`; mọi capability thuộc phạm vi release có dòng trong COVERAGE-MAP | ✓ |
| | ≥2 quyết định `DECISIONS.md` của release này — release ≥2 đếm dưới mốc `(release N)`, ngày ≥ `Release mở`; thiếu mốc → fail-closed | ✓ |
| | Challenge pha S **PASS** ở `STATE.md §Challenge log` — 3–5 câu khó nhất về phạm vi test, trả lời chỉ từ tài liệu đã dịch; ngày ≥ mốc | ✓ |
| | `TEST-PLAN.md` có dòng `Chốt bởi QC: <ISO>` — chữ ký của QC cho plan + ngưỡng | ✓ |
| | **Scope khoá** — từ đây không hỏi QC nữa | người |
| **P** | Challenge pha P **PASS** (ngày ≥ mốc) | ✓ |
| | `context/ENVIRONMENT.md`: **mỗi** boundary/experience trong phạm vi (`ARCHITECTURE.md §1–§3` bản dịch) có một dòng ở §1–§2 — URL/bundle id đã curl xác nhận, hoặc `—` + đường vòng cho service nội bộ · mỗi vai trong ma trận `PERSONAS.md §2` có ≥1 tài khoản test · có mục Tenant + prefix · có mục Seed/Reset hai mốc B0/B1 · phạm vi có mobile → có mục Thiết bị | ✓ |
| | `make doctor` · `make seed` · `make reset` · `make accounts` · `make devices` · `make smoke` đã hiện thực (thân không còn NOT_IMPLEMENTED) | ✓ |
| | Test case đủ phủ: mỗi `TI-n` có ≥1 TC · mỗi AC mới có ≥1 TC · TC loại `phân quyền` phủ đủ ô ✗ của ma trận · mỗi TC có dòng meta máy đọc hợp lệ | ✓ |
| | **Mỗi loại test** tick trong ma trận `TEST-STRATEGY §3` × phạm vi release có ≥1 TC — loại cố tình bỏ phải nằm ở `TEST-PLAN §3` out-of-scope | ✓ |
| | *(release ≥2)* Regression đã chọn: `TEST-PLAN §5` liệt kê ≥ số TC tối thiểu theo `TEST-STRATEGY §6`, mọi TC được liệt kê tồn tại và mang tag `Regression: có` | ✓ |
| | `make doctor` xanh (URL sống, tài khoản đăng nhập được, cách ly đúng) · `make seed` chạy xong không lỗi | người |
| | **Dry-run**: meta tự tay đi MỘT luồng lõi trên môi trường test bằng tài khoản test (skill `spec-browse` / `spec-mobile`) | người |
| **E** | Sổ chạy đúng release + đúng lượt: `context/releases/r<N>/RUNLOG.md` có mục `## Lượt chạy — bàn giao <k>` với k khớp STATE; k ≥2 mà thiếu mục hoặc thiếu `Bàn giao mở` trong STATE → fail-closed | ✓ |
| | Mọi TC trong phạm vi lượt (lượt 1: TC mới của release + regression đã chọn ở TEST-PLAN §5 · lượt k ≥2: bảng `### Phạm vi retest` của mục lượt đó) có ≥1 dòng kết quả `PASS|FAIL|BLOCKED|SKIP` ngày ≥ mốc lượt | ✓ |
| | Mỗi dòng `PASS` có link bằng chứng trỏ `evidence/r<N>/…` **tồn tại trên đĩa** và không nằm trong repo nguồn | ✓ |
| | Mỗi dòng `FAIL` có bug `BUG-r<N>-<số>` trong `BUGS.md` với Severity ∈ S1–S4 · mỗi `BLOCKED` có blocker ở `STATE.md §Blocker` · mỗi `SKIP` có 1 dòng `DECISIONS.md` | ✓ |
| | *(lượt k ≥2)* Mọi bug trạng thái `mở`/`đã fix chờ retest` của lượt trước có dòng kết quả retest trong mục lượt này | ✓ |
| | Kết quả là **thao tác thật** trên môi trường test — không suy từ đọc code/tài liệu của dev (soi bằng `spec-evidence-auditor`, §3b) | người |
| **C** | **Ngưỡng ghi trước**: ngày `Chốt bởi QC` của TEST-PLAN ≤ ngày sớm nhất trong mục lượt chạy bàn giao 1 của RUNLOG | ✓ |
| | **Verdict máy tính khớp verdict ghi**: gate tự tính từ `BUGS.md` (bug `mở` theo severity — **tính cả bug còn mở từ release trước**: cam kết PASS-có-điều-kiện không tự biến mất) + RUNLOG (kết quả lượt hiện tại) đối chiếu bảng ngưỡng `TEST-PLAN §4` → verdict đề xuất; PASS-có-điều-kiện còn đòi tổng TC PASS đạt ngưỡng + từng S2 mở có dòng DECISIONS cam kết; `REPORT.md` mục `## Kết luận — bàn giao <k>` phải ghi đúng verdict đó | ✓ |
| | `REPORT.md` đủ mục: executive summary · số liệu · so ngưỡng · kết quả regression · *(FAIL)* mục `## 5. Bàn giao lại cho dev` liệt kê bug | ✓ |
| | Mọi bug của release có trạng thái cuối: `đóng` · `mở` (đi vào REPORT) · `không sửa`/`deferred` kèm 1 dòng DECISIONS — và bảng `Tổng hợp` của BUGS.md khớp con số đếm từ các khối | ✓ |
| | `COVERAGE-MAP.md` cột Trạng thái cập nhật cho mọi TI của release | người |
| | **QC ký**: dòng `Ký bởi QC: <ISO>` trong mục `## Kết luận — bàn giao <k>`, ngày ≥ mốc lượt | ✓ |
| | PASS → đóng release bằng `python3 scripts/release.py --go` · FAIL → chờ manifest `RELEASE-<k+1>.md`, chạy `python3 scripts/release.py --retest` | ✓ script |

**Vì sao ngưỡng phải ghi trước.** Ngưỡng verdict viết sau khi nhìn kết quả thì đọc kết quả nào cũng thấy sản phẩm "đạt" — cùng lý do mọi quy trình thực nghiệm nghiêm túc cấm sửa tiêu chí sau khi nhìn số. SPEC khoá bằng máy: hook `guard_frozen` chặn sửa `TEST-PLAN.md`/`TEST-STRATEGY.md` ngoài pha S, và gate C so ngày chốt với ngày chạy sớm nhất làm backstop.

### 1.2 Release và lượt bàn giao — đếm theo release, không reset

Một **release** = một lượt S→P→E→C trên một bản deploy bàn giao (chế độ VIPER: một khối loop). Release hiện tại ghi ở `STATE.md` (`Release: N`). Trong một release có thể có nhiều **lượt bàn giao** (`Lần bàn giao: k`): verdict FAIL → dev fix → QC thả manifest mới → SPEC quay lại pha E retest — **cùng release**, không mở release mới.

**KHÔNG có cơ chế reset.** Tài liệu sống tiến hoá qua các release: test case tích luỹ (regression lớn dần), sổ bug append-only, API-SURFACE dày lên. Hàng rào chống "gate release mới xanh sẵn nhờ vết release cũ" là các **cơ chế đếm theo release**:

| Cơ chế | Đóng đường lọt nào |
|---|---|
| Gate S chỉ đọc `intake/releases/r<N>/` **đúng số release** trong STATE | Manifest release cũ không xanh hộ release mới — QC phải thật sự bàn giao từng release |
| Dòng `Rà lại chiến lược (release N): <ngày>` ≥ `Release mở` | TEST-STRATEGY lập một lần ở r1 KHÔNG làm gate mọi release xanh sẵn — mở release nào phải thật sự rà lại chiến lược trước thực tế release đó |
| Mốc `(release N)` / `(release N — bàn giao k)` trong DECISIONS — gate chỉ đếm dưới mốc cuối | Quyết định cũ không gánh hộ |
| Challenge chỉ tính dòng ngày ≥ max(`Release mở`, `Bàn giao mở`) | Challenge PASS cũ không gánh hộ |
| Mỗi release một RUNLOG riêng; trong sổ, mỗi lượt bàn giao một mục có mốc ngày | Kết quả chạy của release/lượt trước không tính là "đã chạy" cho lượt này — kết quả cũ vẫn nằm cạnh làm lịch sử |
| Manifest `RELEASE-<k>.md` cho từng lượt retest, fail-closed | "Team nói mồm đã fix" không mở được lượt chạy — phải có văn bản; team báo qua chat thì meta ghi hộ manifest, trích nguyên văn |
| Re-arm: bỏ tick mục `(mỗi release)` trong `ENVIRONMENT.md` khi mở release | "Môi trường đã kiểm cho release cũ" không tự thành "đã kiểm cho release mới" |
| Ngưỡng chốt ở pha S, `guard_frozen` khoá, gate C so ngày | Không sửa ngưỡng sau khi nhìn kết quả — kể cả giữa hai lượt bàn giao |

`release.py --go` (đóng release N khi verdict PASS + QC ký) chỉ làm sổ sách: archive **snapshot** tài liệu sống (`TEST-STRATEGY/HANDOVER/COVERAGE-MAP/PERSONAS/ARCHITECTURE/ENVIRONMENT/API-SURFACE/BUGS/testcases/STATE` → `context/archive/release-N/` — chỉ copy) · sửa STATE tại chỗ (Release N+1 · `Release mở: <ngày>` · `Lần bàn giao: 1` · pha S · bỏ tick §Gate) · tạo `context/releases/r<N+1>/` (TEST-PLAN/RUNLOG/REPORT scaffold) + `intake/releases/r<N+1>/` rỗng · mốc DECISIONS · bỏ tick mục `(mỗi release)`. `context/releases/r<N>/` và `intake/releases/r<N>/` đánh số theo release nên **tự nó là lưu trữ** — không move đi đâu.

`release.py --retest` (mở lượt bàn giao k+1 khi verdict FAIL): đòi manifest `RELEASE-<k+1>.md` có mục `## Dev đã fix` (nhãn cũ `## VIPER đã fix` vẫn đọc được) liệt kê mã bug — thiếu là từ chối. Chỉ sửa STATE (`Lần bàn giao: k+1` · `Bàn giao mở: <ngày>` · pha E · bỏ tick gate E và C, **giữ nguyên** S và P — scope đã khoá, môi trường còn đó) · append mục lượt mới vào RUNLOG kèm bảng `### Phạm vi retest` sinh cơ học (mọi TC dính bug chưa đóng + regression chọn lọc theo `TEST-STRATEGY §6`) · mốc `(release N — bàn giao k+1)` vào DECISIONS. **KHÔNG đổi ngưỡng** — verdict lượt mới so nguyên bảng ngưỡng cũ.

**Cái đã certify là hợp đồng.** Mọi TC PASS ở release đã đóng là lời hứa với QC — release sau phải giữ: bộ regression = TC sống mang tag `Regression: có` của các release trước, chọn theo chính sách `TEST-STRATEGY §6`. Dữ liệu SPEC tạo ở release trước (`SPEC-r<N-1>-…`) giữ lại làm **dữ liệu di sản** — `spec-tester-compat` kiểm chúng còn đọc/thao tác được sau release mới. Dev được phép phá legacy chỗ nào (ghi trong tài liệu bàn giao / release note) thì TC tương ứng gỡ khỏi regression, ghi 1 dòng DECISIONS.

### 1.3 Intake — bàn giao từ QC, đầu vào chỉ đọc

Đầu vào của một release gồm hai lớp, đều **đóng băng sau khoá scope** (chỉ thêm, không sửa):

| Lớp | Là gì | Máy giữ bằng |
|---|---|---|
| **Manifest** — `intake/releases/r<N>/RELEASE.md` | Chữ ký bàn giao của QC: quy trình dev (VIPER/khác), repo nguồn ở đâu, release gồm phạm vi nào, bản deploy nào, môi trường test (production/staging), điểm vào chính, lần bàn giao thứ mấy, **bảng URL theo từng target** (hệ nhiều microservice khai từng service — tên khớp ARCHITECTURE); kèm bản build mobile/quyền cấp sẵn nếu có. Bàn giao lại lần k → file **mới** `RELEASE-<k>.md`, không sửa file cũ. Định dạng: `intake/_RELEASE-TEMPLATE.md` | gate S fail-closed tới khi có manifest thật; mỗi lượt một manifest |
| **Mirror** — `intake/releases/r<N>/nguon/` (chế độ VIPER: `…/viper/`) | Bản chụp tài liệu then chốt tại thời điểm bàn giao. Chế độ khác: PRD/spec/user story/AC, release note, thiết kế (ảnh/PDF xuất từ Figma), API doc (OpenAPI/Postman), README/DEPLOY, `.env.example`, danh sách vai/quyền… — cái gì dev giao thì chép cái đó. Chế độ VIPER: PRD (+ archive/vong-i từng loop), CAPABILITIES-MAP, PERSONAS, ARCHITECTURE, DESIGN-SYSTEM, TECHSTACK, ROADMAP, DEPLOY.md, `.env.example`, `_PROPOSAL.md` các loop, BC-checklist. **Meta copy ở pha S** — QC không phải làm gì. Mọi phép dịch/đối chiếu về sau đi từ mirror, vì nguồn sống tiếp trong lúc SPEC còn đang test | mirror nằm trong repo SPEC nên bất biến với release |

**Repo nguồn là đầu vào CHỈ ĐỌC** (luật #4): SPEC đọc để mirror và đối chiếu, không bao giờ ghi — hook `guard_readonly` chặn cả Write/Edit lẫn lệnh Bash ghi vào đường dẫn khai ở `Repo nguồn:`. SPEC cũng không sinh file cho đội dev: bug và verdict nằm trong REPORT của repo SPEC, QC chuyển cho dev qua kênh của họ (tracker, chat…).

Sau khi dịch xong, **`context/` là nguồn sự thật** — file trong `intake/` là đầu vào đóng băng. Manifest thiếu/sai → báo QC thả bản mới (vẫn pha S, được hỏi).

### 1.4 TEST-STRATEGY — chiến lược một lần, release nào cũng phải aligned

Kiểm thử cần một bức tranh chung cho cả sản phẩm trước khi đi vào từng release: **release 1, pha S, sau khi dịch tài liệu, lập `context/TEST-STRATEGY.md` cho CẢ sản phẩm** — QC chốt một lần, các release sau không lập lại. Nội dung: chuỗi release dự kiến (theo roadmap/kế hoạch deploy của dev — chế độ VIPER: mỗi loop có P = một release) · ma trận loại test × target · tiếp cận risk-based · định nghĩa severity · chính sách regression · ngưỡng hiệu năng · chuẩn cách ly dữ liệu · chuẩn bằng chứng · khuôn ngưỡng verdict.

Ba mối nối mà `gate.py` đối chiếu để giữ alignment:

1. **Phạm vi**: `Phạm vi` trong manifest ⟷ dòng release N của `TEST-STRATEGY §2`. Lệch → phải có dòng change log §11 ngày ≥ `Release mở`, không có là đỏ.
2. **Loại test**: cột `Loại test` của mỗi TI trong `TEST-PLAN §2` phải là một tên trong ma trận §3, và ô (loại × target) tương ứng phải tick. TI "mồ côi chiến lược" là đỏ.
3. **Ngưỡng & regression**: bảng ngưỡng `TEST-PLAN §4` instantiate từ khuôn §10; ghi đè khuôn → 1 dòng DECISIONS. Số TC regression chọn ≥ tối thiểu §6.

**Sửa chiến lược**: chỉ ở pha S (hook `guard_frozen` chặn ngoài pha S), mỗi lần sửa 1 dòng change log §11 + 1 dòng DECISIONS; đổi lớn (thêm/bớt release, đổi định nghĩa severity, đổi khuôn ngưỡng) → hỏi QC — đang pha S, được hỏi. Nghi thức **rà lại**: mở release nào cũng đọc lại §2/§3/§6 đối chiếu kết quả release trước rồi ghi dòng `Rà lại chiến lược (release N): <ngày>` vào TEST-PLAN — rà mà không đổi gì cũng phải nói được vì sao vẫn đúng.

---

## 2. Tám luật

1. **Scope test khoá sau pha S.** Phát hiện ngoài phạm vi → ghi `BUGS.md` trạng thái `deferred`, release sau nhặt ở pha S — không nới release này. Muốn phá → 1 dòng `DECISIONS.md` nói rõ đánh đổi.
2. **Sau pha S: toàn quyền, không hỏi lại.** Từ pha P trở đi agent **không dùng AskUserQuestion**. Mơ hồ → tự quyết theo TEST-PLAN/TEST-STRATEGY/HANDOVER, ghi 1 dòng `DECISIONS.md`, đi tiếp. Chỉ ba trường hợp được dừng (§3d).
3. **Quyết định không hiển nhiên → 1 dòng `DECISIONS.md` trước khi test.** Đây là thứ **thay thế** cho việc hỏi.
4. **Context là nguồn sự thật; repo nguồn là đầu vào CHỈ ĐỌC.** Không ghi một byte vào repo nguồn (hook `guard_readonly`), không sinh file cho đội dev. Intake đóng băng sau khoá scope — chỉ thêm manifest mới, không sửa manifest cũ. Kết luận lệch tài liệu → sửa tài liệu cùng commit.
5. **Độc lập tuyệt đối với đội dev.** Unit test, dogfood, demo, lời mô tả của dev (người hay agent) chỉ là bối cảnh — **không bao giờ là bằng chứng**. Mọi dòng kết quả trong RUNLOG sinh từ thao tác thật của SPEC, link về `evidence/` của repo SPEC (gate E kiểm đường dẫn).
6. **Dữ liệu test phải cách ly — production hay staging đều vậy.** Chỉ tenant/tài khoản test đã khai ở `ENVIRONMENT.md`; mọi bản ghi tạo ra mang prefix `SPEC-r<N>-`; seed/dọn qua API — **CẤM chạm thẳng DB production** (staging: chỉ khi TEST-STRATEGY khai cho phép, QC quyết); không bắn notification tới người thật. Chi tiết: §7 + `context/shared/SAFETY.md`.
7. **Tiếng Việt có dấu cho mọi văn bản người đọc; bảng đơn giản QA vận hành được.** Giữ tiếng Anh cho ID (`TI-`, `TC-`, `BUG-`), API path, tên lệnh, tên file, term không có bản dịch chuẩn.
8. **Ngưỡng trước — bằng chứng trước — verdict sau.** Ngưỡng chốt ở pha S và khoá bằng hook; TC không bằng chứng thì không được tính PASS; verdict bị `guard_verdict` chặn tới khi test chạy đủ; challenge trước mỗi pha và `spec-evidence-auditor` soi trước khi ký (§3b).

---

## 3. Điểm mấu chốt

### a. Pha S phải hiểu đủ — dịch trung thành + vá lỗ hổng

Pha S có một mục tiêu: **hiểu sản phẩm và phạm vi bàn giao đủ sâu để sau đó không phải hỏi QC nữa**. Nguồn hiểu là bộ mirror — không phỏng vấn ai:

| Việc | Ghi vết ở |
|---|---|
| Mirror tài liệu nguồn + đối chiếu manifest với thực tế repo nguồn | `intake/releases/r<N>/nguon/` (VIPER: `viper/`) · `HANDOVER.md` bảng truy vết |
| Dịch: persona + ma trận vai (→ `PERSONAS.md`, thêm cột tài khoản test) · target + contract + URL (→ `ARCHITECTURE.md`) · capability × release (→ `COVERAGE-MAP.md`) | từng file context |
| Vá lỗ hổng — thứ tài liệu dev thường không nói đủ cho việc test: tài khoản admin lấy đâu, tenant test tạo thế nào, hộp thư test, sandbox thanh toán, giới hạn rate limit… Thứ tự: tìm trong mirror → hỏi QC (vẫn pha S — mỗi câu kèm đề xuất của meta + rủi ro nếu sai) → tự quyết + 1 dòng DECISIONS mỗi lỗ | `HANDOVER.md §Lỗ hổng` · `DECISIONS.md` |
| *(release 1)* Lập TEST-STRATEGY (§1.4) · *(release ≥2)* rà lại chiến lược + đối chiếu kết quả release trước (REPORT, BUGS deferred, phát hiện treo) | `TEST-STRATEGY.md` · `TEST-PLAN.md` |
| Viết TEST-PLAN: AC mới, TI, out-of-scope, **ngưỡng**, regression scope | `TEST-PLAN.md` |

Dấu hiệu dịch hời hợt (≥2 cái → quay lại vá): chỉ đọc PRD mà không mở tài liệu chi tiết (user story, release note, API doc; VIPER: archive từng loop) · bảng truy vết ghi chung chung ("từ tài liệu dev") thay vì trỏ file + mục · không lỗ hổng nào được ghi (tài liệu dev gần như không bao giờ nói đủ cho việc test) · TI không truy được về capability/AC nào · *(r≥2)* không dẫn được kết quả nào của release trước · `Rà lại chiến lược` ghi mà không nói được vì sao kế hoạch vẫn đúng.

### b. Đối kháng nội bộ thay cho hỏi QC — và thay cho tin lời agent

**Challenge trước mỗi pha.** Trước khi khoá scope (pha S) và trước khi dựng môi trường (pha P), meta tự ra 3–5 câu hỏi khó dựa trên tài liệu thật — loại chỉ trả lời được nếu đã đọc và hiểu:

- "AC-3 (l4) có ca 'gửi hai lần' — TC nào phủ, và seed nào dựng được trạng thái đó?"
- "Vai mechanic bị cấm sửa lịch người khác — tài khoản test nào đóng vai đó, gọi endpoint nào để thử?"
- "Release này không đổi UI — vì sao visual vẫn/không nằm trong phạm vi?"

Trả lời chỉ từ tài liệu. Chấm PASS/FAIL vào `STATE.md §Challenge log` (ngày ≥ mốc). FAIL → đọc lại, vá, **không được đi tiếp**.

**Execute độc lập — "chưa có bằng chứng thì chưa test".** Điều kiện xuyên suốt pha E:

1. **Meta tự tay** đi luồng lõi trên môi trường test trước (đợt 0) — không đi nổi là S1, dừng ngay, không phí agent.
2. **Spawn agent tester theo đợt** (≤3 vai/đợt, nhóm theo nhu cầu dữ liệu, reset giữa đợt — trình tự chuẩn ở `/spec-execute`). Trình duyệt riêng từng vai (`--isolated`) nhưng **tenant test dùng chung** — thả hết một lượt là vai này phá cảnh vai kia đang đo.
3. **Dấu hiệu test giả** — kết quả KHÔNG được tính khi: thiếu bằng chứng đúng loại (`TEST-STRATEGY §9`) · screenshot không thấy URL bar đúng môi trường test (khai ở manifest) · TC hình thức không nêu một giá trị computed style · TC phân quyền không có response nguyên văn · cả một agent báo "mọi TC pass" ngay lượt đầu trên release mới → cho chạy lại, đòi thao tác cụ thể + thứ thấy trên màn.
4. **`spec-evidence-auditor`** bốc mẫu dòng RUNLOG, mở evidence đối chiếu — chạy trước khi QC ký. Auditor không sửa gì, chỉ trả danh sách lệch chứng cứ.

### c. Không permission prompt trong sandbox — năm hook chặn cứng

`.claude/settings.json` allow sẵn `Edit`/`Write`/`Bash` trần + `mcp__browser`/`mcp__mobile`, `defaultMode: acceptEdits` — liệt kê prefix lệnh là thua thực tế; an toàn nằm ở thứ tự **deny → ask → allow**. Lớp `ask` cho ngữ cảnh test-trên-môi-trường-thật: `make reset` (xoá dữ liệu tenant test) · `psql`/`mysql`/`mongosh`/`redis-cli` (đường chạm thẳng DB — về nguyên tắc SPEC không dùng, nhưng deny hẳn thì mất đường điều tra; ask = mỗi lần chạm một lần người gật) · `ssh`/`scp`/`git push`. Lớp `deny`: `dropdb`, `sudo`, force-push, đọc `.env` — lưu ý phạm vi: deny chặn các file `.env` NGOÀI workflow; riêng `environment/local/.env` agent phải đọc/ghi được (mật khẩu tài khoản test do chính agent sinh ra ở pha P), nên nó KHÔNG nằm sau deny.

Gate chỉ báo. Năm hook mới chặn — cấm bằng văn xuôi không giữ được luật, nhất là sau compact:

| Hook | Chặn gì | Fail-open khi |
|---|---|---|
| `scripts/guard_ask.py` | `AskUserQuestion` khi ô `Scope khoá` đã tick, hoặc pha ≠ S, hoặc dòng pha sai định dạng (chặn kèm hướng dẫn sửa về `S\|P\|E\|C`). Ngoại lệ "hỏi thật" (§3d) hỏi bằng lời trong chat | không có STATE / không có dòng pha |
| `scripts/guard_readonly.py` | Write/Edit có `file_path` nằm trong repo nguồn (đường dẫn `Repo nguồn:` — hoặc `Repo VIPER:` — lấy từ manifest lượt hiện tại) · lệnh Bash vừa chứa đường dẫn đó vừa mang token ghi (`>`, `tee`, `rm/mv/cp` đích, `sed -i`, `git -C <repo>` subcommand ghi). Lệnh đọc thuần cho qua ngay | không có STATE/manifest |
| `scripts/guard_frozen.py` | Write/Edit vào `TEST-STRATEGY.md` hoặc `context/releases/r*/TEST-PLAN.md` khi pha ≠ S — **và lệnh Bash mang token ghi vào hai file đó** (`sed -i`, `>>`, `tee`, `mv/cp` đích…) — hàng rào "ngưỡng ghi trước" phủ cả hai đường ghi. Phạm vi retest ghi vào RUNLOG, không sửa TEST-PLAN | TEST-PLAN chưa tồn tại (dự án mới) |
| `scripts/guard_verdict.py` | Write/Edit **và lệnh Bash ghi** vào `context/releases/r*/REPORT.md` khi gate E chưa xanh: còn TC chưa có kết quả · FAIL thiếu bug/severity · PASS thiếu bằng chứng tồn tại. Dùng **chung module đếm** với `gate.py` — hai bên không bao giờ lệch nhau | thiếu RUNLOG/TEST-PLAN (chưa tới pha E) |
| `scripts/guard_evidence.py` | Ảnh/video chụp được ghi ra **ngoài `evidence/`** — bắt thẳng ở tool MCP (`browser_take_screenshot` tham số `filename` · `mobile_save_screenshot` `saveTo` · `mobile_start_screen_recording` `output`, **thiếu `output` cũng chặn** vì mobile-mcp ghi vào thư mục tạm) + `browser_run_code_unsafe` (soi `path:` trong code) + lệnh Bash chép file ảnh/video ra ngoài. `--output-dir` chỉ là mặc định, không phải hàng rào | JSON hỏng / lời gọi không mang tham số đường dẫn |

**Vì sao bằng chứng phải nằm trong repo.** Ảnh rơi ra `/tmp` hay Desktop hỏng hai thứ cùng lúc: gate E kiểm đường dẫn dưới `evidence/` nên dòng `PASS` đó **không bao giờ chứng minh được** (phát hiện thì đã sang pha C), và ảnh chụp môi trường thật **mang dữ liệu thật** — để rải rác ngoài repo là rò rỉ thầm lặng, không ai dọn vì không ai biết nó ở đâu. SPEC chặn ngay lúc ghi, chỗ rẻ nhất để sửa.

Thêm `reanchor.py` (SessionStart matcher `compact`): nhồi lại 8 luật + STATE từ file sau khi context bị nén — compact giữ được *đang làm gì* nhưng làm phẳng *đang bị cấm gì*.

### d. Chỉ ba trường hợp được dừng

| Tình huống | Xử lý |
|---|---|
| Phát hiện **ngoài phạm vi test đã khoá** | **Không hỏi** — ghi `BUGS.md` trạng thái `deferred`, test tiếp phần còn lại |
| Hành động **không đảo ngược được hoặc hướng ra ngoài**: đụng dữ liệu **người dùng thật** (production — hoặc staging dùng chung dữ liệu thật), xoá thứ không thuộc tenant test, gửi thông báo tới người thật, tiêu tiền thật (thanh toán ngoài sandbox), lộ thông tin ra ngoài | **Đây là chỗ duy nhất được hỏi thật** — bằng lời trong chat |
| **Chặn cứng** sau khi đã tự thử hết cách (môi trường sập, tài khoản không cấp được…) | Ghi blocker vào `STATE.md`, TC liên quan đánh `BLOCKED`, chuyển việc khác, báo gộp cuối buổi |

Agent tester **không bao giờ** hỏi QC — trả phát hiện + bằng chứng, quyền quyết ở phiên chính.

### e. Chữ ký QC — máy không xác minh được, nên quy ước phải chặt

Ba vết `Chốt bởi QC:` · `Ký bởi QC:` · ô `Scope khoá` là văn bản mà **agent gõ được** — không hook nào phân biệt nổi ai là người điền. Đây là ranh giới tin-bằng-quy-ước lớn nhất còn lại của SPEC (mọi chỗ khác đều có máy chặn), nên quy ước tại đây là luật cứng:

1. Agent chỉ điền/tick **SAU khi QC nói đồng ý tường minh trong chat**, và dẫn **nguyên văn** lời đồng ý đó vào 1 dòng `DECISIONS.md` cùng ngày (cùng nghi thức với ghi hộ manifest, §1.3).
2. Không có lời QC trong phiên → **không điền** — kể cả khi mọi gate máy đã xanh. Một phiên tự chạy trọn S→C không ai duyệt mà sổ sách vẫn "đủ chữ ký" là vi phạm nặng nhất của quy trình, xử như test giả.
3. QC review DECISIONS cuối buổi thấy dòng dẫn lời mình không đúng → sự cố, dừng release cho tới khi làm rõ.
4. Dự án cần mức máy-kiểm-được: QC **tự commit** các dòng ký bằng tay (git author là chữ ký thật) — khai lựa chọn này ở `TEST-STRATEGY §8` khi lập chiến lược.

---

## 4. Makefile là hợp đồng lệnh môi trường test

SPEC không build sản phẩm — sáu lệnh của nó phục vụ **môi trường test**. Thân lệnh viết ở pha P vào `environment/`; quy trình và gate chỉ gọi sáu tên này:

```
make doctor     # kiểm môi trường: URL từng target 200, tài khoản test đăng nhập được,
                # cách ly đúng (API đọc chỉ thấy dữ liệu prefix), env đủ, thiết bị sẵn sàng
make seed       # bơm dữ liệu mẫu vào TENANT TEST về mốc B1 — qua API, không chạm DB
make reset      # dọn tenant test về mốc B0 (chỉ xoá bản ghi prefix SPEC-r<N>- của
                # release hiện tại — dữ liệu di sản release cũ GIỮ LẠI cho test tương thích)
make accounts   # tạo + thử đăng nhập tài khoản test cho từng vai trong ma trận
make devices    # boot đúng MỘT simulator/emulator + cài bản build từ manifest + kiểm checksum
make smoke      # đi nhanh một luồng lõi trên môi trường test bằng tài khoản test
```

(`make gate` = `python3 scripts/gate.py`.)

---

## 5. Khu vực context (nguồn sự thật)

| File | Vai trò |
|---|---|
| `context/TEST-STRATEGY.md` | Chiến lược test **cả sản phẩm**, lập một lần ở release 1, QC chốt (§1.4). Sống — chỉ sửa ở pha S kèm change log §11. Hook `guard_frozen` khoá ngoài pha S |
| `context/HANDOVER.md` | Sổ dịch bàn giao: marker `NGUỒN: <tên nguồn> — <path>` + bảng truy vết nguồn → context + lỗ hổng & cách xử (kèm đề xuất của meta, rủi ro nếu sai). Cập nhật delta mỗi release |
| `context/COVERAGE-MAP.md` | Capability (tính năng) × release giao × TI × trạng thái test — bản đồ phủ, nguồn truy vết của TI |
| `context/PERSONAS.md` | Dịch từ mirror: persona + **ma trận vai × hành động** (nguồn TC phân quyền) + cột tài khoản test tương ứng |
| `context/ARCHITECTURE.md` | Dịch từ mirror: boundary/experience + contract giữa target + URL môi trường test từng target + luồng lõi |
| `context/ENVIRONMENT.md` | Hồ sơ môi trường test: URL/health · tài khoản theo vai · tenant + prefix · seed/reset B0/B1 · thiết bị mobile · rác còn lại. Mục `(mỗi release)` được `release.py` bỏ tick khi mở release |
| `context/API-SURFACE.md` | Sổ surface API do **SPEC tự quan sát và ghi** mỗi release (endpoint · field · mã lỗi) — baseline độc lập cho test tương thích ngược — kể cả khi dev có giao API spec, SPEC vẫn ghi cái **quan sát được** |
| `context/BUGS.md` | Sổ bug **toàn dự án, append-only**: khối `BUG-r<N>-<số>`, severity S1–S4, bằng chứng, trạng thái. Kiêm backlog: `deferred` mang sang release sau |
| `context/DECISIONS.md` | Append-only, mốc `(release N)` và `(release N — bàn giao k)` — thứ THAY THẾ cho việc hỏi |
| `context/LESSONS.md` | Bài học sau mỗi release (append-only). Pha C rút 1–3 lesson; lesson QC duyệt mới được đưa vào skill `spec-knowledge` (checklist/bug-patterns) — kho kinh nghiệm dùng lại cho mọi dự án |
| `context/testcases/` | Test case **sống, tích luỹ qua release**: một file mỗi capability (`CAP-….md`), TC xuyên-capability ở `_CROSS-<loại>.md`; khuôn ở `_TC-TEMPLATE.md`. Regression = truy vấn tag `Regression: có` |
| `context/releases/r<N>/` | Sổ sách theo release — `TEST-PLAN.md` · `RUNLOG.md` · `REPORT.md`. Đánh số theo release nên tự nó là lưu trữ |
| `context/archive/release-N/` | Snapshot tài liệu sống khi đóng release (`release.py` tạo, chỉ copy) |
| `context/archive/ledger/` | Sổ đã gấp tay theo `/spec-compact` |
| `context/shared/CONVENTIONS.md` | Quy ước viết TC, đặt ID, khuôn bảng — QA đọc là viết được |
| `context/shared/SAFETY.md` | Luật an toàn test trên production/staging — bản thao tác của §7 |
| `intake/` | Cửa nhận bàn giao (§1.3): manifest + mirror theo release. Đầu vào đóng băng |
| `environment/` | Artifact CHẠY môi trường test: `.env.example` (chỉ TÊN biến) · `local/` (seed script, plan dữ liệu, `.env` không commit) |
| `evidence/` | Bằng chứng: `_inbox/<agent>/` (MCP đổ thô) · `r<N>/luot-<k>/<TC-ID>/` (đã phân loại — RUNLOG trỏ vào, gate E kiểm) |
| `STATE.md` | Trạng thái sống: pha, release, lần bàn giao, gate, challenge log, blocker |

---

## 6. Ma trận loại test — roster mở

Từ điển loại test mặc định gồm **14 góc nhìn**, khai ở `TEST-STRATEGY §3` (ma trận loại × target). **Mỗi loại một agent tester cùng tên** — thiếu góc nhìn nào thì thêm cột vào ma trận + tạo agent theo khuôn `agents/_TESTER-TEMPLATE.md`; gate P đối chiếu: loại tick trong ma trận × phạm vi release mà không có TC là đỏ, loại cố tình bỏ phải nằm ở out-of-scope.

| Loại test | Agent | Phủ gì |
|---|---|---|
| chức năng | `spec-tester-flow` | AC mới theo happy path |
| workflow | `spec-tester-workflow` | Kịch bản nghiệp vụ end-to-end: vòng đời bản ghi xuyên vai, xuyên trạng thái, nhiều phiên |
| biên | `spec-tester-edge` | Rỗng · lỗi · mạng chậm/mất · nhiều dữ liệu |
| phá-hoại-đầu-vào | `spec-tester-breaker` | Injection, chuỗi dài, ký tự lạ, số âm, double-submit, rate limit, upload bậy |
| phân quyền | `spec-tester-authz` | Từng ô ✗ của ma trận vai × hành động + cross-tenant isolation |
| tương-thích-ngược | `spec-tester-compat` | Đối chiếu `API-SURFACE.md` release trước + checklist tương thích ngược của dev (nếu có — VIPER: BC-checklist) + dữ liệu di sản còn dùng được |
| tích-hợp | `spec-tester-integration` | Dịch vụ ngoài (email/notification tới hộp test, payment sandbox, webhook) + phụ thuộc giữa boundary |
| api | `spec-tester-api` | Hành vi server qua API (gọi thẳng bỏ qua UI): validate, mã lỗi, phân trang, idempotency — và **ghi `API-SURFACE.md`** |
| cross-target | `spec-tester-cross` | Hành động ở experience A hiện đúng ở experience B — cặp bằng chứng hai phía |
| hình thức | `spec-tester-visual` | Computed style so lát token design system + a11y cơ bản (tương phản thật, vùng chạm, bàn phím, nhãn) |
| hiệu năng | `spec-tester-perf` | Thời gian phản hồi luồng lõi/endpoint (p95 gọi thưa), page-load, app start — so `TEST-STRATEGY §7`. **CẤM stress lên production** |
| mobile | `spec-tester-mobile` | Mọi góc nhìn trên app native: thiết bị nhỏ, xoay, bàn phím, gián đoạn, crash |
| bảo-mật | `spec-tester-security` | OWASP Top 10 **chứng minh bằng thao tác** (không chỉ scan): IDOR, injection, auth/JWT/session, misconfig header, SSRF, lộ dữ liệu trong response/log + secrets scan + SBOM/CVE trên repo nguồn. Chỉ đọc-thử/chứng minh, không phá. **Cần xác nhận quyền kiểm thử bảo mật ở pha S** (1 dòng DECISIONS dẫn nguyên văn QC) |
| regression | (mọi agent, theo TC được giao) | TC `Regression: có` của release trước — cái đã certify là hợp đồng |

Cộng `spec-evidence-auditor` — đối kháng nội bộ, soi bằng chứng trước khi QC ký (§3b).

---

## 7. An toàn trên môi trường test (production hoặc staging)

Manifest khai `Môi trường:`. **Production** là dao hai lưỡi; **staging** an toàn hơn nhưng thường dùng chung với dev/QA khác và hay nối dịch vụ thật (SMS, email, thanh toán). Phanh thật nằm ở **cách ly**, không phải ở permission rule — năm mục dưới áp cho CẢ HAI:

1. **Tenant test** — sản phẩm đa tenant: một tenant riêng cho SPEC, tạo qua luồng đăng ký công khai (hoặc QC cấp qua manifest). Sản phẩm không đa tenant: cách ly bằng tài khoản test riêng từng vai + prefix dữ liệu.
2. **Prefix `SPEC-r<N>-`** trên trường nhận diện của **mọi** bản ghi SPEC tạo ra. Không thao tác ghi/xoá lên bản ghi thiếu prefix — kể cả "để thử".
3. **Dữ liệu di sản**: `make reset` chỉ xoá prefix của release hiện tại; bản ghi release cũ giữ lại cho `spec-tester-compat`. Thứ không xoá được qua API → ghi `ENVIRONMENT.md §Rác còn lại` để đội dev biết.
4. **CẤM**: chạm thẳng DB production (seed/dọn đều qua API) · bắn notification/email/SMS tới người thật (TC nào bắn thì địa chỉ nhận thuộc SPEC) · thanh toán ngoài sandbox · stress/load nặng trên production (cần load test → TEST-STRATEGY khai môi trường riêng, QC quyết) · đụng tenant khác ngoài phép **đọc-thử** cross-tenant isolation · active scan bảo mật khi chưa có xác nhận quyền kiểm thử (§6 `bảo-mật`).
5. **Staging** — thêm: (a) `make doctor` cảnh báo nếu URL trông giống production (không có `staging`/`stg`/`dev`/`test`/`uat` trong host, hoặc trùng URL production khai ở `ARCHITECTURE`); (b) seed thẳng DB staging chỉ khi `TEST-STRATEGY §8` khai cho phép — mặc định vẫn qua API; (c) staging dùng chung với người khác → prefix vẫn bắt buộc, `make reset` vẫn chỉ xoá prefix của SPEC; (d) dịch vụ ngoài của staging (SMS/email/payment) phải xác nhận là sandbox trước khi TC chạm — chưa xác nhận → TC `BLOCKED`, không đoán.

Bản thao tác chi tiết: `context/shared/SAFETY.md`. Vi phạm mục 4 thuộc ngoại lệ "hỏi thật" của luật #2 — dừng và hỏi, không tự quyết.

---

## 8. Bản hiện tại — v1.1 ({{DATE}})

**Framework không giữ tham chiếu ngược.** Dự án đọc file này để biết luật **đang** ra sao. Nâng version thì viết lại mục này cho khớp bản mới.

Bản 1.1 đứng trên tám cơ chế (1.1 = 1.0 tổng quát hoá cho mọi quy trình dev + kho kinh nghiệm + bảo mật):

| Cơ chế | Ở đâu |
|---|---|
| **Release theo bản deploy bàn giao, lượt bàn giao trong release** — manifest từng lượt fail-closed, retest cùng release không đổi ngưỡng; hai chế độ đầu vào (khác / VIPER) | §0 · §1.2 · §1.3 |
| **TEST-STRATEGY một lần, release nào cũng aligned** — ba mối nối gate đối chiếu + nghi thức rà lại | §1.4 |
| **Ngưỡng trước — bằng chứng trước — verdict sau** — guard_frozen + guard_verdict + gate C so ngày, so verdict máy tính | §1.1 · luật #8 |
| **Độc lập bằng bằng chứng** — evidence bắt buộc theo loại TC, dấu hiệu test giả, evidence-auditor, `guard_evidence` giữ ảnh/video trong repo | §3b · §3c · luật #5 |
| **Roster mở theo ma trận loại test** — 14 góc nhìn mặc định (gồm `bảo-mật`), thêm góc nhìn = thêm cột + agent theo khuôn | §6 |
| **An toàn bằng cách ly** — production hay staging: tenant/prefix/di sản/danh mục cấm, hook + lớp ask chỉ là gờ giảm tốc | §7 |
| **Kho kinh nghiệm dùng lại** — skill `spec-knowledge` (checklist theo đối tượng + bug-patterns) đối chiếu khi viết TC; `LESSONS.md` sau mỗi release, QC duyệt mới đưa vào kho | §5 |
| **Kỹ thuật thiết kế TC có kỷ luật** — mức rủi ro R1–R3 quyết định kỹ thuật; mỗi AC ≥1 TC normal + ≥1 TC abnormal (`scripts/review_tc.py` đếm) | skill `spec-testcase-design` |
