---
name: qa-evidence
description: >
  Chuẩn bằng chứng kiểm thử — bằng chứng nào đủ tư cách cho từng loại test và từng loại target, quy ước thư
  mục `qa/evidence/<run-id>/<TC-ID>/`, cách thu đúng (ảnh kèm URL, response nguyên văn, stdout/exit code,
  checksum dữ liệu, transcript AI, computed style, số đo hiệu năng), và checklist chống "test giả". Nạp skill
  này khi chạy test, khi ghi kết quả vào RUNLOG, trước khi viết REPORT, và khi đóng vai qa-evidence-check.
---

# qa-evidence — bằng chứng là thứ phân biệt kiểm thử với lời khẳng định

> Một dòng `PASS` không có bằng chứng thì giá trị bằng một lời hứa — mà lời hứa thì dev đã có sẵn rồi.

## 1. Thư mục
```
qa/evidence/
├── _inbox/<vai>/            ← MCP đổ ảnh thô (không commit)
└── <run-id>/<TC-ID>/        ← đã phân loại — RUNLOG trỏ vào ĐÂY
    ├── 01-buoc1.png · 01-snapshot.txt
    ├── 02-request.txt · 02-response.json · 02-status.txt
    ├── 03-stdout.txt · 03-stderr.txt · 03-exit.txt
    └── ghi-chu.md            (tuỳ chọn: một dòng bối cảnh, đường dẫn video)
```
Một thư mục một TC một run; chạy lại ở run khác → thư mục run mới, cũ giữ nguyên. File đánh số theo bước.
Tool MCP (ảnh, snapshot, kết quả evaluate) → khai `filename`/`saveTo` là **đường dẫn tuyệt đối** vào đúng thư mục TC;
không dựa vào `_inbox/` khi có nhiều tester chạy song song (dễ lấy nhầm ảnh của nhau). RUNLOG trỏ tới đúng thư mục
`qa/evidence/<run-id>/<TC-ID>/` — trỏ thư mục chung (`qa/evidence/`, `qa/evidence/<run-id>/`) không được tính.
Hook `guard_evidence` chặn ảnh/video ghi ra ngoài `qa/evidence/` (ảnh môi trường thật mang dữ liệu thật —
nằm rải rác ở /tmp là rò rỉ, và RUNLOG không trỏ được tới).

## 2. Tối thiểu để được ghi PASS/FAIL
| Loại test / target | Bằng chứng |
|---|---|
| chức năng · workflow · biên (web) | Ảnh bước then chốt + `Page URL:` từ snapshot. Workflow: ảnh từng chặng kèm vai |
| mobile · desktop | Ảnh + bundle id/version app + trích cây UI; crash: log nguyên văn |
| api · phân-quyền · phá-đầu-vào | Request đã gửi (che token) + response **nguyên văn** (mã + body) + thời điểm. Ảnh "không thấy nút" không tính |
| cli | Lệnh nguyên văn + stdout + stderr + exit code + version tool |
| batch | Checksum/mẫu input + cách kích + log có run id + output/truy vấn đọc output + diff với expected |
| ai | Transcript nguyên văn N lượt + `cham.md` (lượt × tiêu chí) |
| library | Chương trình dùng thử + output + version gói và runtime |
| tích-hợp | Cả hai đầu: hành động + hộp thư test/log webhook/sandbox |
| khôi-phục | Trạng thái **trước** khi ngắt + cách ngắt (lệnh/thao tác + thời điểm) + trạng thái **sau** khi tiếp tục (dữ liệu, bản ghi, file) |
| tương-thích | Cấu hình/phiên bản đang chạy (trình duyệt/OS/runtime/bản cũ) + kết quả trên từng cấu hình; dữ liệu cũ: bản ghi trước/sau nâng cấp |
| cross-target | Cặp: hành động ở A + kết quả ở B + network của B |
| hình-thức | Giá trị đo + selector/phần tử + màn (`color: rgb(37,99,235) @ button.cta`) |
| hiệu-năng | Từng lần đo + median/max kèm n (p95 chỉ khi n ≥ 20) + cách đo + thời điểm |
| bảo-mật | Request + response nguyên văn (che dữ liệu) + mục OWASP/CVE; secret: file + dòng + loại, **không** ghi giá trị |
| thủ công (người dùng làm) | Ảnh/video/ghi chú người dùng gửi + ghi rõ "người dùng thực hiện" |

Thiếu bằng chứng đúng loại → `BLOCKED`, không phải `PASS`.

## 3. Thu cho đúng
- Chép **nguyên văn**, không tóm tắt ("server trả 4xx" không phải bằng chứng).
- Ghi thời điểm và bản đang kiểm (version/commit/build) ít nhất một lần mỗi run (đầu RUNLOG).
- Che token, mật khẩu, dữ liệu cá nhân **trước khi lưu**.
- Video không commit (`.gitignore`), ghi đường dẫn vào `ghi-chu.md`.

## 4. Checklist chống test giả — tự hỏi trước khi ghi PASS
1. Tôi có **chạy thật** không, hay đang suy từ code/tài liệu?
2. Bằng chứng có chứng minh **đúng môi trường / đúng bản** không?
3. Kỳ vọng **từng bước** đã đối chiếu, hay gộp cả TC thành một kết luận?
4. Kết quả "gần đúng" (thiếu một trường, lệch chữ, số chênh nhỏ) → đó là FAIL hoặc câu hỏi, **không** phải PASS.
5. Phân quyền: có response nguyên văn của lời gọi bị cấm? Cross-target: có cả hai phía? AI: đủ N lượt?
6. Cả đợt toàn PASS, không phát hiện gì — thật không, hay chưa đi hết?

Câu nào "không" → chưa được ghi PASS.

## 5. qa-evidence-check
Trước khi báo cáo: bốc ≥ 30% dòng PASS (mức soi của kit — người dùng muốn khác thì chốt; tối thiểu 5, hoặc tất cả nếu ít hơn; ưu tiên phân quyền, cross, hình thức,
hiệu năng, ai, bảo mật và mọi TC R1) + **mọi** dòng FAIL, mở thư mục và **đọc thật**. Dấu hiệu lệch: thư mục rỗng · file 0 byte · ảnh trùng nhau giữa nhiều TC · timestamp giống hệt cả
chục TC · không có dấu môi trường · TC hình thức không có số đo · phân quyền không có response · AI thiếu lượt.
Lệch → **trình người dùng**; người dùng quyết chạy lại TC hay hạ về `BLOCKED` (ghi DECISIONS). Ghi
`Đã soi bằng chứng <ngày> — <x> lệch` vào Nhật ký RUNLOG. **Không sửa dòng PASS cho đẹp mà không chạy lại.**
