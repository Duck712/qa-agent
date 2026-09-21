---
type: release-report
release: 1
tier: T0
status: DRAFT
---

# BÁO CÁO KIỂM THỬ — release 1

> **Viết ở pha C, sau khi gate E xanh** — hook `guard_verdict` chặn ghi file này khi test
> chưa chạy đủ / FAIL thiếu bug / PASS thiếu bằng chứng. Verdict phải KHỚP verdict máy
> tính (`python3 scripts/gate.py C` in ra) — so với bảng ngưỡng `TEST-PLAN §4` đã khoá.
>
> Mỗi lượt bàn giao một mục `## Kết luận — bàn giao <k>` ở cuối — lượt sau APPEND mục mới,
> không sửa mục cũ. Thân báo cáo (§1–§5) cập nhật theo lượt hiện tại.

---

## 1. Executive summary

<!-- 5 dòng, KHÔNG thuật ngữ — QC đọc 30 giây nắm được: đạt hay không, mấy lượt, bug nặng
     nhất là gì và số phận nó, còn gì treo.
     Ví dụ: "Release 1 đạt sau 2 lượt bàn giao. 42/44 TC pass. Một lỗ phân quyền nghiêm
     trọng (thợ sửa được lịch người khác) đã được dev sửa và kiểm lại đạt. Còn 2 lỗi hình
     thức nhẹ ghi nhận, không cản dùng." -->

_CHƯA ĐIỀN_

## 2. Số liệu

| Chỉ số | Giá trị |
|---|---|
| TC trong phạm vi / đã chạy / PASS lượt cuối | |
| AC mới có ≥1 TC PASS | |
| Regression (trong đó khu vực R1) | |
| Bug S1/S2/S3/S4 — mở cuối kỳ | |
| Lượt bàn giao đã dùng / tối đa | |

## 3. So ngưỡng (TEST-PLAN §4 — đã khoá trước khi chạy)

| Điều kiện | Ngưỡng | Thực tế | Đạt? |
|---|---|---|---|
| | | | |

## 4. Kết quả theo hạng mục (TI)

| TI | TC pass/tổng | Bug liên quan | Ghi chú |
|---|---|---|---|
| | | | |

## 5. Bàn giao lại cho dev

<!-- Verdict FAIL hoặc PASS-có-điều-kiện: danh sách bug mở theo severity, trỏ khối trong
     BUGS.md kèm bằng chứng — đây là đầu vào để đội dev đưa vào vòng fix của họ. SPEC
     không sinh file cho repo nguồn (luật #4) — QC chuyển thông tin này theo kênh của mình
     (tracker, chat…). Verdict PASS: ghi `—`. -->

| Bug | Severity | Một câu | Bằng chứng |
|---|---|---|---|
| | | | |

---

## Kết luận — bàn giao 1

Verdict: _CHƯA ĐIỀN_ <!-- PASS | PASS-có-điều-kiện | FAIL — phải khớp gate.py C -->

Điều kiện kèm theo (PASS-có-điều-kiện): _mỗi điều kiện một dòng: BUG-… + ngày fix cam kết + DECISIONS ngày …_

Ký bởi QC: _CHƯA ĐIỀN_   ← gate C bắt dòng này, ngày ≥ mốc lượt
