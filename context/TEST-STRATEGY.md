---
type: test-strategy
tier: T0
status: DRAFT
last_reviewed: "{{DATE}}"
---

# TEST STRATEGY — {{PROJECT_NAME}}

> **Chiến lược test cho CẢ sản phẩm — lập MỘT lần ở pha S release 1, QC chốt.** Mọi
> `TEST-PLAN.md` của từng release phải aligned với file này (`SPEC.md §1.4`): phạm vi
> release đối chiếu §2, loại test của TI đối chiếu §3, ngưỡng instantiate từ §10.
> Lệch thì **sửa ở đây trước** (kèm 1 dòng §11 + 1 dòng DECISIONS), không lệch ngầm trong plan.
>
> Nguồn lập: mirror ở `intake/releases/r1/nguon/` (PRD/spec/AC, danh sách vai, kiến trúc/URL,
> roadmap/kế hoạch deploy, thiết kế UI, API doc) — chế độ VIPER: `intake/releases/r1/viper/`
> (PRD, CAPABILITIES-MAP, PERSONAS, ARCHITECTURE, ROADMAP §1 kế hoạch vòng, DESIGN-SYSTEM, BC-checklist).
> Chỉ sửa được ở pha S — hook `guard_frozen` chặn ngoài pha đó.
> Xoá hết dấu `_CHƯA ĐIỀN_` khi điền xong — `python3 scripts/gate.py S` bắt dấu này.

Chốt bởi QC: _CHƯA ĐIỀN_   ← ngày ISO khi QC duyệt cả chiến lược; gate S release 1 bắt dòng này

---

## 1. Sản phẩm & nguồn

<!-- Bảng tài liệu nguồn đã đọc để lập chiến lược — mỗi file một dòng, trỏ đúng mục.
     Đây là chỗ chứng minh chiến lược lập từ tài liệu thật chứ không từ phỏng đoán. -->

| Mục | Giá trị |
|---|---|
| Quy trình dev | _CHƯA ĐIỀN_ (`VIPER` hoặc `khác` — khớp manifest) |
| Repo nguồn | _CHƯA ĐIỀN_ (đường dẫn — khớp manifest) |
| Môi trường test | _CHƯA ĐIỀN_ (`production` + tenant cách ly, hoặc `staging` — khớp manifest; đổi môi trường giữa các release = sửa ở đây + §11) |
| Sản phẩm làm gì (2 câu) | _CHƯA ĐIỀN_ |

<!-- Chế độ khác: đổi cột trái thành tên file thật trong mirror `nguon/` (PRD/spec, user story,
     release note, API doc, thiết kế…). Chế độ VIPER: giữ các dòng mẫu dưới. -->

| Tài liệu nguồn đã đọc | Rút ra gì cho chiến lược |
|---|---|
| PRD / spec / AC (VIPER: `PRD.md` + `archive/vong-*/PRD.md`) | _CHƯA ĐIỀN_ (AC từng tính năng / loop) |
| Danh mục tính năng (VIPER: `CAPABILITIES-MAP.md`) | _CHƯA ĐIỀN_ (capability × release giao) |
| Vai + quyền (VIPER: `PERSONAS.md §2`) | _CHƯA ĐIỀN_ (ma trận vai — nguồn test phân quyền) |
| Kiến trúc / service / API doc (VIPER: `ARCHITECTURE.md §1–§5`) | _CHƯA ĐIỀN_ (target + contract — nguồn tầng test) |
| Roadmap / kế hoạch deploy (VIPER: `ROADMAP.md §1`) | _CHƯA ĐIỀN_ (bản deploy dự kiến — nguồn chuỗi release §2) |
| Thiết kế UI / design token (VIPER: `DESIGN-SYSTEM.md`) | _CHƯA ĐIỀN_ (token — nguồn test hình thức; backend-only thì ghi rõ) |

## 2. Chuỗi release dự kiến

