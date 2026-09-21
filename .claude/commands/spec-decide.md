---
description: Append một dòng vào DECISIONS.md — thứ thay thế cho việc hỏi QC
---

# /spec-decide

Ghi một quyết định. Đây là **nghi thức thay cho câu hỏi** (luật #2): thay vì dừng hỏi QC, tự quyết rồi để lại vết cho QC đọc theo lô cuối buổi.

## Khi nào phải ghi

Cách cách ly dữ liệu, ghi đè khuôn ngưỡng, SKIP một TC, hạ severity một bug, gỡ TC khỏi regression, chấp nhận bug `không sửa`, chọn đa-tenant-song-song thay vì chia đợt, escalate vượt trần lượt bàn giao — bất cứ thứ gì mà ba ngày sau QC nhìn lại sẽ hỏi "sao lúc đó làm thế?".

## Khi nào không cần

Tên file evidence, thứ tự chạy TC trong một đợt, chi tiết vặt. Ghi mọi thứ thì `DECISIONS.md` thành nhật ký không ai đọc.

## Cách ghi

Append vào `context/DECISIONS.md`, **không sửa dòng cũ**, **không đụng dòng mốc `(release N)`** (release.py ghi, gate đếm dưới đó).

```markdown
| <ngày ISO> | <quyết định> | <lý do> | <giả định đang mang> | <đảo ngược được?> |
```

| Cột | Viết gì |
|---|---|
| Quyết định | Cụ thể, làm được. "SKIP TC-PAY-01-007 lượt này" — không phải "bỏ bớt test thanh toán" |
| Lý do | Ràng buộc thật, dẫn về TEST-PLAN/STRATEGY/HANDOVER nếu có |
| Giả định | Điều đang tin mà chưa kiểm — **cột quan trọng nhất**, cho QC biết chỗ cần soi |
| Đảo ngược được? | Có / Khó / Không |

## Ví dụ

```markdown
| 2026-09-03 | SKIP TC-PAY-01-007 lượt này | Cần tài khoản ngân hàng thật — ngoài sandbox (HANDOVER lỗ hổng #4) | Luồng nạp tiền đã phủ bởi TC-PAY-01-002 trên sandbox | Có — chạy khi có sandbox đủ |
| 2026-09-05 | Hạ BUG-r2-011 từ S2 xuống S3 | Có đường vòng rõ ràng (bấm lại lần 2 là được), không mất dữ liệu | Người dùng chịu được thao tác thừa một nhịp | Có |
```

## Ở pha C

Bug `không sửa (QC chấp nhận)` và điều kiện của verdict PASS-có-điều-kiện đều phải có một dòng ở đây, kèm ngày fix cam kết nếu có.
