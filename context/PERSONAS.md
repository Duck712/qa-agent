---
type: personas
tier: T0
status: DRAFT
last_reviewed: "{{DATE}}"
---

# PERSONAS — {{PROJECT_NAME}}

> **Dịch từ mirror** (`intake/releases/r<N>/nguon/` — PRD/spec phần người dùng + phân quyền;
> chế độ VIPER: `…/viper/PERSONAS.md`) ở pha S — giữ nguyên persona + ma trận vai × hành động
> của tài liệu nguồn, **thêm cột tài khoản test**. Tài liệu không có ma trận tường minh → dựng
> từ mô tả quyền trong spec, mỗi ô suy ra ghi nguồn; ô không suy ra được → hỏi QC (pha S). Ma trận là danh sách
> phép thử phân quyền: mỗi ô ✗ là một TC bắt buộc (`spec-tester-authz` gọi thẳng URL/API,
> phải bị chặn). Xoá hết dấu `_CHƯA ĐIỀN_` khi điền xong.

---

## 1. Persona

<!-- Mỗi persona một khối, GIỮ mã persona của nguồn nếu có (chưa có → tự đặt `P-<VAI>`). Chỉ chép phần SPEC cần: chân dung ngắn,
     thiết bị chính (quyết viewport/thiết bị test), luồng chính (agent đóng vai đi đúng
     luồng này), năng lực cấp/cấm.

     Ví dụ:
     ### Persona 1 — Chủ gara (role: owner, mã P-OWNER) ← persona chính
     | Mục | Nội dung |
     |---|---|
     | Chân dung + bối cảnh | Quản 3–10 thợ, thao tác giữa hai cuộc gọi, mỗi lần < 1 phút |
     | Thiết bị chính | Điện thoại |
     | Năng lực được cấp | Tạo/sửa/huỷ lịch mọi thợ trong gara mình; xem báo cáo |
     | KHÔNG được làm | Thấy dữ liệu gara khác |
     | Luồng chính | Nhận gọi → mở app → thấy giờ trống → chốt hẹn |
-->

### Persona 1 — _CHƯA ĐIỀN_ (role: _CHƯA ĐIỀN_, mã _CHƯA ĐIỀN_) ← persona chính

| Mục | Nội dung |
|---|---|
| Chân dung + bối cảnh | _CHƯA ĐIỀN_ |
| Thiết bị chính | _CHƯA ĐIỀN_ |
| Năng lực được cấp | _CHƯA ĐIỀN_ |
| KHÔNG được làm | _CHƯA ĐIỀN_ |
| Luồng chính | _CHƯA ĐIỀN_ |

## 2. Ma trận vai × hành động

<!-- Chép TRUNG THÀNH từ mirror — đây là hợp đồng phân quyền mà đội dev đã chốt với
     chủ sản phẩm; SPEC kiểm nó có thật không. Luôn giữ cột "chưa đăng nhập".
     Mỗi ô ✗ = một TC loại `phân quyền` (gate P đếm). Đổi/thêm hành động chỉ khi mirror
     đổi — SPEC không tự nghĩ ra quyền.

     Ví dụ:
     | Tạo / sửa / huỷ lịch hẹn | ✓ | ✗ | ✗ |
-->

| Hành động | _CHƯA ĐIỀN_ (role 1) | chưa đăng nhập |
|---|---|---|
| _CHƯA ĐIỀN_ | | |

## 3. Tài khoản test theo vai

<!-- Cột SPEC thêm vào — pha P điền (make accounts tạo). Mật khẩu KHÔNG ghi ở đây:
     chỉ tên biến env, giá trị nằm ở environment/local/.env (không commit).
     Vai "chưa đăng nhập" không có tài khoản nhưng vẫn là một vai trong TC. -->

| Vai (role) | Persona | Tài khoản | Biến env mật khẩu | Tạo bằng | Đăng nhập ✓? |
|---|---|---|---|---|---|
| _CHƯA ĐIỀN_ | | `spec+<role>@…` | `SPEC_PW_<ROLE>` | | ☐ |
| (chưa đăng nhập) | — | — | — | — | — |
