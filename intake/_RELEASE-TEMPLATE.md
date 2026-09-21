# Manifest bàn giao — mẫu cho `intake/releases/r<N>/RELEASE.md`

> **Đặc tả định dạng, không phải chỗ điền.** Bản thật do QC thả (hoặc meta ghi hộ từ chat,
> trích nguyên văn) vào `releases/r<N>/`. Lượt bàn giao thứ k ≥ 2 → file MỚI
> `RELEASE-<k>.md`, không sửa file cũ.
>
> Các dòng máy đọc ở đầu và bảng `## URL theo target` là thứ **máy đọc** — các dòng đó nằm
> NGOÀI mọi khối `<!-- -->`.

---

## Cấu trúc chuẩn

```markdown
NGUỒN: BÀN GIAO RELEASE — từ {{đội dev / nhà cung cấp}}
Quy trình dev: {{VIPER | khác}}
Repo nguồn: {{đường dẫn tuyệt đối hoặc tương đối tới repo code HOẶC thư mục tài liệu bàn giao}}
Release: {{N}}
Phạm vi: {{mô tả phạm vi release — vd "Đặt lịch + thanh toán ví (sprint 4–5)"; VIPER: l<a>–l<b>}}
Bản deploy: {{version / tag / commit / ngày deploy — vd v1.4.0 (2026-09-20); VIPER: l<b>}}
Môi trường: {{production | staging}}
Điểm vào chính: {{https://… — nơi persona chính bắt đầu, dùng cho make smoke}}
Lần bàn giao: {{k — bản đầu của release ghi 1}}

## URL theo target

{{Một dòng cho MỖI boundary/experience trong phạm vi release — hệ nhiều microservice
  thì đây là chỗ khai từng cái, không nhét hết vào một dòng. Tên target GIỮ NGUYÊN tên
  dùng ở context/ARCHITECTURE §1–§3 (gate đối chiếu theo tên này).}}

| Target | Loại | URL / bundle id | Health check | Ghi chú |
|---|---|---|---|---|
| {{booking-api}} | boundary | {{https://api.x.vn/booking}} | {{/healthz}} | |
| {{notify-worker}} | boundary | — | — | {{nội bộ, chỉ chạm qua booking-api}} |
| {{admin-web}} | web-experience | {{https://admin.x.vn}} | {{/}} | |
| {{gara-app}} | mobile-experience | {{vn.x.gara}} | — | {{build ở mục dưới}} |

## Bản build mobile
{{Chỉ khi phạm vi có mobile-experience — không có thì xoá mục.
  Đường dẫn .app (build cho simulator) / .apk, hoặc link TestFlight/internal track.
  BẮT BUỘC kèm checksum:}}
Build: {{đường dẫn hoặc link}}
Checksum (sha256): {{…}}

## Tài khoản / quyền cấp sẵn
{{Tuỳ chọn: tenant test QC đã tạo, tài khoản admin, seed endpoint, hộp thư test,
  sandbox thanh toán/SMS, token gọi API nội bộ… Không có thì xoá mục — meta sẽ tự dựng ở
  pha P và hỏi khi kẹt (còn trong pha S). KHÔNG ghi mật khẩu vào đây — chỉ tên biến/nơi lấy.}}

## Quyền kiểm thử bảo mật
{{Tuỳ chọn — chỉ khi muốn chạy loại test `bảo-mật` (spec-tester-security): ai cho phép
  (chủ hệ thống / người có thẩm quyền), phạm vi target, khung thời gian. Không có mục này
  thì loại `bảo-mật` chỉ làm phần thụ động (secrets scan, SBOM/CVE trên repo nguồn).}}

## Dev đã fix
{{CHỈ ở manifest lượt k ≥ 2 — liệt kê mã bug đã fix, mỗi bug một dòng:}}
- BUG-r{{N}}-{{số}}: {{một câu — fix ở đâu, deploy chưa}}

## Ghi chú của QC
{{Tuỳ chọn — ràng buộc, deadline, vùng nhạy cảm cần tránh, trọng tâm muốn soi kỹ.}}
```

## Luật từng dòng máy đọc

