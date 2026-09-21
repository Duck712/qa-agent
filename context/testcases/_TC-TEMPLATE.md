# Test case — mẫu cho `context/testcases/` (đặc tả định dạng, không phải chỗ điền)

> **Tổ chức file**: một file MỖI capability, tên file = mã capability (theo `COVERAGE-MAP.md` — giữ mã của tài liệu nguồn nếu có)
> (`CAP-BOOK-01.md`) — QA mở đúng file theo tính năng mà sửa. TC xuyên-capability
> (workflow, tương thích ngược, tích hợp, hiệu năng, cross-target) nằm ở file theo góc
> nhìn: `_CROSS-workflow.md`, `_CROSS-tuong-thich.md`, `_CROSS-tich-hop.md`,
> `_CROSS-hieu-nang.md`, `_CROSS-cross-target.md`, `_CROSS-bao-mat.md`.
>
> File TC **sống qua các release** — release sau append TC mới vào đúng file, không tạo
> thư mục theo release. Bộ regression = truy vấn tag `Regression: có` trên toàn bộ TC sống.
>
> Mọi file TC bắt đầu bằng frontmatter:
>
> ```
> ---
> type: testcases
> capability: CAP-BOOK-01        ← file _CROSS-*: ghi tên góc nhìn thay mã CAP
> tier: T1
> ---
> ```

---

## Khuôn một TC — copy nguyên khối

```markdown
### TC-BOOK-01-001 — Tạo lịch hẹn thành công trong khung giờ trống
AC: AC-1 · Kiểu: normal · Loại: chức năng · Tầng: web · Mức: R1 · Regression: có · Release vào: 1

| Mục | Nội dung |
|---|---|
| Vai / tài khoản | owner — xem `ENVIRONMENT.md §3` |
| Mốc dữ liệu | B1 (đã seed) |
| Tiền điều kiện | Đăng nhập owner; hôm nay còn ≥1 khung giờ trống |
| Bằng chứng cần | Screenshot có URL bar từng bước then chốt (`TEST-STRATEGY §9`) |

| Bước | Thao tác | Dữ liệu | Kỳ vọng |
|---|---|---|---|
| 1 | Mở màn Lịch tuần | — | Thấy khung giờ trống hôm nay |
| 2 | Bấm khung giờ trống | — | Mở form tạo hẹn |
| 3 | Điền tên khách, bấm Lưu | `SPEC-r1-Nguyễn Văn A` | Nút khoá khi đang gửi; quay về lịch, hẹn mới nổi bật |
```

## Dòng meta — máy đọc, giữ ĐÚNG định dạng một dòng

Nằm ngay dưới heading `### TC-…`, các nhãn cách nhau bằng ` · `:

| Nhãn | Giá trị | Bắt buộc? |
|---|---|---|
| `AC:` | Mã AC đúng như cột AC (+ cột Nguồn nếu có) của `TEST-PLAN §1`: `AC-n` hoặc `AC-n (<mã nguồn>)` — VIPER: `AC-n (l<i>)`. TC không gắn AC (regression thuần, tương thích) ghi `—` | Có |
| `Kiểu:` | `normal` (đường thuận, dữ liệu hợp lệ) \| `abnormal` (sai/thiếu/biên/gián đoạn/không quyền). Mỗi AC phải có ≥1 TC mỗi kiểu — `scripts/review_tc.py` đếm | Có |
| `Loại:` | MỘT loại trong ma trận `TEST-STRATEGY §3` (chức năng · workflow · biên · phá-hoại-đầu-vào · phân quyền · tương-thích-ngược · tích-hợp · api · cross-target · hình thức · hiệu năng · mobile · bảo-mật) | Có |
| `Tầng:` | `web` \| `api` \| `mobile` \| `cross` | Có |
| `Mức:` | `R1` \| `R2` \| `R3` — theo `TEST-STRATEGY §4` | Có |
| `Regression:` | `có` \| `không` — theo luật kết nạp `TEST-STRATEGY §6` | Có |
| `Release vào:` | số release TC được viết | Có |
| `Ô ma trận:` | TC loại phân quyền: `<hành động> × <vai> = ✗` | Loại phân quyền |
| `DS:` + `Màn:` | TC loại hình thức: gói design system + mã màn `S<n>` | Loại hình thức |
| `Ngưỡng:` | TC loại hiệu năng: con số so `TEST-STRATEGY §7` | Loại hiệu năng |
| `Surface:` | TC loại tương thích: endpoint/bảng/format + baseline (`API-SURFACE.md r<N>`, hoặc checklist tương thích của dev — VIPER: BC §1) | Loại tương thích |
| `OWASP:` | TC loại bảo-mật: mục OWASP Top 10 (`A01`…`A10`) hoặc `SECRETS` / `SUPPLY-CHAIN` | Loại bảo-mật |

`gate.py P` đếm bằng dòng meta này: mọi AC của TEST-PLAN §1 phải xuất hiện ở ≥1 dòng ·
mọi TI có ≥1 TC (đối chiếu qua Loại + Nguồn) · mọi ô ✗ của ma trận có TC `Ô ma trận:` ·
mọi loại tick trong ma trận × phạm vi có ≥1 TC. Sai định dạng dòng meta = TC vô hình với gate.

## Bốn luật

1. **ID không tái dùng.** `TC-<CAP|CROSS-*>-<số>` tăng dần trong file; TC bỏ đi thì đánh
   dấu `(đã gỡ — DECISIONS <ngày>)` ở tiêu đề, không xoá khối, không đánh lại số.
2. **Bước viết cho người chưa biết sản phẩm** — QA mới đọc là chạy được: thao tác cụ thể,
   dữ liệu cụ thể (mang prefix `SPEC-r<N>-`), kỳ vọng quan sát được. "Kiểm tra hoạt động
   đúng" không phải kỳ vọng.
3. **Mỗi AC ≥1 TC `Kiểu: normal` + ≥1 TC `Kiểu: abnormal`** — bug thật nằm ở ca sai/biên/gián
   đoạn, không ở ca thuận. `python3 scripts/review_tc.py` đếm trước challenge P. Đối chiếu
   checklist trong skill `spec-knowledge` theo đối tượng (form, auth, upload, API, bất thường).
4. **Kỹ thuật thiết kế theo mức R** (skill `spec-testcase-design`): R1 = đủ 4 kỹ thuật
   (phân vùng tương đương · giá trị biên · bảng quyết định · chuyển trạng thái) ·
   R2 = happy + 2 biên · R3 = happy. Đừng đẻ TC "cho đủ số" — mỗi TC phải bắt được một
   kiểu hỏng cụ thể.
