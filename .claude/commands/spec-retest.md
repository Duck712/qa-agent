---
description: Bàn giao lại sau verdict FAIL — kiểm manifest RELEASE-<k>, mở lượt bàn giao mới bằng release.py --retest, chạy phạm vi retest, certify lại (cùng release, ngưỡng không đổi)
---

# /spec-retest — bàn giao lại (pha E, cùng release)

> Verdict FAIL → dev fix → SPEC chạy lại. **Cùng release, lượt bàn giao +1, ngưỡng KHÔNG đổi** (`SPEC.md §1.2`). Thủ tục tối giản: team báo đã fix là chạy lại được.

## Bước 1 — Nhận bàn giao lại

QC thả `intake/releases/r<N>/RELEASE-<k+1>.md` (có `Lần bàn giao: k+1` + mục `## Dev đã fix` liệt kê mã bug — manifest cũ ghi `## VIPER đã fix` vẫn được đọc). Team báo qua chat ("đã fix BUG-…, chạy lại đi") → **meta ghi hộ**: tạo file đúng tên, trích nguyên văn, các dòng máy đọc chép từ manifest lượt trước (đổi `Lần bàn giao`; `Bản deploy` đổi theo bản fix nếu dev báo), thêm mục `## Dev đã fix`.

## Bước 2 — Mở lượt

```bash
python3 scripts/release.py             # xem trước điều kiện --retest
python3 scripts/release.py --retest    # STATE: lượt k+1, Bàn giao mở, pha E, bỏ tick E/C (giữ S/P)
```

Script append vào RUNLOG mục `## Lượt chạy — bàn giao <k+1>` + bảng `### Phạm vi retest` sinh cơ học (TC dính bug chưa đóng). **Bổ sung** vào bảng đó các TC regression chọn lọc theo `TEST-STRATEGY §6` (TC cùng target với chỗ sửa + luồng lõi mỗi release cũ) — sửa một chỗ có thể làm gãy chỗ khác.

## Bước 3 — Chạy phạm vi retest

Như `/spec-execute` nhưng gọn: chỉ phạm vi retest. Trước mỗi lượt `make reset` để trạng thái không nhiễm lượt trước. Mỗi bug đã fix: đi lại đúng bước tái hiện trong `BUGS.md` — PASS thì đổi trạng thái bug `đóng (retest PASS lượt k+1, <ngày>)` + (nếu S1/S2) viết TC regression; vẫn FAIL thì để `mở`, ghi vào RUNLOG.

```bash
python3 scripts/gate.py E
```

## Bước 4 — Certify lại

`/spec-certify` — gate tính verdict mới so **nguyên bảng ngưỡng cũ**, ghi thành mục `## Kết luận — bàn giao <k+1>` trong cùng REPORT. PASS → `release.py --go`.

**Còn FAIL mà lượt kế tiếp sẽ vượt `Lượt bàn giao tối đa`** → `release.py --retest` TỪ CHỐI mở lượt (chặn trước khi rơi vào ngõ cụt: lượt vượt trần thì verdict máy FAIL vĩnh viễn). Đây là quyết định của Authority — dừng lại, **báo QC bằng lời trong chat**. Hai hướng QC chọn:

1. **Nâng trần** — QC **tự tay** sửa con số `Lượt bàn giao tối đa` trong TEST-PLAN (hook `guard_frozen` chỉ chặn agent, không chặn người — agent KHÔNG sửa hộ, kể cả khi QC bảo "sửa giùm"); meta ghi 1 dòng DECISIONS dẫn nguyên văn lời QC. Rồi `--retest` như thường.
2. **Không nâng** — release đứng ở FAIL. QC rà từng bug mở và tự quyết số phận (`không sửa (QC chấp nhận)` / `deferred` — mỗi cái 1 dòng DECISIONS); trần đã ngăn đúng thứ nó phải ngăn: một release không chịu xanh sau chừng đó lượt cần QC nhìn lại, không cần thêm một lượt nữa.

## Ranh giới

- Không mở lượt retest khi chưa có manifest `RELEASE-<k+1>.md` — `release.py --retest` từ chối (fail-closed: mỗi lượt một chữ ký).
- Không đổi ngưỡng, không sửa TEST-PLAN (`guard_frozen`). Nâng `Lượt bàn giao tối đa` là chữ ký TAY của QC — agent không tự sửa.
- Không mở lại pha S/P — scope và môi trường giữ nguyên (script giữ tick S/P). Môi trường hỏng giữa hai lượt → `make doctor` + sửa, không phải làm lại pha P.
