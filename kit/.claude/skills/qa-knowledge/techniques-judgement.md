# Mẹo nghề — ngoài bốn kỹ thuật thiết kế TC

> Kỹ thuật thiết kế TC ở skill `qa-testcase-design` (`ky-thuat/`). Kỹ thuật phân tích/review tài liệu ở `analysis-review.md`.
> Kết luận đạt/không đạt là phép tính theo tiêu chí ghi trước (`qa_check.py run`), không phải phán đoán. File này giữ phần còn lại.

## 1. Khám phá có kỷ luật (exploratory)

Không "mò vô định". Trước khi bắt đầu, xác định trong 1–2 câu:
- **Charter**: đang thăm dò vùng nào? (vd "luồng thanh toán khi kết hợp mã giảm giá + đổi số lượng giữa chừng")
- **Thời gian**: giới hạn (vd 30 phút), hết giờ dừng và ghi lại đã đi qua đâu.
- Ghi chú **ngay** khi thấy điều bất thường, kể cả chưa chắc là bug.

Làm theo phiên có charter, ghi chép và debrief — chi tiết + các "tour": `qa-testcase-design/ky-thuat/kinh-nghiem.md` §3, khuôn `qa/runs/_EXPLORE-TEMPLATE.md`.

Khám phá là **nguồn phát hiện**, không thay TC: thấy lỗi → ghi bug (có bằng chứng) + đề xuất TC mới vào `qa/testcases/`. Ghi đường đã đi vào RUNLOG (dòng `EXPLORE-<n>`) để lần sau không đi lại đúng chỗ đó.

## 2. Viết bug chất lượng cao

- **Tối giản repro**: thử bỏ bớt từng bước xem lỗi còn không → bộ bước còn lại là tối thiểu.
- **Triệu chứng, không kết luận hộ**: "API trả 500 khi X", không phải "chắc backend quên validate" — nghi ngờ khu vực code thì ghi riêng, ghi rõ là suy đoán.
- **1 bug = 1 vấn đề**.
- Luôn kèm: request/response thật, thời điểm (giờ phút), môi trường + bản deploy, tài khoản/vai đã dùng.
- **Severity theo hậu quả, không theo tần suất**: mất dữ liệu / lộ quyền / sai tiền dù chỉ tái hiện 3/10 lần vẫn là S1 — ghi tỉ lệ tái hiện vào bug.

## 3. Soi yêu cầu mơ hồ (khi phân tích tài liệu)

Đầy đủ: `analysis-review.md` (tiêu chí chất lượng, từ yếu, góc nhìn, yêu cầu ngầm, example mapping). Tối thiểu —
câu sau đây **không đủ để viết TC** — ghi `ANALYSIS.md §5` kèm đề xuất và hỏi người dùng:
- "Xử lý đúng", "hiển thị hợp lý", "tối ưu trải nghiệm" → hỏi: đúng là gì, cụ thể bằng con số/hành vi quan sát được.
- Chỉ có happy path, không nói gì về lỗi → hỏi: input sai/thiếu thì hệ thống làm gì (đây chính là nguồn của TC `Kiểu: abnormal`).
- Có 2 cách hiểu → đưa **cả 2 cách hiểu** kèm đề xuất của mình + rủi ro nếu chọn sai, không tự đoán 1 cách.
- Hai tài liệu mâu thuẫn nhau → trích cả hai, hỏi cái nào thắng.

## 4. Cắt phạm vi có trách nhiệm (khi lập kế hoạch)

**Rủi ro = Xác suất lỗi × Thiệt hại nếu lỗi** — bảng chấm 1–3 ở `analysis-review.md` §7. Khi không đủ thời gian test hết:
- Ưu tiên: (1) luồng cốt lõi vừa thay đổi · (2) tiền / dữ liệu / bảo mật · (3) regression của bug từng xảy ra · (4) sau đó mới tới ca hiếm.
- Thứ bị cắt → `SCOPE.md §3` ngoài phạm vi **có lý do**, người dùng chốt. Không im lặng bỏ qua.

## 5. Viết REPORT cho người không rành kỹ thuật

- Kết luận trước, chi tiết sau: dòng đầu là verdict + 1 câu lý do.
- Số cụ thể, không tính từ mơ hồ ("khá ổn") — "23/25 TC PASS, 2 FAIL đều S3".
- Tin xấu nói ngay đầu, không chôn giữa báo cáo.
