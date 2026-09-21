# STATE — {{PROJECT_NAME}}

> Trạng thái sống. Người và agent cùng đọc/ghi. Cập nhật ngay khi đổi pha hoặc tick gate.

```
Pha hiện tại  : S
Release       : 1
Lần bàn giao  : 1
Quy trình dev : (từ manifest — `VIPER` hoặc `khác`)
Phạm vi       : (chưa có — chờ manifest intake/releases/r1/RELEASE.md)
Repo nguồn    : (hiển thị nhanh — nguồn sự thật là dòng `Repo nguồn:` trong manifest)
Môi trường    : (từ manifest — `production` hoặc `staging`)
Điểm vào chính: (từ manifest — URL đầy đủ từng target ở manifest §URL theo target và context/ENVIRONMENT.md §1–§2)
Tenant test   : (pha P điền)
```

> **Release** = một lượt S→P→E→C trên một bản deploy đội dev bàn giao (chế độ VIPER: khối loop kết thúc bằng loop có pha P).
> Đóng release (verdict PASS) bằng `python3 scripts/release.py --go`; verdict FAIL thì chờ
> QC thả manifest `RELEASE-<k+1>.md` rồi mở lượt bàn giao mới bằng `--retest` — CÙNG release,
> không đổi ngưỡng. Từ release 2 script chèn dòng `Release mở: <ngày>`; từ lượt bàn giao 2
> chèn `Bàn giao mở: <ngày>` — challenge và các phép đếm của gate chỉ tính dòng có ngày ≥
> max(hai mốc đó) (SPEC.md §1.2).
>
> **Pha hiện tại** là dòng mà hook `guard_ask`/`guard_frozen` và `gate.py` đọc — vào pha mới
> thì sửa dòng này NGAY (lỗi thực chiến phổ biến nhất là quên đổi pha rồi hook
> chặn/mở sai chỗ).

---

## Gate

