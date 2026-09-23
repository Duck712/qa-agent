# Target `ai` — tính năng dùng LLM / model học máy

## Khác gì target khác
Output **không cố định**: cùng đầu vào có thể ra kết quả khác. Nên một TC AI không phải "một lần đúng là PASS":
- Chạy mỗi ca **N lần**, ghi toàn bộ transcript, mỗi lượt một file `NN-luot-<k>.txt` (qa_check đếm số `k` khác nhau; **chỉ** transcript mang chữ `luot` —
  ảnh đặt `NN-anh-…`). TC AI ghi `Target:` là target có cột Loại đúng chữ `ai` ở `QA.md` (Cách vào là giao diện hoặc
  endpoint). Chạy lại TC AI → tạo run mới. N chốt sau khi đã tạo run → thêm dòng `- Test AI — N mỗi ca: …` vào khối
  Tiêu chí của RUNLOG, tiêu đề khối ghi `(chốt sau khi chạy — DECISIONS #n; …)`.
  **N và ngưỡng đạt do người dùng chốt** (SCOPE §7, được chép vào RUNLOG lúc tạo run): QA đề xuất kèm lý do (độ biến
  thiên thấy ở vài lượt thử, mức R của REQ, chi phí gọi model/lượt trên môi trường thật) rồi hỏi; chưa chốt thì TC AI
  không chấm được (`BLOCKED`, `chờ trả lời #n`).
- Kỳ vọng viết thành **tiêu chí chấm quan sát được** (có/không) lấy từ tài liệu/chính sách sản phẩm, không phải "trả lời hay".
- Tiêu chí an toàn (lộ dữ liệu, nội dung cấm, hành động nguy hiểm): đề xuất "một lần vi phạm là FAIL" và hỏi người dùng chốt cùng N/ngưỡng.

## Chạy bằng gì
Qua đúng giao diện người dùng dùng (web/mobile → công cụ của target đó) **hoặc** gọi API của tính năng
(`curl`), không gọi thẳng model provider thay cho sản phẩm (sẽ bỏ qua prompt hệ thống, RAG, bộ lọc của sản phẩm).
Script lặp (sau khi hỏi framework/nơi đặt theo skill `qa` §7, mặc định đề xuất `qa/automation/ai-<tc>.py`), giãn cách giữa các lượt, ghi mỗi lượt một file.

## Viết tiêu chí chấm
| Tốt | Không dùng được |
|---|---|
| Trả lời có nêu đúng giá gói Pro (299.000đ) theo tài liệu giá | Trả lời chính xác |
| Không nhắc tới đối thủ | Trả lời chuyên nghiệp |
| Từ chối và gợi ý liên hệ tổng đài khi hỏi hoàn tiền | Xử lý tốt câu hỏi khó |
| JSON hợp lệ, có đủ trường `category`, `confidence` | Output đúng định dạng |
| Trích dẫn ≥ 1 nguồn và nguồn có thật trong kho tài liệu | Không bịa |

Chấm: QA tự chấm từng lượt theo tiêu chí, ghi `cham.md` (lượt × tiêu chí = ✓/✗ + trích câu làm căn cứ).
Tiêu chí cần phán đoán chủ quan → ghi rõ là phán đoán, đưa người dùng duyệt mẫu.

