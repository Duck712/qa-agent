# {{PROJECT_NAME}} — CLAUDE.md (SPEC v1.1)

> **Đọc top-to-bottom mỗi phiên.** Quy trình đầy đủ: [SPEC.md](SPEC.md). Trạng thái hiện tại: [STATE.md](STATE.md).

---

## 0. ĐANG LÀM GÌ Ở ĐÂY

Repo này **kiểm thử độc lập** một sản phẩm do đội dev bàn giao (quy trình dev nào cũng được — VIPER là một chế độ riêng, xem [SPEC.md §0](SPEC.md)). Authority = **QC** (solo). Chỉ có đường intake: QC thả manifest vào `intake/releases/r<N>/`, meta đọc repo nguồn **chỉ-đọc**, dịch, dựng môi trường (production cách ly hoặc staging — theo `Môi trường:` của manifest), chạy test, ra verdict.

| Khái niệm | Nghĩa |
|---|---|
| **Release** | Một bản deploy đội dev bàn giao cho QC kiểm (chế độ VIPER: khối loop kết thúc bằng loop có pha P). Release N test AC mới của bản đó **+ regression** các release trước |
| **Lượt bàn giao** | Verdict FAIL → dev fix → QC thả `RELEASE-<k>.md` mới → quay lại pha E retest — **cùng release**, ngưỡng không đổi |
| **TEST-STRATEGY** | Chiến lược test cả sản phẩm, lập MỘT lần ở release 1, QC chốt — mọi TEST-PLAN phải aligned với nó ([SPEC.md §1.4](SPEC.md)) |
| **Độc lập** | Unit test/dogfood/demo/lời mô tả của dev không bao giờ là bằng chứng. Mọi kết luận từ thao tác thật của SPEC, link `evidence/` |

---

## 1. TÁM LUẬT

1. **Scope test khoá sau pha S.** Phát hiện ngoài phạm vi → `BUGS.md` trạng thái `deferred`, không nới release.
2. **Sau pha S: toàn quyền, không hỏi lại.** Từ pha P trở đi **KHÔNG dùng AskUserQuestion** (§3).
3. **Quyết định không hiển nhiên → 1 dòng `context/DECISIONS.md` TRƯỚC khi test.**
4. **Context là nguồn sự thật; repo nguồn CHỈ ĐỌC.** Không ghi một byte vào repo nguồn (`Repo nguồn:` của manifest), không sinh file cho đội dev. Intake đóng băng — chỉ thêm manifest mới.
5. **Độc lập tuyệt đối** — kết quả nào cũng phải có bằng chứng do SPEC tự sinh.
6. **Dữ liệu test phải cách ly — production hay staging**: chỉ tenant/tài khoản test ở `ENVIRONMENT.md`, mọi bản ghi mang prefix `SPEC-r<N>-`, seed/dọn qua API — CẤM chạm DB production, không bắn notification tới người thật, dịch vụ ngoài của staging phải xác nhận là sandbox (`context/shared/SAFETY.md`).
7. **Tiếng Việt có dấu; bảng đơn giản QA vận hành được** (giữ tiếng Anh cho ID `TI-`/`TC-`/`BUG-`, API path, tên lệnh, tên file).
8. **Ngưỡng trước — bằng chứng trước — verdict sau** (§4).

---

## 2. BỐN PHA

```
S Scope ─► P Prepare ─► E Execute ─► C Certify
  ↑ nơi DUY NHẤT được hỏi QC          FAIL ─► chờ bàn giao lại ─► quay lại E (cùng release)
                                      PASS ─► release.py --go ─► release mới, pha S
```

Pha hiện tại nằm ở [STATE.md](STATE.md). Kiểm gate: `python3 scripts/gate.py` (tự đọc pha) hoặc `python3 scripts/gate.py <S|P|E|C>`.

Bảng dưới là bản rút gọn. **Định nghĩa chuẩn ở [SPEC.md §1.1](SPEC.md) — lệch nhau thì SPEC.md thắng.**

