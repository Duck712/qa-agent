# Target `desktop` — Electron và app native

## Chạy bằng gì
| App | Công cụ | Ghi chú |
|---|---|---|
| **Electron** | Playwright `_electron` qua script Node trong `qa/automation/` | Điều khiển như web: selector, computed style, console |
| **Native macOS** | AppleScript / System Events (`osascript`) + `screencapture` | Cần cấp quyền Accessibility + Screen Recording cho Terminal — không có quyền thì BLOCKED, báo người dùng tự cấp |
| **Native Windows** | `pywinauto` / WinAppDriver (chạy trên máy Windows) | Máy macOS không kiểm được → BLOCKED |
| **Linux GUI** | `xdotool` + `xwd`/`import`, hoặc `dogtail` (AT-SPI) | Cần X/Wayland session |
| **Web bọc (Tauri, CEF)** | Nếu bật được remote debugging → Playwright `connectOverCDP` | Không bật được → như native |

App cài từ **bản build được giao** (đường dẫn + version ở `QA.md §Target`). Công cụ chưa có (Playwright trong
`qa/automation/`, xdotool, pywinauto…) hoặc chưa được cấp quyền Accessibility/Screen Recording → BLOCKED + báo người
dùng, không tự cài hay tự cấp quyền.

**Electron — script mẫu** (`qa/automation/desktop-smoke.mjs`). Cần Playwright trong `qa/automation/`
— chưa có → `BLOCKED`, đề xuất lệnh `cd qa/automation && npm init -y && npm i -D playwright@<version>` và hỏi; người
dùng đồng ý (DECISIONS) mới cài — rồi chạy
`APP_PATH=<binary của app> EVIDENCE=qa/evidence/<run>/<TC> node qa/automation/desktop-smoke.mjs`
— trên macOS `APP_PATH` là binary bên trong bundle, vd `/Applications/TenApp.app/Contents/MacOS/TenApp`, không phải `TenApp.app`
(`npm exec -p` không làm `import 'playwright'` trong script tìm thấy gói):
```js
import { _electron as electron } from 'playwright';
const out = process.env.EVIDENCE;                    // qa/evidence/<run>/<TC>
const app = await electron.launch({ executablePath: process.env.APP_PATH });
const win = await app.firstWindow();
await win.screenshot({ path: `${out}/01-mo-app.png` });
console.log('title:', await win.title());
await app.close();
```
**Native macOS — thao tác + chụp**:
```bash
osascript -e 'tell application "TenApp" to activate' \
          -e 'tell application "System Events" to tell process "TenApp" to click button "Lưu" of window 1'
R=$(osascript -e 'tell application "System Events" to tell process "TenApp" to get {position, size} of window 1' | tr -d ' ')
screencapture -x -R"$R" "$D/02-sau-luu.png"          # R = x,y,w,h của cửa sổ; -l cần CGWindowID nên không dùng
osascript -e 'tell application "System Events" to tell process "TenApp" to get entire contents of window 1' > "$D/02-ui-tree.txt"
```

## Công thức riêng desktop
Cài/gỡ/cập nhật (bản cũ → mới giữ dữ liệu?) · mở nhiều cửa sổ/instance · kéo thả file · menu và phím tắt ·
đổi kích thước cửa sổ/màn hình phụ/HiDPI · chế độ tối · offline · file lớn / đường dẫn có dấu cách và unicode ·
quyền hệ điều hành bị từ chối (file, camera, thông báo) · thoát giữa lúc đang lưu rồi mở lại · crash log
(macOS `~/Library/Logs/DiagnosticReports/`, Windows Event Viewer).

## Bằng chứng tối thiểu
Screenshot cửa sổ + cây UI (hoặc selector Electron) + version app đang chạy · crash: file log nguyên văn.
Chạy **tuần tự** — một màn hình, một con trỏ.
