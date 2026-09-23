# Target `mobile` — mobile-mcp trên simulator/emulator

## Chạy bằng gì
mobile-mcp (`@mobilenext/mobile-mcp`, tool `mobile_*`) điều khiển iOS Simulator / Android Emulator qua cây
accessibility. **Không có isolation**: một thiết bị dùng chung → các vai chạy **tuần tự**.

Trước khi gọi tool:
1. **Đúng một thiết bị đang bật**: `xcrun simctl list devices booted` · `adb devices`.
2. **App cài từ bản build được giao** (đường dẫn + version ở `QA.md §Target`). QA không tự build từ code
   sản phẩm trừ khi người dùng nhờ — build sai bản là kiểm nhầm. Cài: `mobile_install_app`, hoặc
   `xcrun simctl install booted <App>.app` (iOS simulator) / `adb install -r <app>.apk` (Android). Kiểm version:
   `mobile_list_apps`; Android `adb shell dumpsys package <pkg> | grep versionName`; iOS
   `xcrun simctl appinfo booted <bundle-id>`. Không có bản build → BLOCKED + hỏi.
3. `mobile_list_apps` thấy bundle id / package name.
4. Build trỏ đúng môi trường test (xem màn cấu hình/network) — sai → toàn bộ TC mobile `BLOCKED`.

Không thấy tool `mobile_*` → server mobile có thể đang tắt ở mức máy; xem CLAUDE.md toàn cục của máy
(vd phải mở phiên bằng lệnh riêng) — không tự sửa cấu hình toàn cục.

## Tool hay dùng
`mobile_launch_app` / `mobile_terminate_app` (vào từ màn đầu) · `mobile_list_elements_on_screen` (nhìn màn, gọi
lại trước mỗi lần chạm) · `mobile_click_on_screen_at_coordinates` · `mobile_type_keys` · `mobile_swipe_on_screen` ·
`mobile_take_screenshot` · `mobile_save_screenshot` (**`saveTo` tuyệt đối trong `qa/evidence/<run>/<TC>/`**) ·
`mobile_list_crashes` / `mobile_get_crash` · `mobile_set_orientation` · `mobile_press_button` · `mobile_open_url` (deep link) ·
`mobile_start_screen_recording` (**phải khai `output` trong `qa/evidence/`**, không khai là rơi ra thư mục tạm).

## Công thức
- **Biên / khôi phục**: HOME giữa luồng rồi quay lại · terminate giữa form rồi mở lại · mất mạng (Android
  `adb shell 'svc wifi disable; svc data disable'`, bật lại bằng `enable`; iOS simulator dùng mạng của máy host — không
  được tắt mạng máy dùng chung → TC mất mạng trên iOS `BLOCKED` hoặc hỏi người dùng cách làm) · cuối mỗi kịch bản `mobile_list_crashes`.
- **Double-submit**: `mobile_double_tap_on_screen` nút gửi. **Deep link** nhảy giữa luồng / vào màn vai bị cấm.
- **Phân quyền**: tuần tự trên một máy — A tạo, đăng xuất, B mở bản ghi của A qua deep link/API.
- **Màn nhỏ / xoay / bàn phím**: thiết bị nhỏ nhất trong dải hỗ trợ, landscape giữa form, ô nhập cuối màn bị bàn phím che?
- **Hình thức**: frame từ `list_elements` (vùng chạm đo được từ frame, so ngưỡng người dùng/tài liệu chốt — tham khảo WCAG 2.2 AA 24×24 CSS px, Apple HIG 44pt, Material 48dp) + screenshot đối chiếu token.
- **Hiệu năng**: bấm giờ launch → màn đầu tương tác được, n ≤ 10.
- **Gián đoạn**: cuộc gọi/thông báo đến (Android emulator `adb emu gsm call 0123456789`, kết thúc `adb emu gsm cancel 0123456789`), quyền bị từ chối, pin yếu, chế độ tối, cỡ chữ lớn.

## Bằng chứng tối thiểu
Screenshot + bundle id + trích `list_elements` · crash: nguyên văn `mobile_get_crash` · video không commit (ghi đường dẫn vào `ghi-chu.md`).
