# Phân tích & review tài liệu — kỹ thuật tĩnh

> Tìm lỗi trong tài liệu (và code) **trước khi** có dòng code chạy là rẻ nhất. Mọi phát hiện ghi `ANALYSIS §5`
> (mơ hồ/thiếu/mâu thuẫn) kèm đề xuất + rủi ro, rồi **hỏi** người dùng — không tự điền câu trả lời.

## 1. Quy trình một lượt review
1. **Đọc lướt toàn bộ** để nắm phạm vi, thuật ngữ, vai, tính năng — ghi bảng thuật ngữ nếu có từ lạ/viết tắt.
2. **Đọc kỹ theo góc nhìn** (§3) — mỗi góc một lượt.
3. **Chấm từng yêu cầu** theo tiêu chí chất lượng (§2) → REQ + điểm hỏi.
4. **Duyệt yêu cầu ngầm** (§4) — những gì tài liệu không nói nhưng sản phẩm phải có.
5. **Dựng mô hình** để lộ lỗ: vai × hành động (ANALYSIS §2), vòng đời trạng thái, use case (§6), ma trận CRUD.
   Ô nào tài liệu không trả lời được → điểm hỏi.
6. **Đối chiếu code** (nếu có): endpoint/màn/cờ có trong code mà không có trong tài liệu, validate/giới hạn trong
   code khác con số tài liệu → điểm hỏi (không lấy code làm yêu cầu).
7. **Rủi ro & ảnh hưởng** (§7, §8) → đưa vào kế hoạch.
8. **Trình kết quả** (§9) và hỏi một lượt.

## 2. Tiêu chí chất lượng của một yêu cầu
| Tiêu chí | Hỏi | Dấu hiệu hỏng |
|---|---|---|
| Kiểm được (testable) | Có kết quả quan sát được, có con số? | "nhanh", "thân thiện", "hợp lý", "đúng" |
| Rõ ràng (unambiguous) | Chỉ một cách hiểu? | từ yếu (§2.1), đại từ mơ hồ ("nó", "cái này") |
| Đầy đủ (complete) | Nói cả đường sai, giới hạn, quyền, trạng thái rỗng? | chỉ có happy path; "v.v.", "…", "TBD" |
| Nhất quán (consistent) | Khớp với yêu cầu khác, design, API doc, code? | hai nơi hai con số, hai tên cho một thứ |
| Khả thi (feasible) | Làm được trong ràng buộc kỹ thuật/thời gian? | mâu thuẫn vật lý ("realtime" qua email) |
| Truy vết được | Biết đến từ đâu (ticket, người yêu cầu), sẽ có TC nào? | yêu cầu mồ côi |
| Cần thiết / đúng chỗ | Là yêu cầu hay là giải pháp thiết kế trá hình? | "dùng dropdown" thay vì "chọn một trong N" |
| Đơn nhất (singular) | Một câu một yêu cầu? | "và", "đồng thời", nhiều động từ trong một câu → tách thành nhiều REQ |

**User story** thêm **INVEST**: Independent · Negotiable · Valuable · Estimable · Small · Testable. Story không có
tiêu chí chấp nhận → đề xuất tiêu chí dạng **Given–When–Then** và hỏi xác nhận (ví dụ dưới là **đề xuất** —
thông điệp/con số trong đó chỉ thành kỳ vọng khi người dùng xác nhận):
```
Given khách đã đăng nhập và giỏ có 2 sản phẩm
When  áp mã GIAM10 hết hạn
Then  hiện "Mã đã hết hạn", tổng tiền không đổi
```

### 2.1 Từ yếu — gặp là soi
nhanh · chậm · dễ · thân thiện · trực quan · hợp lý · phù hợp · tối ưu · hiệu quả · linh hoạt · ổn định · an toàn ·
đúng · chuẩn · bình thường · hỗ trợ · xử lý · quản lý · có thể · nên · tuỳ chọn · nếu cần · khi cần · thường ·
thông thường · hầu hết · tất cả · mọi · không bao giờ · luôn luôn · v.v. · … · và/hoặc · tương tự · như trên · TBD ·
tử tế · rõ ràng · mượt · OK · đủ lâu · kịp thời · gần như ngay lập tức.
Mỗi từ yếu → hỏi: con số là bao nhiêu? hành vi quan sát được là gì? "tất cả" gồm những gì, có ngoại lệ không?

## 3. Đọc theo góc nhìn (perspective-based reading)
| Góc | Hỏi |
|---|---|
| Người dùng cuối | Tôi làm được việc của mình không? Sai thì tôi biết sửa thế nào? Màn rỗng/lần đầu ra sao? |
| Tester | Mỗi câu kiểm được bằng gì? Kỳ vọng đo được không? Dữ liệu/tài khoản nào cần? |
| Dev | Đủ để code không? Giới hạn, định dạng, lỗi trả về, trạng thái được nêu chưa? |
| Vận hành / hỗ trợ | Log, cảnh báo, cấu hình, nâng cấp, rollback, dữ liệu cũ thì sao? |
| Bảo mật & quyền | Ai được làm gì? Dữ liệu nhạy cảm ở đâu? Người ngoài/tenant khác chạm được gì? |
| Chủ sản phẩm / nghiệp vụ | Luật nghiệp vụ, tiền, hạn chót, pháp lý — có chỗ nào mâu thuẫn quy định? |

