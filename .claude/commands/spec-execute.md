---
description: Pha E — chạy test độc lập theo đợt (meta tự tay + agent tester), bằng chứng bắt buộc, FAIL thành bug đúng khuôn, evidence-auditor soi trước khi sang Certify
---

# /spec-execute — Pha E

> **LUẬT #2 — KHÔNG HỎI QC.** Phát hiện thì xử hoặc ghi, không hỏi.
> **LUẬT #5 — ĐỘC LẬP.** Không tin dogfood/mô tả/kết quả tự test của đội dev. Mọi kết quả từ thao tác thật của SPEC, có bằng chứng do SPEC sinh (`SPEC.md §3b`).

Việc đầu tiên: sửa `STATE.md` → `Pha hiện tại : E` (nếu vào từ `/spec-execute` lần đầu; `/spec-retest` đã đặt hộ).

Đích: mọi TC trong phạm vi lượt có kết quả + bằng chứng · FAIL có bug · `gate.py E` xanh.

## Bước 1 — Chuẩn bị

```bash
make doctor     # môi trường còn sống
make seed       # về mốc B1
```

Đọc: `TEST-PLAN §1–§2` (AC/TI) · `§6` (phân công đợt) · `ARCHITECTURE §5` (luồng lõi) · `PERSONAS §2–§3` (ma trận + tài khoản) · skill `spec-evidence` (chuẩn bằng chứng). Phạm vi lượt: lượt 1 = TC mới + regression đã chọn; lượt ≥2 = bảng `### Phạm vi retest` trong RUNLOG.

## Bước 2 — Meta tự tay (đợt 0)

Đích thân đi hết luồng lõi trên môi trường test (`Môi trường:` của manifest) bằng tài khoản test, đóng persona chính (skill `spec-browse`/`spec-mobile`). **Đi không nổi → S1, dừng ngay**, không phí spawn agent vào môi trường hỏng. Ghi mốc đợt 0 vào `RUNLOG §Nhật ký đợt`.

## Bước 3 — Spawn agent tester theo đợt

> **Vì sao không thả hết một lượt.** Trình duyệt riêng từng vai (`--isolated`) nhưng **tenant test dùng chung**: vai ghi/phá đè lên cảnh vai đọc đang nhìn, trạng thái rỗng chết ngay bản ghi đầu tiên. Chia đợt là để tách chỗ dùng chung đó (bài học từ các lần dogfood nhiều vai).

Theo `TEST-PLAN §6`, mặc định nhóm theo **nhu cầu dữ liệu** (≤3 agent/đợt):

| Đợt | Mốc | Agent | Vì sao gom |
|---|---|---|---|
| 1 | **B0 rỗng** | edge · visual · flow(đọc) | trạng thái rỗng/hình thức đo TRƯỚC khi ai ghi |
| — | reset → B1 | | ghi mốc vào RUNLOG |
| 2 | B1 (đọc/đo) | api · compat · perf | perf đo trên trạng thái ổn định, chưa ghi |
| 3 | B1 (ghi) | flow(ghi) · workflow · integration | tạo/sửa bản ghi |
| 4 | B1 (bẩn nhất) | breaker · authz · cross | phá quyền + cross-target, dọn ngay sau |
| 5 | B1 (sau đợt 4) | security | chỉ khi loại `bảo-mật` trong phạm vi **và** DECISIONS có dòng xác nhận quyền kiểm thử bảo mật; production → chỉ phép thử thụ động/đọc-thử (agent tự áp) |

Không phải release nào cũng đủ loại — chỉ spawn agent cho loại test trong phạm vi (`TEST-PLAN §2` + regression). Mobile: các vai chạm mobile chạy **tuần tự** (thiết bị dùng chung). Ràng buộc cứng: ≤3/đợt · không mở đợt sau khi đợt trước chưa xong · reset giữa các mốc khác nhau.

> **Pha E chạy CÓ NGƯỜI TRÔNG**: `make reset` nằm lớp `ask` của settings — mỗi lần reset giữa đợt cần một cái gật của người (xoá dữ liệu tenant test là thao tác đáng một nhịp dừng). Đừng lên kế hoạch chạy pha E qua đêm không ai ngồi cạnh.

Mỗi agent nhận: URL/bundle id + tenant + tài khoản vai · **danh sách TC-ID cụ thể** (kiểm có kế hoạch, không khám phá tự do) · mốc dữ liệu · chuẩn bằng chứng phải nộp · ranh giới `SAFETY.md`. `authz` nhận thêm ma trận `PERSONAS §2`; `visual` nhận đúng một experience + lát token gói của nó; `compat` nhận `API-SURFACE.md` release trước + danh sách dữ liệu di sản; `security` nhận thêm dòng DECISIONS xác nhận quyền + đường dẫn repo nguồn (chỉ đọc). Phát hiện bảo mật S1 → báo QC ngay trong buổi (ngoại lệ "lộ thông tin" của luật #2), bằng chứng che token/dữ liệu cá nhân trước khi lưu.

Mỗi agent tester được dặn nạp checklist tương ứng trong skill `spec-knowledge` (vd `breaker` → `form-input`, `authz` → `auth-login`, `api` → `api-common`, `edge` → `abnormal`) để đi tìm đúng chỗ dev hay sai — **nhưng chỉ chạy TC-ID được giao**; case hay ngoài danh sách → báo thành phát hiện, không tự thêm TC.

## Bước 4 — Thu kết quả, ghi RUNLOG + evidence + BUGS

- Screenshot agent đổ về `evidence/_inbox/<agent>/` → **phân loại** vào `evidence/r<N>/luot-<k>/<TC-ID>/`.
- Mỗi TC → một dòng `RUNLOG §Kết quả chạy`: `PASS` (link evidence tồn tại) · `FAIL` (mã bug) · `BLOCKED` (blocker ở STATE) · `SKIP` (DECISIONS).
- Mỗi FAIL → `/spec-bug` (khuôn đúng, severity theo `TEST-STRATEGY §5`). Lỗ phân quyền/cross-tenant/mất dữ liệu = S1, báo lên đầu.
- `spec-tester-api` cập nhật `API-SURFACE.md` (baseline cho compat release sau).

**Dấu hiệu test giả** (không được ghi PASS): thiếu bằng chứng đúng loại · screenshot không thấy URL bar của đúng môi trường test · hình thức không nêu computed style · phân quyền không có response nguyên văn · agent báo "mọi TC pass" lượt đầu → cho chạy lại, đòi thao tác + thứ thấy.

## Bước 5 — Đối kháng nội bộ

Spawn `spec-evidence-auditor`: bốc mẫu dòng RUNLOG (ưu tiên PASS của loại nặng: authz/compat/cross), mở evidence đối chiếu, trả danh sách lệch. Lệch nào → sửa (chạy lại TC hoặc hạ về FAIL/BLOCKED).

## Bước 6 — Chốt

```bash
make reset                        # dọn dữ liệu phá của lượt này
python3 scripts/gate.py E
```

Xanh → tick gate E, sửa `Pha hiện tại : C`, chạy `/spec-certify`.

## Ranh giới

- Không sửa AC/ngưỡng để cho dễ pass — hook `guard_frozen` chặn; TC khó thì BLOCKED + blocker, không giả PASS.
- Không thao tác ngoài tenant test, không bản ghi thiếu prefix, không notification tới người thật (`SAFETY.md`).
- Không ghi vào repo nguồn. Regression gãy (TC release cũ FAIL vì code mới) = phát hiện nặng, bug bình thường — không xoá TC cho qua.
