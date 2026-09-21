---
name: spec-evidence
description: >
  Chuẩn bằng chứng của SPEC — bằng chứng nào đủ tư cách cho từng loại test case, quy ước đặt tên/thư mục
  evidence/r<N>/luot-<k>/<TC-ID>/, cách thu đúng (ảnh thấy URL bar, computed style kèm selector,
  request/response nguyên văn, crash log, số đo hiệu năng), và checklist chống "test giả". Nạp skill này ở
  pha E khi ghi kết quả vào RUNLOG, ở pha C trước khi ký verdict, và khi đóng vai spec-evidence-auditor.
---

# spec-evidence — bằng chứng là thứ phân biệt kiểm thử với lời khẳng định

> Luật #5: lời tự test/dogfood của dev không bao giờ là bằng chứng. Luật #8: PASS phải chứng minh được.
> Một dòng `PASS` không có bằng chứng thì giá trị bằng một lời hứa — mà lời hứa thì SPEC đã có sẵn
> từ phía dev rồi, không cần kiểm lại để có thêm cái thứ hai.

## 1. Thư mục và đặt tên

```
evidence/
├── _inbox/<vai>/                 ← MCP đổ screenshot thô (--output-dir), KHÔNG commit
└── r<N>/luot-<k>/<TC-ID>/        ← đã phân loại — RUNLOG trỏ vào ĐÂY, gate E kiểm tồn tại
    ├── 01-buoc1.png
    ├── 02-ket-qua.png
    ├── request.txt · response.txt         (api / phân quyền / tương thích)
    ├── computed-style.txt                  (hình thức)
    ├── console.txt · network.txt           (biên)
    ├── do-thoi-gian.txt                    (hiệu năng)
    └── ghi-chu.md                          (tuỳ chọn — một dòng bối cảnh)
```

Quy tắc: **một thư mục một TC một lượt**. TC chạy lại ở lượt sau → thư mục `luot-<k+1>/` mới, thư mục cũ giữ nguyên (là lịch sử của lượt đó). Ảnh đánh số theo thứ tự bước.

Dòng RUNLOG trỏ tới **cấp thư mục TC-ID** (`evidence/r1/luot-1/TC-BOOK-01-001/`), không trỏ file lẻ — `gate.py E` và `guard_verdict` kiểm đường dẫn này tồn tại trên đĩa và **không nằm trong repo nguồn**.

**Không có bằng chứng nào sống ngoài `evidence/`.** Hook `guard_evidence` chặn mọi lời gọi chụp ảnh/quay màn hình ghi ra ngoài thư mục này — `filename` (browser), `saveTo` (mobile), `output` (recording, **bỏ trống cũng bị chặn** vì mobile-mcp rơi vào thư mục tạm), `path:` trong `browser_run_code_unsafe`, và lệnh Bash chép file ảnh ra ngoài repo. Hai lý do: ảnh ở `/tmp` làm dòng `PASS` **không bao giờ chứng minh được** (gate E chỉ đọc dưới `evidence/`), và ảnh môi trường thật **mang dữ liệu thật** — nằm rải rác ngoài repo là rò rỉ không ai dọn.

## 2. Bằng chứng đủ tư cách theo loại TC

| Loại TC | Tối thiểu để được ghi PASS |
|---|---|
| chức năng · workflow · biên | Screenshot **thấy URL bar đúng môi trường test** ở bước then chốt + trích snapshot/console. Workflow: ảnh **từng chặng kèm vai** |
| phá-hoại-đầu-vào · phân quyền | **Dữ liệu chính xác đã gửi** + **response NGUYÊN VĂN** (mã + body). Ảnh "không thấy nút" không tính |
| api | Request + response nguyên văn + **timestamp** |
| tương-thích-ngược | **Diff** so baseline (`API-SURFACE.md` release trước) hoặc thao tác thật trên bản ghi di sản `SPEC-r<N-1>-…` |
| tích-hợp | Bằng chứng **CẢ HAI đầu**: hành động + hộp thư test/log webhook/sandbox |
| cross-target | **CẶP** ảnh: hành động ở A + kết quả ở B + `network.txt` của B (chứng minh không phải cache) |
| hình thức | **Giá trị computed style + selector + màn** (`color: rgb(37,99,235) @ button.cta`). Mobile: frame/toạ độ + screenshot |
| hiệu năng | **Từng lần đo + p95 + cách đo + thời điểm** — thiếu cách đo thì release sau không so được |
| mobile | Screenshot màn (kèm bundle id) + `mobile_list_crashes` |
| bảo-mật | Request đã gửi + response nguyên văn (che token/dữ liệu cá nhân) + mục OWASP/CVE làm nguồn; CVE/secret: output nguyên văn của tool (secret chỉ ghi file + dòng + loại, **không** ghi giá trị) |