<!-- MỖI BẢN DEPLOY DỰ KIẾN BÀN GIAO CHO QC = MỘT RELEASE (theo roadmap/kế hoạch deploy của dev).
     Liệt kê CẢ các release dự kiến chưa chạy tới. Gate S release 1 đòi ≥1 dòng; chế độ VIPER
     đòi số dòng ≥ số loop ĐÃ khai P trong các _PROPOSAL.md hiện có.
     Cột `Phạm vi` phải GIỐNG CHỮ dòng `Phạm vi:` của manifest release đó (gate so chuỗi, bỏ
     khoảng trắng) — lệch thì sửa bảng này + ghi §11.

     Ví dụ (khác):
     | r1 | Đặt lịch lõi (sprint 1–3) | v1.0.0 | Đặt lịch + huỷ lịch | — | đang test |
     | r2 | Nhắc lịch + báo cáo (sprint 4–5) | v1.1.0 | Nhắc lịch SMS | regression r1 | chưa bàn giao |
     Ví dụ (VIPER):
     | r1 | l1–l3 | l3 | Đặt lịch lõi (CAP-BOOK-01..03) | — | đang test | -->

| Release | Phạm vi | Bản deploy | Trọng tâm test | Regression kèm | Trạng thái |
|---|---|---|---|---|---|
| r1 | _CHƯA ĐIỀN_ | _CHƯA ĐIỀN_ | _CHƯA ĐIỀN_ | — | chưa bàn giao |

## 3. Ma trận loại test × target

<!-- TỪ ĐIỂN ĐÓNG cho cột `Loại test` của TI (TEST-PLAN §2) và dòng meta `Loại:` của TC —
     và là DANH MỤC ROSTER AGENT (SPEC.md §6): mỗi cột một agent spec-tester-* cùng tên.
     Hàng = boundary/experience của ARCHITECTURE §1–§3 (bản dịch). Ô: ✓ = áp cho target đó,
     — = không áp (kèm lý do ngắn nếu không hiển nhiên).
     Thêm góc nhìn mới = thêm cột + tạo agent theo agents/_TESTER-TEMPLATE.md.
     Gate P đối chiếu: loại ✓ × target trong phạm vi release mà không có TC → đỏ. -->

| Target | chức năng | workflow | biên | phá-hoại-đầu-vào | phân quyền | tương-thích-ngược | tích-hợp | api | cross-target | hình thức | hiệu năng | mobile | bảo-mật |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| _CHƯA ĐIỀN_ | | | | | | | | | | | | | |

<!-- `regression` không có cột riêng — nó là thuộc tính của TC (tag `Regression: có`),
     mọi agent đều chạy TC regression thuộc loại của mình.
     `bảo-mật` (spec-tester-security): chỉ tick khi manifest có mục `## Quyền kiểm thử bảo mật`
     hoặc DECISIONS có dòng xác nhận quyền (dẫn nguyên văn QC). Không tick → khai ở TEST-PLAN §3. -->

## 4. Tiếp cận risk-based

<!-- Mỗi dòng một khu vực rủi ro, dịch từ: luồng tiền/dữ liệu, ma trận phân quyền,
     contract giữa target, ca biên đã quyết trong tài liệu nguồn (ARCHITECTURE §6 bản dịch).
     Đối chiếu thêm skill `spec-knowledge` (bug-patterns + checklist) để không sót vùng hay hỏng.
     Mức R quyết mật độ TC:
       R1 = happy + biên đủ 4 kỹ thuật (skill spec-testcase-design) + phân quyền · vào regression vĩnh viễn
       R2 = happy + 2 biên chọn lọc
       R3 = happy là đủ -->

| Khu vực | Vì sao rủi ro | Mức | Hệ quả thiết kế test |
|---|---|---|---|
| _CHƯA ĐIỀN_ | | R1 | |

## 5. Định nghĩa severity

<!-- Tiêu chí phải QUAN SÁT ĐƯỢC — "nghiêm trọng" không phải tiêu chí. Không hạ mức
     để đẹp số; hạ mức là một quyết định, ghi DECISIONS. -->

