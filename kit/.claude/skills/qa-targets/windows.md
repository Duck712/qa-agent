# Windows — công thức PowerShell cho mọi target

Máy chạy QA là Windows (tool `PowerShell`, Windows PowerShell 5.1) → dùng các khối dưới thay cho khối Bash trong
`cli.md`, `api.md`, `batch.md`, `desktop.md`. Công thức (kiểm gì) giữ nguyên — chỉ đổi cách chạy và thu bằng chứng.
Mỗi khối là **một** lệnh PowerShell: biến không giữ giữa các lần gọi.

## 1. Bẫy của PowerShell 5.1 (đọc trước)
| Bẫy | Hậu quả | Làm thế này |
|---|---|---|
| `>` / `*>` / `Out-File` mặc định | file UTF-16 — diff/grep đọc sai | `Set-Content -Encoding utf8` (có BOM) · cần không BOM (body JSON gửi đi): `[IO.File]::WriteAllText("$PWD\<đường dẫn>", $s)` |
| `2>&1` với exe ngoài | stderr bị bọc thành ErrorRecord, `$?` sai | tách stdout/stderr bằng `Start-Process -Redirect…` (§2) |
| `curl` | là alias của `Invoke-WebRequest` | gọi `curl.exe` (có sẵn từ Windows 10 1803) |
| Chuỗi JSON truyền thẳng cho exe ngoài | dấu `"` bị nuốt | ghi body ra file rồi `--data-binary "@<file>"` (§3) |
| `[IO.File]::…` với đường dẫn tương đối | tính theo thư mục của tiến trình, không theo `Set-Location` | luôn ghép `"$PWD\…"` |
| File `.ps1` có chữ có dấu | 5.1 đọc file không BOM theo bảng mã ANSI → hỏng chữ | lưu `.ps1` UTF-8 **có BOM** |
| Gõ phím (`SendKeys`) | đi qua bộ gõ đang bật (Telex/VNI, IME Nhật…) → "test" thành "tét" | nhập chữ bằng UI Automation `ValuePattern` hoặc dán qua clipboard (§5) |

## 2. CLI / batch — chạy lệnh, thu stdout · stderr · exit
```powershell
$RUN='<run-id>'; $TC='<TC-ID>'; $D="qa/evidence/$RUN/$TC"; $S="qa/sandbox/$RUN/$TC"
New-Item -ItemType Directory -Force $D, $S | Out-Null
'$ tool convert in.csv --out out.json' | Set-Content -Encoding utf8 "$D/01-command.txt"
$sw = [Diagnostics.Stopwatch]::StartNew()
$p = Start-Process -FilePath tool.exe -ArgumentList 'convert','in.csv','--out','out.json' -WorkingDirectory $S `
     -NoNewWindow -Wait -PassThru -RedirectStandardOutput "$D/01-stdout.txt" -RedirectStandardError "$D/01-stderr.txt"
"exit=$($p.ExitCode) · $($sw.ElapsedMilliseconds) ms" | Set-Content -Encoding utf8 "$D/01-exit.txt"
```
`-ArgumentList` ghép bằng dấu cách, **không** tự thêm nháy: tham số có dấu cách viết `'"C:\thu muc\a.csv"'`.
Lệnh `.cmd`/`.bat` → `-FilePath cmd.exe -ArgumentList '/c','tool.cmd',…`.
- **Checksum**: `(Get-FileHash -Algorithm SHA256 <file>).Hash` (thay `sha256sum`/`shasum`).
- **Thời gian**: `[Diagnostics.Stopwatch]` như trên, hoặc `(Measure-Command { … }).TotalMilliseconds` (thay `/usr/bin/time`).
- **Diff với expected**: `Compare-Object (Get-Content $D/out.csv) (Get-Content qa/testdata/$TC/expected/out.csv)` — rỗng là khớp;
  so cả byte: so `Get-FileHash` hai file. `fc.exe /b a b` cho file nhị phân.
- **Ngắt giữa chừng**: Ctrl-C/Ctrl-Break **không** gửi được ổn định từ phiên agent (không có console) — chỉ ngắt cứng được:
  `python -c "import subprocess,time,sys; p=subprocess.Popen(sys.argv[1:]); time.sleep(2); p.kill(); print('exit', p.wait())" tool.exe convert big.csv`
  Ngắt cứng ≈ mất điện/kill, **không** phải Ctrl-C — ghi rõ trong bằng chứng. TC cần đúng Ctrl-C → `Thực hiện: người` (người bấm tay,
  skill `qa` §7), hoặc `BLOCKED`.
- **Lịch chạy** (Task Scheduler): xem `Get-ScheduledTask -TaskName <tên> | Get-ScheduledTaskInfo` (chỉ đọc). Không tự tạo/sửa
  task dùng chung — kích job bằng đường chính thức như `batch.md`.

## 3. API — `curl.exe`, bí mật từ `qa/.env`
```powershell
$RUN='<run-id>'; $TC='<TC-ID>'; $D="qa/evidence/$RUN/$TC"; New-Item -ItemType Directory -Force $D | Out-Null
foreach ($l in Get-Content qa/.env) { if ($l -match '^\s*([A-Za-z_]\w*)\s*=\s*(.*)$') { Set-Item "env:$($Matches[1])" ($Matches[2].Trim().Trim('"',"'")) } }
$BODY = '{"name":"QA-' + $RUN + '-o1"}'
[IO.File]::WriteAllText("$PWD\$D\01-request-body.json", $BODY)
"POST $env:BASE/api/orders (token vai B)" | Set-Content -Encoding utf8 "$D/01-request.txt"
curl.exe -sS -X POST "$env:BASE/api/orders" -H "Authorization: Bearer $env:TOKEN_B" -H "Content-Type: application/json" `
  --data-binary "@$D/01-request-body.json" -o "$D/01-response.json" -D "$D/01-headers.txt" `
  -w "HTTP %{http_code} - %{time_total}s" | Set-Content -Encoding utf8 "$D/01-status.txt"
