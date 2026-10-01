# Oracle · metamorphic · property · fuzz — khi không biết trước đáp án đúng

"Oracle" là cách biết kết quả đúng hay sai. Hệ AI, xếp hạng tìm kiếm, batch dữ liệu lớn, tính toán phức tạp,
mô phỏng… thường **không có đáp án tính tay được** cho mọi đầu vào. Khi đó dùng các oracle dưới.

## 1. Chọn oracle
| Oracle | Dùng khi | Ví dụ |
|---|---|---|
| Đáp án biết trước | Bộ dữ liệu nhỏ tự dựng | batch: 20 dòng + `expected/` |
| Tính tay / công cụ khác | Có cách tính độc lập | tổng tiền tính bằng Python so với hệ thống |
| So bản trước (regression oracle) | Hành vi không được đổi | output v1 vs v2 trên cùng input — hai hệ chạy song song: §7 |
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
Bắn vài request/thao tác giống nhau **cùng lúc** (số lượng đề xuất và hỏi, n nhỏ): script song song có barrier (luồng chờ nhau rồi cùng gửi) hoặc hai
phiên trình duyệt bấm cùng mốc (`Promise.all`). Race không tất định → lặp nhiều lần; số lần đề xuất và hỏi người dùng (cân chi phí và nhịp `qa-targets` §3 mục 4). Oracle là **trạng thái cuối** (số
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
5. **Lần sinh mốc không phải kết quả test** — ghi Nhật ký, không ghi PASS (so chính bản vừa sinh mốc thì luôn khớp; mốc chỉ
   có giá trị cho bản sau). Trước khi so, chuẩn hoá/che trường không tất định (thời điểm, id sinh, thứ tự không cam kết) —
   danh sách trường che do người dùng duyệt. Khớp mốc = PASS; lệch mốc = `BLOCKED` `chờ trả lời #n` tới khi người dùng nói là
   sửa có chủ đích (cập nhật mốc, DECISIONS) hay lỗi (FAIL + BUG).

## 7. So sánh song song hai hệ (back-to-back) · đối soát dữ liệu
Dùng khi hệ **mới** phải làm giống hệ **cũ**: di trú dữ liệu, đổi máy chủ/hạ tầng/cloud, nâng OS/DB/runtime/framework,
viết lại bằng công nghệ khác, chạy song song trước khi tắt hệ cũ. Oracle là **hệ cũ** — nên tài liệu mỏng vẫn kiểm
được, nhưng lỗi có sẵn ở hệ cũ thì không bắt được (nói rõ với người dùng ở SCOPE §1). Khác §6: §6 so một hệ qua thời
gian, ở đây so hai hệ cùng lúc.

**Chốt với người dùng trước khi viết TC** (thiếu điều nào → `ANALYSIS §5`, không tự chọn):
1. **Phạm vi so**: màn hình / output file (CSV, PDF, Excel, in) / dữ liệu lưu (DB, file) / API / log — mỗi thứ là một lớp so riêng.
2. **"Giống" nghĩa là gì**: khớp từng byte, khớp sau chuẩn hoá, hay chỉ khớp nghĩa nghiệp vụ.
3. **Danh sách khác biệt chấp nhận được** — người dùng duyệt, ghi `DECISIONS`, mỗi dòng: trường/vùng · kiểu khác · lý do.
   Ứng viên hay gặp (đề xuất, **không** tự áp): thời điểm/ID sinh tự động · định dạng ngày giờ, số thập phân, phân cách hàng
   nghìn · thứ tự dòng khi đặc tả không cam kết thứ tự · font/khoảng cách/kích thước cửa sổ · encoding và ký tự xuống dòng
   của file xuất · làm tròn số thực (cần dung sai cụ thể).
4. **Ai phán xử khác biệt mới** (ngoài danh sách) — kết quả của TC đó chờ người này, không do QA quyết.
5. **Đối soát dữ liệu di trú** có trong phạm vi không, và được đọc DB hai bên ở mức nào (SCOPE §7).

**Dựng phép so**
- **Cùng đầu vào**: hai hệ chạy trên cùng bộ dữ liệu (cùng bản sao/backup, cùng mốc thời gian); TC có ghi trạng thái → khôi
  phục dữ liệu hai bên về cùng điểm trước mỗi lượt, hoặc dùng bản ghi `QA-<run-id>-` tạo song song ở cả hai. Không cùng
  đầu vào thì khác biệt không nói lên gì.
- **Cùng thao tác**: một TC = một chuỗi bước chạy y hệt trên A (cũ) và B (mới); ghi rõ môi trường + phiên bản từng bên.
- **Ngày giờ**: chức năng phụ thuộc ngày (cuối tháng, cuối năm, hạn) → hai bên cùng "ngày nghiệp vụ" (tham số ngày của
  sản phẩm); không tự đổi giờ máy dùng chung.
- **Chuẩn hoá trước khi so** chỉ theo danh sách đã duyệt (mục 3) — script chuẩn hoá đặt ở `qa/automation/`, dùng cho cả hai
  bên, giữ file gốc chưa chuẩn hoá làm bằng chứng.

**Vùng hay lệch khi đổi nền tảng** (gợi ý quan điểm — `Nguồn: ngoài đặc tả`, người dùng duyệt): bảng mã/encoding và chữ
đặc biệt (ký tự ngoài bảng mã cũ, chữ ghép, emoji) · collation → thứ tự sắp xếp, tìm kiếm phân biệt hoa/thường, dấu ·
kiểu số/ngày của DB (độ chính xác, múi giờ, NULL vs chuỗi rỗng) · làm tròn và phép chia · thư viện in/xuất file (ngắt
trang, font, định dạng ô Excel) · đường dẫn/quyền file, chia sẻ mạng · khoá và giao dịch khi nhiều người dùng · tác vụ
theo lịch (cron/Task Scheduler) · cấu hình mang sang (chuỗi kết nối, cài đặt người dùng) · thông báo lỗi và log.

**Đối soát dữ liệu di trú** (`Kỹ thuật: đối soát dữ liệu`) — chỉ đọc, theo quyền SCOPE §7:
1. Số dòng mỗi bảng/thực thể A vs B (kèm điều kiện lọc nếu chỉ di trú một phần).
2. Tổng kiểm cho cột quan trọng: tổng tiền, đếm theo trạng thái, min/max ngày, đếm NULL.
3. Checksum từng dòng theo khoá (băm các cột đã chuẩn hoá) → liệt kê khoá thiếu / thừa / khác.
4. Mẫu dòng biên đọc tận mắt: dòng có ký tự đặc biệt, giá trị cực trị, NULL, dữ liệu rất cũ.
5. Ràng buộc còn đúng ở B: khoá ngoại không mồ côi, duy nhất, giá trị trong miền.
Truy vấn đặt ở `qa/scripts/`, kết quả hai bên lưu nguyên văn.

**Kết quả** (`Kỹ thuật: so sánh song song`): khớp, hoặc chỉ lệch trong danh sách chấp nhận = `PASS` · lệch ngoài danh sách =
`BLOCKED` `chờ trả lời #n` gửi người phán xử (mục 4) → họ nói lỗi thì `FAIL` + BUG, nói chấp nhận thì thêm vào danh sách
(DECISIONS) rồi chấm lại · bên **cũ** cũng sai so với đặc tả → ghi phát hiện riêng, không tính là lệch của hệ mới.
**Bằng chứng theo cặp**: `A-…` / `B-…` cùng số bước (ảnh, file xuất, kết quả truy vấn) + file diff sau chuẩn hoá + môi
trường/phiên bản từng bên.