| Mức | Định nghĩa | Ví dụ |
|---|---|---|
| S1 — chặn | Mất/hỏng dữ liệu · thủng phân quyền/cross-tenant · auth bypass · RCE/injection chứng minh được · lộ secret thật · luồng lõi không đi được · crash · tiền sai. Không đường vòng. Tái hiện thỉnh thoảng vẫn là S1 (ghi tỉ lệ) | Tài khoản B đọc được bản ghi của A |
| S2 — nặng | AC không đạt · chức năng chính sai, đường vòng khó · regression gãy · trộn design system | Gửi hai lần ra hai bản ghi |
| S3 — vừa | Sai có đường vòng dễ · lệch token/thiếu trạng thái component · khuôn rỗng/lỗi sai chuẩn · thiếu security header / lộ stack trace | Màu lạ ngoài bảng token |
| S4 — nhẹ | Cosmetic, chính tả, lệch nhỏ không cản thao tác | |

## 6. Chính sách regression

<!-- LUẬT CHỌN, không phải danh sách — danh sách cụ thể mỗi release nằm ở TEST-PLAN §5,
     chọn từ TC sống mang tag `Regression: có`. -->

| Luật | Nội dung |
|---|---|
| Kết nạp **vĩnh viễn** | TC khu vực R1 · TC phân quyền · TC tương thích ngược · TC cross-target · TC tái hiện bug S1/S2 đã đóng (mỗi bug S1/S2 đóng PHẢI sinh 1 TC regression) |
| Kết nạp **theo điều kiện** | TC hình thức — chỉ chạy lại khi release đổi design system hoặc có màn mới |
| Không kết nạp | TC S4/cosmetic đã pass 2 release liền |
| Số TC regression tối thiểu mỗi release | _CHƯA ĐIỀN_ (con số — gate P đếm `TEST-PLAN §5` so với đây) |
| Khi retest (lượt bàn giao ≥2) | Mọi TC dính bug được fix + TC regression cùng target với chỗ sửa + luồng lõi mỗi release cũ |
| Gỡ khỏi regression | Chỉ khi dev được phép phá legacy chỗ đó (release note / tài liệu bàn giao — VIPER: tài liệu vòng, thấy trong mirror) — 1 dòng DECISIONS |

## 7. Ngưỡng hiệu năng

<!-- Mức AN-TOÀN: đo bằng số lần gọi thưa (n ≤ 20, giãn cách ≥1s), KHÔNG stress — trên production
     tuyệt đối, trên staging dùng chung cũng vậy (máy/môi trường người khác đang dùng).
     Cần load test thật → khai môi trường riêng ở đây và QC quyết; không có thì ghi
     "không load test — ngoài phạm vi SPEC". -->

| Phép đo | Ngưỡng | Cách đo |
|---|---|---|
| p95 luồng lõi (end-to-end) | _CHƯA ĐIỀN_ (ví dụ: < 3s) | n=10 lượt qua browser, giãn cách |
| p95 endpoint ghi chính | _CHƯA ĐIỀN_ | n=10 curl, giãn cách |
| Page-load màn đầu | _CHƯA ĐIỀN_ | performance timing của browser |
| App start (mobile, nếu có) | _CHƯA ĐIỀN_ | bấm giờ launch → màn đầu tương tác được |

Load/stress test: _CHƯA ĐIỀN_ (không làm — hoặc môi trường riêng + điều kiện)

## 8. Chuẩn cách ly dữ liệu

| Mục | Chuẩn |
|---|---|
| Tenant test | _CHƯA ĐIỀN_ (đa tenant: tên tenant + cách tạo · không đa tenant: ghi "cách ly bằng tài khoản + prefix") |
| Tài khoản | `spec+<role>@…` — một tài khoản mỗi vai trong ma trận `PERSONAS.md §2`; chi tiết ở `ENVIRONMENT.md §3` |
| Prefix dữ liệu | Mọi bản ghi SPEC tạo mang tiền tố `SPEC-r<N>-` trong trường tên/tiêu đề |
| Dữ liệu di sản | `make reset` chỉ xoá prefix release hiện tại — bản ghi release cũ GIỮ LẠI cho test tương thích ngược |
| Dọn rác | Qua API; thứ không xoá được → `ENVIRONMENT.md §Rác còn lại` |
| Seed thẳng DB (chỉ staging) | _CHƯA ĐIỀN_ (mặc định: KHÔNG — qua API. Cho phép thì ghi DB nào, script nào, QC chốt. Production: luôn KHÔNG) |
| Dịch vụ ngoài (SMS/email/push/thanh toán) | _CHƯA ĐIỀN_ (sandbox/hộp thư test nào; staging chưa xác nhận sandbox → TC chạm vào là `BLOCKED`) |
| Ký bằng git author | _CHƯA ĐIỀN_ (có/không — QC tự commit dòng `Chốt bởi QC`/`Ký bởi QC`, SPEC.md §3e) |
| Ranh giới cứng | Không ghi/xoá bản ghi KHÔNG mang prefix — kể cả để "thử". Chi tiết: `context/shared/SAFETY.md` |

