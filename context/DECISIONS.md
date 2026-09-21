---
type: decisions
tier: T1
append_only: true
last_reviewed: "{{DATE}}"
---

# DECISIONS — {{PROJECT_NAME}}

> **Append-only.** Không sửa dòng cũ; quyết định mới đè quyết định cũ thì thêm dòng mới và ghi `thay cho: <ngày>`.
>
> File này **thay thế cho việc hỏi QC**. Từ pha P trở đi, gặp mơ hồ → chọn phương án hợp lý
> nhất theo `TEST-PLAN` / `TEST-STRATEGY` / `HANDOVER` → ghi một dòng ở đây → đi tiếp.
> QC đọc một lượt cuối buổi, không bị ngắt giữa dòng.
>
> `release.py` append mốc `| (release N) |` khi mở release và `| (release N — bàn giao k) |`
> khi mở lượt retest — `gate.py` chỉ đếm quyết định **dưới mốc cuối**. Đừng ghi mốc bằng tay.

**Khi nào phải ghi**: chọn cách cách ly dữ liệu, xác nhận quyền kiểm thử bảo mật (dẫn nguyên văn QC), QC đồng ý chốt/ký (dẫn nguyên văn — SPEC.md §3e), ghi đè khuôn ngưỡng, SKIP một TC, hạ severity một bug, gỡ TC khỏi regression, chấp nhận bug `không sửa`, chọn đa-tenant-song-song thay vì chia đợt — bất cứ thứ gì mà ba ngày sau QC nhìn lại sẽ hỏi "sao lúc đó làm thế?".

**Khi nào không cần**: đặt tên file evidence, thứ tự chạy TC trong một đợt, chi tiết vặt đổi lúc nào cũng được.

---

| Ngày | Quyết định | Lý do | Giả định đang mang | Đảo ngược được? |
|---|---|---|---|---|
| (template) | Dùng quy trình SPEC cho việc kiểm thử sản phẩm này | Sản phẩm cần test độc lập theo từng bản deploy bàn giao | QC là Authority duy nhất; release nhận diện được qua bản deploy (VIPER: loop có P) | Có |

<!-- Dòng seed trên cố ý ghi ngày là "(template)" để gate KHÔNG đếm nó —
     gate đòi ≥2 quyết định có ngày ISO do chính dự án này ghi ra.

     Mẫu dòng:
| 2026-09-01 | Cách ly bằng tài khoản + prefix, không tạo tenant riêng | Sản phẩm không đa tenant (HANDOVER lỗ hổng #2) | Prefix SPEC-r1- đủ phân biệt khi dọn | Có |
| 2026-09-03 | SKIP TC-BOOK-01-007 lượt này | Cần tài khoản ngân hàng thật — ngoài sandbox | Luồng nạp tiền đã phủ bởi TC-PAY-01-002 trên sandbox | Có — chạy khi có sandbox đủ |
-->
