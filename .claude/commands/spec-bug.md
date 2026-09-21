---
description: Ghi một bug đúng khuôn vào BUGS.md — mã, severity, bước tái hiện, bằng chứng, TC/AC ref
---

# /spec-bug

Ghi một bug — QA-friendly, đủ để dev fix mà không phải hỏi lại. Dùng ở pha E khi một TC FAIL, và bất cứ lúc nào phát hiện lỗi (ngoài scope → trạng thái `deferred`).

## Cách ghi

Append một khối vào `context/BUGS.md §Sổ bug`, và cập nhật bảng `## Tổng hợp`.

```markdown
### BUG-r<N>-<số> — <một câu mô tả, viết theo HẬU QUẢ NGƯỜI DÙNG>

| Mục | Nội dung |
|---|---|
| Severity | S1 / S2 / S3 / S4 (theo TEST-STRATEGY §5) |
| AC / TC | AC-2 · TC-BOOK-01-005  (VIPER: `AC-2 (l2)`) |
| Lượt phát hiện | bàn giao <k> · đợt <n> · <agent> |
| Môi trường | <production/staging> · bản deploy <…> · tài khoản/vai <…> · thời điểm <ISO giờ phút> |
| Bước tái hiện | 1. … 2. … 3. …  (đủ để người khác làm lại từ số 0) |
| Kỳ vọng | <thứ lẽ ra phải xảy ra> |
| Bằng chứng | evidence/r<N>/luot-<k>/<TC-ID>/ |
| Trạng thái | mở |
```

## Quy tắc

- **Mã `BUG-r<N>-<số>`**: N = release **phát hiện**; số tăng dần, không tái dùng.
- **Tiêu đề theo hậu quả**: "Thợ sửa được lịch của người khác", không phải "PUT /bookings thiếu check owner". QC và dev đọc tiêu đề để hiểu mức nghiêm trọng.
- **Bước tái hiện đủ để làm lại**: tài khoản nào, URL/API nào, dữ liệu gì (prefix `SPEC-r<N>-`). Bug không tái hiện được là bug không fix được.
- **Severity chấm lúc ghi**, theo bảng — không hạ mức để đẹp số; hạ sau đó = 1 dòng DECISIONS.
- **Lỗ phân quyền / cross-tenant / mất dữ liệu / crash / tiền sai = S1**, không ngoại lệ, báo lên đầu.
- **Bằng chứng bắt buộc**: mọi bug trỏ thư mục evidence tồn tại. Bug không bằng chứng là suy đoán, không phải phát hiện.

## Trạng thái — vòng đời

```
mở → đã fix chờ retest → đóng (retest PASS lượt k, <ngày>)
mở → không sửa (QC chấp nhận — DECISIONS <ngày>)
mở → deferred (ngoài scope — release sau nhặt ở pha S)
```

Bug S1/S2 chuyển `đóng` → phải sinh 1 TC regression (`TEST-STRATEGY §6`) — không thì lỗ đó quay lại release sau mà không ai bắt.
