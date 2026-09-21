---
description: Pha C — máy tính verdict từ kết quả so ngưỡng đã ghi trước, viết REPORT, QC ký; PASS đóng release, FAIL in điều kiện bàn giao lại
---

# /spec-certify — Pha C

> **LUẬT #8 — verdict SAU cùng.** Ngưỡng ghi ở pha S không đổi; verdict là phép tính máy làm, người ký. Không "nới tay" vì đã tốn công test.

Việc đầu tiên: sửa `STATE.md` → `Pha hiện tại : C`.

## Bước 1 — Máy tính verdict

```bash
python3 scripts/gate.py C
```

Gate tự tính verdict từ `BUGS.md` (bug `mở` theo severity — **cả bug còn mở từ release trước**) + `RUNLOG.md` (kết quả lượt hiện tại) so bảng ngưỡng `TEST-PLAN §4` — in ra `PASS | PASS-có-điều-kiện | FAIL` kèm số liệu. PASS-có-điều-kiện không phải cửa thoát ngưỡng: tổng TC PASS vẫn phải đạt, và **từng S2 mở phải có dòng DECISIONS cam kết** (máy kiểm). Đây là verdict **phải** ghi vào REPORT; ghi khác là gate đỏ.

Trước khi viết REPORT, đảm bảo mọi bug của release có trạng thái cuối: `đóng (retest PASS lượt k)` · `mở` (vào REPORT) · `không sửa (QC chấp nhận — DECISIONS)` · `deferred (release sau)`. Bug S1/S2 đóng chưa có TC regression → nhắc pha P release sau (ghi lỗ hổng), hoặc viết TC ngay nếu nhanh.

## Bước 2 — Viết REPORT

`context/releases/r<N>/REPORT.md` — hook `guard_verdict` chặn tới khi gate E xanh:

- §1 Executive summary: **5 dòng, không thuật ngữ** — QC đọc 30 giây nắm được đạt/không, mấy lượt, bug nặng nhất và số phận nó, còn gì treo.
- §2 Số liệu · §3 So ngưỡng (chép từ gate) · §4 kết quả theo TI.
- §5 Bàn giao lại cho dev (FAIL/PASS-có-điều-kiện): bug mở theo severity, trỏ khối BUGS + bằng chứng. **SPEC không sinh file vào repo nguồn** — QC chuyển cho dev theo kênh của mình.
- Mục `## Kết luận — bàn giao <k>`: `Verdict:` (khớp gate) + điều kiện (nếu PASS-có-điều-kiện: mỗi cái một BUG + ngày fix cam kết + DECISIONS) + `Ký bởi QC: <ISO>`.

## Bước 3 — QC ký, rồi rẽ

Trình REPORT cho QC. QC ký → điền `Ký bởi QC: <ISO>` — **chỉ sau khi QC nói đồng ý tường minh trong chat**, dẫn nguyên văn vào 1 dòng DECISIONS (`SPEC.md §3e`); phiên không có lời QC thì không điền, kể cả khi gate máy xanh.

```bash
python3 scripts/gate.py C     # phải xanh
```

**Verdict PASS / PASS-có-điều-kiện** → cập nhật `COVERAGE-MAP` cột Trạng thái (`đã certify (r<N>)`) → commit → đóng release:

```bash
git add -A && git commit -m "certify release <N> — PASS"
python3 scripts/release.py          # xem trước
python3 scripts/release.py --go     # archive snapshot, mở release N+1, pha S
```

**Verdict FAIL** → in mục `## 5. Bàn giao lại cho dev` cho QC. Dừng ở đây — chờ dev fix. Khi team báo đã fix (QC thả `RELEASE-<k+1>.md`, hoặc báo qua chat → meta ghi hộ manifest): chạy `/spec-retest`.

## Bước 4 — Rút bài học (sau khi QC ký, cả PASS lẫn FAIL)

Kinh nghiệm của release này phải chảy vào lần viết TC sau, không nằm chết trong REPORT.

1. **Tự ghi — không cần duyệt**: append mục `## Release <N> — bàn giao <k> (<ISO>)` vào `context/LESSONS.md` với 1–3 bài học: bug pattern mới, ca đã lọt khỏi bộ TC (bug tìm được ngoài TC đã viết), severity chấm sai phải hạ/nâng, lỗ hổng môi trường, mẹo thu bằng chứng. Mỗi bài học: *điều đã xảy ra* · *vì sao* · *lần sau làm gì*. Không có gì đáng ghi → vẫn ghi 1 dòng `Không có bài học mới — <lý do>`. Append-only, không sửa mục cũ.
2. **Đề xuất nâng thành kinh nghiệm dùng chung** — trình QC trong cùng lượt ký (QC đang ở đây để ký nên được trình, không phải "hỏi sau pha S"): bài học nào nên thành một dòng trong `spec-knowledge` (`checklists/<đối tượng>.md` hoặc `bug-patterns.md`). Mỗi đề xuất: dòng sẽ thêm + file đích + lý do. QC đồng ý tường minh → sửa skill + 1 dòng DECISIONS dẫn nguyên văn; không đồng ý hoặc không trả lời → để nguyên ở `LESSONS.md`.
3. Commit cùng commit certify.

## Ranh giới

- Không tự sửa `spec-knowledge` (checklist/bug-patterns) khi QC chưa duyệt — chỉ `LESSONS.md` là tự ghi.
- Không ghi verdict khác gate máy tính. Bất đồng với verdict → không phải sửa REPORT, mà là challenge lại kết quả (bug thiếu? severity sai?) — xử ở RUNLOG/BUGS, rồi gate tính lại.
- Không đóng release khi verdict chưa PASS — `release.py --go` từ chối.
- Không sửa ngưỡng để verdict đổi màu (`guard_frozen` chặn).
- Không quay vòng release khi bug S1 còn mở.
