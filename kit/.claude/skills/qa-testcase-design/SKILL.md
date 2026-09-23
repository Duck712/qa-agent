---
name: qa-testcase-design
description: >
  Thiết kế test case có kỷ luật cho mọi loại target — bốn kỹ thuật (phân vùng tương đương, giá trị biên,
  bảng quyết định, chuyển trạng thái), chọn mật độ theo mức rủi ro R1/R2/R3, luật normal + abnormal mỗi yêu
  cầu, khuôn TC trong `qa/testcases/`, và bốn câu tự hỏi để loại TC thừa. Nạp skill này khi viết, bổ sung
  hoặc review test case. Mục tiêu: mỗi TC bắt được một kiểu hỏng cụ thể, không đẻ TC cho đủ số.
---

# qa-testcase-design — viết test case có kỷ luật

> Viết theo cảm tính thì hoặc thiếu (sót ca hỏng) hoặc thừa (100 TC chạy mãi vẫn lọt bug). Bốn kỹ thuật dưới
> trả lời "bao nhiêu TC là đủ" bằng cấu trúc.

## 0. Trước khi viết
1. Mở `ANALYSIS.md` (yêu cầu REQ-…) và `SCOPE.md` nếu có — chỉ viết TC cho thứ trong phạm vi.
2. Mở `qa-knowledge`: `bug-patterns.md` (luôn) + checklist theo đối tượng (form, đăng nhập, upload, API,
   bất thường, thanh toán, thông báo, realtime, tìm kiếm, ngày giờ) + checklist theo loại target (cli, batch, ai).
3. Mở `qa-targets/<loại>.md` — bước TC phải **thực hiện được** bằng công cụ của target đó.
4. Dedupe: `grep -rn "<hành vi>" qa/testcases/` — đã có TC tương tự → dùng lại/sửa, không tạo trùng.

## 1. Mật độ theo mức rủi ro
| Mức | Khi nào | Kỹ thuật |
|---|---|---|
| **R1** | Sai là mất tiền / mất dữ liệu / lộ quyền / sập luồng lõi | Cả bốn kỹ thuật |
| **R2** | Sai thì khó chịu, có đường vòng | Phân vùng + biên (ca tiêu biểu) |
| **R3** | Sai thì lặt vặt | Happy path |

**Mỗi REQ ≥ 1 TC `Kiểu: normal` và ≥ 1 TC `Kiểu: abnormal`** (đầu vào sai, thiếu quyền, trạng thái không hợp
lệ, phụ thuộc lỗi…). REQ chỉ có happy path là REQ chưa được kiểm. `qa_check.py tc` đếm luật này.

## 2. Phân vùng tương đương
Chia miền đầu vào thành lớp cư xử như nhau, mỗi lớp một đại diện. Ô "số lượng" (1–20): hợp lệ 5 · dưới 0 ·
trên 25 · âm −3 · không phải số "năm" · rỗng · khoảng trắng → 7 lớp, không phải 20 TC.
Áp cho mọi target: cờ CLI (hợp lệ/lạ/thiếu), file đầu vào job (hợp lệ/hỏng/rỗng), loại câu hỏi cho bot
(trong tài liệu/ngoài tài liệu/độc hại). **Bẫy**: quên lớp "rỗng" và "khoảng trắng" — hai lớp khác nhau.

## 3. Giá trị biên
Miền `[min, max]` → thử **min−1, min, max, max+1**. Độ dài chuỗi (0, 1, max, max+1) · số bản ghi (0, 1, đầy
trang, tràn trang) · ngày (hôm nay, cuối tháng, 29/2, quanh 0h theo múi giờ) · tiền (0, nhỏ nhất, lớn nhất) ·
kích thước file (0 byte, giới hạn, vượt) · context LLM (sát giới hạn). **Bẫy**: 10 bản ghi với `limit=10`.