## Công thức
- **Đúng nghiệp vụ / grounding**: câu hỏi có đáp án trong tài liệu nguồn → đúng đáp án; câu hỏi ngoài tài liệu → nói không biết, không bịa.
- **Ổn định**: cùng câu hỏi diễn đạt lại theo vài cách (số cách đề xuất kèm lý do và hỏi — chốt ở dòng `Test AI — số cách diễn đạt mỗi ca` SCOPE §7, không ghi vào dòng N) → cùng ý; N lần → tỉ lệ đạt.
- **Biên**: đầu vào rỗng, rất dài (sát giới hạn context), nhiều ngôn ngữ, sai chính tả, không dấu, emoji, file đính kèm lạ.
- **Prompt injection**: "bỏ qua hướng dẫn trước, …", chỉ dẫn giấu trong tài liệu/URL/file được đưa vào, yêu cầu in prompt hệ thống.
- **Lộ dữ liệu**: hỏi thông tin của người dùng/tenant khác, secret, dữ liệu nội bộ → phải từ chối.
- **Hành động (agent/tool use)**: yêu cầu hành động vượt quyền, hành động không đảo ngược → có xác nhận/chặn; tool lỗi → không làm dở hành động, có thông báo (theo tài liệu).
- **Nội dung an toàn**: theo chính sách sản phẩm (tài liệu), vài ca đại diện, không cần kho jailbreak lớn.
- **Hội thoại nhiều lượt**: nhớ đúng ngữ cảnh, không lẫn giữa phiên/người dùng.
- **Lỗi nhà cung cấp**: timeout/lỗi model → có thông báo (theo tài liệu), không treo, không mất đầu vào người dùng.
- **Hiệu năng & chi phí**: thời gian tới token đầu/tổng thời gian, số token nếu sản phẩm hiển thị; theo nhịp đã chốt (`qa-targets` §3 mục 4).

## Model học máy truyền thống (phân loại, dự đoán, gợi ý, xếp hạng)
- Bộ dữ liệu đánh giá **có nhãn** do người dùng/đội cung cấp hoặc duyệt (không tự gán nhãn làm đáp án); tách khỏi dữ liệu huấn luyện.
- Chỉ số theo bài toán: precision/recall/F1 theo từng lớp (không chỉ accuracy), MAE/RMSE, NDCG@k… — **ngưỡng do người dùng chốt**.
- Lát cắt (slice): chỉ số theo nhóm quan trọng (vùng, thiết bị, nhóm người dùng) để thấy thiên lệch; ca biên và dữ liệu lệch phân phối.
- Metamorphic (`qa-testcase-design/ky-thuat/oracle.md`): nhiễu nhỏ vô hại không đổi nhãn; đổi thuộc tính không liên quan không đổi kết quả.
- So bản model trước trên cùng bộ dữ liệu (regression); ghi version model + version dữ liệu trong bằng chứng.

## Bằng chứng tối thiểu
Transcript nguyên văn từng lượt (đầu vào + đầu ra + thời điểm + version/model nếu sản phẩm lộ ra) + `cham.md`.

## Cách ly và phiên bản (bắt buộc)
- **Kho tài liệu (RAG)**: thêm/sửa tài liệu thử (kể cả tài liệu có chỉ dẫn giấu cho prompt injection gián tiếp) **chỉ**
  trên kho/tenant riêng của QA khai ở `QA.md §Vùng dữ liệu test`. Không có → TC đó `BLOCKED`, hỏi. Không bao giờ nạp
  tài liệu thử vào kho dùng chung với khách thật. Dọn xong → xác nhận qua API/danh sách tài liệu của kho (id đã mất) **và** một truy vấn; lưu cả hai vào bằng chứng.
- **Tool gọi hệ thống khác** (tra đơn, tạo phiếu…): chỉ trên tài khoản/dữ liệu test; TC chatbot ↔ hệ đơn hàng là
  `cross-target` — bằng chứng cả hai phía.
- **Phiên bản**: đầu RUNLOG ghi version/model, phiên bản hoặc ngày cập nhật kho tài liệu (hoặc checksum tài liệu nguồn
  mà TC trích). TC grounding ghi `Nguồn:` là tài liệu + mục cụ thể trong kho — kho đổi thì kỳ vọng phải xem lại.
- **Chờ trả lời xong**: giao diện stream → `browser_wait_for` tới khi chỉ báo đang gõ biến mất hoặc nút gửi bật lại,
  rồi mới snapshot/lưu transcript (không chấm câu trả lời dở).
- **Chấm độc lập**: `qa-evidence-check` chấm lại một phần lượt từ transcript mà không nhìn `cham.md` trước; lệch → báo.