| Dòng | Luật |
|---|---|
| `Quy trình dev:` | `VIPER` hoặc `khác`. Quyết định gate S kiểm gì thêm (xem SPEC.md §0, §1.1). Thiếu dòng này nhưng có `Repo VIPER:` → coi là VIPER |
| `Repo nguồn:` | Thư mục tồn tại (repo code hoặc thư mục tài liệu bàn giao). Chế độ VIPER: thêm có `VIPER.md` + `context/`. Hook `guard_readonly` dùng đúng đường dẫn này để chặn ghi. Nhãn cũ `Repo VIPER:` vẫn đọc được |
| `Release:` | Khớp dòng `Release` trong `STATE.md` — lệch là gate đỏ (manifest thả nhầm thư mục) |
| `Phạm vi:` | Không rỗng. Chế độ khác: văn bản tự do, so chuỗi với cột phạm vi dòng r<N> của `TEST-STRATEGY §2` (lệch → change log §11). Chế độ VIPER: `l<a>–l<b>`, mỗi loop trong khoảng phải có `intake/loops/l<i>/_PROPOSAL.md` bên repo VIPER. Nhãn cũ `Phạm vi loop:` vẫn đọc được |
| `Bản deploy:` | Không rỗng — version/tag/commit/ngày giúp đối chiếu "đang kiểm bản nào". Chế độ VIPER: `l<b>` nằm trong phạm vi và `_PROPOSAL.md` của nó khai `P` trong `Pha vòng này`. Nhãn cũ `Loop deploy:` vẫn đọc được |
| `Môi trường:` | `production` hoặc `staging` — quyết định luật an toàn áp thêm (SPEC.md §7). Thiếu dòng → coi là `production` |
| `Điểm vào chính:` | Không rỗng — URL persona chính bắt đầu, dùng cho `make smoke` và dry-run. (Template cũ ghi `URL production:` vẫn đọc được) |
| `Lần bàn giao:` | Khớp `Lần bàn giao` trong STATE. k ≥ 2 → file phải tên `RELEASE-<k>.md` và có mục `## Dev đã fix` không rỗng (nhãn cũ `## VIPER đã fix` vẫn đọc) — `release.py --retest` từ chối khi thiếu |

## Luật bảng `## URL theo target`

Đây là chỗ hệ **nhiều microservice** được khai đủ. Một dòng một target:

| Cột | Luật |
|---|---|
| `Target` | **Tên khớp `ARCHITECTURE §1–§3`** (bản dịch trong `context/`; gate S đối chiếu theo tên). Đây cũng là tên dùng ở `ENVIRONMENT.md`, TEST-PLAN cột Target, và ma trận loại test × target |
| `Loại` | `boundary` · `web-experience` · `mobile-experience` |
| `URL / bundle id` | URL của target đó **trên đúng môi trường khai ở `Môi trường:`**; mobile ghi bundle id. **Không expose ra ngoài** → ghi `—` và nói rõ ở Ghi chú (SPEC chạm nó qua gateway nào) |
| `Health check` | Path health nếu có (`/healthz`) — `make doctor` dùng để kiểm từng service còn sống; không có thì `—` |
| `Ghi chú` | Nội bộ/qua gateway nào · cần token riêng · rate limit đặc biệt · vùng nhạy cảm · (staging) dịch vụ ngoài đã là sandbox chưa |

**Gate S đòi**: bảng có ≥1 dòng thật, và **mọi target khai `Trong phạm vi` = có** ở `context/ARCHITECTURE §1–§3` (bản dịch) phải xuất hiện trong bảng — hoặc được ghi vào `HANDOVER §Lỗ hổng & cách xử` (QC chưa biết URL → meta dò ở pha P, có vết). Không có đường thứ ba: một service không ai biết địa chỉ thì không kiểm được, và điều đó phải hiện ra ở pha S chứ không phải lúc đang chạy test.

**Gate P đòi**: mỗi target đó có dòng ở `ENVIRONMENT §1–§2` với URL đã curl xác nhận sống (nội bộ thì ghi đường vòng).

## Ví dụ ngắn — dự án không dùng VIPER

```markdown
NGUỒN: BÀN GIAO RELEASE — từ đội app đặt lịch
Quy trình dev: khác
Repo nguồn: ../booking-docs
Release: 1
Phạm vi: Đặt lịch hẹn + nhắc lịch qua SMS (sprint 1–3)
Bản deploy: v1.0.0 (2026-09-20)
Môi trường: staging
Điểm vào chính: https://staging.booking.example.com
Lần bàn giao: 1
```

## Ghi hộ từ chat

QC báo bàn giao qua chat (kể cả "đã fix xong, chạy lại đi") → meta tạo file đúng tên,
dòng đầu tiên của phần ghi chú ghi `Nguồn: chat với QC, <ngày ISO>`, nội dung **trích
nguyên văn** — không diễn giải. Các dòng máy đọc + bảng URL meta điền từ thông tin thật
(thiếu thì hỏi — việc nhận bàn giao thuộc pha S, được hỏi).
