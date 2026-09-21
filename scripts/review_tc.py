#!/usr/bin/env python3
"""review_tc.py — soát bộ test case vòng 1 (máy đếm) ở pha P, trước challenge P.

    python3 scripts/review_tc.py            # release hiện tại (STATE.md): tóm tắt + chỗ thiếu
    python3 scripts/review_tc.py --ac       # thêm chi tiết từng AC
    python3 scripts/review_tc.py --release 2

VÌ SAO CÓ FILE NÀY
    gate P chỉ đòi "mỗi AC có ≥1 TC" — một AC phủ bằng đúng một ca thuận vẫn qua gate,
    trong khi bug thật nằm ở ca sai/biên/gián đoạn. Script này soát bảy thứ mắt người dễ
    bỏ sót khi bộ TC lên hàng trăm:
      1. mỗi AC của TEST-PLAN §1 có ≥1 TC `Kiểu: normal` VÀ ≥1 TC `Kiểu: abnormal`
      2. mọi TC của release có nhãn `Kiểu:` hợp lệ (normal | abnormal)
      3. `Loại:` thuộc từ điển đóng của ma trận TEST-STRATEGY §3
      4. TC mồ côi: gắn AC không có trong TEST-PLAN (§1 hoặc AC cũ nhắc ở §5 regression)
      5. TC thiếu ô `Bằng chứng cần` (không có bằng chứng thì không được PASS — §9)
      6. kỳ vọng rỗng nghĩa ("hoạt động đúng", "không lỗi"…) — dấu hiệu TC hình thức
      7. TC loại `phân quyền` thiếu nhãn `Ô ma trận:`

    Chỉ BÁO, không sửa gì. Vòng 2 (mắt người đối chiếu mirror tài liệu bàn giao) không
    thay được bằng script — ghi kết quả vào STATE §Challenge log pha P.

Exit codes: 0 sạch · 1 còn nhóm cần vá · 2 sai tham số
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _counts as C  # noqa: E402

ROOT = C.ROOT
KIEU = ("normal", "abnormal")
MO_HO = ("hoạt động đúng", "hoạt động bình thường", "chạy đúng", "thành công là được",
         "không lỗi", "ok là được", "đúng như mong đợi", "đúng nghiệp vụ", "hiển thị hợp lý")


def ac_label(ac: str, src: str) -> str:
    """Nhãn hiển thị — có loop (VIPER) thì kèm loop, không thì mã trần."""
    needle = C.ac_needle(ac, src)
    return f"{ac} ({src})" if needle != ac else ac


def main(argv: list[str]) -> int:
    n = C.state().get("release") or 1
    if "--release" in argv:
        try:
            n = int(argv[argv.index("--release") + 1])
        except (IndexError, ValueError):
            print("Usage: python3 scripts/review_tc.py [--ac] [--release N]")
            return 2

    plan = C.plan(n)
    if not plan["exists"]:
        print(f"✗ chưa có {C.plan_path(n)}")
        return 1
    tcs_all = C.all_testcases()
    tcs = C.tcs_of_release(n, tcs_all)
    stg = C.strategy()
    loai_hop_le = {C.norm_type(x) for x in stg["loai"]}

    ac_keys = [(C.ac_needle(a, l), ac_label(a, l)) for a, l, _ in plan["ac"]]
    hop_le = {k for k, _ in ac_keys}
    # AC cũ nhắc ở §5 regression (release trước) cũng là đích hợp lệ cho TC gắn vào
    for m in re.finditer(r"AC-\d+(?:\s*\(l\d+\))?", C.section(plan["text"], "## 5.")):
        hop_le.add(re.sub(r"\s+", "", m.group(0)))

    by_ac: dict[str, list[dict]] = defaultdict(list)
    for t in tcs_all:
        nen = re.sub(r"\s+", "", t["meta"].get("AC", ""))
        for key, label in ac_keys:
            if C.id_in(key, nen):
                by_ac[label].append(t)

    thieu_tc, thieu_n, thieu_a, du = [], [], [], []
    for _key, label in ac_keys:
        hit = [t for t in by_ac.get(label, []) if not t["removed"]]
        if not hit:
            thieu_tc.append(label)
            continue
        kinds = {t["meta"].get("Kiểu", "").strip().lower() for t in hit}
        if "normal" not in kinds:
            thieu_n.append(label)
        if "abnormal" not in kinds:
            thieu_a.append(label)
        if set(KIEU) <= kinds:
            du.append(label)

    kieu_sai = [t["id"] for t in tcs
                if t["meta"].get("Kiểu", "").strip().lower() not in KIEU]
    loai_sai = [f"{t['id']} ({t['meta'].get('Loại') or 'trống'})" for t in tcs
                if loai_hop_le and C.norm_type(t["meta"].get("Loại", "")) not in loai_hop_le]
    mo_coi = []
    for t in tcs:
        raw = t["meta"].get("AC", "").strip()
        if raw in ("", "—", "-"):
            continue
        nen = re.sub(r"\s+", "", raw)
        if not any(C.id_in(k, nen) for k in hop_le):
            mo_coi.append(f"{t['id']} (AC: {raw})")
    authz_no_cell = [t["id"] for t in tcs
                     if C.norm_type(t["meta"].get("Loại", "")) == C.norm_type("phân quyền")
                     and not t["meta"].get("Ô ma trận")]

    text_of: dict[str, str] = {}
    tc_dir = ROOT / "context" / "testcases"
    for f in tc_dir.glob("*.md") if tc_dir.is_dir() else []:
        text_of[f.name] = C.read_live(f)
    thieu_bc, ky_vong_mo_ho = [], []
    for t in tcs:
        body = text_of.get(t["file"], "")
        # neo vào ĐÚNG heading của TC — tìm id trần sẽ bắt nhầm chỗ TC khác tham chiếu chéo
        i = body.find(f"### {t['id']}")
        block = body[i:] if i >= 0 else ""
        nxt = block.find("\n### ", 4)
        block = block[:nxt] if nxt > 0 else block
        if "Bằng chứng cần" not in block:
            thieu_bc.append(t["id"])
        low = block.lower()
        if any(m in low for m in MO_HO):
            ky_vong_mo_ho.append(t["id"])

    print(f"\nreview_tc — release {n} · vòng 1 (máy đếm)\n" + "=" * 68)
    n_ac = len(ac_keys)
    print(f"  AC trong TEST-PLAN §1        : {n_ac}")
    print(f"  AC có TC                     : {n_ac - len(thieu_tc)}")
    print(f"  AC đủ normal + abnormal      : {len(du)}")
    print(f"  TC của release (Release vào: {n}) : {len(tcs)}  · TC sống toàn dự án: "
          f"{len([t for t in tcs_all if not t['removed']])}")
    print("-" * 68)

    bad = 0

    def hang(nhan: str, ds: list[str], ghi: str = "") -> None:
        nonlocal bad
        if ds:
            bad += 1
        print(f"  {'✗' if ds else '✓'} {nhan}: {len(ds)}" + (f" — {ghi}" if ghi and ds else ""))
        for x in ds[:14]:
            print(f"      · {x}")
        if len(ds) > 14:
            print(f"      … và {len(ds) - 14} nữa")

    hang("AC chưa có TC nào", thieu_tc, "viết TC")
    hang("AC thiếu TC normal", thieu_n, "thêm ca thuận (đối chứng dương)")
    hang("AC thiếu TC abnormal", thieu_a, "thêm ca sai/biên/gián đoạn")
    hang("TC thiếu/sai nhãn `Kiểu:` (normal | abnormal)", kieu_sai)
    hang("TC có `Loại:` ngoài từ điển ma trận TEST-STRATEGY §3", loai_sai)
    hang("TC gắn AC không có trong TEST-PLAN", mo_coi)
    hang("TC phân quyền thiếu nhãn `Ô ma trận:`", authz_no_cell)
    hang("TC thiếu ô `Bằng chứng cần`", thieu_bc)
    hang("TC có kỳ vọng rỗng nghĩa", ky_vong_mo_ho, "viết kỳ vọng quan sát được")

    print("=" * 68)
    print(f"  {'XANH — vòng 1 sạch' if bad == 0 else f'ĐỎ — {bad} nhóm cần vá'}"
          "  (vòng 2 đối chiếu mirror vẫn phải làm bằng mắt)\n")

    if "--ac" in argv:
        print("Chi tiết từng AC:")
        for _key, label in ac_keys:
            hit = [t for t in by_ac.get(label, []) if not t["removed"]]
            kinds = sorted({t["meta"].get("Kiểu", "?") for t in hit})
            print(f"  {label:<16} {len(hit):>3} TC  {','.join(kinds) or '—'}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
