# Quan điểm test — <Tính năng>

> `/qa-viewpoint`. Một file một tính năng (`qa/viewpoints/<tinh-nang>.md`), mỗi quan điểm một dòng. File bắt đầu bằng `_`
> bị bỏ qua. Cách rút quan điểm + checklist review: `qa-testcase-design/ky-thuat/quan-diem.md`.
> Quan điểm test = **điều cần kiểm** (chưa phải bước/dữ liệu). TC viết SAU khi quan điểm được **người dùng duyệt**, mỗi TC
> trỏ về quan điểm bằng trường `VP:`.
>
> **Bám đặc tả** — mỗi dòng phải có:
> - `Nguồn`: file + mục (vd docs/prd.md §3.2, api/openapi.yaml) hoặc URL.
> - `Trích nguyên văn`: câu gốc trong tài liệu, chép y nguyên (bỏ đoạn giữa bằng `…`). `qa_check.py vp` / `src` đối chiếu
>   với file cục bộ; URL/pdf/docx → `qa-source-check` đối chiếu.
> - Điều đặc tả KHÔNG nói mà QA thấy nên kiểm (checklist, bug-patterns, yêu cầu ngầm) → `Nguồn: ngoài đặc tả — <lý do/checklist>`,
>   để `nháp`, trình người dùng; chỉ `duyệt` khi họ đồng ý (ghi `duyệt (DECISIONS #n)`). Không bao giờ trình như thể đặc tả nói.
> - Chưa rõ kỳ vọng → thêm `(chờ trả lời #n)` vào cột Quan điểm, mở câu hỏi ở ANALYSIS §5.
>
> Trạng thái: `nháp` (QA đề xuất) · `duyệt` (người dùng đã duyệt) · `bỏ` (không dùng — giữ dòng, không xoá mã).
> Kiểu: `normal` · `abnormal` — mỗi REQ cần ≥ 1 mỗi kiểu. Mức: mức rủi ro của REQ (SCOPE §2; trước khi chốt là đề xuất).

- Duyệt bởi: 
- Ngày duyệt: 

| VP | REQ | Hạng mục | Quan điểm test | Kiểu | Kỹ thuật dự kiến | Mức | Nguồn | Trích nguyên văn | Trạng thái |
|---|---|---|---|---|---|---|---|---|---|
| VP-FEAT-001 | REQ-FEAT-1 | <màn/chức năng con> | <điều cần kiểm — hành vi quan sát được> | normal | <tên chuẩn qa-testcase-design §1> | <R1/R2/R3> | <file §mục> | <câu gốc> | nháp |
