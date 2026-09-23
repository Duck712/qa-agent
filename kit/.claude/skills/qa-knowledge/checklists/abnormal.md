# Checklist — Case bất thường / edge cross-cutting
> Áp dụng khi test luồng đi qua nhiều màn / nhiều component / phụ thuộc hạ tầng.
> Các case ở đây KHÔNG thuộc riêng form/auth/upload/api — mà là "cả hệ thống" phải chịu được.
> Không cover hết cho MỌI feature — chọn nhóm phù hợp với luồng đang test.

## 1. Network & infrastructure failure
- [ ] Mất mạng GIỮA request (đã gửi, chưa nhận response) → UI ở trạng thái gì? Retry được không? Có tạo dữ liệu ma không?
- [ ] Mạng chậm (3G/simulated 500ms+ latency) → loading indicator đủ lâu không? Timeout có xử lý tử tế không?
- [ ] Backend trả 5xx ngẫu nhiên (503/502/504) → UI hiện lỗi thân thiện hay stack trace?
- [ ] Dep service phụ thuộc chết (payment gateway, SMS, mail) → luồng chính có bị block cả không, có fallback không?
- [ ] DNS lỗi / SSL cert lỗi → thông báo có rõ nguyên nhân không?

## 2. Concurrent user / race condition
- [ ] 2 user cùng edit 1 record → ai save sau ăn ai? Có warning conflict không?
- [ ] 2 tab của CÙNG user cùng edit 1 record → tab nào "thắng"? Reload có báo stale không?
- [ ] Đăng ký / mua hàng cùng lúc với số lượng còn cuối cùng (last item) → oversell không?
- [ ] Double-click nút payment → charge 2 lần không? (idempotency key)
- [ ] Race giữa upload file + xoá parent record đang chứa file đó
- [ ] Approve + Reject đồng thời (2 admin) cùng 1 request

## 3. Time / timezone / clock
- [ ] Data tạo lúc 23:xx ngày X → hiển thị đúng ngày X (không lệch sang X+1) ở mọi timezone
- [ ] Filter theo ngày quanh 0h / cuối tháng / cuối năm / 29/2 năm không nhuận
- [ ] DST: test data quanh 2h sáng ngày đổi giờ (mất 1h hoặc thừa 1h)
- [ ] Client clock lệch server clock 30 phút → token/session có bị coi là expired sai không?
- [ ] Leap second, năm nhuận, timezone lệch nửa múi (India +05:30, Nepal +05:45)

## 4. Browser edge
- [ ] Bấm Back sau khi submit form → form còn data cũ? Resubmit được không? Có warning "form đã nộp"?
- [ ] Refresh (F5) giữa multi-step wizard → step nào bị reset? Data điền dở còn không?
- [ ] Đóng tab giữa upload / long process → server còn dọn không? Data mồ côi?
- [ ] Mở app trong Incognito / Private mode → cookie/storage restricted có work không?
- [ ] Disable cookie hoàn toàn → app hiện thông báo rõ hay lặng lẽ vỡ?
- [ ] localStorage full (quota exceeded) → app crash hay handle được?
- [ ] Copy URL đang login gửi cho người khác → họ vào có bypass auth không?

## 5. Mobile-specific (nếu có app / responsive web)
- [ ] Xoay ngang màn giữa nhập form → data còn không, layout không vỡ
- [ ] Chuyển app sang background 10 phút → back lại: session còn, data còn?
- [ ] Nhận notification / cuộc gọi giữa lúc thao tác → về app: trạng thái đúng?
- [ ] Bàn phím Vietnamese Telex / GBoard / iOS Bàn phím: composing char có gây lỗi validate on-change không?
- [ ] Pinch zoom, viewport meta đúng chưa
- [ ] Chế độ tiết kiệm pin làm chậm animation / timer → có logic phụ thuộc timer bị lệch?

## 6. Session / state mid-flow
- [ ] Session hết hạn GIỮA multi-step form → redirect login rồi có quay lại được step đang dở?
- [ ] Đổi quyền user (dev thao tác backend) GIỮA lúc user đang thao tác → next request trả 403 xử lý sao?
- [ ] Feature flag OFF giữa lúc user đang trong luồng feature đó → gãy giữa chừng thế nào?
- [ ] Đổi locale/currency ở giữa flow checkout → giá đã chọn có bị recalculate sai không?

## 7. Data volume / boundary
- [ ] Empty state (0 item) → hiện gì? Có nút call-to-action tạo mới không?
- [ ] Chính xác 1 item → grammar số ít/số nhiều đúng chưa ("1 kết quả" vs "1 kết quảS")
- [ ] Max item (theo giới hạn hệ thống) → hiển thị + performance OK?
- [ ] Vượt max: cố tạo item thứ (max+1) → có bị chặn tử tế không?
- [ ] Pagination: trang 1, trang cuối, trang quá cuối (`?page=99999`), trang có 0 item sau xoá
- [ ] Số tiền: 0đ, âm, thập phân (0.001), số cực lớn (10^15) → tính toán đúng, hiển thị format đúng

## 8. Locale / i18n / character encoding
- [ ] Chuyển ngôn ngữ giữa flow → không lẫn ngôn ngữ, không lỗi thiếu key
- [ ] RTL (Arabic, Hebrew) — nếu có support: layout không lộn ngược logic (icon Back sang phải?)
- [ ] Currency format: dấu phẩy vs chấm decimal khác locale (1,234.56 vs 1.234,56)
- [ ] Nhập tiếng Việt có dấu qua Telex → composing bị submit sớm không?
- [ ] Copy paste chuỗi có ký tự vô hình (zero-width space, BOM) → hệ thống trim / báo lỗi không?

## 9. Cache / stale data
- [ ] Update record ở màn A → về màn list ở màn B: thấy giá trị mới hay cũ?
- [ ] Sau logout, bấm Back → cached page còn hiện data cũ không? (S2 — bảo mật, nếu là data nhạy cảm)
- [ ] CDN cache: user mới deploy version mới nhưng bị hit cache cũ → phiên bản asset có versioning không?
- [ ] Service worker (PWA) giữ bản cũ sau khi user "cập nhật" — có invalidate đúng không?

## 10. Recovery / graceful degradation
- [ ] App restart giữa long-running task (import, export) → task bị mất hay resume được?
- [ ] Storage service (S3, GCS) chết → upload thất bại nhưng UI hiện success? (state không sync)
- [ ] Rollback deploy version → user đang có session ở version cũ bấm action mới → API mismatch có handle không?
