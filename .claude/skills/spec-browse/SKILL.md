---
name: spec-browse
description: >
  Duyệt web thật để kiểm thử sản phẩm trên môi trường test (production cách ly hoặc staging, theo manifest) với tenant/tài khoản test — mở trang, bấm, gõ, chụp
  màn hình, đọc lỗi console và lời gọi mạng, đo computed style, mô phỏng mạng chậm/mất. Chạy bằng Playwright
  MCP (@playwright/mcp), khai sẵn trong template. Nạp skill này khi chạy /spec-execute hoặc dry-run của
  /spec-prepare, hoặc khi đóng vai tester (spec-tester-*). Gồm: cách gọi, tool hay dùng, công thức cho từng
  loại test, chuẩn bằng chứng, và ranh giới an toàn khi thao tác trên môi trường có người dùng/dữ liệu thật.
---

# spec-browse — duyệt web để kiểm thử thật

> Luật #5 nói **không tin lời tự test của dev**; luật #8 nói **PASS phải chứng minh được**. Skill này là
> công cụ để "kiểm" nghĩa là kiểm thật: mở trình duyệt, bấm, đo, chụp. Đọc code rồi suy ra **không tính**.
>
> Khác trình duyệt dev dùng khi làm ở local một điểm sống còn: môi trường test là **production có người dùng thật**
> hoặc **staging dùng chung** với đội khác. Mọi thao tác phải nằm trong tenant/tài khoản test và mang prefix — xem §5.

## 1. Chạy bằng gì

Playwright MCP (`@playwright/mcp`). Template khai sẵn hai nơi:

| Nơi khai | Dùng cho | Kiểu |
|---|---|---|
| `.mcp.json` gốc repo | Phiên chính (meta tự tay: dry-run pha P, đợt 0 pha E) | dùng chung cả phiên |
| `mcpServers` trong frontmatter mỗi `spec-tester-*` | Các agent tester | **inline `--isolated`** — mỗi agent một trình duyệt riêng, chạy song song không giẫm nhau |

Mỗi khai báo có `--output-dir evidence/_inbox/<vai>` — screenshot rơi thẳng vào inbox, phiên chính phân loại sang `evidence/r<N>/luot-<k>/<TC-ID>/`.

> **`--output-dir` là mặc định, KHÔNG phải hàng rào.** Tham số `filename` của `browser_take_screenshot` vẫn trỏ đi chỗ khác được, nên hook `guard_evidence` chặn mọi đường dẫn ra ngoài `evidence/` (tuyệt đối ngoài repo, hoặc tương đối có `..`). Cách dùng đúng: **bỏ hẳn `filename`** cho MCP tự đặt, hoặc khai tên tương đối trần (`01-buoc1.png`).

**Trình duyệt riêng ≠ dữ liệu riêng.** Tenant test dùng chung → `/spec-execute` chia đợt ≤3 vai + reset giữa đợt.

## 2. Tool hay dùng

| Tool | Việc |
|---|---|
| `browser_navigate` | Mở URL. **Vào từ trang đầu**, không nhảy thẳng URL trong (trừ TC phân quyền cố tình) |
| `browser_snapshot` | "Nhìn màn hình" — cây accessibility, có ref để bấm. Gọi sau mỗi thao tác |
| `browser_click` · `browser_type` · `browser_fill_form` | Bấm và gõ |
| `browser_take_screenshot` | **Bằng chứng** — ảnh + `browser_snapshot` (dòng `Page URL:`) chứng minh đúng môi trường test (screenshot headless không có thanh URL) |
| `browser_console_messages` · `browser_network_requests` | Lỗi thật, request thật — đừng đoán từ giao diện |
| `browser_evaluate` | Đo computed style, đọc performance timing |
| `browser_run_code_unsafe` | Mô phỏng mạng, nhịp bấm (xem §3) |

**Hai điều dễ vấp**: `browser_click`/`browser_type` nhận **`target`** (ref từ snapshot như `e4`, hoặc CSS selector) — không phải `ref`. `browser_navigate` không trả nội dung trang; đọc bằng `browser_snapshot`.

## 3. Công thức theo loại test

### Biên — mạng chậm / mất mạng / API lỗi (`spec-tester-edge`)
```js
await page.context().setOffline(true);                    // mất mạng
await page.route('**/api/**', r => r.abort());            // API hỏng
const c = await page.context().newCDPSession(page);       // mạng chậm
await c.send('Network.emulateNetworkConditions',
  { offline:false, latency:400, downloadThroughput:400*1024/8, uploadThroughput:400*1024/8 });
```
Rồi `browser_console_messages` + `browser_network_requests` xem lỗi thật.

### Phá đầu vào / double-submit (`spec-tester-breaker`)
```js
await Promise.all([ page.click('#submit'), page.click('#submit') ]);   // hai lần ~50ms
```
`browser_type` chuỗi 10.000 ký tự, emoji, `<script>alert(1)</script>`, `'; DROP TABLE x;--`, số âm. Sau mỗi lần: snapshot (hiện ra **như chữ thường**?) + console + network (server trả mã gì).

### Phân quyền A↛B (`spec-tester-authz`)
Đăng nhập A tạo bản ghi (prefix!), ghi id → đăng nhập B (trình duyệt/context riêng) → `browser_navigate` tới URL bản ghi của A → phải bị chặn. Gọi thẳng API bằng `browser_evaluate` + fetch với token của B để chứng minh **server** chặn, không phải UI giấu nút. **Chép response nguyên văn** vào bằng chứng.

