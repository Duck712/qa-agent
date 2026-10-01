---
name: qa-testcase-design
description: >
  Thiết kế và review quan điểm test (test viewpoint, bám đặc tả có trích nguyên văn) và test case có kỷ luật cho
  mọi loại target. Đủ bộ kỹ thuật: phân vùng tương đương, giá trị
  biên (2/3 giá trị, biên nhiều chiều), syntax testing, bảng quyết định, ma trận phân quyền, ma trận CRUD,
  chuyển trạng thái (bảng trạng thái × sự kiện, 0/1-switch), use case / kịch bản, pairwise & classification
  tree, hộp trắng nhẹ từ code, oracle & metamorphic, fuzz/property, error guessing, checklist, khám phá theo
  phiên (SBTM, tour), kỹ thuật phi chức năng (ISO 25010, heuristic khả dụng, WCAG). Kèm cách chọn kỹ thuật
  theo tài liệu và mức rủi ro, mật độ R1/R2/R3, luật normal + abnormal, khuôn TC, checklist review TC và ma trận
  truy vết. Nạp skill này khi viết, bổ sung hoặc review test case.
---

# qa-testcase-design — viết và review test case có kỷ luật

> Viết theo cảm tính thì hoặc thiếu (sót ca hỏng) hoặc thừa (100 TC chạy mãi vẫn lọt bug). Kỹ thuật trả lời
> "bao nhiêu TC là đủ" bằng cấu trúc: mỗi TC bắt một kiểu hỏng cụ thể, mỗi kiểu hỏng có ít nhất một TC.

## 0. Trước khi viết
1. Đọc REQ trong `qa/ANALYSIS.md` và phạm vi trong `qa/SCOPE.md` — chỉ viết TC cho thứ trong phạm vi.
   REQ còn `(chờ trả lời)` → không đoán kỳ vọng, hỏi trước.
   Đọc **quan điểm test đã duyệt** ở `qa/viewpoints/<tính-năng>.md` (`ky-thuat/quan-diem.md`): mỗi TC hiện thực hoá một
   quan điểm và trỏ về bằng `VP:`. Chưa có quan điểm → làm `/qa-viewpoint` trước (hoặc hỏi người dùng có bỏ qua bước này
   không — đồng ý thì ghi DECISIONS). Kỳ vọng không nói nhiều hơn câu trích của quan điểm + câu trả lời ANALYSIS §5.
2. Mở `qa-knowledge`: `qa-knowledge/bug-patterns.md` (luôn) + checklist theo đối tượng/loại target. Đọc `qa/LESSONS.md`.
3. Mở `qa-targets/<loại>.md` — bước TC phải **thực hiện được** bằng công cụ của target đó.
4. Có code → đọc để biết bề mặt thật (endpoint, validate, nhánh, mã lỗi) — `ky-thuat/hop-trang.md`.
5. Dedupe: `grep -rn "<hành vi>" qa/testcases/` — trùng rõ thì dùng lại; na ná không chắc thì hỏi.

## 1. Chọn kỹ thuật — theo hình dạng của yêu cầu

| Yêu cầu trông như thế này | Kỹ thuật | File |
|---|---|---|
| Trường nhập có miền giá trị, độ dài, khoảng | Phân vùng + giá trị biên | `ky-thuat/phan-vung-bien.md` |
| Nhiều trường ràng buộc lẫn nhau (từ ngày < đến ngày, tổng = đơn giá × SL) | Biên nhiều chiều (domain analysis) | `ky-thuat/phan-vung-bien.md` §3 |
| Định dạng có ngữ pháp (email, SĐT, mã, URL, ngày, file CSV) | Syntax testing | `ky-thuat/phan-vung-bien.md` §4 |
| "Nếu A và B thì…, nếu A mà không B thì…" | Bảng quyết định | `ky-thuat/bang-quyet-dinh.md` |
| Vai × hành động, tenant | Ma trận phân quyền (bảng quyết định đặc biệt) | `ky-thuat/bang-quyet-dinh.md` §3 |
| Thực thể được tạo/xem/sửa/xoá | Ma trận CRUD | `ky-thuat/bang-quyet-dinh.md` §4 |
| Đối tượng có trạng thái (đơn, job, phiên, bản cài) | Chuyển trạng thái | `ky-thuat/trang-thai.md` |
| User story / use case / quy trình nhiều bước | Use case & kịch bản | `ky-thuat/use-case.md` |
| Nhiều tham số cấu hình/môi trường kết hợp | Pairwise, classification tree | `ky-thuat/to-hop.md` |
| Có code trong tay | Hộp trắng nhẹ (mỗi nhánh/validate/mã lỗi có TC) | `ky-thuat/hop-trang.md` |
| Không biết trước đáp án đúng (AI, xếp hạng, batch lớn, tính toán phức tạp) | Oracle, metamorphic, property | `ky-thuat/oracle.md` |
| Thay hệ cũ bằng hệ mới (di trú dữ liệu, đổi nền tảng/hạ tầng, nâng OS/DB/framework, viết lại, chạy song song) | So sánh song song + đối soát dữ liệu | `ky-thuat/oracle.md` §7 |
| Đầu vào tự do, parser, upload | Fuzz / sinh đầu vào | `ky-thuat/oracle.md` §4 |
| Tài liệu mỏng, vùng rủi ro chưa rõ | Error guessing, checklist, khám phá theo phiên | `ky-thuat/kinh-nghiem.md` |
| Hiệu năng, khả dụng, a11y, tương thích, i18n, tin cậy | Kỹ thuật phi chức năng | `ky-thuat/phi-chuc-nang.md` |

