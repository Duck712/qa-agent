# Hộp trắng nhẹ — dùng code để không sót nhánh (vẫn test hộp đen)

Agent được đọc code. Mục tiêu **không** phải đo coverage bằng công cụ, mà: mọi nhánh quan trọng trong code đều có
ít nhất một TC hộp đen chạm tới — kết quả vẫn phải chạy thật, không suy từ code.

## 1. Rút danh sách từ code
Với phần code của tính năng trong phạm vi, liệt kê:
| Thứ | Tìm ở đâu | Sinh TC |
|---|---|---|
| Nhánh điều kiện (`if/else`, `switch`, early return) | handler, service | mỗi nhánh một TC — nhánh `else` thường là ca abnormal; điều kiện ghép (`a && b \|\| c`) ở R1: mỗi điều kiện con lật được kết quả ít nhất một lần (tinh thần MC/DC) |
| Validate & giới hạn (`max_length`, `min`, regex, schema) | model, DTO, schema, migration | biên của chính con số trong code (so với tài liệu — lệch là điểm hỏi) |
| Mã lỗi / exception trả ra | `raise`, `throw`, `return 4xx` | mỗi mã lỗi một TC tái hiện được |
| Kiểm quyền (decorator, middleware, policy) | router, controller | endpoint **không** có kiểm quyền → TC phân quyền ưu tiên |
| Truy vấn có lọc tenant/owner | repository, ORM query | truy vấn không lọc → TC IDOR/cross-tenant |
| Cấu hình / feature flag | config, env | TC cho giá trị bật/tắt nếu trong phạm vi |
| Vùng vừa thay đổi | `git diff`/`git log` của bản đang kiểm | ưu tiên TC + regression quanh đó |

## 2. Ghi lại
Mỗi mục thành một dòng "nguồn code" (`app/orders.py:88 — nhánh hết hàng`) trong `Nguồn:` của TC. Mục không
test được từ ngoài (nhánh chết, lỗi nội bộ không kích được) → ghi ở ANALYSIS §6 như rủi ro, không bịa TC.

## 3. Ranh giới
- Code cho biết hệ thống **đang** làm gì, không phải **phải** làm gì. Code lệch tài liệu → hỏi, không lấy code làm kỳ vọng.
- Không sửa code, không thêm log/print vào code sản phẩm để test (nguồn chỉ đọc).
- Đo coverage bằng công cụ (coverage.py, istanbul) chỉ khi người dùng nhờ và có cách chạy không đụng code nguồn.
