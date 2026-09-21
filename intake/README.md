# intake/ — cửa nhận bàn giao từ QC

> Quy trình đầy đủ: [SPEC.md §1.3](../SPEC.md). Đây là đường vào **duy nhất** của pha S:
> QC thả một manifest nhỏ, meta lo phần còn lại (mirror + dịch + bootstrap môi trường).

## Hợp đồng thả file

| File / thư mục | Vai trò | Ai tạo |
|---|---|---|
| `releases/r<N>/RELEASE.md` | **Manifest bàn giao — trigger của release N.** Khai: quy trình dev (VIPER/khác), repo nguồn ở đâu, phạm vi, bản deploy, môi trường (production/staging), điểm vào chính, lần bàn giao. Định dạng: [`_RELEASE-TEMPLATE.md`](_RELEASE-TEMPLATE.md). Gate S fail-closed tới khi có bản thật (hết `{{…}}`) | **QC** (hoặc meta ghi hộ từ chat — trích nguyên văn, ghi nguồn + ngày) |
| `releases/r<N>/RELEASE-<k>.md` | Manifest của **lượt bàn giao thứ k** (k ≥ 2) — sau verdict FAIL, dev fix xong thì QC thả file MỚI này (có mục `## Dev đã fix`). **Không sửa manifest cũ** — mỗi lượt một chữ ký | QC (hoặc meta ghi hộ từ chat) |
| `releases/r<N>/nguon/` (chế độ VIPER: `viper/`) | **Mirror** — bản chụp tài liệu bàn giao then chốt tại thời điểm bàn giao. Mọi phép dịch/đối chiếu về sau đi từ đây, vì nguồn sống tiếp trong lúc SPEC còn test | **Meta** copy ở pha S (`/spec-scope` Bước 2) — QC không phải làm gì |

## Luật của thư mục này

1. **Đầu vào đóng băng, chỉ thêm không sửa.** Sau khoá scope của release, manifest và mirror
   của release đó không đụng nữa. Bàn giao lại = file `RELEASE-<k>.md` MỚI. Sau khi dịch,
   `context/` là nguồn sự thật (luật #4).
2. **`_RELEASE-TEMPLATE.md` là đặc tả định dạng, không phải chỗ điền.** Giữ nguyên; file
   `_*.md` không được gate tính là manifest.
3. **Repo nguồn mà manifest trỏ tới là CHỈ ĐỌC** — hook `guard_readonly` chặn mọi lệnh ghi
   vào đó. SPEC cũng không sinh file cho đội dev: bug/verdict nằm ở `context/releases/r<N>/REPORT.md`,
   QC tự chuyển theo kênh của mình.
4. **Thư mục đánh số theo release nên tự nó là lưu trữ** — `release.py` không move gì;
   gate S chỉ đọc đúng `r<N>` của release hiện tại, manifest cũ không xanh hộ release mới.

## Mirror gồm những gì (meta copy — danh sách tối thiểu)

### Chế độ khác (mặc định) — vào `releases/r<N>/nguon/`

Chép **cái đội dev thật sự giao**, giữ nguyên tên file. Không có gì để chép thì hỏi QC (pha S).
PDF/Word/ảnh chép nguyên file; nếu đọc được thì kèm bản trích `.md` cạnh nó để dịch.

| Loại tài liệu (tên tuỳ dự án) | Để làm gì |
|---|---|
| PRD / spec / user story / ticket kèm AC | AC → TEST-PLAN §1 |
| Release note / changelog của bản deploy | Phạm vi release, thứ đổi so bản trước, legacy được phép phá |
| Danh sách vai + quyền (hoặc mô tả phân quyền trong spec) | PERSONAS + ma trận vai × hành động → TC phân quyền |
| Sơ đồ kiến trúc / danh sách service + URL / DEPLOY / `.env.example` | ARCHITECTURE + ENVIRONMENT |
| API doc (OpenAPI/Swagger/Postman) | ARCHITECTURE §4 + baseline phụ cho `API-SURFACE` |
| Thiết kế UI (ảnh/PDF xuất từ Figma, design token) | TC hình thức |
| Roadmap / kế hoạch deploy | Chuỗi release `TEST-STRATEGY §2` |

Thiếu loại nào → một dòng vào `context/HANDOVER.md §Lỗ hổng & cách xử` (kèm đề xuất + rủi ro).

### Chế độ VIPER — vào `releases/r<N>/viper/`

Từ repo VIPER (đường dẫn trong manifest), giữ nguyên tên file:

| Nguồn bên VIPER | Để làm gì |
|---|---|
| `context/PRD.md` + `context/archive/vong-<i>/PRD.md` (từng loop trong phạm vi) | AC từng loop → TEST-PLAN §1 |
| `context/CAPABILITIES-MAP.md` | Capability × loop giao → COVERAGE-MAP |
| `context/PERSONAS.md` | Persona + ma trận vai × hành động → PERSONAS + TC phân quyền |
| `context/ARCHITECTURE.md` | Target, contract, luồng lõi, ca biên → ARCHITECTURE |
| `context/DESIGN-SYSTEM.md` (+ `PROTOTYPE.md` nếu có UI) | Token/màn → TC hình thức |
| `context/TECHSTACK.md` | Bundle id mobile, stack — phục vụ dựng môi trường |
| `context/ROADMAP.md` | Kế hoạch vòng — đối chiếu chuỗi release `TEST-STRATEGY §2` |
| `context/shared/DEPLOY.md` + `deployment/.env.example` | URL production, tên biến → ENVIRONMENT |
| `intake/loops/l<i>/_PROPOSAL.md` (từng loop trong phạm vi) | Pha vòng (loop deploy có `P`?), legacy được phép phá |
| `context/BACKWARD-COMPATIBILITY-CHECKLIST.md` (nếu có) | Sổ hợp đồng surface — baseline phụ cho test tương thích |

Archive theo loop (`vong-<i>`) copy vào `viper/vong-<i>/` để giữ ngữ cảnh từng loop.
File nào repo VIPER không có → ghi một dòng vào `context/HANDOVER.md §Lỗ hổng`.