Một REQ thường cần **nhiều** kỹ thuật (ô đặt lịch: phân vùng + biên + chuyển trạng thái + phân quyền). Ghi kỹ
thuật đã dùng vào trường `Kỹ thuật:` của TC bằng **tên chuẩn** dưới (qa_check cảnh báo tên lạ) —
`python3 .claude/qa-scripts/qa_check.py trace` cho thấy REQ nào mới chỉ được nhìn một góc.

| Họ | Tên chuẩn dùng trong `Kỹ thuật:` |
|---|---|
| dữ liệu | `phân vùng` · `giá trị biên` · `biên nhiều chiều` · `syntax` |
| logic | `bảng quyết định` · `phân quyền` · `CRUD` · `chuyển trạng thái` · `use case` · `pairwise` · `classification tree` · `hộp trắng` |
| oracle | `metamorphic` · `property` · `fuzz` · `đồng thời` · `rubric` (chấm AI theo tiêu chí) · `mốc hành vi` · `so sánh song song` · `đối soát dữ liệu` |
| kinh nghiệm | `error guessing` · `checklist` · `khám phá` |
| phi chức năng | `phi chức năng` · `a11y` · `khả dụng` · `hiệu năng` · `tương thích` · `i18n` |

Mã quy tắc/luồng/chuyển (Q3, `UC-DATLICH 3a`, `chờ duyệt --huỷ--> ?`) ghi ở `Nguồn:` hoặc tiêu đề, **không** ghi trong
`Kỹ thuật:`. R1 cần kỹ thuật thuộc **≥ 2 họ** khác nhau (phân vùng + giá trị biên cùng họ "dữ liệu" — chưa đủ, vì BVA là phần mở
rộng của EP, không thêm góc nhìn).

## 2. Mật độ theo mức rủi ro

Mức R của REQ do **người dùng xác nhận** ở SCOPE §2 (đề xuất từ bảng rủi ro `qa-knowledge/analysis-review.md` §7);
`Mức:` của TC = mức đó, không tự nâng/hạ.

| Kỹ thuật \ Mức | R1 (mất tiền/dữ liệu/lộ quyền/sập luồng lõi) | R2 (khó chịu, có đường vòng) | R3 (lặt vặt) |
|---|---|---|---|
| Họ kỹ thuật | ≥ 2 họ | ≥ 1 | ≥ 1 |
| Phân vùng | mọi lớp | mọi lớp không hợp lệ chính | 1 hợp lệ + 1 không hợp lệ tiêu biểu |
| Giá trị biên | 3 giá trị mỗi mép | 2 giá trị mỗi mép | mép chính |
| Bảng quyết định | mọi quy tắc | mọi quy tắc sau gộp | quy tắc chính |
| Phân quyền | **mọi ô ✗** (lỗ = S1, ở mọi mức) | mọi ô ✗ | mọi ô ✗ |
| Chuyển trạng thái | 0-switch + mọi ô ✗ + 1-switch | 0-switch + ô ✗ nguy hiểm | luồng chính |
| Use case | chính + thay thế + mọi ngoại lệ đã biết | chính + thay thế chính | chính |
| Tổ hợp | pairwise + tích đầy đủ cho cặp R1 | pairwise | 1 cấu hình chính |

**Mọi mức: mỗi REQ ≥ 1 TC `Kiểu: normal` và ≥ 1 TC `Kiểu: abnormal`** (đầu vào sai, thiếu quyền, trạng thái
không hợp lệ, phụ thuộc lỗi…). `python3 .claude/qa-scripts/qa_check.py tc` đếm luật này; REQ R1 có kỹ thuật thuộc < 2 họ bị cảnh báo.

