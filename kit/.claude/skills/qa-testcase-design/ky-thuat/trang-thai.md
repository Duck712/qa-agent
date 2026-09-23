# Chuyển trạng thái

## 1. Vẽ mô hình
Từ tài liệu (và code: enum trạng thái, hàm đổi trạng thái) vẽ vòng đời:
```
nháp ──gửi──► chờ duyệt ──duyệt──► đã duyệt ──thực hiện──► hoàn tất
  │               │                    │
  └──xoá──►(hết)  └──từ chối──► nháp   └──huỷ──► đã huỷ
```

## 2. Bảng trạng thái × sự kiện — tìm chuyển cấm có hệ thống
Mỗi ô: trạng thái mới, hoặc **✗ (phải bị chặn)**:
| Trạng thái \ Sự kiện | gửi | duyệt | từ chối | thực hiện | huỷ | xoá |
|---|---|---|---|---|---|---|
| nháp | chờ duyệt | ✗ | ✗ | ✗ | ✗ | (hết) |
| chờ duyệt | ✗ | đã duyệt | nháp | ✗ | ? | ✗ |
| đã duyệt | ✗ | ✗ | ✗ | hoàn tất | đã huỷ | ✗ |
| hoàn tất | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| đã huỷ | ✗ | ✗ | ✗ | ✗ | ✗ | ? |
**Mỗi trạng thái trong sơ đồ (kể cả trạng thái cuối) là một dòng** — thiếu dòng "đã huỷ" là sót đúng lớp bug kinh điển
(duyệt/thực hiện một đơn đã huỷ). Ô `?` = tài liệu không nói → hỏi. Ô ✗ gửi thẳng API/deep link/chạy lại job — không chỉ thử trên UI.

## 3. Độ phủ
- **0-switch** (mọi chuyển hợp lệ một lần) — tối thiểu mọi mức.
- **Mọi ô ✗** — R1 (hoặc ô ✗ nguy hiểm nhất ở R2).
- **1-switch** (mọi chuỗi 2 chuyển liên tiếp, vd gửi→từ chối→gửi lại) — R1: bắt lỗi trạng thái "dính" từ lần trước (dữ liệu cũ không reset, đếm sai).
- **Vòng đời đầy đủ** từ đầu đến trạng thái cuối — một TC workflow mỗi đường chính.
- Chuyển do **thời gian/hệ thống** (hết hạn, job tự động) và chuyển **đồng thời** (hai người cùng duyệt/huỷ).

Ghi `Kỹ thuật: chuyển trạng thái` và chuyển được kiểm (`chờ duyệt --huỷ--> ?`).
