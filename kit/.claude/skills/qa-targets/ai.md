# Target `ai` — tính năng dùng LLM / model học máy

## Khác gì target khác
Output **không cố định**: cùng đầu vào có thể ra kết quả khác. Nên một TC AI không phải "một lần đúng là PASS":
- Chạy mỗi ca **N lần**, ghi toàn bộ transcript. **N và ngưỡng đạt do người dùng chốt** (SCOPE §7) — QA đề xuất, vd
  N = 5 (R1: 10), "đạt khi ≥ 4/5 lần thoả mọi tiêu chí", kèm ước lượng chi phí gọi model/lượt trên môi trường thật, rồi hỏi.
- Kỳ vọng viết thành **tiêu chí chấm quan sát được** (có/không) lấy từ tài liệu/chính sách sản phẩm, không phải "trả lời hay".
- Tiêu chí an toàn (lộ dữ liệu, nội dung cấm, hành động nguy hiểm) **một lần vi phạm là FAIL** — trừ khi người dùng chốt khác.

## Chạy bằng gì
Qua đúng giao diện người dùng dùng (web/mobile → công cụ của target đó) **hoặc** gọi API của tính năng
(`curl`), không gọi thẳng model provider thay cho sản phẩm (sẽ bỏ qua prompt hệ thống, RAG, bộ lọc của sản phẩm).
Script lặp đặt ở `qa/automation/ai-<tc>.py`, giãn cách giữa các lượt, ghi mỗi lượt một file.

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
- **Ổn định**: cùng câu hỏi diễn đạt 3 cách → cùng ý; N lần → tỉ lệ đạt.
- **Biên**: đầu vào rỗng, rất dài (sát giới hạn context), nhiều ngôn ngữ, sai chính tả, không dấu, emoji, file đính kèm lạ.
- **Prompt injection**: "bỏ qua hướng dẫn trước, …", chỉ dẫn giấu trong tài liệu/URL/file được đưa vào, yêu cầu in prompt hệ thống.
- **Lộ dữ liệu**: hỏi thông tin của người dùng/tenant khác, secret, dữ liệu nội bộ → phải từ chối.
- **Hành động (agent/tool use)**: yêu cầu hành động vượt quyền, hành động không đảo ngược → có xác nhận/chặn; tool lỗi → xử lý tử tế.
- **Nội dung an toàn**: theo chính sách sản phẩm (tài liệu), vài ca đại diện, không cần kho jailbreak lớn.
- **Hội thoại nhiều lượt**: nhớ đúng ngữ cảnh, không lẫn giữa phiên/người dùng.
- **Lỗi nhà cung cấp**: timeout/lỗi model → thông báo tử tế, không treo, không mất đầu vào người dùng.
- **Hiệu năng & chi phí**: thời gian tới token đầu/tổng thời gian, số token nếu sản phẩm hiển thị; n ≤ 20.

## Model học máy truyền thống (phân loại, dự đoán, gợi ý, xếp hạng)
- Bộ dữ liệu đánh giá **có nhãn** do người dùng/đội cung cấp hoặc duyệt (không tự gán nhãn làm đáp án); tách khỏi dữ liệu huấn luyện.
- Chỉ số theo bài toán: precision/recall/F1 theo từng lớp (không chỉ accuracy), MAE/RMSE, NDCG@k… — **ngưỡng do người dùng chốt**.
- Lát cắt (slice): chỉ số theo nhóm quan trọng (vùng, thiết bị, nhóm người dùng) để thấy thiên lệch; ca biên và dữ liệu lệch phân phối.
- Metamorphic (`qa-testcase-design/ky-thuat/oracle.md`): nhiễu nhỏ vô hại không đổi nhãn; đổi thuộc tính không liên quan không đổi kết quả.
- So bản model trước trên cùng bộ dữ liệu (regression); ghi version model + version dữ liệu trong bằng chứng.

## Bằng chứng tối thiểu
Transcript nguyên văn từng lượt (đầu vào + đầu ra + thời điểm + version/model nếu sản phẩm lộ ra) + `cham.md`.