## 9. Chuẩn bằng chứng

<!-- Bằng chứng tối thiểu để một TC được tính ĐÃ chạy — thiếu là ghi BLOCKED, không phải PASS.
     Bản thao tác chi tiết + quy ước thư mục: skill `spec-evidence`. -->

| Loại TC | Bằng chứng tối thiểu |
|---|---|
| chức năng / workflow / biên | Screenshot có URL bar đúng môi trường test (headless: `console.txt` ghi URL từng bước) + trích snapshot/console |
| phá-hoại-đầu-vào / phân quyền | Request đã gửi (tài khoản, URL/API, dữ liệu) + response NGUYÊN VĂN (mã + body) |
| tương-thích-ngược / api | Cặp request/response + diff so baseline (`API-SURFACE.md` / surface cũ) |
| tích-hợp | Bằng chứng ở CẢ hai đầu: hành động + hộp nhận (email test/log webhook/sandbox) |
| cross-target | CẶP ảnh: hành động ở A + kết quả ở B + network log ở B |
| hình thức | Giá trị computed style + selector + màn (`rgb(…)`, `13px`) — không có số đo là chưa soi |
| hiệu năng | Bảng số đo từng lần gọi + timestamp + cách đo |
| mobile | Screenshot màn + kết quả `mobile_list_crashes` |
| bảo-mật | **Chứng minh bằng thao tác**: request/payload đã gửi (nguồn payload: OWASP cheat sheet / CVE public — ghi trong `ghi-chu.md`) + response NGUYÊN VĂN cho thấy khai thác được/không. Ngoại lệ không cần PoC: output nguyên văn của tool uy tín — CVE (grype / npm audit / pip-audit), secret đã verify (gitleaks / trufflehog), TLS (testssl.sh / openssl). Secret/token trong evidence phải che `<REDACTED>`. Scan báo "có thể" mà không tái hiện được → `INFO` trong REPORT, không phải bug |

## 10. Khuôn ngưỡng verdict

<!-- TEST-PLAN mỗi release instantiate khuôn này bằng số thật Ở PHA S, TRƯỚC khi execute.
     Ghi đè khuôn → 1 dòng DECISIONS của release đó. -->

| Verdict | Điều kiện mặc định |
|---|---|
| **FAIL** | ≥1 bug S1 mở · HOẶC có AC mới không TC nào PASS ở lượt cuối · HOẶC vượt quá {{3}} lượt bàn giao |
| **PASS** | 0 S1 · 0 S2 mở · 100% AC mới có ≥1 TC PASS · regression khu vực R1 pass 100% · tổng TC PASS ≥ {{95}}% |
| **PASS-có-điều-kiện** | 0 S1 · S2 mở ≤ {{2}}, từng cái có ngày fix cam kết + QC chấp nhận (1 dòng DECISIONS mỗi cái — máy KIỂM dòng này) · các điều kiện PASS còn lại vẫn phải đạt (100% AC mới, regression R1, tổng TC PASS ≥ ngưỡng) — đây không phải cửa thoát ngưỡng |

## 11. Change log

<!-- Append-only. Mỗi lần sửa chiến lược (chỉ ở pha S): một dòng ở đây + một dòng DECISIONS.
     Gate S release ≥2 đối chiếu: phạm vi manifest lệch §2 mà không có dòng ở đây ngày ≥
     `Release mở` → đỏ. -->

| Ngày | Release | Đổi gì | Vì sao | QC chốt |
|---|---|---|---|---|
| | | | | |
