---
name: spec-mobile
description: >
  Điều khiển app mobile thật trên iOS Simulator / Android Emulator để kiểm thử sản phẩm — mở app, chạm, gõ,
  vuốt, xoay, chụp màn hình, đọc cây accessibility và crash log. App cài từ BẢN BUILD BÀN GIAO kèm manifest
  (SPEC không build code). Chạy bằng mobile-mcp (@mobilenext/mobile-mcp), khai sẵn trong template. Nạp skill
  này khi kiểm một experience mobile ở /spec-execute hoặc dry-run /spec-prepare, hoặc khi đóng vai
  spec-tester-mobile. Gồm: điều kiện tiên quyết, ràng buộc thiết-bị-dùng-chung (chạy TUẦN TỰ), công thức
  theo loại test, chuẩn bằng chứng, ranh giới an toàn. Web thì dùng spec-browse.
---

# spec-mobile — kiểm thử app mobile thật

> Với experience mobile, "kiểm" nghĩa là mở app thật trên thiết bị (giả lập), chạm, nhìn màn hình.
> Đọc code React Native/Flutter rồi suy ra **không tính** — y như web không được đọc code thay cho bấm.

## 1. Chạy bằng gì + điều kiện tiên quyết

mobile-mcp (`@mobilenext/mobile-mcp`) — điều khiển iOS Simulator / Android Emulator qua **cây accessibility**, rơi về screenshot khi cần. Khai ở `.mcp.json` (phiên chính) và inline trong frontmatter mỗi `spec-tester-*`.

**Khác biệt SỐNG CÒN so với `spec-browse`: KHÔNG có `--isolated`.** Simulator/emulator là **một thiết bị dùng chung** — hai vai cùng chạm một màn là giẫm nhau theo nghĩa đen. Vì vậy các vai chạm mobile trong một đợt chạy **TUẦN TỰ** (vẫn chia đợt, vẫn reset giữa đợt như `/spec-execute`).

Trước khi gọi tool:

1. **Đúng MỘT thiết bị đang bật** — iOS: `xcrun simctl list devices booted` · Android: `adb devices`. Nhiều thiết bị → server không biết chọn cái nào, tắt bớt.
2. **App đã cài từ BẢN BUILD BÀN GIAO** — `make devices` boot thiết bị + cài build lấy ở manifest (`Bản build mobile:` + checksum). **SPEC không build code sản phẩm**; build không có/checksum lệch → BLOCKED + báo QC, không tự build.
3. **Bundle id / package name** từ `ENVIRONMENT.md §6` (nguồn: mirror — tài liệu techstack/deploy của dev, hoặc manifest). `mobile_list_apps` phải thấy nó — không thấy nghĩa là `make devices` chưa tròn.
4. **Build phải trỏ đúng môi trường test** (manifest `Môi trường:`) — xem network log/màn hình cấu hình; trỏ môi trường khác/localhost thì toàn bộ TC mobile BLOCKED + bug bàn giao (kiểm nhầm môi trường còn tệ hơn không kiểm).

iOS cần Xcode, Android cần SDK + platform-tools. Bản `.app` cho simulator phải do dev build đúng kiến trúc simulator; TestFlight/store chỉ chạy trên **thiết bị thật**.

## 2. Tool hay dùng

| Tool | Việc |
|---|---|
| `mobile_launch_app` | Mở app theo bundle id. **Vào từ màn đầu**: `mobile_terminate_app` rồi mở lại, đừng tiếp trạng thái dở của vai trước |
| `mobile_list_elements_on_screen` | "Nhìn màn hình" — toạ độ, nhãn, thuộc tính. Gọi sau mỗi thao tác |
| `mobile_click_on_screen_at_coordinates` · `mobile_type_keys` · `mobile_swipe_on_screen` | Chạm, gõ, vuốt |
| `mobile_take_screenshot` | **Bằng chứng** — và là cách duy nhất bắt lỗi thị giác (accessibility tree không có màu) |
| `mobile_list_crashes` · `mobile_get_crash` | Crash report — chạy sau mỗi kịch bản gián đoạn |

> **Đường dẫn phải trỏ vào `evidence/`.** mobile-mcp không có `--output-dir` như Playwright: `mobile_save_screenshot` **bắt buộc** khai `saveTo`, còn `mobile_start_screen_recording` không khai `output` thì ghi vào **thư mục tạm của hệ điều hành** — ngoài repo, không ai dọn. Hook `guard_evidence` chặn cả hai ca. Viết `evidence/_inbox/mobile/<tên>.png|mp4`.

Còn lại: `mobile_set_orientation` · `mobile_get_screen_size` · `mobile_press_button` (HOME/BACK) · `mobile_open_url` (deep link) · `mobile_double_tap_on_screen` · `mobile_long_press_on_screen_at_coordinates` · `mobile_start/stop_screen_recording` · `mobile_install_app` · `mobile_list_apps`.

