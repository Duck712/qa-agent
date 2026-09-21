---
type: test-plan
release: 1
tier: T0
status: DRAFT
---

# TEST PLAN — release 1

> **Lát cắt kiểm thử của MỘT release** — viết ở pha S, QC chốt, rồi KHOÁ (hook
> `guard_frozen` chặn sửa ngoài pha S; phạm vi retest của lượt bàn giao sau ghi vào
> `RUNLOG.md`, không sửa file này). Ngưỡng §4 là thứ verdict sẽ so — ghi TRƯỚC khi
> chạy test, không sửa sau khi nhìn kết quả (luật #8).
> Xoá hết dấu `_CHƯA ĐIỀN_` khi điền xong.

<!-- Bốn dòng dưới nằm NGOÀI comment — máy đọc. Dòng `Rà lại chiến lược`: release 1 ghi
     ngày lập plan; release ≥2 ghi ngày THẬT SỰ đọc lại TEST-STRATEGY đối chiếu kết quả
     release trước (gate S đòi ngày ≥ `Release mở`). -->

NGUỒN: intake/releases/r1/ — dịch ngày _CHƯA ĐIỀN_
Phạm vi: _CHƯA ĐIỀN_
Lượt bàn giao tối đa: {{3}}
Rà lại chiến lược (release 1): _CHƯA ĐIỀN_

---

## 1. Phạm vi — AC mới

<!-- Hợp AC của các tính năng trong phạm vi release, lấy từ mirror (PRD/spec/user story;
     VIPER: PRD hiện hành + archive/vong-i/PRD.md). GIỮ NGUYÊN mã AC của nguồn + capability để
     máy truy vết — gate P đối chiếu bảng này với nhãn `AC:` trong testcases/.
     Cột "Nguồn": ĐỂ TRỐNG nếu mã AC không trùng giữa các tài liệu (TC ghi `AC: AC-3`);
     trùng thì ghi mã ngắn phân biệt và TC ghi đúng dạng `AC-3 (<mã>)` — VIPER: `l<i>`,
     TC ghi `AC-3 (l4)`. Nguồn chưa đánh mã AC → tự đặt `AC-n` theo thứ tự, ghi truy vết HANDOVER. -->

| AC | Nguồn | Capability | Diễn giải 1 dòng |
|---|---|---|---|
| _CHƯA ĐIỀN_ | | | |

## 2. Hạng mục test (TI)

<!-- Mỗi TI một cụm việc kiểm — to hơn TC, nhỏ hơn release. `Loại test` phải là MỘT tên
     trong ma trận `TEST-STRATEGY §3` và ô (loại × target) phải tick — TI mồ côi chiến
     lược là gate đỏ. `Nguồn` trỏ CAP/AC. ≥3 TI.

     Ví dụ:
     | TI-1 | Đặt lịch lõi hoạt động đúng | chức năng | CAP-BOOK-01 · AC-1..3 (l2) | R1 |
     | TI-2 | Ma trận phân quyền kín | phân quyền | PERSONAS §2 — 8 ô ✗ | R1 |
     | TI-3 | Luồng đặt lịch nhanh (p95) | hiệu năng | TEST-STRATEGY §7 | R2 | -->

| TI | Tên | Loại test | Nguồn | Mức |
|---|---|---|---|---|
| TI-1 | _CHƯA ĐIỀN_ | | | |
| TI-2 | _CHƯA ĐIỀN_ | | | |
| TI-3 | _CHƯA ĐIỀN_ | | | |

## 3. Out-of-scope của release này

<!-- Tường minh — gồm cả LOẠI TEST cố tình bỏ (gate P tra ở đây trước khi đỏ):
     "hình thức — release này không đổi UI (mirror diff DESIGN-SYSTEM trống)". -->

- _CHƯA ĐIỀN_

## 4. Ngưỡng verdict — GHI TRƯỚC, KHÔNG SỬA SAU KHI EXECUTE BẮT ĐẦU

<!-- Instantiate khuôn `TEST-STRATEGY §10` bằng SỐ THẬT. Ghi đè khuôn → 1 dòng DECISIONS.
     gate.py C tự tính verdict từ BUGS + RUNLOG so đúng bảng này — REPORT phải ghi verdict
     máy tính ra. -->

| Điều kiện | Ngưỡng release này |
|---|---|
| Bug S1 mở | 0 |
| Bug S2 mở | 0 (PASS) / ≤ _CHƯA ĐIỀN_ có cam kết (PASS-có-điều-kiện) |
| AC mới có ≥1 TC PASS | 100% |
| Regression khu vực R1 | 100% PASS |
| Tổng TC PASS | ≥ _CHƯA ĐIỀN_ % |
| Lượt bàn giao tối đa | (dòng 3 đầu file) |

## 5. Regression scope

<!-- Release 1 chưa có release trước → ghi `— (release đầu)`. Release ≥2: liệt kê TC-ID
     chọn từ TC sống tag `Regression: có`, theo luật `TEST-STRATEGY §6`; gate P đếm
     ≥ tối thiểu và kiểm từng ID tồn tại. TC bị gỡ (dev phá legacy có phép) ghi rõ
     kèm DECISIONS. -->

| TC | Lý do chọn |
|---|---|
| — (release đầu) | |

## 6. Phân công đợt

<!-- Kế hoạch đợt cho pha E — nhóm theo NHU CẦU DỮ LIỆU, ≤3 agent/đợt (trình tự chuẩn ở
     /spec-execute). Đợt nào cần mốc nào, agent nào chạy, phủ TI nào. -->

| Đợt | Mốc dữ liệu | Agent (≤3) | Phủ TI |
|---|---|---|---|
| 0 | B1 | meta tự tay — smoke luồng lõi | — |
| 1 | B0 | _CHƯA ĐIỀN_ | |

## 7. Rủi ro release này

| Rủi ro | Ứng phó |
|---|---|
| _CHƯA ĐIỀN_ | |

## 8. Truy vết TEST-STRATEGY

<!-- Mỗi dòng: mục nào của chiến lược áp vào release này thế nào. Lệch → sửa STRATEGY
     trước (pha S) + change log §11, không lệch ngầm ở đây. -->

| Mục STRATEGY | Áp vào release này |
|---|---|
| §2 dòng r1 | _CHƯA ĐIỀN_ |
| §4 khu vực R1 | _CHƯA ĐIỀN_ |

---

Chốt bởi QC: _CHƯA ĐIỀN_   ← gate S bắt dòng này; sau ngày này hết hỏi QC, ngưỡng khoá
