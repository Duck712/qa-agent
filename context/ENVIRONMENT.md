---
type: environment
tier: T0
status: DRAFT
last_reviewed: "{{DATE}}"
---

# ENVIRONMENT — {{PROJECT_NAME}}

> **Hồ sơ môi trường test — điền ở pha P, meta bootstrap toàn bộ.** Môi trường = dòng
> `Môi trường:` của manifest (`production` + tenant cách ly, hoặc `staging`). Nguồn dịch:
> `context/ARCHITECTURE.md §1–§5` (danh sách target) + tài liệu deploy trong mirror (URL) +
> tài liệu stack (bundle id mobile) + `PERSONAS.md` (vai) + manifest (bảng URL, build mobile,
> quyền cấp sẵn). `make doctor` đọc file này để kiểm sống từng dòng.
>
> **KHÔNG ghi mật khẩu/secret vào đây** — chỉ ghi TÊN biến env; giá trị ở
> `environment/local/.env` (không commit).
>
> Mục gắn `(mỗi release)` được `release.py --go` bỏ tick khi mở release mới — môi trường
> đúng cho release cũ không tự đúng cho release mới.
> Xoá hết dấu `_CHƯA ĐIỀN_` khi điền xong.

---

## 1. Boundary / microservice

<!-- MỖI boundary trong phạm vi một dòng — tên khớp ARCHITECTURE §1 và bảng
     `## URL theo target` của manifest (gate P đối chiếu theo tên). Hệ nhiều
     microservice thì đây là bảng dài, đó là bình thường.

     Nguồn URL: manifest trước (QC khai), rồi tài liệu deploy trong mirror; không có ở đâu cả →
     curl dò + hỏi QC (pha S) hoặc ghi lỗ hổng HANDOVER rồi tự dò ở pha P.
     Health check phải TỰ CURL nhận 200 mới tick.

     Cột "Chạm từ ngoài?": `có` = SPEC gọi thẳng được · `không` = nội bộ, ghi rõ đi
     qua gateway/BFF nào — TC loại `api` phải đi đường vòng đó, không được kết luận
     "không kiểm được".

     Ví dụ:
     | booking-api   | https://api.x.vn/booking | /healthz | có     | 2026-09-01 ✓ |
     | notify-worker | —                        | —        | không — qua booking-api | — | -->

| Boundary | URL (môi trường test) | Health check | Chạm từ ngoài? | Kiểm lần cuối |
|---|---|---|---|---|
| _CHƯA ĐIỀN_ | | | | |

## 2. Web / mobile experience

<!-- Mỗi experience trong phạm vi một dòng, tên khớp ARCHITECTURE §2–§3. -->

| Experience | Loại | URL / bundle id | Persona chính |
|---|---|---|---|
| _CHƯA ĐIỀN_ | web | | |

## 3. Tài khoản test theo vai

<!-- make accounts tạo + thử đăng nhập từng dòng. Map 1-1 với PERSONAS.md §3. -->

| Vai | Tài khoản | Tenant | Biến env mật khẩu | Tạo bằng (đăng ký/mời/QC cấp) | Đăng nhập ✓? |
|---|---|---|---|---|---|
| _CHƯA ĐIỀN_ | | | `SPEC_PW_<ROLE>` | | ☐ |

## 4. Tenant test + cách ly

| Mục | Giá trị |
|---|---|
| Tenant | _CHƯA ĐIỀN_ (tên + tạo ngày nào, qua luồng nào / QC cấp qua manifest) |
| Sản phẩm đa tenant? | _CHƯA ĐIỀN_ (không → ghi rõ: cách ly bằng tài khoản + prefix, theo `TEST-STRATEGY §8`) |
| Prefix dữ liệu | `SPEC-r<N>-` |
| Dữ liệu di sản | Bản ghi prefix release cũ GIỮ LẠI — `spec-tester-compat` dùng; `make reset` không đụng |

## 5. Seed / reset — hai mốc dữ liệu

<!-- B0 = tenant chỉ có tài khoản §3, không bản ghi. B1 = B0 + dữ liệu mẫu theo persona
     (environment/local/plan-B1.yaml — QA sửa được). Seed QUA API — cấm chạm DB. -->

| Mốc | Nghĩa là | Lệnh | Thời gian chạy |
|---|---|---|---|
| B0 | Tenant sạch (giữ tài khoản + dữ liệu di sản) | `make reset` | _CHƯA ĐIỀN_ |
| B1 | B0 + dữ liệu mẫu theo persona | `make seed` | _CHƯA ĐIỀN_ |

Đường seed: _CHƯA ĐIỀN_ (API công khai — script ở `environment/local/` · seed endpoint QC cấp qua manifest: ghi rõ)

## 6. Thiết bị mobile

<!-- Chỉ khi phạm vi có mobile-experience. Build lấy từ manifest bàn giao — SPEC không
     build code; checksum phải khớp. Đúng MỘT thiết bị boot khi test (mobile-mcp). -->

| Thiết bị | Nền tảng | Vì sao chọn | Build cài (từ manifest) | Checksum khớp? |
|---|---|---|---|---|
| — | | | | |

## 7. Rác còn lại

<!-- Bản ghi SPEC tạo mà không xoá được qua API — để QC/đội dev biết mà xử. -->

| Ngày | Bản ghi | Vì sao không xoá được |
|---|---|---|
| | | |

## 8. Kiểm lại mỗi release

<!-- release.py --go bỏ tick các dòng này khi mở release mới; pha P release mới tick lại
     sau khi tự kiểm (make doctor chạy cả cụm). -->

- [ ] (mỗi release) URL từng target ở §1–§2 còn sống — curl 200
- [ ] (mỗi release) Từng tài khoản §3 còn đăng nhập được
- [ ] (mỗi release) `make seed` còn chạy đúng (sản phẩm đổi API là seed gãy)
- [ ] (mỗi release) Cách ly còn đúng: API đọc bằng tài khoản test chỉ thấy dữ liệu prefix/tenant test
- [ ] (mỗi release) (staging) URL không trỏ nhầm production · dịch vụ ngoài (SMS/email/payment) vẫn là sandbox
- [ ] (mỗi release) Thiết bị + build mobile khớp manifest mới (nếu có mobile)
