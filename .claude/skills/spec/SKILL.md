---
name: spec
description: >
  Quy trình SPEC — kiểm thử độc lập sản phẩm do một đội dev bàn giao (bất kỳ quy trình dev nào; VIPER có
  chế độ riêng). Solo Authority = QC, chỉ đường intake, đơn vị lặp là RELEASE (một đợt bàn giao có deploy). Nạp skill này khi: bắt đầu một dự án
  SPEC mới, quên đang ở pha/release/lượt bàn giao nào, không nhớ luật nào áp dụng, hoặc cần biết pha hiện tại
  phải làm gì và gate ra sao. Bao gồm: 4 pha S-P-E-C, 8 luật, cơ chế "không hỏi QC sau pha S", ngưỡng ghi
  trước, bằng chứng bắt buộc, roster agent theo ma trận loại test.
---

# SPEC — vận hành quy trình

> Policy đầy đủ ở `SPEC.md` (T0). Skill này là bản thao tác: đang ở đâu, làm gì tiếp, gate ra sao.

## Định vị nhanh

```bash
head -15 STATE.md                    # pha · release · lượt bàn giao · URL
python3 scripts/gate.py              # gate của pha hiện tại (hoặc truyền S|P|E|C)
cat intake/releases/r*/RELEASE*.md   # manifest bàn giao — quy trình dev, phạm vi, bản deploy, môi trường
```

## SPEC là gì trong một bảng

| | SPEC |
|---|---|
| Authority | **QC** — solo, chốt scope ở pha S, ký verdict ở pha C |
| Đầu vào | Manifest QC thả + **repo nguồn chỉ đọc** (repo code hoặc thư mục tài liệu bàn giao) — mirror vào `intake/releases/r<N>/nguon/` (VIPER: `viper/`) |
| Chế độ | `Quy trình dev: VIPER` → đối chiếu loop/_PROPOSAL như cũ · `khác` → tổng quát: phạm vi + bản deploy do dev mô tả |
| Đơn vị lặp | **Release** = một đợt bàn giao có deploy (VIPER: khối loop kết thúc bằng loop có pha P). Release N test AC mới + **regression** các release trước |
| Lượt bàn giao | FAIL → dev fix → QC thả `RELEASE-<k>.md` → mở lại pha E **cùng release**, ngưỡng không đổi |
| Môi trường | Khai trong manifest: **production** + tenant/tài khoản test cách ly, hoặc **staging** — prefix `SPEC-r<N>-` ở cả hai (`context/shared/SAFETY.md`) |
| Độc lập | Dogfood/mô tả/kết quả tự test của dev **không bao giờ là bằng chứng** — mọi kết quả từ thao tác thật của SPEC |

## Bốn pha

| Pha | Lệnh | Xong khi |
|---|---|---|
| **S** Scope | `/spec-scope` | Manifest hợp lệ + mirror đóng băng + HANDOVER (marker/truy vết/lỗ hổng) · *(r1)* TEST-STRATEGY QC chốt · *(r≥2)* rà lại chiến lược · TEST-PLAN (AC · ≥3 TI · out-of-scope · **ngưỡng có số** · regression) · challenge S PASS · QC chốt · scope khoá |
| **P** Prepare | `/spec-prepare` | ENVIRONMENT sống thật (`make doctor` xanh) · 6 lệnh make có thân · TC phủ đủ (AC/TI/ô ✗/loại test; mỗi AC có normal + abnormal — `review_tc.py` sạch; đã đối chiếu `spec-knowledge`) · regression đã rà · **dry-run** một luồng lõi |
| **E** Execute | `/spec-execute` (hoặc `/spec-retest`) | Mọi TC trong phạm vi lượt có kết quả + bằng chứng tồn tại · FAIL có bug severity · evidence-auditor đã soi |
| **C** Certify | `/spec-certify` | Verdict máy tính = verdict REPORT · bug có trạng thái cuối · QC ký · bài học ghi `context/LESSONS.md` (+ đề xuất nâng vào `spec-knowledge`, QC duyệt) · PASS → `release.py --go` · FAIL → chờ bàn giao lại |

