---
description: Pha P — bootstrap môi trường test (URL, tenant, tài khoản theo vai, seed B0/B1, thiết bị mobile) + viết test case phủ đủ + chọn regression + dry-run luồng lõi
---

# /spec-prepare — Pha P

> **LUẬT #2 — KHÔNG HỎI QC.** Mơ hồ → tự quyết theo TEST-PLAN/TEST-STRATEGY/HANDOVER → 1 dòng `DECISIONS.md` → đi tiếp. Ngoại lệ "hỏi thật": đụng dữ liệu người thật / không đảo ngược được / hướng ra ngoài. Chặn cứng → `STATE.md §Blocker`.

Việc đầu tiên: sửa `STATE.md` → `Pha hiện tại : P`.

Đích: `ENVIRONMENT.md` đầy đủ và **sống thật** (`make doctor` xanh) · test case phủ đủ · regression đã chọn · dry-run xong.

## Bước 1 — Challenge (luật #8)

Trước khi dựng gì: một câu hỏi khó từ tài liệu — "TC nào sẽ phủ ca X của `ARCHITECTURE §6`? Seed nào dựng được trạng thái đó? Vai nào chạy?". FAIL → đọc lại TEST-PLAN/ARCHITECTURE, không được dựng. PASS → `STATE.md §Challenge log` pha `P`.

## Bước 2 — Bootstrap môi trường (meta lo trọn — QC không phải làm gì)

1. **URL từng target** — nguồn theo thứ tự: **bảng `## URL theo target` của manifest** (QC khai, chuẩn nhất) → mirror (VIPER: `shared/DEPLOY.md §1` + `.env.example`; tổng quát: ghi chú deploy / cấu hình dev bàn giao) → tự dò. Manifest khai `Môi trường: staging` mà URL trông như production (không có `staging`/`stg`/`dev`/`uat`/`test` trong host, hoặc trùng URL production đã biết) → **dừng, hỏi thật** — nhầm môi trường là hướng ra ngoài. Chép vào `ENVIRONMENT.md §1–§2` **một dòng mỗi target trong phạm vi** (gate P đối chiếu theo tên với `ARCHITECTURE §1–§3`), rồi curl health **thật** — 200 mới tick cột "Kiểm lần cuối". Ba trường hợp:
   - Service **chạm được từ ngoài** → URL + health, cột `Chạm từ ngoài? = có`.
   - Service **nội bộ** (worker, boundary sau gateway) → `—` + ghi rõ `không — qua <gateway>`; TC loại `api`/`tích-hợp` đi đường vòng đó, không được bỏ qua service.
   - URL chết hoặc không ai biết → `/spec-bug` (bug loại triển khai) hoặc lỗ hổng HANDOVER + tự quyết + DECISIONS; TC phụ thuộc nó đánh `BLOCKED` ở pha E.
2. **Tenant + cách ly** (`TEST-STRATEGY §8`): đa tenant → tạo tenant test qua luồng đăng ký công khai (lượt tạo này tự nó là một phép thử onboarding) hoặc nhận từ manifest. Không đa tenant → tài khoản riêng từng vai + prefix `SPEC-r<N>-` + luật dọn. Ghi `ENVIRONMENT.md §4`.
3. **Tài khoản theo vai**: viết script tạo (qua đăng ký/luồng mời của vai admin) cho **từng cột vai** của ma trận `PERSONAS.md §2` → điền thân `make accounts` → chạy, thử đăng nhập từng tài khoản. Mật khẩu sinh ngẫu nhiên vào `environment/local/.env` (không commit); `ENVIRONMENT.md §3` + `PERSONAS.md §3` chỉ ghi tên biến.
4. **Seed hai mốc**: viết `environment/local/seed.py` + `plan-B1.yaml` (dữ liệu theo persona, nguồn: mirror — VIPER `PRD §7`, tổng quát: dữ liệu mẫu/persona trong đặc tả) — **qua API**, idempotent, prefix bắt buộc (staging: seed thẳng DB chỉ khi `TEST-STRATEGY §8` khai cho phép, QC đã chốt); điền thân `make seed` / `make reset` (reset chỉ xoá prefix release hiện tại — dữ liệu di sản giữ lại). Chạy thử cả hai.
5. **Mobile** (nếu phạm vi có): lấy build từ manifest, kiểm checksum → điền thân `make devices` (boot đúng MỘT thiết bị theo `ENVIRONMENT.md §6` + `xcrun simctl install` / `adb install`) → `mobile_list_apps` thấy đúng bundle id. Build trỏ sai env (network log) → toàn bộ TC mobile `BLOCKED` + bug.
6. **`make doctor`**: viết thân kiểm trọn — manifest/mirror đủ · **health 200 cho TỪNG target chạm được từ ngoài** (in tên target, không phải một URL duy nhất; service nội bộ in `bỏ qua — nội bộ qua <gateway>`) · login từng tài khoản · cách ly đúng (API đọc bằng tài khoản test chỉ thấy dữ liệu prefix/tenant test) · seed dry-run · thiết bị/checksum · `.env` đủ biến (đối chiếu `.env.example`, mỗi service một biến `SPEC_URL_<TARGET>`) · đếm nhanh AC↔TC. Chạy tới khi xanh.
7. **`make smoke`**: thân đi nhanh một luồng lõi (`ARCHITECTURE §5`) bằng tài khoản test.