Thiếu bằng chứng đúng loại → ghi `BLOCKED`, **không phải** `PASS`. Đây không phải hình thức: gate E và hook `guard_verdict` đọc đúng chỗ này.

## 3. Cách thu cho đúng

- **Ảnh phải thấy URL bar** (web) — chứng minh đang ở đúng môi trường test khai trong manifest, không phải localhost / môi trường khác. Screenshot trang của Playwright MCP (headless) **không chụp thanh URL** → ở bước then chốt chụp kèm `browser_snapshot` (dòng `Page URL:`) lưu thành `NN-snapshot.txt` cùng thư mục, hoặc chép URL vào `ghi-chu.md` — không có dấu URL nào thì chưa chứng minh được môi trường. Mobile: kèm bundle id đang chạy.
- **Response chép nguyên văn** vào `.txt`, không tóm tắt, không "server trả lỗi 4xx" — ghi đúng mã + body.
- **Computed style kèm selector**: `font-size: 13px @ span.label` — số trần trụi không tra lại được.
- **Số đo hiệu năng kèm thời điểm**: giờ trong ngày ảnh hưởng tải môi trường.
- **Crash log lấy nguyên văn** bằng `mobile_get_crash`, không chỉ "có crash".
- Video chỉ khi luồng khó tả bằng lời — **không commit** (`.gitignore` chặn), ghi đường dẫn ngoài vào `ghi-chu.md`.

## 4. Checklist chống test giả

Trước khi ghi PASS vào RUNLOG, tự hỏi:

1. Tôi có **mở ra bấm thật** không, hay đang suy từ code/tài liệu của dev?
2. Ảnh có **thấy URL đúng môi trường test** không (URL bar, hoặc `Page URL` của `browser_snapshot` cùng bước)?
3. TC hình thức: tôi có nêu được **một giá trị computed style** không?
4. TC phân quyền: tôi có **response nguyên văn** của lời gọi bị cấm không?
5. TC cross-target: tôi có bằng chứng **cả hai phía** không?
6. Cả một đợt của tôi **toàn PASS, không phát hiện gì** — có thật không, hay tôi chưa đi hết?

Câu nào "không" → chưa được ghi PASS.

## 5. Với `spec-evidence-auditor`

Auditor bốc ≥30% dòng PASS (ưu tiên authz/compat/cross/visual/perf), mở thư mục evidence và **đọc thật**. Dấu hiệu lệch: thư mục rỗng · file 0 byte · **ảnh trùng nhau giữa nhiều TC** · timestamp giống hệt cho cả chục TC · ảnh không có URL bar · TC hình thức không có số đo · TC phân quyền không có response.

Lệch → phiên chính xử: chạy lại TC, hoặc hạ về `BLOCKED`. **Không sửa dòng PASS thành PASS đẹp hơn** — sửa sổ mà không chạy lại là đúng thứ cơ chế này sinh ra để chặn.

## 6. Ranh giới

- Bằng chứng **do SPEC sinh** — không dùng lại screenshot/log của dev (luật #5, gate E kiểm đường dẫn không nằm trong repo nguồn).
- Không chụp màn hình chứa **dữ liệu người dùng thật** — nếu lỡ thấy (lỗ cách ly), đó là bug S1: chụp phần chứng minh lỗ, che phần dữ liệu cá nhân, ghi rõ trong bug.
- Không commit `evidence/_inbox/` (thô, trùng lặp) — chỉ commit bản đã phân loại.