### Hình thức — đo, đừng nhìn (`spec-tester-visual`)
```js
() => {
  const seen = new Map();
  for (const el of document.querySelectorAll('*')) {
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height) continue;
    const cs = getComputedStyle(el);
    const sel = el.tagName.toLowerCase()
      + (el.id ? '#' + el.id : '')
      + (el.className && typeof el.className === 'string'
         ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '');
    for (const p of ['color','background-color','border-color','font-family',
                     'font-size','padding','gap','border-radius','box-shadow']) {
      const v = cs.getPropertyValue(p);
      if (!v || v === 'none' || v === 'rgba(0, 0, 0, 0)' || v === '0px') continue;
      const k = p + '|' + v;
      if (!seen.has(k)) seen.set(k, sel);
    }
  }
  return [...seen].map(([k, sel]) => k + ' @ ' + sel).sort();
}
```
Tương phản — đọc cặp chữ/nền thật (leo lên tổ tiên tìm nền đục):
```js
() => {
  const el = document.querySelector('.canh-bao');
  let bg = 'rgba(0, 0, 0, 0)', n = el;
  while (n && bg === 'rgba(0, 0, 0, 0)') { bg = getComputedStyle(n).backgroundColor; n = n.parentElement; }
  return { fg: getComputedStyle(el).color, bg, size: getComputedStyle(el).fontSize };
}
```
a11y: `browser_press_key Tab` lần lượt xem focus có thấy được và tới đủ nút; kiểm nhãn qua snapshot (nút có tên, input có label).

### Hiệu năng — gọi thưa (`spec-tester-perf`)
```js
() => { const t = performance.getEntriesByType('navigation')[0];
        return { ttfb: t.responseStart, domContentLoaded: t.domContentLoadedEventEnd, load: t.loadEventEnd }; }
```
Luồng lõi: bấm giờ quanh thao tác, lặp n ≤ 10, **giãn cách ≥1s**. CẤM vòng lặp bắn liên tục.

### Cross-target (`spec-tester-cross`)
`browser_tabs` mở tab thứ hai cho experience B (hoặc trình duyệt riêng) — hành động ở A, snapshot + screenshot ở B, kèm `browser_network_requests` của B để chứng minh dữ liệu đến thật, không phải cache.

## 4. Chứng minh đã kiểm thật

```
browser_take_screenshot   → ảnh bước then chốt; kèm browser_snapshot → `Page URL:` đúng môi trường test
browser_snapshot          → trích đúng đoạn text/nhãn đã thấy
browser_console_messages  → lỗi JS nguyên văn
browser_network_requests  → request/response mã thật
browser_evaluate          → số đo (computed style, timing)
```

Chuẩn tối thiểu theo loại TC: `TEST-STRATEGY §9`. Thiếu → kết quả ghi `BLOCKED`, không phải `PASS`.

## 5. Ranh giới — môi trường có người/dữ liệu thật

- Chỉ thao tác trên **URL môi trường test khai trong manifest (`Điểm vào chính` + bảng URL theo target)** của chính sản phẩm này, bằng **tài khoản test** trong **tenant test**. Manifest ghi `staging` mà trang đang mở là production (hoặc ngược lại) → dừng, báo.
- **Không ghi/sửa/xoá bản ghi thiếu prefix `SPEC-r<N>-`** — kể cả để thử. Thấy dữ liệu người thật (lỗ cách ly) → chụp bằng chứng, dừng tay, báo S1.
- **Không bắn notification/email/SMS tới người thật** — địa chỉ nhận phải thuộc SPEC; không có hộp test → TC `BLOCKED`.
- **Không stress/load**: n ≤ 20, giãn cách ≥1s; thấy 429 thì dừng (đã xác nhận có rate limit).
- **Không sửa file dự án** — các agent `spec-tester-*` đã bị chặn `Write`/`Edit`; phát hiện thì **báo**.
- **Không ghi ảnh ra ngoài `evidence/`** — kể cả `/tmp` "cho nhanh". Ảnh chụp môi trường thật mang dữ liệu thật, và gate E chỉ kiểm được đường dẫn dưới `evidence/`; hook `guard_evidence` chặn sẵn, cả trong `browser_run_code_unsafe` (`page.screenshot({ path: … })`).
- `browser_run_code_unsafe` dùng cho mô phỏng mạng/nhịp bấm — **không** để đi tắt qua UI rồi kết luận "luồng chạy được". Đi tắt là hết kiểm thử.

Đầy đủ: `context/shared/SAFETY.md`.

## 6. Hỏng thì xem đây

| Triệu chứng | Nguyên nhân thường gặp |
|---|---|
| Server MCP không lên | `npx` trong PATH là gói standalone đời cũ — template dùng `npm exec` chính vì vậy |
| Lần đầu rất lâu | Đang tải Chromium; chạy trước `npx playwright install chromium` |
| Trang trắng / lỗi kết nối | URL sai hoặc môi trường test đang lỗi — `make doctor` kiểm lại, đúng thì đó là **phát hiện** |
| Không thấy tool `browser_*` | Chưa duyệt MCP server cho dự án — duyệt một lần khi Claude Code hỏi |
| Đăng nhập không được | Tài khoản test hết hạn/đổi mật khẩu — `make accounts`; vẫn không được → BLOCKED + blocker |
