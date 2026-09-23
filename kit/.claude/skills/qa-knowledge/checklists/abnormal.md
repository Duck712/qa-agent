# Checklist — Case bất thường / edge cross-cutting
> Áp dụng khi test luồng đi qua nhiều màn / nhiều component / phụ thuộc hạ tầng.
> Các case ở đây KHÔNG thuộc riêng form/auth/upload/api — mà là "cả hệ thống" phải chịu được.
> Không cover hết cho MỌI feature — chọn nhóm phù hợp với luồng đang test.

> **Mục checklist là câu hỏi để thử, không phải kỳ vọng.** Kỳ vọng lấy từ tài liệu; tài liệu không nói → điểm hỏi.
> Không chép từ như "tử tế / rõ ràng / OK" vào Kỳ vọng. Trích nguồn trong TC: `Nguồn: <checklist> <số mục>`, vd `form-input 2.3`.

## 1. Network & infrastructure failure
- [ ] 1.1 Mất mạng GIỮA request (đã gửi, chưa nhận response) → UI ở trạng thái gì? Retry được không? Có tạo dữ liệu ma không?
- [ ] 1.2 Mạng chậm (3G/simulated 500ms+ latency) → có chỉ báo đang tải trong suốt thời gian chờ không? Hết thời gian chờ thì hiện gì, có giữ dữ liệu đã nhập không?
- [ ] 1.3 Backend trả 5xx ngẫu nhiên (503/502/504) → UI hiện thông báo lỗi (theo tài liệu) hay lộ stack trace?
- [ ] 1.4 Dep service phụ thuộc chết (payment gateway, SMS, mail) → luồng chính có bị block cả không, có fallback không?
- [ ] 1.5 DNS lỗi / SSL cert lỗi → thông báo có rõ nguyên nhân không?

## 2. Concurrent user / race condition
- [ ] 2.1 2 user cùng edit 1 record → ai save sau ăn ai? Có warning conflict không?
- [ ] 2.2 2 tab của CÙNG user cùng edit 1 record → tab nào "thắng"? Reload có báo stale không?
- [ ] 2.3 Đăng ký / mua hàng cùng lúc với số lượng còn cuối cùng (last item) → oversell không?
- [ ] 2.4 Double-click nút payment → charge 2 lần không? (idempotency key)
- [ ] 2.5 Race giữa upload file + xoá parent record đang chứa file đó
- [ ] 2.6 Approve + Reject đồng thời (2 admin) cùng 1 request

## 3. Time / timezone / clock
- [ ] 3.1 Data tạo lúc 23:xx ngày X → hiển thị đúng ngày X (không lệch sang X+1) ở mọi timezone
- [ ] 3.2 Filter theo ngày quanh 0h / cuối tháng / cuối năm / 29/2 năm không nhuận
- [ ] 3.3 DST: test data quanh 2h sáng ngày đổi giờ (mất 1h hoặc thừa 1h)
- [ ] 3.4 Client clock lệch server clock 30 phút → token/session có bị coi là expired sai không?
- [ ] 3.5 Leap second, năm nhuận, timezone lệch nửa múi (India +05:30, Nepal +05:45)

## 4. Browser edge
- [ ] 4.1 Bấm Back sau khi submit form → form còn data cũ? Resubmit được không? Có warning "form đã nộp"?
- [ ] 4.2 Refresh (F5) giữa multi-step wizard → step nào bị reset? Data điền dở còn không?
- [ ] 4.3 Đóng tab giữa upload / long process → server còn dọn không? Data mồ côi?
- [ ] 4.4 Mở app trong Incognito / Private mode → cookie/storage restricted có work không?
- [ ] 4.5 Disable cookie hoàn toàn → app hiện thông báo rõ hay lặng lẽ vỡ?
- [ ] 4.6 localStorage full (quota exceeded) → app crash hay handle được?
- [ ] 4.7 Copy URL đang login gửi cho người khác → họ vào có bypass auth không?