## Bước 3 — Viết test case (skill `spec-testcase-design` + `spec-knowledge`)

Vào `context/testcases/` — file theo capability, TC xuyên-capability vào `_CROSS-<loại>.md`, đúng khuôn `_TC-TEMPLATE.md` (dòng meta máy đọc!). Phủ đủ, theo mức R của `TEST-STRATEGY §4`:

- Mỗi **AC mới** ≥1 TC · mỗi **TI** ≥1 TC · mỗi **ô ✗** của ma trận một TC phân quyền (`Ô ma trận:`).
- Mỗi **loại test** tick trong ma trận §3 × phạm vi có ≥1 TC — loại cố tình bỏ phải nằm ở `TEST-PLAN §3` out-of-scope.
- TC hình thức: `DS:` + `Màn:` từ mirror DESIGN-SYSTEM/PROTOTYPE · TC hiệu năng: `Ngưỡng:` từ §7 chiến lược · TC tương thích: `Surface:` trỏ `API-SURFACE.md` release trước / BC-checklist mirror.
- Bug S1/S2 đã đóng ở release trước mà chưa có TC regression → viết bổ sung (luật kết nạp §6).
- **Đối chiếu kinh nghiệm tích luỹ** (skill `spec-knowledge`): với mỗi đối tượng trong phạm vi (form, đăng nhập/phân quyền, upload, API, luồng nhiều màn) mở checklist tương ứng + `bug-patterns.md` → case nào áp dụng được mà chưa có TC thì viết thêm. Case không áp dụng được thì bỏ **chủ động** (không phải vì quên). Đọc cả `context/LESSONS.md` của các release trước.
- Viết xong → `python3 scripts/review_tc.py` (máy kiểm vòng 1: mỗi AC ≥1 TC normal + ≥1 abnormal, `Loại:` thuộc ma trận, TC mồ côi, thiếu `Bằng chứng cần`, kỳ vọng rỗng nghĩa) → vá tới khi sạch; rồi tự rà vòng 2 bằng mắt, đối chiếu mirror. Ghi kết quả hai vòng vào `STATE.md §Challenge log` pha `P`.

## Bước 4 — Rà lại regression (release ≥2)

Danh sách regression đã **CHỐT ở pha S** (`TEST-PLAN §5`, chọn theo `TEST-STRATEGY §6` — Bước 5 của `/spec-scope`); plan đã khoá, pha P không chọn thêm bớt gì. Việc của pha P chỉ là **rà lại trước thực tế môi trường**: TC nào môi trường mới làm vô nghĩa (URL đổi, vai bị bỏ, dữ liệu di sản mất…) → **không sửa plan** — ghi 1 dòng DECISIONS, sang pha E đánh `SKIP` có vết trong RUNLOG.

## Bước 5 — Dry-run rồi chốt

Meta **tự tay** đi MỘT luồng lõi trên môi trường test (`Môi trường:` của manifest) bằng tài khoản test (skill `spec-browse`/`spec-mobile`) — môi trường phải chứng minh sống bằng thao tác thật, không phải bằng bảng đã điền. Đi không nổi → sửa môi trường trước, chưa sang E.

**Lần đầu tiên của dự án**: smoke cả roster — spawn MỘT agent tester (vd `spec-tester-flow`) với prompt chỉ yêu cầu liệt kê tool `browser_*`/`mobile_*` nó gọi được, không test gì. MCP server khai inline trong frontmatter không lên được là tester "test chay" đúng kiểu test giả mà quy trình sợ nhất — phải phát hiện ở đây, không phải giữa pha E.

```bash
make doctor && python3 scripts/gate.py P
```

Xanh → tick gate P trong STATE, sửa `Pha hiện tại : E`.

## Ranh giới

- Không chạy test thật ở pha này (trừ dry-run một luồng) — chạy là việc của E, và kết quả pha P không được ghi vào RUNLOG.
- Không sửa `TEST-PLAN.md`/`TEST-STRATEGY.md` — hook `guard_frozen` chặn; thấy plan sai → DECISIONS + Blocker, xử ở pha S release sau.
- Không chạm DB production để seed — API only (`SAFETY.md`). Staging: như trên, trừ khi `TEST-STRATEGY §8` khai khác.
- Không scaffold môi trường cho target ngoài phạm vi release.
