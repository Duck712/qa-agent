# Tổ hợp: pairwise · classification tree

## 1. Khi nào
Nhiều tham số độc lập kết hợp: trình duyệt × OS × vai × ngôn ngữ × gói dịch vụ × cấu hình cờ × loại thiết bị.
Chạy đủ tích Descartes thì bùng nổ (4×3×3×2×2 = 144); chọn bừa thì sót. Phần lớn lỗi tổ hợp do **hai** tham số
tương tác → **pairwise** (mọi cặp giá trị xuất hiện ít nhất một lần) thường còn ~10–20 dòng.

## 2. Sinh bộ pairwise
```bash
python3 .claude/qa-scripts/pairwise.py "Trình duyệt=Chrome,Firefox,Safari,Edge" "OS=Windows,macOS,Linux" \
    "Vai=admin,member,guest" "Ngôn ngữ=vi,en" --khong "Safari&Windows" --khong "Safari&Linux"
```
In bảng markdown + số cặp đã phủ. `--khong "A&B"` loại tổ hợp không tồn tại (ràng buộc; giá trị trùng tên giữa
hai tham số thì viết `Tên=giá trị`). `--tat-ca` in tích đầy đủ trừ tổ hợp cấm. Mỗi dòng = một cấu hình; chạy bộ TC luồng lõi (smoke) trên từng cấu hình, hoặc gán
mỗi dòng cho một TC khác nhau để trải cấu hình.
- Tham số **R1** (vd vai × gói trả tiền) → dùng tích đầy đủ cho riêng cặp đó, pairwise cho phần còn lại.
- Dòng pairwise lỗi → thu hẹp: đổi từng tham số về giá trị "an toàn" để tìm cặp gây lỗi, ghi vào bug.

## 3. Classification tree
Khi tham số có cấu trúc (loại khách → cá nhân/doanh nghiệp → doanh nghiệp có/không mã thuế): vẽ cây phân loại
(mỗi nhánh là một lớp phân vùng), rồi chọn tổ hợp lá: tối thiểu mỗi lá xuất hiện một lần, R1 thì pairwise giữa các nhánh.
Cây vẽ bằng thụt dòng trong TC hoặc ANALYSIS là đủ.

Ghi `Kỹ thuật: pairwise` (hoặc `classification tree`) + bảng cấu hình vào TC.