## 4. Yêu cầu ngầm — duyệt theo ISO 25010 (bản 2023)
Tài liệu hay chỉ viết chức năng. Với mỗi đặc tính, hỏi có yêu cầu không, con số là gì, hay để ngoài phạm vi (bảng
ANALYSIS §7 có đúng các dòng này):
**Chức năng** (đủ, đúng, phù hợp) · **Hiệu năng** (thời gian phản hồi, dung lượng, tài nguyên) · **Tương thích**
(cùng tồn tại và tương tác với hệ khác, API/bản cũ) · **Khả dụng / khả năng tương tác** (dễ học, phòng lỗi, a11y — WCAG
mức nào) · **Tin cậy** (sẵn sàng, chịu lỗi, khôi phục, sao lưu) · **Bảo mật** (xác thực, phân quyền, bảo mật dữ liệu,
nhật ký kiểm toán, quyền riêng tư) · **Bảo trì** (log, cấu hình, khả năng kiểm thử) · **Linh hoạt** (cài đặt, nâng cấp,
chạy trên trình duyệt/OS/thiết bị khác, bản địa hoá/múi giờ) · **An toàn** (hệ có thể gây hại người/tài sản: IoT, y tế,
xe, điều khiển thiết bị — trạng thái an toàn khi lỗi, cảnh báo).
Ghi vào `ANALYSIS §7`. Không có con số → điểm hỏi, không tự đặt.

## 5. Example mapping — làm rõ bằng ví dụ
Khi một luật nghiệp vụ khó nói rõ, hỏi người dùng bằng **ví dụ cụ thể** thay vì câu hỏi trừu tượng:
```
Luật: Khách thành viên được giảm 10% cho đơn từ 500k
  Ví dụ 1: đơn 500.000đ, thành viên → giảm 50.000đ?          (biên đúng mép)
  Ví dụ 2: đơn 499.999đ, thành viên → không giảm?
  Ví dụ 3: đơn 600.000đ gồm 100.000đ phí ship → tính 500k hay 600k?   (câu hỏi mở)
  Ví dụ 4: thành viên hết hạn hôm nay → có giảm không?               (câu hỏi mở)
```
Ví dụ người dùng xác nhận → thành TC trực tiếp. Ví dụ gây tranh cãi → điểm hỏi quan trọng nhất.

## 6. Mô hình hoá để lộ lỗ
- **Use case**: luồng chính / thay thế / ngoại lệ từng bước (`qa-testcase-design/ky-thuat/use-case.md`) — bước nào tài liệu không nói xử lý khi hỏng?
- **Trạng thái**: bảng trạng thái × sự kiện (`qa-testcase-design/ky-thuat/trang-thai.md`) — ô nào không biết kết quả?
- **Vai × hành động** và **CRUD** (`qa-testcase-design/ky-thuat/bang-quyet-dinh.md`) — ô nào không ai nói?
- **Luồng dữ liệu**: dữ liệu vào từ đâu, lưu ở đâu, hiện ở những màn nào, xuất đi đâu — sửa ở một chỗ thì mọi chỗ cập nhật?

## 7. Phân tích rủi ro sản phẩm
Mỗi tính năng/REQ chấm hai trục, 1–3:
| REQ | Xác suất lỗi (mới/phức tạp/tích hợp/đổi nhiều = cao) | Thiệt hại (tiền/dữ liệu/quyền/pháp lý/số người dùng) | Rủi ro | Mức |
|---|---|---|---|---|
| REQ-TT-1 thanh toán | 3 | 3 | 9 | R1 |
| REQ-HS-2 đổi ảnh đại diện | 1 | 1 | 1 | R3 |
Mốc chấm:
| Điểm | Xác suất lỗi | Thiệt hại |
|---|---|---|
| 1 | không đổi, đơn giản, đã chạy ổn | thẩm mỹ, lặt vặt |
| 2 | sửa một phần, logic có nhánh | tính năng hỏng, có đường vòng |
| 3 | mới, tích hợp ngoài, đổi nhiều, đồng thời | mất tiền / mất dữ liệu / lộ quyền / pháp lý / sập luồng lõi |

Rủi ro 6–9 → R1 · 3–4 → R2 · 1–2 → R3, **nhưng Thiệt hại = 3 thì tối thiểu R1** bất kể xác suất (một REQ thanh toán ít
thay đổi vẫn là R1). Điểm do QA chấm là **đề xuất** — trình người dùng ở bước chốt scope; mức chính thức là mức người
dùng xác nhận ở SCOPE §2.

## 8. Phân tích ảnh hưởng — chọn regression
Khi có bản mới: đọc changelog/release note/ticket + `git diff`/`git log` giữa bản cũ và mới (nếu có code) →
liệt kê **tính năng bị chạm trực tiếp** + **tính năng dùng chung thành phần bị chạm** (cùng bảng dữ liệu, cùng API,
cùng màn, cùng thư viện) → regression = TC `Regression: có` của các tính năng đó + TC R1 luồng lõi + TC tái hiện
bug cũ quanh vùng đó. Không đọc được thay đổi → hỏi người dùng đã đổi gì, hoặc đề xuất regression toàn bộ R1.

## 9. Trình kết quả review
```
Tài liệu đã đọc: <danh sách> · Code đã đối chiếu: <phạm vi>
REQ: <n> (theo tính năng) · Yêu cầu ngầm đã nêu: <n>
Điểm hỏi (xếp theo mức chặn): #1 … (đề xuất / rủi ro nếu sai) · #2 …
Lệch tài liệu ↔ code: <danh sách>
Rủi ro đề xuất: R1 <…> · R2 <…> · R3 <…>
```
