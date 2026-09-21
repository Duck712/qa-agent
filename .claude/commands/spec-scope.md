---
description: Pha S — nhận manifest bàn giao, mirror + dịch tài liệu của dev (repo nguồn chỉ đọc), (release 1) lập TEST-STRATEGY, viết TEST-PLAN + ngưỡng, challenge, QC chốt, khoá scope. Nơi DUY NHẤT được hỏi QC.
---

# /spec-scope — Pha S

**Đây là nơi DUY NHẤT được hỏi QC.** Sau khoá scope, mọi câu hỏi là ma sát — hiểu bàn giao ở đây cho đủ và cho sâu. Việc đầu tiên: sửa `STATE.md` → `Pha hiện tại : S` (nếu chưa đúng) — hook và gate đọc dòng này.

Mục tiêu: manifest hợp lệ + mirror đóng băng + `HANDOVER.md` + *(r1)* `TEST-STRATEGY.md` + `TEST-PLAN.md` (kèm **ngưỡng verdict**) + `COVERAGE-MAP.md`, qua challenge, QC chốt, khoá scope.

## Bước 1 — Nhận manifest

Đọc `intake/releases/r<N>/RELEASE.md` (lượt k ≥2: `RELEASE-<k>.md` — nhưng lượt retest đi `/spec-retest`, không quay lại đây).

- Chưa có → báo QC thả theo `intake/_RELEASE-TEMPLATE.md`. QC nói qua chat → **ghi hộ**: trích nguyên văn, ghi `Nguồn: chat với QC, <ISO>`, các dòng máy đọc + bảng URL điền từ thông tin thật (thiếu thì hỏi — đang pha S).
- Đọc `Quy trình dev:` để biết chế độ, `Môi trường:` để biết luật cách ly (`production` → cách ly đầy đủ; `staging` → xem `context/shared/SAFETY.md`):
  - **Chế độ VIPER** (`Quy trình dev: VIPER` hoặc manifest cũ có dòng `Repo VIPER:`): đối chiếu chéo repo nguồn (chỉ đọc) — mỗi loop trong `Phạm vi` (`l<a>–l<b>`) có `intake/loops/l<i>/_PROPOSAL.md`; `Bản deploy` (loop deploy) khai `P` trong `Pha vòng này`. Lệch → báo QC sửa manifest, **không tự suy**.
  - **Chế độ tổng quát** (`Quy trình dev: khác`): `Repo nguồn:` là thư mục tồn tại (repo code hoặc thư mục tài liệu bàn giao); `Phạm vi:` + `Bản deploy:` (version/tag/commit/ngày deploy) mô tả được bằng lời của dev. Mơ hồ → **hỏi QC** (đang pha S), không tự suy.
- **Bảng `## URL theo target`**: hệ nhiều microservice thì mỗi boundary/experience một dòng, tên khớp `ARCHITECTURE §1–§3` (bản dịch ở `context/`). Sau khi dịch ARCHITECTURE (Bước 3), quay lại đối chiếu: target nào trong phạm vi mà bảng chưa có → **hỏi QC** (đang pha S, được hỏi); QC cũng chưa biết → ghi vào `HANDOVER §Lỗ hổng` và tự dò ở pha P. Service nội bộ không expose: ghi `—` + gateway chạm vào, **không bỏ trống dòng** — bỏ trống là mất luôn dấu vết rằng nó tồn tại.

## Bước 2 — Mirror (đóng băng đầu vào)

Copy tài liệu then chốt của dev vào mirror — danh sách tối thiểu ở `intake/README.md §Mirror`. Copy bằng `cp` (đọc từ repo nguồn, ghi vào SPEC — hợp lệ):

- **VIPER** → `intake/releases/r<N>/viper/` (≥5 file .md), archive theo loop vào `viper/vong-<i>/`.
- **Tổng quát** → `intake/releases/r<N>/nguon/` (≥1 file — .md/.pdf/.docx/ảnh thiết kế/Postman/OpenAPI… đều tính): PRD/đặc tả, user story + AC, tài liệu API, thiết kế, danh sách vai/quyền, ghi chú deploy — cái gì dev có.

File nguồn không có → một dòng `HANDOVER.md §Lỗ hổng`.

**Từ đây mọi phép dịch đi từ mirror, không từ repo sống** — repo nguồn có thể đã đổi sau bàn giao.