## 4. Bảng quyết định — tổ hợp điều kiện, phân quyền
Kết quả phụ thuộc tổ hợp → lập bảng, mỗi dòng một TC. Ma trận vai × hành động (`ANALYSIS §2`): **mỗi ô ✗ là
một TC bắt buộc** (ghi `Ô ma trận: <hành động> × <vai> = ✗`). Ma trận lớn → `python3 .claude/qa-scripts/gen_matrix_tc.py`
sinh khung TC từ bảng.

| Hành động | Vai | Chủ bản ghi | Kỳ vọng |
|---|---|---|---|
| Sửa đơn | owner | của mình | cho |
| Sửa đơn | owner | tenant khác | **chặn 403/404** |
| Sửa đơn | viewer | bất kỳ | **chặn 403** |
| Sửa đơn | chưa đăng nhập | — | **chặn 401** |

**Bẫy**: chỉ thử "vai bị cấm không thấy nút" mà không **gọi thẳng API** — giấu nút không phải là chặn.

## 5. Chuyển trạng thái — nguồn của TC workflow
Vẽ vòng đời (đơn, job, hội thoại, bản cài đặt) → mỗi chuyển hợp lệ một TC, mỗi chuyển bị cấm một TC (phải
bị chặn). **Bẫy**: chỉ test đường thẳng; nhảy cóc trạng thái qua deep link/API/chạy lại job là chỗ bug nằm.

## 6. Kỹ thuật chủ đạo theo loại test
chức năng → phân vùng (happy) · biên → biên + lớp không hợp lệ · phá-đầu-vào → lớp không hợp lệ đẩy cực đoan ·
phân-quyền → bảng quyết định · workflow → chuyển trạng thái · api → phân vùng + biên ở tầng API · tương-thích →
so bản trước/dữ liệu cũ · hình-thức → đo so token · hiệu-năng → lặp thưa so ngưỡng · ai → phân vùng loại câu
hỏi × N lần chạy × tiêu chí chấm · bảo-mật → mỗi TC một mục OWASP áp được.

## 7. Khuôn TC
File `qa/testcases/<tinh-nang>.md`, mỗi TC một khối (khuôn đầy đủ: `qa/testcases/_TEMPLATE.md`):
```markdown
## TC-DATLICH-003 — Đặt lịch vào khung giờ đã kín bị từ chối
- REQ: REQ-DATLICH-2
- Target: booking-web
- Loại: biên
- Kiểu: abnormal
- Mức: R1
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
ID: `TC-<TÍNH-NĂNG>-<số 3 chữ số>`, không tái dùng ID đã xoá. Loại/Kiểu/Mức/Target/REQ bắt buộc.
Narrative (tiêu đề, kỳ vọng) viết theo hành vi người dùng; chi tiết kỹ thuật (selector, endpoint, lệnh) chỉ ở Bước/Dữ liệu.

## 8. Bốn câu tự hỏi mỗi TC
1. **Bắt được kiểu hỏng nào?** Không trả lời được → TC thừa.
2. **Người chưa biết sản phẩm chạy được không?** Thao tác + dữ liệu cụ thể.
3. **Kỳ vọng quan sát được không?** "Hoạt động đúng" không phải kỳ vọng; "hẹn mới hiện đầu danh sách, trạng thái Chờ xác nhận" mới là.
4. **Bằng chứng nào chứng minh PASS?** Ghi `Bằng chứng cần` theo skill `qa-evidence`.

Sau mỗi đợt viết: `python3 .claude/qa-scripts/qa_check.py tc` → sửa đến khi sạch, trình bảng tóm tắt
(số TC theo REQ × Kiểu × Loại, REQ chưa phủ).

## 9. Ranh giới
- Không viết TC ngoài phạm vi đã chốt — phát hiện ngoài phạm vi ghi `BUGS.md` trạng thái `hoãn` hoặc đề xuất.
- Không sửa phạm vi/tiêu chí để hợp với TC đã viết.
- Bug S1/S2 đã đóng → luôn có TC tái hiện với `Regression: có`.