## 3. Công thức theo loại test

**Chức năng / workflow**: đi luồng như người dùng; đổi vai = đăng xuất/đăng nhập **tuần tự** (không có hai profile song song như web).

**Biên** (`edge`): mở app trên tenant B0 (màn rỗng hiện gì) · `mobile_press_button HOME` giữa luồng rồi quay lại · `mobile_terminate_app` giữa form rồi mở lại (dữ liệu dở ra sao) · mất mạng: iOS Simulator dùng mạng host nên **dừng backend** hoặc Android `adb shell svc wifi disable` + `svc data disable`. Kết mỗi kịch bản: `mobile_list_crashes`.

**Người vội / double-submit** (`breaker`): `mobile_double_tap_on_screen` vào nút gửi — bản ghi có nhân đôi không; `mobile_open_url` deep link nhảy giữa luồng.

**Phân quyền** (`authz`): tuần tự trên một thiết bị — đăng nhập A tạo bản ghi (prefix!), đăng xuất, đăng nhập B, thử mở bản ghi của A qua deep link/danh sách. Deep link tới màn của vai bị cấm — chặn ở **server** hay chỉ giấu nút?

**Màn hình nhỏ** (`mobile`): chọn thiết bị nhỏ nhất trong dải hỗ trợ · `mobile_set_orientation landscape` giữa form · chạm ô nhập cuối màn (bàn phím che nút gửi không, có tự cuộn không) · vuốt tới cuối danh sách dài.

**Hình thức** (`visual`): native **không có `getComputedStyle`** — thước đo đổi, tinh thần không đổi:
- **Kích thước/vị trí**: frame từ `mobile_list_elements_on_screen` — nút dưới 44×44 là số đo được, trích thẳng vào báo cáo.
- **Màu/chữ**: bắt buộc `mobile_take_screenshot` từng màn, đối chiếu **có kỷ luật** với lát token — nêu đích danh *phần tử + màn + khác gì bảng token* ("nút chính màn Đặt lịch nền nhạt hơn `--color-primary`, ảnh kèm").
- Ép trạng thái: chạm gửi rồi chụp ngay (bắt "đang gửi"), dừng backend (khuôn lỗi), B0 (khuôn rỗng).

**Hiệu năng** (`perf`): bấm giờ launch → màn đầu tương tác được, lặp n ≤ 10, giãn cách.

**Cross-target** (`cross`): mobile một phía + `spec-browse` phía web, chạy tuần tự; bằng chứng cả hai phía.

## 4. Chứng minh đã kiểm thật

```
mobile_list_elements_on_screen  → trích nhãn/phần tử + toạ độ đã thấy
mobile_take_screenshot          → ảnh chỗ hỏng (kèm bundle id đang chạy)
mobile_list_crashes             → crash report; mobile_get_crash lấy nguyên văn
mobile_start/stop_screen_recording → video cho luồng khó tả (KHÔNG commit video — .gitignore chặn)
```

Báo "không thấy vấn đề gì" mà không kèm được thao tác + ảnh/frame → chưa dùng thật, sẽ bị cho chạy lại.

## 5. Ranh giới

- Chỉ thao tác trên **app của sản phẩm này**, bằng tài khoản test, dữ liệu prefix (`context/shared/SAFETY.md`).
- **Các vai chạy TUẦN TỰ** — thiết bị là tài nguyên dùng chung.
- **Ảnh/video luôn ghi vào `evidence/`** — `saveTo`/`output` trỏ ra ngoài repo (hoặc bỏ trống `output`) bị `guard_evidence` chặn; ảnh màn hình môi trường thật mang dữ liệu thật.
- Không sửa file dự án — `spec-tester-*` bị chặn `Write`/`Edit`; phát hiện thì **báo**.
- Web experience → skill `spec-browse`, không dùng skill này.
- Không tự build app từ repo nguồn (vi phạm luật #4 read-only + kiểm sai bản đã bàn giao) — build đến từ manifest.

## 6. Hỏng thì xem đây

| Triệu chứng | Nguyên nhân |
|---|---|
| Không thấy thiết bị nào | Chưa boot: `xcrun simctl boot "<tên máy>"` / mở AVD hoặc `emulator -avd <tên>` |
| Thấy nhiều thiết bị, tool chọn sai | Tắt bớt — chỉ để đúng một thiết bị bật khi kiểm thử |
| `mobile_launch_app` không thấy app | Chưa cài build → `make devices`; bundle id sai → tra `mobile_list_apps` |
| Android không kết nối | `adb` không có trong PATH / `ANDROID_HOME` chưa đặt |
| Chạm không ăn | Toạ độ từ snapshot cũ — gọi lại `mobile_list_elements_on_screen` ngay trước khi chạm |
| App trỏ sai môi trường | Build bàn giao sai — BLOCKED toàn bộ TC mobile + bug, không "tạm chấp nhận" |