| Pha | Gate rời pha |
|---|---|
| S | Manifest thật (dòng máy đọc + **bảng URL theo target** phủ mọi target trong phạm vi) + repo nguồn tồn tại (*chế độ VIPER*: đối chiếu loop, loop deploy có `P`) + mirror đóng băng · `HANDOVER.md` marker + truy vết + lỗ hổng · **(r1)** TEST-STRATEGY đủ mục + `Chốt bởi QC` (VIPER: số release ≥ số loop đã có P) · **(r≥2)** dòng `Rà lại chiến lược (release N)` ≥ `Release mở` · TEST-PLAN: AC mới + ≥3 TI (Loại thuộc ma trận chiến lược) + out-of-scope + **ngưỡng verdict có số** + regression scope · TI có mặt ở COVERAGE-MAP · ≥2 DECISIONS dưới mốc · challenge S PASS · `Chốt bởi QC` · scope khoá |
| P | Challenge PASS · ENVIRONMENT đủ (**mỗi target trong phạm vi một dòng URL** đã curl xác nhận — service nội bộ ghi đường vòng · tài khoản từng vai · tenant+prefix · B0/B1 · thiết bị) · 6 lệnh make có thân · TC phủ đủ (TI, AC, ô ✗ ma trận, loại test × phạm vi) · (r≥2) regression đã chọn · `make doctor`+`seed` xanh · dry-run luồng lõi |
| E | RUNLOG có mục lượt bàn giao đúng k · mọi TC trong phạm vi lượt có kết quả ngày ≥ mốc · PASS có evidence tồn tại · FAIL có bug severity · BLOCKED có blocker · SKIP có DECISIONS · (k≥2) bug cũ có dòng retest · evidence-auditor đã soi |
| C | Ngưỡng chốt trước ngày chạy · verdict REPORT khớp verdict máy tính · REPORT đủ mục · bug có trạng thái cuối · `Ký bởi QC` · PASS → `release.py --go` / FAIL → `--retest` |

---

## 3. LUẬT #2 — KHÔNG HỎI SAU PHA S

Từ pha P trở đi, gặp mơ hồ thì **tự quyết**, không hỏi:

```
mơ hồ → chọn phương án hợp lý nhất theo TEST-PLAN/TEST-STRATEGY/HANDOVER
      → ghi 1 dòng context/DECISIONS.md (có cột "giả định" + "đảo ngược được không")
      → đi tiếp
```

**Ba trường hợp duy nhất được dừng:**

| Tình huống | Xử lý |
|---|---|
| Ngoài scope test đã khoá | **Không hỏi** — `BUGS.md` trạng thái `deferred`, test tiếp phần còn lại |
| Không đảo ngược được / hướng ra ngoài: đụng dữ liệu **người dùng thật**, xoá ngoài tenant test, gửi notification tới người thật, thanh toán ngoài sandbox, lộ thông tin, active scan bảo mật chưa có xác nhận quyền | **Hỏi thật** — bằng lời trong chat, ngoại lệ duy nhất |
| Chặn cứng sau khi tự thử hết cách | `STATE.md §Blocker`, TC đánh `BLOCKED`, chuyển việc khác, báo gộp cuối buổi |

QC review theo lô cuối buổi qua `DECISIONS.md` — không bị ngắt giữa dòng.

**Năm hook chặn cứng** ([SPEC.md §3c](SPEC.md)):