```
Không in biến bí mật ra màn hình; che token trong file bằng chứng. Song song (idempotency/race): `Start-Job` hoặc hai tiến trình
`Start-Process curl.exe …` rồi `Wait-Process` — số lượng theo nhịp `SKILL.md` §3 mục 4.

## 4. Desktop native Windows (WinForms, WPF, Win32, UWP/WinUI) — UI Automation có sẵn, không cần cài
```powershell
$RUN='<run-id>'; $TC='<TC-ID>'; $D="$PWD\qa\evidence\$RUN\$TC"; New-Item -ItemType Directory -Force $D | Out-Null
Add-Type -Name Dpi -Namespace W -MemberDefinition '[DllImport("user32.dll")] public static extern bool SetProcessDPIAware();'
[W.Dpi]::SetProcessDPIAware() | Out-Null          # phải gọi TRƯỚC khi chụp: màn hình 125%/150% mới ra đúng toạ độ
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes, System.Drawing, System.Windows.Forms
$A = [Windows.Automation.AutomationElement]; $T = [Windows.Automation.TreeScope]
function By($prop, $val) { New-Object Windows.Automation.PropertyCondition($A::$prop, $val) }
$p = Get-Process -Name <TenApp> | Where-Object MainWindowHandle -ne 0 | Select-Object -First 1
$win = $A::FromHandle($p.MainWindowHandle)
# bấm nút theo tên hiển thị (hoặc By 'AutomationIdProperty' '<id>' — WinForms: id = Name của control)
$win.FindFirst($T::Descendants, (By 'NameProperty' '<Lưu>')).GetCurrentPattern([Windows.Automation.InvokePattern]::Pattern).Invoke()
# nhập chữ: ValuePattern; control không hỗ trợ → dán qua clipboard (không gõ phím — bộ gõ làm sai chữ)
$box = $win.FindFirst($T::Descendants, (By 'AutomationIdProperty' '<txtTen>'))
try { $box.GetCurrentPattern([Windows.Automation.ValuePattern]::Pattern).SetValue("QA-$RUN-ten") }
catch { $box.SetFocus(); Set-Clipboard -Value "QA-$RUN-ten"; [Windows.Forms.SendKeys]::SendWait('^v') }
Start-Sleep -Milliseconds 300
# chụp cửa sổ + cây UI
$r = $win.Current.BoundingRectangle; $bmp = New-Object Drawing.Bitmap ([int]$r.Width), ([int]$r.Height)
$g = [Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen([int]$r.X, [int]$r.Y, 0, 0, $bmp.Size)
$bmp.Save("$D\02-sau-luu.png", [Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose()
$win.FindAll($T::Descendants, [Windows.Automation.Condition]::TrueCondition) |
  ForEach-Object { '{0} | {1} | {2}' -f $_.Current.ControlType.ProgrammaticName, $_.Current.Name, $_.Current.AutomationId } |
  Set-Content -Encoding utf8 "$D\02-ui-tree.txt"
```
- Đọc giá trị để so kỳ vọng: `$el.Current.Name`, hoặc `ValuePattern` → `.Current.Value`; bảng/lưới: `GridPattern`/`TablePattern`
  (không đọc được → ảnh + ghi chú, và nêu giới hạn).
- **Phiên bản app**: `(Get-Item '<đường dẫn exe>').VersionInfo | Select-Object FileVersion, ProductVersion`.
- **Crash**: ghi `$t0 = Get-Date` trước TC, sau đó
  `Get-WinEvent -FilterHashtable @{LogName='Application'; Id=1000,1026; StartTime=$t0} | Format-List TimeCreated, Id, Message`
  (1000 Application Error, 1026 .NET Runtime) → lưu nguyên văn.
- **Giới hạn**: app cũ (VB6, Delphi, control tự vẽ, game) có thể không lộ phần tử qua UI Automation — cây UI trống/chỉ thấy cửa
  sổ → không bấm theo toạ độ đoán mò; báo người dùng, TC đó `BLOCKED` hoặc chuyển thủ công. Hộp thoại hệ thống (UAC) không
  điều khiển được. Chạy **tuần tự**, không đụng chuột/bàn phím của người dùng khi đang chạy (báo trước).
- Electron/WebView2 bật được remote debugging → điều khiển như web (`desktop.md`), chính xác hơn UI Automation.

## 5. Tóm tắt thay thế
| macOS / Linux | Windows |
|---|---|
| `mkdir -p` | `New-Item -ItemType Directory -Force` |
| `cmd > out 2> err; echo $?` | `Start-Process … -RedirectStandardOutput/-Error -PassThru` → `.ExitCode` |
| `sha256sum` / `shasum -a 256` | `Get-FileHash -Algorithm SHA256` |
| `/usr/bin/time` | `[Diagnostics.Stopwatch]` / `Measure-Command` |
| `diff` | `Compare-Object` · `fc.exe` |
| `curl` | `curl.exe` |
| `set -a; . qa/.env; set +a` | vòng `foreach … Set-Item env:` (§3) |
| `kill -INT` (Ctrl-C) | không ổn định từ agent — `p.kill()` = ngắt cứng (§2) |
| `osascript` + `screencapture` | UI Automation + `CopyFromScreen` (§4) |
| `cat > f <<'EOF'` | here-string `@'` … `'@` → `Set-Content -Encoding utf8` |