## Bước 3 — Dịch sang context/

**Dịch trung thành, không "cải tiến"** — tài liệu bàn giao là lời hứa của dev, SPEC kiểm lời hứa đó. Bảng dưới là tên file của chế độ VIPER; chế độ tổng quát dịch **theo nội dung tương đương** (đặc tả/user story → AC, danh sách vai/quyền → PERSONAS, sơ đồ hệ thống/tài liệu API → ARCHITECTURE…). Tài liệu dev không có mã AC → SPEC tự đánh `AC-1…AC-n` theo thứ tự trong tài liệu, cột Nguồn trỏ file + mục (ghi 1 dòng DECISIONS về cách đánh mã).

| Nguồn (mirror) | Đích | Cách dịch |
|---|---|---|
| `PRD.md` + `vong-<i>/PRD.md` (tổng quát: đặc tả / user story) | `TEST-PLAN §1` | VIPER: hợp AC các loop, GIỮ mã `AC-n (l<i>)` + capability. Tổng quát: giữ mã AC của dev nếu có, không có thì `AC-n` + cột Nguồn |
| `CAPABILITIES-MAP.md` | `COVERAGE-MAP.md` | Giữ mã `CAP-…`; cột Release test theo `TEST-STRATEGY §2` |
| `PERSONAS.md` | `PERSONAS.md` | Giữ persona + ma trận vai × hành động nguyên vẹn; thêm §3 tài khoản test (pha P điền) |
| `ARCHITECTURE.md` | `ARCHITECTURE.md` | Target (§1–§3, đánh dấu trong/ngoài phạm vi) · contract §4 · luồng lõi §5 · ca biên §6 · dịch vụ ngoài §7 |
| `DESIGN-SYSTEM.md` | (không dịch riêng) | Lát token là đầu vào cho `spec-tester-visual` — trỏ thẳng mirror |
| `shared/DEPLOY.md` + `.env.example` | `ENVIRONMENT.md` (pha P) | Ghi chú URL/biến vào HANDOVER trước |

Cập nhật `HANDOVER.md`: marker `NGUỒN: <tên nguồn> — <path>` (VIPER: `NGUỒN: VIPER — <path>`) + bảng `## Truy vết` (VIPER ≥5 dòng, tổng quát ≥3 dòng, trỏ đúng file + mục) + **Lỗ hổng & cách xử** — thứ tài liệu dev không nói đủ cho việc test (tài khoản admin, tenant, hộp thư test, sandbox, rate limit, build mobile, AC mơ hồ, mâu thuẫn giữa hai tài liệu…). Mỗi lỗ ghi kèm **đề xuất của meta + rủi ro nếu đề xuất sai**, rồi: tìm trong mirror → **hỏi QC** (gom thành một lượt hỏi, mỗi câu kèm đề xuất) → QC trả lời thì ghi nguyên văn vào cột xử lý; QC không biết → tự quyết + 1 dòng `DECISIONS.md` mỗi lỗ.

## Bước 4 — (Release 1) Lập TEST-STRATEGY · (Release ≥2) Rà lại chiến lược

**Release 1**: điền `TEST-STRATEGY.md` §1–§11 từ mirror — chuỗi release (VIPER: mỗi loop có P = một release, đối chiếu ROADMAP §1; tổng quát: theo lộ trình/đợt deploy dev khai, không có thì mỗi bàn giao là một release) · ma trận loại test × target · risk R1/R2/R3 · severity · chính sách regression · ngưỡng hiệu năng · cách ly · chuẩn bằng chứng · khuôn ngưỡng verdict. Nếu tick loại `bảo-mật` → hỏi QC **xác nhận quyền kiểm thử bảo mật** (ai cho phép, trên target nào, môi trường nào, khung thời gian) và trích nguyên văn vào 1 dòng DECISIONS — thiếu dòng này thì `spec-tester-security` tự trả BLOCKED ở pha E. **Trình QC duyệt từng mục lớn** (đây là chữ ký một lần cho cả sản phẩm) → ghi `Chốt bởi QC: <ISO>`.

**Release ≥2**: đọc lại `TEST-STRATEGY §2/§3/§6` đối chiếu kết quả release trước (REPORT, BUGS `deferred`, phát hiện treo) → chỉnh nếu lệch (sửa STRATEGY + change log §11 + DECISIONS; đổi lớn thì hỏi QC) → ghi `Rà lại chiến lược (release N): <hôm nay>` vào TEST-PLAN. Rà mà không đổi gì cũng phải nói được vì sao vẫn đúng.

