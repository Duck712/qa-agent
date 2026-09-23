---
name: qa-testcase-design
description: >
  Thiết kế và review test case có kỷ luật cho mọi loại target. Đủ bộ kỹ thuật: phân vùng tương đương, giá trị
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
2. Mở `qa-knowledge`: `bug-patterns.md` (luôn) + checklist theo đối tượng/loại target. Đọc `qa/LESSONS.md`.
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
| Đầu vào tự do, parser, upload | Fuzz / sinh đầu vào | `ky-thuat/oracle.md` §4 |
| Tài liệu mỏng, vùng rủi ro chưa rõ | Error guessing, checklist, khám phá theo phiên | `ky-thuat/kinh-nghiem.md` |
| Hiệu năng, khả dụng, a11y, tương thích, i18n, tin cậy | Kỹ thuật phi chức năng | `ky-thuat/phi-chuc-nang.md` |

Một REQ thường cần **nhiều** kỹ thuật (ô đặt lịch: phân vùng + biên + chuyển trạng thái + phân quyền). Ghi kỹ
thuật đã dùng vào trường `Kỹ thuật:` của TC — `qa_check.py trace` cho thấy REQ nào mới chỉ được nhìn một góc.

## 2. Mật độ theo mức rủi ro

| Mức | Khi nào | Tối thiểu |
|---|---|---|
| **R1** | Sai là mất tiền / mất dữ liệu / lộ quyền / sập luồng lõi | ≥ 2 kỹ thuật khác nhau · biên 3 giá trị · mọi ô ✗ phân quyền · mọi chuyển cấm · luồng ngoại lệ của use case |
| **R2** | Sai thì khó chịu, có đường vòng | Phân vùng + biên 2 giá trị · luồng chính + luồng thay thế chính |
| **R3** | Sai thì lặt vặt | Happy path + 1 ca abnormal tiêu biểu |

**Mọi mức: mỗi REQ ≥ 1 TC `Kiểu: normal` và ≥ 1 TC `Kiểu: abnormal`** (đầu vào sai, thiếu quyền, trạng thái
không hợp lệ, phụ thuộc lỗi…). `qa_check.py tc` đếm luật này; REQ R1 dùng < 2 kỹ thuật bị cảnh báo.

## 3. Khuôn TC
File `qa/testcases/<tinh-nang>.md`, mỗi TC một khối (khuôn đầy đủ: `qa/testcases/_TEMPLATE.md`):
```markdown
## TC-DATLICH-003 — Đặt lịch vào khung giờ đã kín bị từ chối
- REQ: REQ-DATLICH-2
- Target: booking-web
- Loại: biên
- Kiểu: abnormal
- Mức: R1
- Kỹ thuật: giá trị biên, chuyển trạng thái
- Nguồn: REQ-DATLICH-2 · form-input §3
- Regression: có
- Tiền điều kiện: khung 09:00 ngày mai đã có 3/3 lịch (seed QA-<run>-full)
- Dữ liệu: khách QA-<run>-k1, khung 09:00
- Bước:
  1. Mở trang đặt lịch, chọn ngày mai
  2. Chọn khung 09:00, bấm "Đặt"
- Kỳ vọng:
  1. Khung 09:00 hiện "Đã kín", không chọn được
  2. Gọi thẳng API đặt khung 09:00 → 409 kèm thông điệp "khung giờ đã kín"
- Bằng chứng cần: ảnh bước 1 + Page URL · request/response bước 2
```
ID `TC-<TÍNH-NĂNG>-<3 chữ số>`, không tái dùng ID đã xoá. Bắt buộc: REQ, Target, Loại, Kiểu, Mức, Nguồn, Bước,
Kỳ vọng, Bằng chứng cần. Nên có: Kỹ thuật. Tiêu đề/kỳ vọng viết theo hành vi người dùng; chi tiết kỹ thuật
(selector, endpoint, lệnh) chỉ ở Bước/Dữ liệu. Một TC nhiều ca dữ liệu (bảng phân vùng) được — mỗi dòng dữ liệu
một kỳ vọng.

**Bốn câu tự hỏi mỗi TC**: (1) bắt được kiểu hỏng nào? (2) người chưa biết sản phẩm chạy được không? (3) kỳ vọng
quan sát được không — "hoạt động đúng" không phải kỳ vọng? (4) bằng chứng nào chứng minh PASS?

## 4. Review bộ TC
Sau mỗi đợt viết, và khi được nhờ review TC của người khác: `python3 .claude/qa-scripts/qa_check.py tc` (hình
thức) → `qa_check.py trace` (ma trận truy vết) → checklist `ky-thuat/review-tc.md` (nội dung). Trình người dùng:
REQ × số TC normal/abnormal × kỹ thuật; lỗ phủ; TC thừa/trùng; kỳ vọng mơ hồ; mục checklist chủ động bỏ và lý do.

## 5. Ranh giới
- Không viết TC ngoài phạm vi đã chốt — phát hiện ngoài phạm vi ghi đề xuất/`hoãn`.
- Không sửa phạm vi/tiêu chí để hợp với TC đã viết.
- Bug S1/S2 đã đóng → luôn có TC tái hiện với `Regression: có`.
- Kỹ thuật là công cụ, không phải chỉ tiêu: không đẻ TC cho đủ số — TC không trả lời được câu (1) thì bỏ.