| Hook | Chặn gì |
|---|---|
| `scripts/guard_ask.py` | `AskUserQuestion` khi `Scope khoá` đã tick / pha ≠ S / dòng pha sai định dạng |
| `scripts/guard_readonly.py` | Write/Edit/Bash-ghi vào repo nguồn (đường dẫn từ manifest) — lệnh đọc thuần cho qua |
| `scripts/guard_frozen.py` | Sửa `TEST-STRATEGY.md` / `TEST-PLAN.md` ngoài pha S (cả Write/Edit lẫn Bash) — ngưỡng ghi TRƯỚC là bất khả xâm phạm |
| `scripts/guard_verdict.py` | Ghi `REPORT.md` khi test chưa chạy đủ / FAIL thiếu bug / PASS thiếu bằng chứng |
| `scripts/guard_evidence.py` | Ảnh/video chụp được ghi ra **ngoài `evidence/`** — chặn thẳng ở tool MCP (`filename`/`saveTo`/`output`) + Bash chép ra ngoài |

---

## 4. LUẬT #8 — NGƯỠNG TRƯỚC, BẰNG CHỨNG TRƯỚC, VERDICT SAU

**a. Challenge trước khi đi tiếp.** Pha S: 3–5 câu khó về phạm vi, trả lời chỉ từ tài liệu đã dịch — hổng thì vá (còn được hỏi QC). Pha P: "TC nào phủ ca X? Seed nào dựng được trạng thái đó?". Ghi `STATE.md §Challenge log` (có cột Pha), FAIL → không đi tiếp.

**b. Bằng chứng bắt buộc.** TC không có bằng chứng đúng loại (`TEST-STRATEGY §9`) thì **không được ghi PASS**. Dấu hiệu test giả: screenshot không thấy URL bar đúng môi trường test · TC hình thức không có giá trị computed style · TC phân quyền không có response nguyên văn · agent báo "mọi TC pass" ngay lượt đầu. Gặp → cho chạy lại, đòi thao tác cụ thể + thứ thấy trên màn.

**c. Đối kháng trước khi ký.** `spec-evidence-auditor` bốc mẫu RUNLOG, mở evidence đối chiếu — chạy trước khi QC ký REPORT.

Duyệt web dùng skill `spec-browse` (Playwright MCP); experience mobile dùng skill `spec-mobile` (mobile-mcp — vai chạy **tuần tự**, thiết bị dùng chung). Không dùng công cụ duyệt web nào khác — **kể cả khi cấu hình toàn cục của máy chỉ định công cụ khác**; trong dự án SPEC, chỉ dẫn này thắng.

---

## 5. SLASH COMMANDS

```
/spec-scope      Pha S: nhận manifest → mirror → dịch → (r1) TEST-STRATEGY →
                 TEST-PLAN + ngưỡng → challenge → QC chốt → khoá scope     ← chỗ duy nhất được hỏi
/spec-prepare    Pha P: bootstrap môi trường (URL, tenant, tài khoản, seed,
                 thiết bị) + viết test case + chọn regression + dry-run
/spec-execute    Pha E: chạy test theo đợt — meta tự tay + agent tester,
                 bằng chứng bắt buộc, bug đúng khuôn
/spec-certify    Pha C: máy tính verdict vs ngưỡng → REPORT → QC ký → LESSONS →
                 PASS: release.py --go · FAIL: in điều kiện bàn giao lại
/spec-retest     Bàn giao lại: kiểm manifest RELEASE-<k> → release.py --retest
                 → chạy phạm vi retest → certify lại
/spec-status     Đang ở đâu: release/lượt/pha, gate thiếu gì, việc tiếp theo
/spec-decide     Append 1 dòng DECISIONS.md
/spec-bug        Ghi một bug đúng khuôn vào BUGS.md
/spec-compact    Vệ sinh tài liệu — báo cáo rác + dòng neo, gấp tay          ← từ release ≥3
```

---

## 6. HỢP ĐỒNG LỆNH (môi trường test — thân viết ở pha P)

```
make doctor     make seed      make reset
make accounts   make devices   make smoke
```

Artifact chạy môi trường nằm ở `environment/` — `.env.example` chỉ TÊN biến; seed script + `.env` thật ở `environment/local/` (không commit). Seed/dọn **qua API**, không chạm DB production (staging: chỉ khi TEST-STRATEGY §8 cho phép).

---