> Bản thao tác. Định nghĩa chuẩn ở `SPEC.md §1.1` — lệch nhau thì sửa chỗ này cho khớp (luật #4).

**S — Scope**
- [ ] Manifest `intake/releases/r<N>/RELEASE.md` (lượt k ≥2: `RELEASE-<k>.md`) là bản thật — hết `{{…}}`, đủ dòng máy đọc (`Quy trình dev` · `Repo nguồn` · `Release` · `Phạm vi` · `Bản deploy` · `Môi trường` · `Điểm vào chính` · `Lần bàn giao`), khớp STATE
- [ ] Manifest có bảng `## URL theo target` phủ mọi target trong phạm vi (thiếu → ghi `HANDOVER §Lỗ hổng`, tự dò ở pha P)
- [ ] `Repo nguồn` tồn tại · *(chế độ VIPER)* mỗi loop trong phạm vi có `_PROPOSAL.md`; loop deploy có `P` trong `Pha vòng này`
- [ ] Mirror đã copy — dịch từ mirror, không từ nguồn sống: `intake/releases/r<N>/nguon/` ≥1 file (VIPER: `viper/` ≥5 file .md)
- [ ] `context/HANDOVER.md`: marker `NGUỒN: <tên nguồn> — <path>` + bảng `## Truy vết nguồn → context` ≥3 dòng (VIPER ≥5) + `## Lỗ hổng & cách xử`
- [ ] (release 1) `context/TEST-STRATEGY.md` đủ §1–§10 + `Chốt bởi QC:` · §2 ≥1 dòng (VIPER: số dòng §2 ≥ số loop đã khai `P`)
- [ ] (nếu loại `bảo-mật` tick ở ma trận) `DECISIONS.md` có dòng xác nhận quyền kiểm thử bảo mật — dẫn nguyên văn QC
- [ ] (release ≥2 — thay dòng trên) `TEST-PLAN.md` có `Rà lại chiến lược (release N): <ISO>` ngày ≥ `Release mở`; phạm vi lệch §2 chiến lược → có change log §11
- [ ] `context/releases/r<N>/TEST-PLAN.md`: 4 dòng đầu máy đọc · §1 AC mới · §2 ≥3 TI (Nguồn + Loại test thuộc ma trận) · §3 out-of-scope · §4 ngưỡng verdict CÓ SỐ · §5 regression scope
- [ ] Mọi TI có mặt ở `COVERAGE-MAP.md`; mọi capability trong phạm vi có dòng
- [ ] `context/DECISIONS.md`: ≥2 quyết định của release này (release ≥2: dưới mốc `(release N)`, ngày ≥ `Release mở`)
- [ ] Challenge pha S **PASS** (§Challenge log, ngày ≥ mốc)
- [ ] `TEST-PLAN.md` có dòng `Chốt bởi QC: <ISO>`
- [ ] **Scope khoá** — từ đây không hỏi QC nữa

**P — Prepare**
- [ ] Challenge pha P PASS (ngày ≥ mốc)
- [ ] `context/ENVIRONMENT.md` đủ: **mỗi target trong phạm vi một dòng** URL/bundle id (nội bộ → `—` + đường vòng) · tài khoản test từng vai · tenant + prefix · seed/reset B0/B1 · thiết bị (nếu có mobile)
- [ ] `make doctor` · `make seed` · `make reset` · `make accounts` · `make devices` · `make smoke` đã hiện thực
- [ ] TC đủ phủ: mỗi TI ≥1 TC · mỗi AC mới ≥1 TC · TC phân quyền phủ đủ ô ✗ ma trận · dòng meta hợp lệ
- [ ] Mỗi loại test tick trong ma trận `TEST-STRATEGY §3` × phạm vi có ≥1 TC — loại bỏ qua nằm ở out-of-scope
- [ ] (release ≥2) Regression đã chọn ở `TEST-PLAN §5` — ≥ tối thiểu `TEST-STRATEGY §6`, mọi TC tồn tại và mang `Regression: có`
- [ ] `make doctor` xanh · `make seed` chạy xong không lỗi
- [ ] **Dry-run** — meta tự tay một luồng lõi trên môi trường test bằng tài khoản test

**E — Execute**
- [ ] `context/releases/r<N>/RUNLOG.md` có mục `## Lượt chạy — bàn giao <k>` khớp STATE (k ≥2 thiếu mục/mốc → fail-closed)
- [ ] Mọi TC trong phạm vi lượt có kết quả `PASS|FAIL|BLOCKED|SKIP`, ngày ≥ mốc lượt
- [ ] Mỗi PASS có link `evidence/r<N>/…` tồn tại trên đĩa (không nằm trong repo nguồn)
- [ ] Mỗi FAIL có bug severity S1–S4 · mỗi BLOCKED có blocker · mỗi SKIP có dòng DECISIONS
- [ ] (lượt k ≥2) Mọi bug `mở`/`đã fix chờ retest` của lượt trước có dòng retest
- [ ] Kết quả là thao tác thật — đã cho `spec-evidence-auditor` soi

**C — Certify**
- [ ] Ngày `Chốt bởi QC` (TEST-PLAN) ≤ ngày chạy sớm nhất của lượt 1
- [ ] Verdict trong `REPORT.md` mục `## Kết luận — bàn giao <k>` KHỚP verdict máy tính (`gate.py C` in ra)
- [ ] `REPORT.md` đủ mục: executive summary · số liệu · so ngưỡng · regression · (FAIL) `## 5. Bàn giao lại cho dev`
- [ ] Mọi bug có trạng thái cuối (`đóng` / `mở` / `không sửa`+DECISIONS / `deferred`+DECISIONS) · bảng `Tổng hợp` BUGS khớp các khối
- [ ] `COVERAGE-MAP.md` cột Trạng thái cập nhật
- [ ] `Ký bởi QC: <ISO>` trong mục kết luận lượt này
- [ ] `context/LESSONS.md` có mục của release này (1–3 lesson, hoặc 1 dòng lý do không có) · lesson QC duyệt đã vào skill `spec-knowledge`
- [ ] PASS → `python3 scripts/release.py --go` · FAIL → chờ `RELEASE-<k+1>.md` rồi `--retest`

---

## Challenge log

Meta tự ra câu hỏi khó dựa trên tài liệu thật, chấm PASS/FAIL. **Pha S**: 3–5 câu về phạm vi test, trả lời chỉ từ tài liệu đã dịch — không trả lời được là lỗ dịch, quay lại vá (còn được hỏi QC). **Pha P**: câu kiểu "TC nào phủ ca X? Seed nào dựng được trạng thái đó?". FAIL → đọc lại, vá, không đi tiếp. Gate chỉ tính dòng ngày ≥ max(`Release mở`, `Bàn giao mở`).

| Ngày | Pha | Câu hỏi | Phán quyết | Ghi chú |
|---|---|---|---|---|
| | | | | |

---

## Blocker

Chặn cứng sau khi đã tự thử hết cách (môi trường sập, tài khoản không cấp được, build mobile sai env…). Không hỏi giữa chừng — dồn vào đây, TC liên quan đánh `BLOCKED`, báo gộp cuối buổi.

| Ngày | Blocker | Đã thử gì | TC bị chặn | Trạng thái |
|---|---|---|---|---|
| | | | | |