Cả 4 pha bắt buộc mọi release — kiểm thử không có pha tuỳ chọn.

## Luật quan trọng nhất khi đang chạy

**Không hỏi QC sau pha S.** Mơ hồ → tự quyết theo TEST-PLAN/TEST-STRATEGY/HANDOVER → 1 dòng `DECISIONS.md` → đi tiếp.

| Tình huống | Làm gì |
|---|---|
| Ngoài scope test đã khoá | `BUGS.md` trạng thái `deferred`, **không hỏi**, test tiếp |
| Đụng dữ liệu người dùng thật / không đảo ngược được / hướng ra ngoài | **Hỏi thật** — bằng lời trong chat |
| Chặn cứng sau khi thử hết cách | `STATE.md §Blocker`, TC đánh `BLOCKED`, chuyển việc khác |

Năm hook chặn cứng (`SPEC.md §3c`): `guard_ask` (hỏi ngoài pha S) · `guard_readonly` (ghi vào repo nguồn) · `guard_frozen` (sửa ngưỡng/chiến lược ngoài pha S) · `guard_verdict` (ghi REPORT khi test chưa đủ) · `guard_evidence` (ảnh/video chụp được ghi ra ngoài `evidence/`).

## Ba thứ giữ chất lượng (luật #8)

1. **Ngưỡng trước**: verdict chốt ở pha S, khoá bằng hook — không sửa sau khi nhìn kết quả.
2. **Bằng chứng trước**: TC không có bằng chứng đúng loại (`TEST-STRATEGY §9`) thì không được PASS. Dấu hiệu test giả: ảnh không thấy URL bar · hình thức không có computed style · phân quyền không có response nguyên văn · agent báo "toàn pass" lượt đầu.
3. **Đối kháng**: challenge trước pha S/P; `spec-evidence-auditor` soi trước khi QC ký.

## Roster agent — theo ma trận loại test

Từ điển loại test ở `TEST-STRATEGY §3`; **mỗi loại một agent** `spec-tester-<loại>`: flow · workflow · edge · breaker · authz · compat · integration · api · cross · visual · perf · mobile · security (loại `bảo-mật` — cần QC xác nhận quyền ở pha S) (+ `spec-evidence-auditor`). Thiếu góc nhìn → thêm cột ma trận + agent theo `.claude/agents/_TESTER-TEMPLATE.md`.

Chạy **theo đợt ≤3 vai**, nhóm theo nhu cầu dữ liệu (B0 rỗng → đọc/đo → ghi → phá), reset giữa đợt. Mobile tuần tự.

## Hợp đồng lệnh

```
make doctor   make seed   make reset   make accounts   make devices   make smoke
```

Seed/dọn **qua API** — cấm chạm DB production (staging: chỉ khi `TEST-STRATEGY §8` cho phép). `make reset` chỉ xoá prefix release hiện tại (dữ liệu di sản giữ cho test tương thích).

## Khi mọi thứ rối

1. `head -15 STATE.md` — pha/release/lượt nào
2. `python3 scripts/gate.py` — thiếu chính xác cái gì
3. `cat context/releases/r<N>/TEST-PLAN.md` — phạm vi + ngưỡng đã khoá
4. Vẫn rối → làm nốt TC/đợt gần nhất trong RUNLOG, đừng mở việc mới

## Ranh giới SPEC

Không hợp: nhiều bên sign-off chéo · sản phẩm không cách ly nổi dữ liệu test trên production (khi đó `TEST-STRATEGY` phải khai môi trường staging riêng, QC quyết) · dev không bàn giao được tài liệu nào để biết release test cái gì (khi đó pha S hỏi QC cho đủ rồi ghi thành tài liệu trong mirror).
