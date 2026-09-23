# Oracle · metamorphic · property · fuzz — khi không biết trước đáp án đúng

"Oracle" là cách biết kết quả đúng hay sai. Hệ AI, xếp hạng tìm kiếm, batch dữ liệu lớn, tính toán phức tạp,
mô phỏng… thường **không có đáp án tính tay được** cho mọi đầu vào. Khi đó dùng các oracle dưới.

## 1. Chọn oracle
| Oracle | Dùng khi | Ví dụ |
|---|---|---|
| Đáp án biết trước | Bộ dữ liệu nhỏ tự dựng | batch: 20 dòng + `expected/` |
| Tính tay / công cụ khác | Có cách tính độc lập | tổng tiền tính bằng Python so với hệ thống |
| So bản trước (regression oracle) | Hành vi không được đổi | output v1 vs v2 trên cùng input |
| Nhất quán nội tại | Các con số phải khớp nhau | tổng dòng chi tiết = dòng tổng; đếm list = số hiện ở badge |
| **Metamorphic** | Không biết đáp án nhưng biết quan hệ giữa các lần chạy | xem §2 |
| **Property** | Biết tính chất luôn đúng | xem §3 |
| Tiêu chí chấm (rubric) | Output ngôn ngữ tự nhiên | AI — `qa-targets/ai.md` |

## 2. Metamorphic testing
Đổi đầu vào theo một phép biến đổi mà **quan hệ đầu ra đã biết**, rồi so hai lần chạy:
| Hệ | Biến đổi đầu vào | Quan hệ đầu ra phải giữ |
|---|---|---|
| Tìm kiếm | thêm bộ lọc | kết quả mới ⊆ kết quả cũ |
| Tìm kiếm | đổi hoa/thường, có dấu/không dấu (nếu tài liệu nói không phân biệt) | cùng kết quả |
| Batch/tổng hợp | đảo thứ tự dòng đầu vào | tổng/đếm không đổi |
| Batch | nhân đôi dữ liệu | tổng gấp đôi, đếm gấp đôi |
| Tính giá | đổi đơn vị tiền theo tỉ giá | kết quả đổi đúng tỉ giá |
| AI phân loại/tóm tắt | diễn đạt lại câu hỏi, thêm câu thừa vô hại | cùng nhãn / cùng ý chính |
| AI trả lời theo tài liệu | bỏ đoạn tài liệu chứa đáp án | phải nói không biết (không bịa) |
| Xếp hạng | thêm một mục kém liên quan | thứ tự các mục cũ không đổi |
Mỗi quan hệ một TC: chạy nguồn + chạy biến đổi, bằng chứng cả hai, kết luận theo quan hệ.

**Quan hệ metamorphic là kỳ vọng** — phải có cơ sở trong tài liệu/thiết kế hoặc được người dùng xác nhận, và ghi điều
kiện áp dụng: "nhân đôi dữ liệu → tổng gấp đôi" sai nếu job khử trùng/upsert theo khoá; "đổi tiền theo tỉ giá" cần dung
sai làm tròn; "thêm mục kém liên quan không đổi thứ tự cũ" không đúng với BM25/IDF hay xếp hạng học máy; "bỏ đoạn chứa
đáp án → phải nói không biết" chỉ đúng khi sản phẩm cam kết chỉ trả lời từ tài liệu. Không chắc → hỏi.

**Oracle heuristic HICCUPPS** (History, Image, Comparable products, Claims, User expectations, Product, Purpose,
Standards) — dùng khi khám phá để nhận ra "có gì đó lạ" (lệch bản trước, lệch sản phẩm tương tự, lệch lời quảng cáo…).
Chỉ là **lý do mở điểm hỏi hoặc viết TC**, không phải kỳ vọng.

## 3. Property (tính chất luôn đúng)
Encode rồi decode = ban đầu · sắp xếp xong thì tăng dần và cùng số phần tử · tổng tiền không âm · id duy nhất ·
chạy lại idempotent · output luôn là JSON hợp lệ. Thử tính chất trên nhiều đầu vào sinh ra (§4).

## 4. Fuzz / sinh đầu vào
Cho parser, upload, API, CLI, prompt: sinh hàng loạt đầu vào lệch (ngẫu nhiên có seed, đột biến từ đầu vào hợp lệ:
cắt cụt, lặp, đảo byte, chèn ký tự đặc biệt/unicode/null, số cực trị) bằng script nhỏ trong `qa/automation/`.
Oracle: **không crash, không 500, không treo, lỗi có thông điệp**, và property ở §3.

## 5. Đồng thời (race) — dựng được, chạy được
Bắn 2–5 request/thao tác giống nhau **cùng lúc**: script song song có barrier (luồng chờ nhau rồi cùng gửi) hoặc hai
phiên trình duyệt bấm cùng mốc (`Promise.all`). Race không tất định → lặp nhiều lần; số lần đề xuất và hỏi người dùng (cân chi phí và nhịp `qa-targets` §3). Oracle là **trạng thái cuối** (số
bản ghi, số tiền, số lượt còn lại, trạng thái đơn), không phải response từng request. Chỉ trên dữ liệu test, n nhỏ.
`Kỹ thuật: đồng thời`. Luật an toàn: n nhỏ, giãn
cách, chỉ trên môi trường được phép; ghi seed để tái hiện. Đầu vào gây lỗi → rút gọn tối thiểu rồi ghi bug.

## 6. Chốt hành vi hiện tại (characterization / golden master)
Dùng khi **không ai biết luật đúng** (job cũ không tài liệu, hệ di sản) nên REQ rút từ code cứ mãi `(chờ trả lời #n)`:
1. Đề xuất với người dùng lấy hành vi hiện tại làm **mốc**; nói rõ hệ quả: test sẽ bắt thay đổi, không bắt lỗi nghiệp vụ sẵn có.
2. Người dùng đồng ý (DECISIONS trích nguyên văn) → REQ ghi `(mốc hành vi hiện tại — DECISIONS #n)`, gỡ nhãn chờ.
3. Chạy bản hiện tại trên bộ dữ liệu cố định `qa/testdata/<TC-ID>/input/` để sinh `expected/`; người dùng duyệt mẫu
   `expected/` rồi mới dùng. `Kỹ thuật: mốc hành vi`.
4. Kết quả về sau là "khớp mốc / lệch mốc" — lệch mốc → hỏi người dùng đó là sửa có chủ đích hay lỗi.
