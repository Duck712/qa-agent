---
type: conventions
tier: T2
last_reviewed: "{{DATE}}"
---

# CONVENTIONS — {{PROJECT_NAME}}

> Quy ước viết tài liệu test — để QA engineer đọc là viết được, và để máy (gate/hook)
> đếm được. Ngắn có chủ đích.

---

## 1. ID

- `TI-<số>` — hạng mục test, sống trong một release (TEST-PLAN §2).
- `TC-<CAP-XXX-NN>-<số>` — test case theo capability · `TC-CROSS-<loại>-<số>` — TC xuyên-capability. Tăng dần trong file, **không tái dùng số** — TC bỏ đi đánh dấu `(đã gỡ — DECISIONS <ngày>)`, giữ khối.
- `BUG-r<N>-<số>` — N là release **phát hiện**; bug sống tiếp qua release thì giữ nguyên mã.
- Ngày luôn ISO `YYYY-MM-DD`.

## 2. Viết test case

- Bước viết cho người CHƯA biết sản phẩm: thao tác cụ thể · dữ liệu cụ thể (mang prefix `SPEC-r<N>-`) · kỳ vọng **quan sát được**. "Kiểm tra hoạt động đúng" không phải kỳ vọng.
- Dòng meta dưới heading giữ đúng định dạng một dòng, nhãn cách nhau ` · ` — sai là TC vô hình với gate (`testcases/_TC-TEMPLATE.md`).
- Một TC bắt một kiểu hỏng. TC "đi hết mọi thứ một lượt" là TC không bao giờ FAIL rõ ràng.

## 3. Viết bug

- Tiêu đề theo **hậu quả người dùng**, không theo kỹ thuật: "Thợ sửa được lịch của người khác", không phải "PUT /bookings thiếu check owner".
- Bước tái hiện đủ để người khác làm lại từ số 0: tài khoản nào, URL nào, dữ liệu nào.
- Kỳ vọng ghi riêng một dòng — người đọc không phải đoán "thế đúng ra phải sao".
- Severity theo `TEST-STRATEGY §5`, chấm lúc ghi; hạ mức sau đó = 1 dòng DECISIONS.

## 4. Bằng chứng

- Thư mục: `evidence/r<N>/luot-<k>/<TC-ID>/` — mọi dòng RUNLOG trỏ vào đúng cấp TC-ID.
- Screenshot phải **thấy URL bar** (web) hoặc kèm bundle id đang chạy (mobile).
- Request/response dán **nguyên văn** vào file text, không tóm tắt.
- Chuẩn tối thiểu theo loại TC: `TEST-STRATEGY §9`; cách thu: skill `spec-evidence`.

## 5. Báo cáo

- Executive summary: 5 dòng, không thuật ngữ, QC đọc 30 giây nắm được.
- Số phải khớp sổ: REPORT chép từ RUNLOG/BUGS, không "làm tròn cho đẹp" — gate C đối chiếu.
- Phản hồi/kết quả xấu ghi nguyên trạng — báo cáo tồn tại để QC quyết đúng, không phải để dễ nghe.

## 6. Git

- Commit nhỏ, message tiếng Việt, thể chủ động: `chạy đợt 2 release 1 — 12 TC, 2 bug mới`.
- Kết luận lệch tài liệu → sửa tài liệu **cùng commit** (luật #4).
- Evidence nhị phân commit được (ảnh/log nhỏ); video KHÔNG commit — ghi đường dẫn ngoài.

## 7. Trước khi nói "xong một lượt chạy"

```
Mọi TC trong phạm vi lượt có kết quả       (gate.py E xanh)
Mọi FAIL có bug đúng khuôn                 (BUGS.md)
spec-evidence-auditor đã soi               (báo cáo lệch = xử trước)
```
