# Checklist — Đăng nhập / Session / Phân quyền

## 1. Login flow
- [ ] Đúng user + sai pass, sai user + đúng pass → message có LỘ "user tồn tại" không? (phải chung chung)
- [ ] Sai pass N lần liên tiếp → có lock/captcha không? lock bao lâu? unlock thế nào?
- [ ] Password có ký tự đặc biệt, khoảng trắng đầu cuối → login được không?
- [ ] Login thành công → redirect về đúng trang đích (kể cả khi vào từ deep-link)

## 2. Session
- [ ] Logout → bấm Back → còn thấy trang cần đăng nhập không? (cache)
- [ ] Logout tab 1 → tab 2 còn thao tác được không?
- [ ] Token/session hết hạn GIỮA LÚC đang điền form dài → submit → mất data hay được redirect tử tế?
- [ ] Đổi password → các session/device khác có bị kick không?
- [ ] Remember me: đóng browser mở lại, và sau thời hạn

## 3. Phân quyền (authorization) — rủi ro R1, lỗ = S1
- [ ] User quyền thấp gõ THẲNG URL trang admin → 403 hay lộ trang?
- [ ] Gọi THẲNG API của chức năng không có quyền (lấy endpoint từ DevTools) → 403?
- [ ] Sửa id trong URL/API (`/users/123` → `/users/124`) → xem được data người khác không? (IDOR)
- [ ] Bị thu hồi quyền KHI ĐANG trong trang → thao tác tiếp thì sao?
- [ ] Hệ thống multi-tenant: user tenant A có nhìn/sửa được data tenant B không? (mọi API có filter tenant)
