---
description: In trạng thái hiện tại — release/lượt/pha, đường vào, gate còn thiếu, bug mở, việc tiếp theo
---

# /spec-status

Đọc nhanh, không sửa gì. Dùng khi mở phiên mới hoặc thấy rối.

## Chạy

```bash
python3 scripts/gate.py        # tự đọc pha từ STATE.md, in ✓/✗ từng mục
```

Rồi đọc thêm:

- `STATE.md` (khối đầu — pha, release, lượt bàn giao, URL; blocker ở cuối)
- `intake/releases/r<N>/RELEASE*.md` — quy trình dev, phạm vi, bản deploy, môi trường, lần bàn giao
- `context/releases/r<N>/REPORT.md` — verdict lượt gần nhất (nếu có)
- `context/BUGS.md §Tổng hợp` — bug mở theo severity
- `context/DECISIONS.md` (5 dòng cuối)

## Báo cáo theo dạng này

```
Pha         : <S|P|E|C>
Release     : <N> / <tổng theo TEST-STRATEGY §2, hoặc "—" nếu chưa lập>
Lượt bàn giao: <k> / <tối đa theo TEST-PLAN>
Nguồn       : <VIPER | khác> — <repo nguồn>
Phạm vi     : <phạm vi>  (bản deploy <…>; VIPER: l<a>–l<b>, loop deploy l<b>)
Môi trường  : <production | staging> — <điểm vào chính>
Tenant test : <tên hoặc chưa dựng>

Gate <pha>  : <x>/<y> mục máy xong
  ✗ <mục còn thiếu>

Bug mở      : S1=<> S2=<> S3=<> S4=<>
Blocker     : <số> — <tóm tắt>
Verdict gần nhất: <PASS|FAIL|— chưa certify>

Việc tiếp theo: <một việc cụ thể>
```

## Quy tắc

- **"Việc tiếp theo" phải cụ thể**: "chạy đợt 3 (authz+cross) trên B1", không phải "tiếp tục pha E".
- Có bug S1 mở → nêu lên đầu.
- Gate máy xanh hết mà STATE chưa chuyển pha → nói rõ nên chuyển.
- Verdict FAIL mà chưa có `RELEASE-<k+1>.md` → việc tiếp theo là chờ QC bàn giao lại, không phải tự chạy.
- Không tự sửa `STATE.md` trong lệnh này.