## 5. Mobile-specific (nếu có app / responsive web)
- [ ] 5.1 Xoay ngang màn giữa nhập form → data còn không, layout không vỡ
- [ ] 5.2 Chuyển app sang background 10 phút → back lại: session còn, data còn?
- [ ] 5.3 Nhận notification / cuộc gọi giữa lúc thao tác → về app: trạng thái đúng?
- [ ] 5.4 Bàn phím Vietnamese Telex / GBoard / iOS Bàn phím: composing char có gây lỗi validate on-change không?
- [ ] 5.5 Pinch zoom, viewport meta đúng chưa
- [ ] 5.6 Chế độ tiết kiệm pin làm chậm animation / timer → có logic phụ thuộc timer bị lệch?

## 6. Session / state mid-flow
- [ ] 6.1 Session hết hạn GIỮA multi-step form → redirect login rồi có quay lại được step đang dở?
- [ ] 6.2 Đổi quyền user (dev thao tác backend) GIỮA lúc user đang thao tác → next request trả 403 xử lý sao?
- [ ] 6.3 Feature flag OFF giữa lúc user đang trong luồng feature đó → gãy giữa chừng thế nào?
- [ ] 6.4 Đổi locale/currency ở giữa flow checkout → giá đã chọn có bị recalculate sai không?

## 7. Data volume / boundary
- [ ] 7.1 Empty state (0 item) → hiện gì? Có nút call-to-action tạo mới không?
- [ ] 7.2 Chính xác 1 item → số ít/số nhiều đúng theo ngôn ngữ giao diện (en: "1 result" / "2 results"; tiếng Việt không đổi dạng nhưng kiểm lượng từ)
- [ ] 7.3 Max item (theo giới hạn hệ thống) → hiển thị không vỡ; thời gian phản hồi so với ngưỡng tài liệu (không có → hỏi)
- [ ] 7.4 Vượt max: cố tạo item thứ (max+1) → bị chặn, có thông báo chỉ ra giới hạn, không tạo dở
- [ ] 7.5 Pagination: trang 1, trang cuối, trang quá cuối (`?page=99999`), trang có 0 item sau xoá
- [ ] 7.6 Số tiền: 0đ, âm, thập phân (0.001), số cực lớn (10^15) → tính toán đúng, hiển thị format đúng

## 8. Locale / i18n / character encoding
- [ ] 8.1 Chuyển ngôn ngữ giữa flow → không lẫn ngôn ngữ, không lỗi thiếu key
- [ ] 8.2 RTL (Arabic, Hebrew) — nếu có support: layout không lộn ngược logic (icon Back sang phải?)
- [ ] 8.3 Currency format: dấu phẩy vs chấm decimal khác locale (1,234.56 vs 1.234,56)
- [ ] 8.4 Nhập tiếng Việt có dấu qua Telex → composing bị submit sớm không?
- [ ] 8.5 Copy paste chuỗi có ký tự vô hình (zero-width space, BOM) → hệ thống trim / báo lỗi không?

## 9. Cache / stale data
- [ ] 9.1 Update record ở màn A → về màn list ở màn B: thấy giá trị mới hay cũ?
- [ ] 9.2 Sau logout, bấm Back → cached page còn hiện data cũ không? (data nhạy cảm của người khác lộ ra = S1 theo thang BUGS.md)
- [ ] 9.3 CDN cache: user mới deploy version mới nhưng bị hit cache cũ → phiên bản asset có versioning không?
- [ ] 9.4 Service worker (PWA) giữ bản cũ sau khi user "cập nhật" — có invalidate đúng không?

## 10. Recovery / graceful degradation
- [ ] 10.1 App restart giữa long-running task (import, export) → task bị mất hay resume được?
- [ ] 10.2 Storage service (S3, GCS) chết → upload thất bại nhưng UI hiện success? (state không sync)
- [ ] 10.3 Rollback deploy version → user đang có session ở version cũ bấm action mới → API mismatch có handle không?
