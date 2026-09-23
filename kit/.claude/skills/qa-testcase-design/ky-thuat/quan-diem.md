# Quan điểm test (test viewpoint) — rút từ đặc tả, review, truy vết

> Quan điểm test trả lời "**kiểm cái gì**" cho từng yêu cầu, trước khi viết TC trả lời "**kiểm thế nào**". Người dùng
> duyệt bộ quan điểm (nhanh, một bảng) thì TC viết sau ít lệch hướng và không sót góc. Khuôn: `qa/viewpoints/_TEMPLATE.md`.

## 1. Nguồn hợp lệ — bám đặc tả
Quan điểm chỉ sinh ra từ:
1. **Câu trong đặc tả / tài liệu liên quan** (PRD, story + tiêu chí chấp nhận, API doc, design, quy định nghiệp vụ,
   câu trả lời đã chốt ở `ANALYSIS §5`) → `Nguồn` = file + mục, `Trích nguyên văn` = câu gốc chép y nguyên.
2. **Mô hình đã dựng từ đặc tả** (bảng trạng thái, ma trận quyền, use case ở `ANALYSIS §2/§4`) → trích câu đặc tả mà ô
   đó dựa vào. Ô mô hình mà đặc tả không trả lời → **điểm hỏi**, không phải quan điểm.
3. **Ngoài đặc tả** — checklist `qa-knowledge`, `qa-knowledge/bug-patterns.md`, yêu cầu ngầm ISO 25010, bài học
   `LESSONS.md`: được **đề xuất**, ghi `Nguồn: ngoài đặc tả — <checklist/bài học>`, để `nháp`, trình riêng một nhóm cho
   người dùng quyết. Kỳ vọng cụ thể của quan điểm ngoài đặc tả (con số, thông điệp) vẫn phải hỏi — không tự đặt.

Không có nguồn nào ở trên → **không viết quan điểm đó**. Diễn đạt lại được, nhưng không nói **nhiều hơn** câu trích:
phần thêm (con số, thông điệp, điều kiện) là điểm hỏi `(chờ trả lời #n)`.

## 2. Cách rút quan điểm
Với mỗi REQ trong phạm vi, đi qua các góc dưới — góc nào đặc tả có câu nói tới thì thành một dòng:

| Góc | Hỏi | Kỹ thuật dự kiến |
|---|---|---|
| Luồng chính | Làm được việc đặc tả mô tả, kết quả đúng như câu trích? | `use case` |
| Luồng thay thế / ngoại lệ | Đặc tả nói gì khi hủy, quay lại, lỗi giữa chừng? | `use case` |
| Dữ liệu vào | Miền, độ dài, định dạng, bắt buộc/tuỳ chọn, giá trị mặc định? | `phân vùng`, `giá trị biên`, `syntax` |
| Luật nghiệp vụ | Điều kiện kết hợp → kết quả khác nhau? | `bảng quyết định` |
| Trạng thái | Chuyển nào được, chuyển nào cấm? | `chuyển trạng thái` |
| Quyền | Vai nào làm được, vai nào không (mỗi ô ✗)? | `phân quyền` |
| Hiển thị / thông báo | Chữ, định dạng, thứ tự, trạng thái rỗng đặc tả quy định? | `phân vùng`, `checklist` |
| Tích hợp | Hệ khác nhận/gửi gì, khi hệ kia chậm/lỗi thì sao? | `use case`, `error guessing` |
| Phi chức năng | Con số hiệu năng, a11y, tương thích đặc tả đưa ra? | `phi chức năng`, `hiệu năng`, `a11y` |

Mỗi REQ: ≥ 1 quan điểm `normal` + ≥ 1 `abnormal` (đặc tả không nói gì về đường sai → điểm hỏi "sai thì sao?", và đề
xuất quan điểm abnormal `ngoài đặc tả`). Một quan điểm = một điều cần kiểm, viết thành hành vi quan sát được (không
"hoạt động đúng"). `Hạng mục` gom theo màn/chức năng con để người dùng duyệt nhanh.

## 3. Checklist review bộ quan điểm
**Máy** — `python3 .claude/qa-scripts/qa_check.py vp [<tính năng>]` (trường, mã, REQ có thật, trích dẫn khớp file,
ngoài đặc tả đã duyệt chưa, normal+abnormal mỗi REQ) · `python3 .claude/qa-scripts/qa_check.py src` (nguồn REQ + quan điểm).

**Người / agent đọc:**
- [ ] Mọi REQ trong SCOPE có quan điểm; mọi tiêu chí chấp nhận của story có ít nhất một quan điểm.
- [ ] Mỗi quan điểm đọc câu trích là thấy căn cứ — không suy thêm con số, thông điệp, điều kiện ngoài câu trích.
- [ ] Câu trích đúng nguyên văn và đúng mục (đặc biệt nguồn URL/pdf/docx máy không mở được → `qa-source-check`).
- [ ] Quan điểm ngoài đặc tả tách riêng, ghi rõ lấy từ đâu, đã được người dùng duyệt (DECISIONS).
- [ ] Điểm mơ hồ đã trả lời ở `ANALYSIS §5` được phản ánh; điểm chưa trả lời mang `(chờ trả lời #n)`.
- [ ] Không trùng (cùng REQ, cùng điều kiện, cùng kết quả → gộp); không quá rộng ("kiểm chức năng đặt lịch").
- [ ] Đủ các góc §2 mà đặc tả có nói tới; góc đặc tả im lặng đã thành câu hỏi.
- [ ] `Mức` khớp mức người dùng chốt ở SCOPE §2; `Kỹ thuật dự kiến` dùng tên chuẩn `qa-testcase-design` §1.

Kết quả review trình người dùng:
```
Bộ quan điểm <tính năng>: <n> dòng · REQ phủ <x>/<y> · normal/abnormal <a>/<b>
Nguồn: khớp <k> · máy không kiểm được <m> (đã/ chưa qua qa-source-check) · ngoài đặc tả <o> (chờ duyệt <p>)
Lỗ phủ: <REQ/góc chưa có quan điểm> · Trùng/quá rộng: <…> · Câu hỏi mở: #…
Đề xuất: <thêm/sửa/bỏ> — chờ người dùng duyệt
```

## 4. Từ quan điểm sang TC
- Chỉ quan điểm `duyệt` mới được viết TC (`qa_check.py tc` báo lỗi TC trỏ quan điểm chưa duyệt; run tự bỏ TC đó).
- Một quan điểm → một hoặc nhiều TC (theo mật độ mức R, `qa-testcase-design` §2); mỗi TC trỏ `VP:` về đúng quan điểm.
- Kỳ vọng của TC không được nói nhiều hơn câu trích của quan điểm + câu trả lời ở ANALYSIS §5.
- `python3 .claude/qa-scripts/qa_check.py trace` cho thấy REQ → quan điểm → TC; quan điểm đã duyệt chưa có TC là lỗ.