## 3. Khuôn TC
File `qa/testcases/<tinh-nang>.md`, mỗi TC một khối (khuôn đầy đủ: `qa/testcases/_TEMPLATE.md`):
```markdown
## TC-DATLICH-003 — Khung giờ đã đủ chỗ không đặt thêm được, kể cả gọi thẳng API
- REQ: REQ-DATLICH-2
- VP: VP-DATLICH-004
- Target: booking-web
- Loại: biên
- Kiểu: abnormal
- Mức: R1
- Kỹ thuật: giá trị biên, chuyển trạng thái
- Nguồn: REQ-DATLICH-2 (sức chứa 3 lịch/khung) · bug-patterns #11
- Regression: có
- Tiền điều kiện: khung 09:00 ngày mai đã có 3/3 lịch (seed QA-<run>-full)
- Dữ liệu: khách QA-<run>-k1, khung 09:00
- Bước:
  1. Mở trang đặt lịch, chọn ngày mai, xem khung 09:00
  2. Gọi thẳng `POST /api/bookings` (ví dụ — dùng endpoint thật) cho khung 09:00 bằng tài khoản khách (bỏ qua giao diện)
  3. Mở lại danh sách lịch khung 09:00
- Kỳ vọng:
  1. Khung 09:00 hiện trạng thái đã đủ chỗ và không bấm chọn được (chữ hiển thị theo REQ-DATLICH-2)
  2. Bị từ chối, không tạo lịch — mã/thông điệp theo câu trả lời ANALYSIS §5 #4 (chưa trả lời thì kỳ vọng này ghi `(chờ trả lời #4)` và TC chưa vào run)
  3. Vẫn đúng 3 lịch, không có lịch của QA-<run>-k1
- Bằng chứng cần: ảnh + URL trang bước 1 · request/response nguyên văn bước 2 · ảnh/response bước 3
```
ID `TC-<TÍNH-NĂNG>-<3 chữ số>`, không tái dùng ID đã xoá. Bắt buộc: REQ, Target, Loại, Kiểu, Mức, Nguồn, Bước,
Kỳ vọng, Bằng chứng cần; `VP` khi dự án có quan điểm test (TC tái hiện bug được miễn). Nên có: Kỹ thuật. Tuỳ chọn:
`Thực hiện: người` khi bước không tự động được — người dùng duyệt (skill `qa` §7); bước + kỳ vọng phải đủ rõ để người
chưa biết sản phẩm làm theo. Tiêu đề/kỳ vọng viết theo hành vi người dùng; chi tiết kỹ thuật
(selector, endpoint, lệnh) chỉ ở Bước/Dữ liệu. Mỗi kỳ vọng ứng với một bước — hành động nào kiểm ở kỳ vọng phải có
trong Bước.

**Kỳ vọng phải có nguồn**: mọi con số, thông điệp, mã trạng thái trong Kỳ vọng truy được về REQ, API doc hoặc câu
trả lời ở ANALYSIS §5. Tài liệu không nêu → ghi hành vi bắt buộc (bị chặn · không tạo/sửa bản ghi · có thông báo chỉ
ra trường lỗi) và mở điểm hỏi cho thông điệp/mã chính xác. Không ghi hai đáp án "A hoặc B" (vd "403/404" — TC gần
như không thể FAIL, và 403 vs 404 còn khác nhau về lộ sự tồn tại bản ghi).

**Một TC nhiều dòng dữ liệu** được (bảng phân vùng cùng bước): mỗi dòng một kỳ vọng; một dòng sai = TC FAIL, ghi
dòng nào trong bug. Lớp không hợp lệ vẫn mỗi dòng một lớp sai.

**Bốn câu tự hỏi mỗi TC**: (1) bắt được kiểu hỏng nào? (2) người chưa biết sản phẩm chạy được không? (3) kỳ vọng
quan sát được không — "hoạt động đúng" không phải kỳ vọng? (4) bằng chứng nào chứng minh PASS?

## 4. Review bộ TC
TC của người khác viết bằng Excel/Sheets: lưu CSV UTF-8 rồi `python3 .claude/qa-scripts/qa_check.py import tc <file.csv> --feature <tên>`
(chỉ chuyển định dạng — trường trống giữ trống, không tự điền, không tự đặt mã). Xuất ra Excel: `qa_check.py export tc`.
Sau mỗi đợt viết, và khi được nhờ review TC của người khác: `python3 .claude/qa-scripts/qa_check.py tc [REQ-… | <tính năng>]` (hình
thức) → `python3 .claude/qa-scripts/qa_check.py trace` (ma trận truy vết) → checklist `ky-thuat/review-tc.md` (nội dung). Trình người dùng:
REQ × số TC normal/abnormal × kỹ thuật; lỗ phủ; TC thừa/trùng; kỳ vọng mơ hồ; mục checklist chủ động bỏ và lý do.

## 5. Ranh giới
- Không viết TC ngoài phạm vi đã chốt — phát hiện ngoài phạm vi nêu thành đề xuất cho người dùng; nếu là bug thì ghi
  `mở` như thường, chuyển `hoãn` chỉ khi người dùng quyết (DECISIONS).
- Không sửa phạm vi/tiêu chí để hợp với TC đã viết.
- Bug S1/S2 đã đóng → luôn có TC tái hiện với `Regression: có`.
- Kỹ thuật là công cụ, không phải chỉ tiêu: không đẻ TC cho đủ số — TC không trả lời được câu (1) thì bỏ.