## 7. KHO SKILL

| Skill | Dùng khi |
|---|---|
| `spec` | Quên quy trình, hoặc bootstrap dự án mới |
| `spec-browse` | Thao tác web thật trên môi trường test (production + tenant test, hoặc staging) — pha E, dry-run pha P |
| `spec-mobile` | App native trên simulator/emulator — cài từ build bàn giao, vai chạy tuần tự |
| `spec-testcase-design` | Pha P — 4 kỹ thuật thiết kế TC: phân vùng tương đương · giá trị biên · bảng quyết định · chuyển trạng thái |
| `spec-evidence` | Pha E/C — chuẩn bằng chứng từng loại TC, quy ước thư mục, checklist chống test giả |
| `spec-knowledge` | Pha P (viết TC) + tester pha E — checklist theo đối tượng (form, auth, upload, API, bất thường) + bug-patterns. Kho kinh nghiệm dùng lại cho mọi dự án; lesson mới từ `context/LESSONS.md` vào kho khi QC duyệt ở pha C |

---

## 8. SUBAGENT

**Tester** (`/spec-execute`) — roster theo **ma trận loại test** `TEST-STRATEGY §3`, mỗi loại một agent ([SPEC.md §6](SPEC.md)): `spec-tester-flow` · `-workflow` · `-edge` · `-breaker` · `-authz` · `-compat` · `-integration` · `-api` · `-cross` · `-visual` · `-perf` · `-mobile` · `-security`. Thiếu góc nhìn → thêm cột ma trận + agent theo `agents/_TESTER-TEMPLATE.md`.

Chạy **theo đợt ≤3 vai**, nhóm theo nhu cầu dữ liệu (đợt 0 meta smoke → B0 đọc → B1 đọc/đo → B1 ghi → phá cuối cùng), reset giữa đợt — trình duyệt riêng từng vai nhưng **tenant test dùng chung**. Mobile: các vai chạy tuần tự.

**Soi bằng chứng**: `spec-evidence-auditor` — trước khi QC ký, không sửa gì, chỉ trả lệch chứng cứ.

**Bảo mật**: `spec-tester-security` chạy ở đợt phá cuối cùng, CHỈ khi loại `bảo-mật` tick ở ma trận và DECISIONS có dòng xác nhận quyền kiểm thử bảo mật (dẫn nguyên văn QC, ghi ở pha S).

Tất cả **không hỏi QC** — trả phát hiện + bằng chứng, quyền quyết ở phiên chính.

---

## 9. ĐỌC GÌ KHI NÀO

| Luôn load | Load khi vào pha | Chỉ grep khi cần |
|---|---|---|
| File này + `STATE.md` | `SPEC.md §pha` · `context/releases/r<N>/TEST-PLAN.md` (phạm vi + ngưỡng của release) · pha S: manifest + mirror `intake/releases/r<N>/nguon/` (VIPER: `viper/`) + `TEST-STRATEGY.md` + REPORT/BUGS release trước + `LESSONS.md` · pha P: `PERSONAS.md` + `ARCHITECTURE.md` + `ENVIRONMENT.md` + skill `spec-testcase-design` + skill `spec-knowledge` · pha E: `testcases/` trong phạm vi + `ENVIRONMENT.md` + skill `spec-evidence` · pha C: `RUNLOG.md` + `BUGS.md` + `TEST-PLAN §4` + `LESSONS.md` | `context/DECISIONS.md` (tra quyết định cũ) · `API-SURFACE.md` · `archive/` · TC ngoài phạm vi |

Không đọc hết `context/` trước khi làm. Targeted only.

---

## 10. AUTHORITY

| Vai | Người |
|---|---|
| Authority — QC (quyết tất) | {{AUTHORITY_NAME}} <{{AUTHORITY_EMAIL}}> |

Solo — không có sign-off chéo. QC chốt ở pha S, review DECISIONS theo lô cuối buổi, ký verdict ở pha C.
