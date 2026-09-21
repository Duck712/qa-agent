---
name: spec-knowledge
description: >
  Kinh nghiệm kiểm thử tích luỹ qua nhiều dự án — checklist theo đối tượng (form nhập liệu, đăng nhập/phiên/
  phân quyền, upload file, API bất kỳ, ca bất thường xuyên hệ thống), danh sách lỗi dev hay mắc (bug-patterns),
  và mẹo nghề (khám phá có kỷ luật, viết bug tốt, soi AC mơ hồ, báo cáo cho người không rành kỹ thuật).
  Nạp skill này ở pha P khi viết test case (cùng spec-testcase-design), ở pha S khi soi tài liệu tìm lỗ hổng,
  và khi đóng vai spec-tester-* để biết chỗ nào đáng đào. Ở pha C, bài học mới được đề xuất nâng vào đây —
  chỉ sửa skill này khi QC đã duyệt.
---

# spec-knowledge — kinh nghiệm dùng lại được

> `spec-testcase-design` trả lời **cách** nghĩ ra đủ ca (bốn kỹ thuật). Skill này trả lời **chỗ nào** dev hay
> sai — những thứ tài liệu bàn giao gần như không bao giờ nhắc. Đối chiếu, không chép máy móc: case không áp
> dụng được cho sản phẩm này thì bỏ **chủ động**, không phải vì quên.

## Mục lục

| File | Mở khi | Dùng cho loại test / agent |
|---|---|---|
| `checklists/form-input.md` | Có form nhập liệu (field, validate, submit) | biên · phá-hoại-đầu-vào — `spec-tester-edge`, `spec-tester-breaker` |
| `checklists/auth-login.md` | Đăng nhập / phiên / phân quyền / đa tenant | phân quyền — `spec-tester-authz` (§3 = rủi ro R1) |
| `checklists/file-upload.md` | Upload file, ảnh, media | phá-hoại-đầu-vào · tích-hợp — `spec-tester-breaker`, `spec-tester-integration` |
| `checklists/api-common.md` | Bất kỳ API nào (contract, phân trang, method, rate limit, CORS, encoding) | api · tương-thích-ngược — `spec-tester-api`, `spec-tester-compat` |
| `checklists/abnormal.md` | Luồng đi qua nhiều màn/component/hạ tầng (mạng, race, múi giờ, trình duyệt, mobile, phiên giữa luồng, cache, dữ liệu lớn, i18n, phục hồi) | biên · workflow · mobile — `spec-tester-edge`, `spec-tester-workflow`, `spec-tester-mobile` |
| `bug-patterns.md` | **Luôn** — soi trước khi viết TC cho mọi feature | mọi loại |
| `techniques-judgement.md` | Khám phá có kỷ luật · viết bug · soi AC mơ hồ ở pha S · cắt phạm vi · viết REPORT | pha S, E, C |

Bảo mật chuyên sâu (OWASP Top 10, CVE, secrets) **không** nằm ở đây — thuộc agent `spec-tester-security` (loại `bảo-mật`). Ở đây chỉ giữ ca bảo mật cơ bản ai cũng phải thử (`auth-login §3`, `form-input §2`, `api-common §1/§6`).

## Cách dùng theo pha

- **Pha S** — soi tài liệu đã dịch bằng `techniques-judgement §3` (AC mơ hồ) + `bug-patterns`: lỗ nào tài liệu không nói → ghi `HANDOVER §Lỗ hổng` kèm đề xuất.
- **Pha P** — với mỗi đối tượng trong phạm vi, mở checklist tương ứng → mỗi mục áp dụng được mà chưa có TC → viết TC (Loại + Kiểu đúng, `Bằng chứng cần` đủ). Cộng `context/LESSONS.md` các release trước.
- **Pha E** — tester nạp checklist loại mình để biết chỗ đáng đào, **nhưng chỉ chạy TC-ID được giao**; thấy chỗ hay ngoài danh sách → báo thành phát hiện.
- **Pha C** — bài học mới ghi `context/LESSONS.md` (tự ghi). Đề xuất nâng thành một dòng ở đây → trình QC; **QC duyệt tường minh mới sửa**, 1 dòng DECISIONS dẫn nguyên văn.

## Luật sửa skill này

- Mỗi dòng thêm vào phải là **một phép thử cụ thể** (thao tác + điều quan sát), không phải lời khuyên chung chung.
- Ghi nguồn gốc cuối dòng khi nâng từ LESSONS: `(bài học r<N>)`.
- Không xoá dòng cũ vì "dự án này không dùng" — dự án khác vẫn dùng. Dòng sai thật → sửa, kèm DECISIONS.