## Bước 5 — Viết TEST-PLAN

`context/releases/r<N>/TEST-PLAN.md`: 4 dòng đầu máy đọc · §1 AC mới · §2 ≥3 TI (Loại thuộc ma trận §3 chiến lược, Nguồn trỏ CAP/AC) · §3 out-of-scope **kể cả loại test cố tình bỏ** · §4 **ngưỡng verdict có số** (instantiate khuôn §10; ghi đè → DECISIONS) · §5 regression scope (r≥2: chọn từ TC sống tag `Regression: có`, ≥ tối thiểu §6; TC bị gỡ vì dev phá legacy có phép (tài liệu bàn giao ghi rõ) → DECISIONS) · §6 phân công đợt · §7 rủi ro · §8 truy vết chiến lược.

Bug release trước chưa xong: `deferred` → nhặt vào phạm vi (thành TI/TC) hoặc ghi tiếp lý do hoãn; **bug còn `mở`** (cam kết của PASS-có-điều-kiện) → đưa TC dính nó vào phạm vi retest của release này — chúng **vẫn được verdict release mới đếm** (`gate.py C` đếm bug mở mọi release), không tự biến mất.

## Bước 6 — Challenge pha S (luật #8)

3–5 câu khó nhất về phạm vi test, trả lời **chỉ từ tài liệu đã dịch**:

- "AC-3 có ca 'gửi hai lần' — TI nào phủ, dữ liệu nào dựng được trạng thái đó?"
- "Vai X bị cấm hành động Y — gọi endpoint nào để thử, bằng tài khoản nào?"
- "Release này loại test nào bỏ, và out-of-scope đã ghi lý do chưa?"

Không trả lời được = lỗ dịch → quay lại Bước 3/5 (còn được hỏi QC). PASS → ghi `STATE.md §Challenge log` pha `S`, ngày hôm nay.

## Bước 7 — QC chốt, khoá scope

```bash
python3 scripts/gate.py S
```

Trình QC: phạm vi + TI + **ngưỡng** + out-of-scope. QC đồng ý → ghi `Chốt bởi QC: <ISO>` vào TEST-PLAN → tick `Scope khoá` trong STATE → sửa `Pha hiện tại : P`.

> **Chữ ký là của QC, không phải của agent** (`SPEC.md §3e`): chỉ điền `Chốt bởi QC`/tick `Scope khoá` SAU khi QC nói đồng ý tường minh trong chat, và dẫn **nguyên văn** lời đồng ý vào 1 dòng DECISIONS cùng ngày. Không có lời QC trong phiên → không điền, kể cả khi gate máy đã xanh.

Rồi nói với QC, nguyên văn ý này:

> Scope test đã khoá, ngưỡng đã ghi. Từ đây tôi không hỏi nữa — mơ hồ sẽ tự quyết theo TEST-PLAN/TEST-STRATEGY và ghi `DECISIONS.md` để anh xem cuối buổi. Chỉ dừng nếu chạm dữ liệu người dùng thật hoặc việc không đảo ngược được.

## Dấu hiệu dịch hời hợt (≥2 cái → quay lại vá)

- Chỉ đọc tài liệu tổng (PRD), không mở tài liệu chi tiết từng phần trong phạm vi (VIPER: archive từng loop)
- Bảng truy vết ghi "từ dev" chung chung thay vì trỏ file + mục
- Không lỗ hổng nào được ghi — tài liệu dev gần như không bao giờ nói đủ cho việc test
- TI không truy được về capability/AC nào, hoặc loại test không có trong ma trận chiến lược
- *(r≥2)* Không dẫn được kết quả nào của release trước; `Rà lại chiến lược` ghi mà không nói được vì sao kế hoạch vẫn đúng

## Ranh giới

- Không viết test case ở pha này (việc của P), không chạy test (việc của E).
- Không ghi gì vào repo nguồn — hook `guard_readonly` chặn, và mirror là chỗ thay thế.
- Ngưỡng chưa có số → chưa được trình QC chốt. QC chưa chốt / challenge chưa PASS → chưa khoá scope — `gate.py S` chặn đúng chỗ.
