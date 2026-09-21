---
name: spec-testcase-design
description: >
  Thiết kế test case có kỷ luật cho SPEC — bốn kỹ thuật kinh điển (phân vùng tương đương, giá trị biên,
  bảng quyết định, chuyển trạng thái) áp vào tài liệu bàn giao của dev đã dịch, kèm cách chọn kỹ thuật theo mức rủi ro
  R1/R2/R3 và cách viết TC đúng khuôn máy đếm được. Nạp skill này ở pha P (/spec-prepare) khi viết test case,
  hoặc khi QA cần bổ sung TC bằng tay. Mục tiêu: mỗi TC bắt được một kiểu hỏng cụ thể, không đẻ TC cho đủ số.
---

# spec-testcase-design — viết test case có kỷ luật

> Viết TC theo cảm tính thì hoặc thiếu (bỏ sót ca hỏng), hoặc thừa (100 TC chạy mãi không hết mà vẫn
> lọt bug). Bốn kỹ thuật dưới đây trả lời câu "bao nhiêu TC là đủ" bằng cấu trúc, không bằng cảm giác.

## 0. Chọn kỹ thuật theo mức rủi ro

Mức R lấy ở `TEST-STRATEGY §4` (bảng risk-based):

| Mức | Kỹ thuật phải dùng | Ý nghĩa |
|---|---|---|
| **R1** | Cả bốn: phân vùng + biên + bảng quyết định + chuyển trạng thái | Sai là mất tiền/dữ liệu/lộ quyền — phủ kín |
| **R2** | Phân vùng + biên (2 ca tiêu biểu) | Sai thì khó chịu, có đường vòng |
| **R3** | Happy path | Sai thì lặt vặt |

Mọi TC viết vào `context/testcases/` theo khuôn `_TC-TEMPLATE.md` — **dòng meta phải đúng định dạng** (`AC: · Loại: · Kiểu: · Tầng: · Mức: · Regression: · Release vào:`), nếu không TC vô hình với gate.

**Mỗi AC ≥1 TC `Kiểu: normal` (đường đúng) VÀ ≥1 TC `Kiểu: abnormal` (đầu vào sai, thiếu quyền, trạng thái không hợp lệ, lỗi mạng…)** — AC chỉ có happy path là AC chưa được kiểm. `python3 scripts/review_tc.py` đếm luật này cùng các lỗi hình thức khác; chạy sau mỗi đợt viết TC.

**Trước khi viết, mở skill `spec-knowledge`**: checklist theo đối tượng (form, đăng nhập/phân quyền, upload, API, ca bất thường xuyên hệ thống) + `bug-patterns.md` là kinh nghiệm đã tích luỹ qua nhiều dự án — bốn kỹ thuật dưới đây cho biết *cách* nghĩ ra ca đủ, checklist cho biết *chỗ nào* dev hay sai. Cộng thêm `context/LESSONS.md` của các release trước.

---

## 1. Phân vùng tương đương

**Ý tưởng**: chia miền đầu vào thành các lớp mà mọi giá trị trong lớp cư xử như nhau — mỗi lớp một TC đại diện là đủ, thử thêm 50 giá trị cùng lớp không bắt thêm được gì.

**Cách làm**: với mỗi trường đầu vào, liệt kê lớp **hợp lệ** và lớp **không hợp lệ**.

Ví dụ ô "số lượng thợ" (1–20):

| Lớp | Đại diện | Kỳ vọng |
|---|---|---|
| hợp lệ | 5 | nhận |
| dưới miền | 0 | báo lỗi "tối thiểu 1" |
| trên miền | 25 | báo lỗi "tối đa 20" |
| âm | −3 | báo lỗi |
| không phải số | "năm" | báo lỗi |
| rỗng | (để trống) | báo lỗi bắt buộc |

→ 6 TC (hoặc 1 TC nhiều bước nếu form giữ được trạng thái), không phải 20.

**Bẫy hay gặp**: quên lớp "rỗng" và lớp "khoảng trắng" — hai lớp khác nhau ở phần lớn sản phẩm.

---

## 2. Giá trị biên

**Ý tưởng**: lỗi tụ ở mép. Với mỗi miền hợp lệ `[min, max]`, thử **min−1, min, max, max+1**.

Ví dụ khung giờ đặt lịch 08:00–18:00:

| Giá trị | Kỳ vọng |
|---|---|
| 07:59 | từ chối |
| 08:00 | nhận (mép dưới) |
| 18:00 | nhận (mép trên) |
| 18:01 | từ chối |

Áp cho mọi thứ có mép: độ dài chuỗi (0, 1, max, max+1 ký tự), số lượng bản ghi (danh sách rỗng, 1, đầy trang, tràn trang), ngày (hôm qua, hôm nay, ngày cuối tháng, 29/2), tiền (0, nhỏ nhất, lớn nhất).

**Bẫy**: mép "đầy trang" của phân trang hay bị quên — 10 bản ghi với `limit=10` là ca sinh lỗi off-by-one kinh điển.

---

## 3. Bảng quyết định — sinh TC phân quyền từ ma trận

**Ý tưởng**: khi kết quả phụ thuộc **tổ hợp** điều kiện, lập bảng tổ hợp rồi mỗi dòng một TC.

