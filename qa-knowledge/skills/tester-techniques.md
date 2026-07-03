# Kỹ thuật thiết kế test case (Tester)
> Dùng SONG SONG với checklists/ — checklist cho biết "test đối tượng gì", file này cho biết
> "cách nghĩ ra case đủ và không thừa" khi checklist không cover hết tình huống cụ thể của feature.

## 1. Boundary Value Analysis (giá trị biên)
Với mọi giới hạn số (min/max, độ dài, số lượng): luôn test 5 điểm quanh biên, không chỉ 1.
- min-1 (phải FAIL) → min (phải PASS) → min+1 (PASS) ... → max-1 (PASS) → max (PASS) → max+1 (FAIL)
- Áp cho: độ dài chuỗi, giá trị số, số lượng item trong giỏ hàng, thời hạn hiệu lực.

## 2. Equivalence Partitioning (phân vùng tương đương)
Input có nhiều giá trị hợp lệ na ná nhau → không cần test hết, chia thành các "vùng" và test
đại diện 1 giá trị mỗi vùng (đủ, không thừa):
- Vùng hợp lệ, vùng không hợp lệ (nhỏ hơn min), vùng không hợp lệ (lớn hơn max), vùng sai kiểu.
- Vd tuổi 18-60: test 1 giá trị trong [18-60], 1 giá trị <18, 1 giá trị >60 — không cần test cả 43 số.

## 3. Decision Table (bảng quyết định) — cho luồng nhiều điều kiện kết hợp
Khi kết quả phụ thuộc TỔ HỢP nhiều điều kiện (không phải 1 field đơn lẻ):
| Điều kiện A | Điều kiện B | Điều kiện C | → Kết quả mong đợi |
|---|---|---|---|
Liệt kê đủ tổ hợp có ý nghĩa (không cần 2^n nếu vài điều kiện độc lập nhau).
Vd: giảm giá = f(loại khách hàng, giá trị đơn, có mã khuyến mãi không) → viết bảng trước khi viết TC,
tránh bỏ sót tổ hợp.

## 4. State Transition (chuyển trạng thái) — cho entity có vòng đời
Khi đối tượng có trạng thái (order, ticket, bài viết...): vẽ sơ đồ trạng thái → test:
- Mọi transition HỢP LỆ (draft → published)
- Mọi transition KHÔNG HỢP LỆ bị chặn đúng cách (published → draft có được phép lùi không?)
- Trạng thái "mồ côi": data bị kẹt giữa chừng do lỗi (thanh toán xong nhưng order chưa update)

## 5. Exploratory Testing có kỷ luật
Không "mò vô định". Trước khi bắt đầu, xác định trong 1-2 câu:
- **Charter**: đang thăm dò vùng nào? (vd: "thăm dò luồng thanh toán khi kết hợp mã giảm giá + đổi số lượng giữa chừng")
- **Thời gian**: giới hạn (vd 30 phút), hết giờ thì dừng và ghi lại đã đi qua đâu.
- Ghi chú lại NGAY khi thấy điều bất thường, kể cả chưa chắc là bug — đừng để "lát nữa nhớ lại".

## 6. Viết bug chất lượng cao
- **Tối giản hoá repro**: thử bỏ bớt từng bước xem lỗi còn xảy ra không → step cuối cùng còn lại
  là bộ step tối thiểu, dev debug nhanh hơn nhiều.
- **Triệu chứng, không kết luận hộ**: viết "API trả 500 khi X" chứ không viết "chắc do backend
  quên validate" — trừ khi có bằng chứng rõ (stack trace) thì ghi vào mục Suggested area riêng.
- **1 bug = 1 vấn đề**: đừng gộp nhiều lỗi không liên quan vào 1 bug report.
- Luôn kèm: request/response thật (không paraphrase), timestamp, môi trường, tài khoản dùng để test.
