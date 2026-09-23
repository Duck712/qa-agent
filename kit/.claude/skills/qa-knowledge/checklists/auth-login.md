# Checklist — Đăng nhập / Session / Phân quyền

> **Mục checklist là câu hỏi để thử, không phải kỳ vọng.** Kỳ vọng lấy từ tài liệu; tài liệu không nói → điểm hỏi.
> Không chép từ như "tử tế / rõ ràng / OK" vào Kỳ vọng. Trích nguồn trong TC: `Nguồn: <checklist> <số mục>`, vd `form-input 2.3`.

## 1. Login flow
- [ ] 1.1 Đúng user + sai pass, sai user + đúng pass → message có LỘ "user tồn tại" không? (phải chung chung)
- [ ] 1.2 Sai pass N lần liên tiếp → có lock/captcha không? lock bao lâu? unlock thế nào?
- [ ] 1.3 Password có ký tự đặc biệt, khoảng trắng đầu cuối → login được không?
- [ ] 1.4 Login thành công → redirect về đúng trang đích (kể cả khi vào từ deep-link)

## 2. Session
- [ ] 2.1 Logout → bấm Back → còn thấy trang cần đăng nhập không? (cache)
- [ ] 2.2 Logout tab 1 → tab 2 còn thao tác được không?
- [ ] 2.3 Token/session hết hạn GIỮA LÚC đang điền form dài → submit → dữ liệu đã nhập còn không, có được đưa về đăng nhập rồi quay lại đúng chỗ không?
- [ ] 2.4 Đổi password → các session/device khác có bị kick không?
- [ ] 2.5 Remember me: đóng browser mở lại, và sau thời hạn

## 3. Phân quyền (authorization) — rủi ro R1, lỗ = S1
- [ ] 3.1 User quyền thấp gõ THẲNG URL trang admin → 403 hay lộ trang?
- [ ] 3.2 Gọi THẲNG API của chức năng không có quyền (lấy endpoint từ DevTools) → 403?
- [ ] 3.3 Sửa id trong URL/API (`/users/123` → `/users/124`) → xem được data người khác không? (IDOR)
- [ ] 3.4 Bị thu hồi quyền KHI ĐANG trong trang → thao tác tiếp thì sao?
- [ ] 3.5 Hệ thống multi-tenant: user tenant A có nhìn/sửa được data tenant B không? (mọi API có filter tenant)
- [ ] 3.6 Gửi thêm `role` / `tenant_id` / `owner_id` / `is_admin` trong body tạo/sửa (mass assignment) → server bỏ qua, không nâng quyền
- [ ] 3.7 Tài khoản bị khoá / vô hiệu / xoá khỏi tổ chức → token cũ còn gọi API được không?
- [ ] 3.8 Đổi tenant bằng header / tham số / subdomain → không vào được tenant không thuộc về mình

## 4. Đặt lại mật khẩu, đăng ký, xác minh
- [ ] 4.1 Link/token đặt lại mật khẩu: hết hạn, dùng lại lần 2, dùng sau khi đã đổi mật khẩu/email, dùng bởi tài khoản khác
- [ ] 4.2 Đăng ký trùng email/số điện thoại (hoa thường, dấu cách, `+alias`) → báo đúng, không lộ tài khoản có tồn tại (theo tài liệu)
- [ ] 4.3 Email chưa xác minh → được làm gì, không được làm gì (theo tài liệu)

## 5. MFA / OTP / SSO
- [ ] 5.1 OTP sai N lần → khoá/giới hạn; OTP cũ/đã dùng bị từ chối; OTP của phiên khác không dùng được
- [ ] 5.2 Bỏ qua bước 2: gọi thẳng API/URL của bước sau khi mới qua bước 1 → bị chặn
- [ ] 5.3 SSO/OAuth: thiếu hoặc sai `state`, `redirect_uri` lạ, dùng lại `code` → bị từ chối

## 6. Token & phiên (kỹ thuật)
- [ ] 6.1 Session id/cookie đổi sau khi đăng nhập (chống session fixation)
- [ ] 6.2 JWT sửa payload giữ chữ ký cũ, `alg: none`, token hết hạn, token của tenant/môi trường khác → bị từ chối