Đây chính là cách sinh TC loại `phân quyền` từ `PERSONAS §2`: **mỗi ô là một dòng của bảng quyết định**, mỗi ô ✗ là một TC bắt buộc.

| Hành động | Vai | Chủ sở hữu bản ghi | Kỳ vọng | TC |
|---|---|---|---|---|
| Sửa lịch hẹn | owner | của gara mình | cho | TC-…-011 |
| Sửa lịch hẹn | owner | gara khác | **chặn 403** | TC-…-012 |
| Sửa lịch hẹn | mechanic | bất kỳ | **chặn 403** | TC-…-013 |
| Sửa lịch hẹn | chưa đăng nhập | — | **chặn 401** | TC-…-014 |

TC ô ✗ ghi thêm nhãn `Ô ma trận: <hành động> × <vai> = ✗` — gate P đếm nhãn này.

Cùng kỹ thuật cho tổ hợp nghiệp vụ: (trạng thái đơn × loại khách × có mã giảm giá) → cho/không cho huỷ.

**Bẫy**: chỉ thử "vai bị cấm bấm nút" mà không **gọi thẳng API** — UI giấu nút không phải là chặn.

---

## 4. Chuyển trạng thái — nguồn của TC workflow

**Ý tưởng**: vẽ vòng đời bản ghi, rồi phủ **mọi chuyển hợp lệ** (mỗi cái một TC) và **các chuyển bị cấm** (mỗi cái một TC — phải bị chặn).

```
nháp ──gửi──► chờ duyệt ──duyệt──► đã duyệt ──thực hiện──► hoàn tất
  │               │                    │
  └──xoá──►(hết)  └──từ chối──► nháp   └──huỷ──► đã huỷ
```

| Chuyển | Vai | Hợp lệ? | TC |
|---|---|---|---|
| nháp → chờ duyệt | owner | ✓ | TC-…-021 |
| chờ duyệt → đã duyệt | manager | ✓ | TC-…-022 |
| nháp → hoàn tất | bất kỳ | **✗ — phải chặn** | TC-…-023 |
| đã huỷ → thực hiện | bất kỳ | **✗ — phải chặn** | TC-…-024 |

Nguồn vẽ sơ đồ: `context/ARCHITECTURE §5` (luồng lõi) + §6 (ca biên) + AC trong phạm vi (VIPER: AC các loop).

**Bẫy**: chỉ test đường thẳng "tạo → hoàn tất". Chuyển bị cấm và **nhảy cóc trạng thái** (deep link/API thẳng) là chỗ bug thật hay nằm.

---

## 5. Ghép kỹ thuật vào loại test

| Loại test | Kỹ thuật chủ đạo |
|---|---|
| chức năng | phân vùng (happy) |
| biên | giá trị biên + phân vùng lớp không hợp lệ |
| phá-hoại-đầu-vào | phân vùng lớp không hợp lệ, đẩy tới cực đoan (10k ký tự, injection) |
| phân quyền | bảng quyết định từ ma trận vai × hành động |
| workflow | chuyển trạng thái |
| tương-thích-ngược | so baseline `API-SURFACE.md` + thao tác trên dữ liệu di sản |
| api | phân vùng + biên **ở tầng API** (bỏ qua validate client) |
| cross-target | chuyển trạng thái, nhưng quan sát ở target thứ hai |
| hình thức | không phải kỹ thuật đầu vào — đo computed style so token |
| hiệu năng | lặp thưa + so ngưỡng |
| bảo-mật | mỗi TC một mục OWASP áp được cho target (A01/A02/A03/A05/A06/A07/A09/A10 + secret), kỳ vọng quan sát được (header có mặt, 401/403, đầu vào hiện như chữ) — TC ghi `Nguồn:` mục OWASP/CVE |

## 6. Chất lượng một TC — bốn câu tự hỏi

1. **TC này bắt được kiểu hỏng nào?** Không trả lời được → TC thừa, xoá.
2. **Người chưa biết sản phẩm có chạy được không?** Bước phải có thao tác cụ thể + dữ liệu cụ thể (prefix `SPEC-r<N>-`).
3. **Kỳ vọng có quan sát được không?** "Hoạt động đúng" không phải kỳ vọng; "quay về màn lịch, hẹn mới hiện đầu danh sách" mới là.
4. **Bằng chứng nào chứng minh nó PASS?** Điền ô `Bằng chứng cần` theo `TEST-STRATEGY §9` — TC không nói được cần bằng chứng gì thì lúc chạy sẽ PASS bừa.

## 7. Ranh giới

- **Không viết TC cho thứ ngoài phạm vi release** (`TEST-PLAN §1–§2`) — ngoài scope thì ghi `BUGS.md` `deferred`.
- **Không đẻ TC cho đủ số**: mật độ theo mức R, không theo cảm giác "test kỹ hơn cho chắc".
- **Không sửa TEST-PLAN** để hợp với TC đã viết — plan khoá từ pha S (`guard_frozen`); TC phải phủ plan, không phải ngược lại.
- TC tái hiện bug S1/S2 đã đóng là **bắt buộc** (`TEST-STRATEGY §6`) — không có thì lỗ đó quay lại release sau mà không ai bắt.
