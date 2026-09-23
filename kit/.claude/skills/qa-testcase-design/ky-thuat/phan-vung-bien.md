# Phân vùng tương đương · giá trị biên · biên nhiều chiều · syntax testing

## 1. Phân vùng tương đương (EP)
Chia miền đầu vào (và **đầu ra**) thành lớp mà mọi giá trị trong lớp cư xử như nhau; mỗi lớp một đại diện.

Ô "số lượng" (1–20):
| Lớp | Đại diện | Kỳ vọng |
|---|---|---|
| hợp lệ | 5 | nhận |
| dưới miền | 0 | "tối thiểu 1" |
| trên miền | 25 | "tối đa 20" |
| âm | −3 | báo lỗi |
| không phải số | "năm", `1e3`, `5.5` | báo lỗi |
| rỗng | (trống) | "bắt buộc" |
| khoảng trắng | `"  "` | như rỗng (hoặc hỏi) |

- **Lớp không hợp lệ: mỗi TC chỉ một lớp sai** — gộp hai giá trị sai vào một TC thì lỗi này che lỗi kia.
- Lớp hợp lệ gộp được nhiều trường trong một TC.
- Phân vùng cả **đầu ra**: kết quả rỗng / một / nhiều; thông báo thành công / cảnh báo / lỗi.
- Áp cho mọi target: cờ CLI (hợp lệ/lạ/thiếu), file job (hợp lệ/hỏng/rỗng), câu hỏi cho bot (trong/ngoài tài liệu/độc hại).

## 2. Giá trị biên (BVA)
- **2 giá trị** (R2): mỗi mép thử giá trị mép + giá trị ngay ngoài: `min−1, min, max, max+1`.
- **3 giá trị** (R1): thêm giá trị ngay trong: `min−1, min, min+1, max−1, max, max+1` — bắt lỗi `<` viết thành `<=` ở cả hai phía.
- "Ngay cạnh" theo **đơn vị của miền**: số nguyên ±1; tiền ±0,01 (hoặc ±1đ); thời gian ±1 phút/giây theo độ chính xác lưu; độ dài chuỗi ±1 ký tự (đếm theo ký tự hay byte? — emoji, tiếng Việt có dấu tổ hợp).
- Mép ẩn hay bị quên: đầy trang phân trang (`limit=10` với 10 bản ghi), kích thước file ở giới hạn, 0 và số âm, 00:00 / 23:59, cuối tháng / 29-2, giới hạn kiểu dữ liệu (2³¹−1), giới hạn context LLM, số phần tử tối đa của danh sách.

## 3. Biên nhiều chiều (domain analysis)
Khi các trường **ràng buộc lẫn nhau**, biên nằm trên quan hệ, không nằm trên từng trường:
| Ràng buộc | Điểm trên biên (on) | Điểm ngay ngoài (off) | Điểm trong (in) |
|---|---|---|---|
| từ ngày ≤ đến ngày | từ = đến | từ = đến + 1 ngày | từ < đến |
| giảm giá ≤ tổng đơn | giảm = tổng | giảm = tổng + 1đ | giảm < tổng |
| số người ≤ sức chứa phòng | = sức chứa | sức chứa + 1 | ít hơn |
Với mỗi ràng buộc: 1 điểm on, 1 điểm off (và 1 điểm in dùng chung). Ràng buộc chéo tài liệu không ghi → hỏi.

## 4. Syntax testing — đầu vào có ngữ pháp
Với định dạng có quy tắc (email, số điện thoại, mã số thuế, biển số, URL, ngày, JSON/CSV, lệnh CLI):
1. Viết ngữ pháp từ tài liệu (vd SĐT VN: `0` + 9 chữ số, hoặc `+84` + 9 chữ số).
2. Một TC hợp lệ cho **mỗi nhánh** của ngữ pháp (có `0`, có `+84`).
3. Một TC không hợp lệ cho **mỗi kiểu phá**: thiếu phần tử, thừa phần tử, sai ký tự, sai thứ tự, lặp phần tử,
   phần tử rỗng, ký tự phân cách lạ, khoảng trắng đầu/cuối/giữa, chữ hoa/thường, full-width digit (`０９`).
Ngữ pháp mơ hồ (có nhận dấu cách trong SĐT không?) → điểm hỏi.
