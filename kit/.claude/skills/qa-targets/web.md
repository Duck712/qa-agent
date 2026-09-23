# Target `web` — Playwright MCP

## Chạy bằng gì
Playwright MCP (`@playwright/mcp`, tool `browser_*`). Cài sẵn hai nơi:
- `.mcp.json` của dự án — cho phiên chính.
- Frontmatter agent `qa-tester` / `qa-security` — mỗi agent một trình duyệt `--isolated`, chạy song song không giẫm nhau.

Server trong agent tên riêng (`browser-tester`, `browser-security` → tool `mcp__browser-tester__browser_…`), phiên chính
dùng `browser`. **Luôn khai `filename` là đường dẫn tuyệt đối** trong `qa/evidence/<run-id>/<TC-ID>/` cho
`browser_take_screenshot`, `browser_snapshot`, `browser_evaluate`. Tên tương đối/tên trần được Playwright tính từ **gốc
dự án** (không phải `--output-dir`) — hook `guard_evidence` chặn. Bỏ `filename` thì file rơi vào `--output-dir`
(`qa/evidence/_inbox/<vai>/`) — chỉ dùng khi làm một mình, không có tester song song.

## Tool hay dùng
| Tool | Việc |
|---|---|
| `browser_navigate` | Mở URL — vào từ trang đầu, không nhảy URL trong (trừ TC phân quyền) |
| `browser_snapshot` | Nhìn màn hình (cây accessibility, có ref để bấm) — gọi sau mỗi thao tác; bước then chốt thêm `filename` tuyệt đối `…/NN-snapshot.md` để lưu cây (URL lưu riêng — xem dưới) |
| `browser_click` · `browser_type` · `browser_fill_form` · `browser_select_option` | Thao tác (tham số `target` = ref hoặc selector) |
| `browser_take_screenshot` | Bằng chứng — `filename` tuyệt đối `…/qa/evidence/<run>/<TC>/01-buoc1.png` |
| `browser_console_messages` · `browser_network_requests` | Lỗi JS, request/response thật |
| `browser_evaluate` | Đo computed style, performance timing, gọi fetch bằng token vai khác — `filename` tuyệt đối để lưu kết quả nguyên văn |
| `browser_run_code_unsafe` | Mô phỏng mạng, nhịp bấm, nhiều context |

Screenshot headless **không có thanh URL**, và file do `browser_snapshot` ghi ra (khi có `filename`) chỉ chứa cây
aria YAML — URL nằm trong **phản hồi** của tool, không nằm trong file. Bước then chốt lưu URL riêng: `browser_evaluate`
với `() => location.href` và `filename` tuyệt đối `…/NN-url.txt`, hoặc chép nguyên văn dòng `- Page URL: …` của phản hồi
vào `NN-url.txt` bằng Bash heredoc.

## Công thức
**Biên — mạng/API lỗi**
```js
await page.context().setOffline(true);                 // mất mạng
await page.route('**/api/**', r => r.abort());         // API hỏng
const c = await page.context().newCDPSession(page);    // mạng chậm
await c.send('Network.emulateNetworkConditions', { offline:false, latency:400, downloadThroughput:51200, uploadThroughput:51200 });
```
**Double-submit**: `await Promise.all([page.click('#submit'), page.click('#submit')])` → bản ghi có nhân đôi?
**Phá đầu vào**: chuỗi 10.000 ký tự, emoji, `<script>alert(1)</script>`, `'; --`, số âm → hiện ra như chữ? server trả mã gì? (mã/thông điệp đúng lấy từ tài liệu; không có → câu hỏi)
**Phân quyền**: vai A tạo bản ghi (prefix) → vai B thử mở/gọi bản ghi đó bằng `curl` với token/cookie của vai B, **hoặc**
trong **một** lời gọi `browser_run_code_unsafe`: tạo `ctxB`, đăng nhập vai B, `pB.goto`/`pB.request`, lưu
`pB.screenshot({path:'<tuyệt đối>/qa/evidence/<run>/<TC>/…'})` và response vào evidence, rồi `ctxB.close()`. Phải bị chặn
ở server (mã theo tài liệu API; không nói → hỏi; 403 vs 404 có lộ sự tồn tại không). **Không** dùng `browser_evaluate` +
`fetch` của trang vai A (mang phiên vai A → PASS giả). UI giấu nút không phải là chặn.
**Hình thức**: đo, đừng nhìn
```js
() => { const el = document.querySelector('button.primary'); const s = getComputedStyle(el);
        return ['color','background-color','font-size','font-family','padding','border-radius'].map(p => `${p}: ${s[p]} @ button.primary`); }
```
Tương phản: leo lên tổ tiên tìm nền đục rồi tính tỉ lệ. a11y: `browser_press_key Tab` xem focus thấy được, nút có tên, input có label.
**Hiệu năng**: `performance.getEntriesByType('navigation')[0]` → ttfb/DCL/load; lặp theo nhịp đã chốt (`qa-targets` §3 mục 4), báo median + max
kèm n. Ngưỡng do tài liệu/người dùng cho.
**Responsive**: `browser_resize` 375×812, 768×1024, 1440×900.
**Cross-target**: `browser_tabs` mở tab B; hành động ở A, snapshot + network ở B (chứng minh không phải cache).

## Bằng chứng tối thiểu
Ảnh bước then chốt + URL trang (`NN-url.txt`) · phân quyền/phá đầu vào: request + response nguyên văn · hình thức: giá trị computed style + selector · hiệu năng: từng lần đo + cách đo + giờ đo.

## Hỏng thì xem
| Triệu chứng | Nguyên nhân |
|---|---|
| Không thấy tool `browser_*` | Chưa duyệt MCP server của dự án — duyệt khi Claude Code hỏi, hoặc `/mcp` |
| Lần đầu rất lâu | Đang tải Chromium (`npx playwright install chromium`) |
| Ảnh không thấy trong `qa/evidence/_inbox` | `.mcp.json` còn đường dẫn tương đối — chạy lại `python3 <source>/install.py . --update` (`source` ghi trong `.claude/qa-agent.json`) |

## Nhiều vai cùng lúc
Mỗi trình duyệt `--isolated` là **một** browser context — các tab dùng chung cookie. Hai vai cùng lúc **không** dùng
`browser_tabs`. Dùng `browser_run_code_unsafe`:
```js
const ctxB = await page.context().browser().newContext();   // phiên riêng cho vai B
const pB = await ctxB.newPage(); await pB.goto(URL); /* đăng nhập vai B trong pB */
```
hoặc gọi `curl` với cookie/token của vai B (lấy từ `qa/.env`). Mọi thao tác **và bằng chứng** của vai B phải nằm trong
cùng một lời gọi `browser_run_code_unsafe` (biến `ctxB`/`pB` mất sau lời gọi; các tool `browser_*` khác chỉ thấy trang vai A). Site dùng cookie session thì `fetch` trong trang luôn
mang phiên hiện tại — không dùng nó để thử vai khác (PASS giả).
