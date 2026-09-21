---
type: architecture
tier: T0
status: DRAFT
last_reviewed: "{{DATE}}"
---

# ARCHITECTURE — {{PROJECT_NAME}}

> **Dịch từ mirror** (`intake/releases/r<N>/nguon/` — sơ đồ kiến trúc, danh sách service, API doc,
> DEPLOY; chế độ VIPER: `…/viper/ARCHITECTURE.md`) ở pha S — SPEC chỉ giữ
> phần cần cho việc test: danh sách target (hàng của ma trận loại test), contract giữa
> target (nguồn TC api/cross-target), luồng lõi (đường dry-run + smoke), ca biên đã quyết
> (nguồn TC biên). **Không tự đẻ target ngoài danh sách mirror** — tài liệu không nói gì về
> kiến trúc thì mỗi app/API người dùng chạm được là một target, ghi lỗ hổng vào HANDOVER.
> Xoá hết dấu `_CHƯA ĐIỀN_` khi điền xong.

---

## 1. Backend boundaries

<!-- Mỗi boundary của mirror một dòng, GIỮ NGUYÊN tên. Cột "Giao ở": bản deploy/sprint đưa
     boundary đó vào (VIPER: loop giao, từ ROADMAP/proposal).
     Sản phẩm một app: đúng một dòng tên `app`. -->

| Boundary | Nhiệm vụ (1 dòng) | Giao ở | Trong phạm vi release hiện tại? |
|---|---|---|---|
| _CHƯA ĐIỀN_ | | | |

## 2. Frontend experiences — web

| Experience | Persona | Giao ở | Design system | Trong phạm vi? |
|---|---|---|---|---|
| _CHƯA ĐIỀN_ | | | — | |

## 3. Frontend experiences — mobile

<!-- Không có mobile thì ghi `—`. Bundle id + build lấy ở ENVIRONMENT.md §6. -->

| Experience | Nền tảng | Persona | Giao ở | Trong phạm vi? |
|---|---|---|---|---|
| — | | | | |

## 4. Contract giữa các target

<!-- Chép từ mirror ARCHITECTURE §5 — nguồn TC loại `api` và `cross-target`, và là khung
     cho sổ API-SURFACE.md. Sản phẩm một app: ghi `—`. -->

| Contract | Bên cung cấp | Bên dùng | Kiểu | Ghi chú test |
|---|---|---|---|---|
| — | | | | |

## 5. Luồng lõi

<!-- Chép từ mirror ARCHITECTURE §7 — đường mà dry-run (pha P) và smoke (make smoke) đi,
     và là khung cho TC loại `workflow`. Ghi rõ bước nào đi qua ranh giới target. -->

_CHƯA ĐIỀN_

```
1. …
2. …
```

## 6. Ca biên dev đã quyết

<!-- Chép từ tài liệu nguồn (spec/AC/ghi chú kỹ thuật; VIPER: ARCHITECTURE §6) — mỗi dòng là một lời hứa của dev về cách xử ca biên;
     SPEC kiểm lời hứa đó (nguồn TC loại `biên` và `phá-hoại-đầu-vào`). -->

| Tình huống | Dev hứa xử thế nào | TC kiểm |
|---|---|---|
| _CHƯA ĐIỀN_ | | |

## 7. Dịch vụ ngoài

<!-- Chép từ tài liệu nguồn (VIPER: ARCHITECTURE §9) — nguồn TC loại `tích-hợp`: mỗi dịch vụ một hướng kiểm
     (email → hộp test, thanh toán → sandbox, webhook → endpoint nhận thử). -->

| Dịch vụ | Sản phẩm dùng để | Kiểm bằng |
|---|---|---|
| _CHƯA ĐIỀN_ | | |
