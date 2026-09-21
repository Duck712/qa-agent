#!/usr/bin/env python3
"""gate.py — kiểm điều kiện rời pha SPEC. In ✓/✗ từng mục, exit 1 nếu còn thiếu.

KHÔNG chặn tool, không sửa gì. Chỉ báo. Quyết định đi tiếp hay không vẫn là của người
(bốn hook guard_* mới chặn — SPEC.md §3c).

Usage:
    python3 scripts/gate.py S|P|E|C   # kiểm gate của một pha
    python3 scripts/gate.py           # tự đọc pha hiện tại từ STATE.md
    make gate P=S

Nguồn chuẩn của mọi gate: SPEC.md §1.1. Lệch nhau thì SPEC.md thắng.
Mọi phép đếm nằm ở scripts/_counts.py — dùng chung với guard_verdict.py.

Windows: dùng `python scripts\\gate.py` nếu không có lệnh `python3`.

Exit codes: 0 = qua · 1 = còn thiếu · 2 = sai tham số
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _counts as C  # noqa: E402

ROOT = C.ROOT


def _color_on() -> bool:
    import os
    return sys.stdout.isatty() and not os.environ.get("NO_COLOR")


_COLOR = _color_on()
GREEN = "\033[32m" if _COLOR else ""
RED = "\033[31m" if _COLOR else ""
GREY = "\033[90m" if _COLOR else ""
RESET = "\033[0m" if _COLOR else ""


class Report:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0

    def ok(self, msg: str) -> None:
        print(f"  {GREEN}✓{RESET} {msg}")
        self.passed += 1

    def no(self, msg: str) -> None:
        print(f"  {RED}✗{RESET} {msg}")
        self.failed += 1

    def check(self, cond: bool, msg: str) -> bool:
        (self.ok if cond else self.no)(msg)
        return cond

    def note(self, msg: str) -> None:
        print(f"    {GREY}{msg}{RESET}")


# --- gate S ------------------------------------------------------------------

def gate_s(r: Report, st: dict) -> None:
    n, k = st["release"], max(st["ban_giao"], 1)
    mp = C.manifest_path(n, k)
    mf = C.parse_manifest(mp)
    viper = mf["mode"] == "viper"
    if r.check(mp is not None and mf["ok"],
               f"Manifest intake/releases/r{n}/"
               f"{'RELEASE.md' if k == 1 else f'RELEASE-{k}.md'} là bản thật"):
        if viper:
            head_ok = all([mf["repo"], mf["release"] == n, mf["loop_a"], mf["loop_b"],
                           mf["loop_deploy"], mf["url"], mf["ban_giao"] == k])
            r.check(head_ok, "Manifest đủ dòng máy đọc (chế độ VIPER), khớp STATE (Release, Lần bàn giao)")
            if not head_ok:
                r.note(f"đọc được: repo={mf['repo']} release={mf['release']} "
                       f"phạm vi={mf['loop_a']}–{mf['loop_b']} deploy=l{mf['loop_deploy']} "
                       f"điểm vào={mf['url']} lượt={mf['ban_giao']} (STATE: release={n}, lượt={k})")
        else:
            def real(v):
                return bool(v) and C.UNFILLED not in v and v not in ("—", "-")
            head_ok = all([real(mf["quy_trinh"]), real(mf["repo"]), mf["release"] == n,
                           real(mf["pham_vi"]), real(mf["ban_deploy"]), mf["url"],
                           mf["ban_giao"] == k])
            r.check(head_ok, "Manifest đủ dòng máy đọc (Quy trình dev · Repo nguồn · Release · "
                             "Phạm vi · Bản deploy · Điểm vào chính · Lần bàn giao), khớp STATE")
            if not head_ok:
                r.note(f"đọc được: quy trình={mf['quy_trinh']} repo={mf['repo']} "
                       f"release={mf['release']} phạm vi={mf['pham_vi']} "
                       f"bản deploy={mf['ban_deploy']} điểm vào={mf['url']} "
                       f"lượt={mf['ban_giao']} (STATE: release={n}, lượt={k})")
        r.check(mf["moi_truong"] in C.ENVIRONMENTS,
                f"`Môi trường:` hợp lệ (production | staging — đang: {mf['moi_truong']})")
    else:
        r.note("QC thả manifest theo intake/_RELEASE-TEMPLATE.md — gate fail-closed tới khi có")
        r.no("Manifest đủ dòng máy đọc")

    urls = mf.get("urls") or []
    r.check(len(urls) >= 1,
            f"Manifest có bảng `## URL theo target` ({len(urls)} dòng thật)")
    if mf["moi_truong"] == "staging":
        prod_like = [u["url"] for u in urls
                     if u["url"].startswith("http") and not re.search(
                         r"(?<![a-z])(stag\w*|stg|dev|test\w*|uat|sandbox|qa|preprod|pre-prod|sit|local\w*)(?![a-z])"
                         r"|127\.0\.0\.1",
                         u["url"], re.I)]
        if prod_like:
            r.note(f"CẢNH BÁO: khai `Môi trường: staging` nhưng URL trông như production: "
                   f"{prod_like} — xác nhận lại với QC (đang pha S, được hỏi)")
    targets = C.inscope_targets()
    if targets:
        named = {u["target"] for u in urls}
        ho = C.read_live("context/HANDOVER.md")
        thieu = [t for t in targets if t not in named and t not in ho]
        r.check(not thieu,
                f"Mọi target trong phạm vi có URL ở manifest ({len(targets)} target)"
                + (f" — thiếu: {thieu}" if thieu else ""))
        if thieu:
            r.note("Hệ nhiều microservice: mỗi boundary/experience một dòng trong bảng. "
                   "QC chưa biết URL nào → hỏi (đang pha S) hoặc ghi vào HANDOVER §Lỗ hổng "
                   "rồi tự dò ở pha P.")

    vr = C.source_root(st)
    if viper:
        if r.check(vr is not None and (vr / "VIPER.md").is_file() and (vr / "context").is_dir(),
                   "Repo VIPER tồn tại (có VIPER.md + context/)"):
            loops = list(range(mf["loop_a"], mf["loop_b"] + 1)) if mf["loop_a"] and mf["loop_b"] else []
            missing = [i for i in loops
                       if not (vr / f"intake/loops/l{i}/_PROPOSAL.md").is_file()]
            r.check(loops != [] and not missing,
                    f"Mỗi loop trong phạm vi có _PROPOSAL.md bên repo VIPER"
                    + (f" — thiếu: {missing}" if missing else ""))
            p_loops = C.viper_loops_with_p(vr)
            r.check(mf["loop_deploy"] in p_loops,
                    f"Loop deploy l{mf['loop_deploy']} có `P` trong `Pha vòng này` "
                    f"(loop có P bên VIPER: {p_loops or 'không thấy'})")
        else:
            r.no("Đối chiếu chéo repo VIPER (không tìm được repo)")
            r.no("Loop deploy có `P`")
    else:
        r.check(vr is not None,
                f"Repo nguồn tồn tại — thư mục chỉ đọc ({mf['repo'] or 'chưa khai `Repo nguồn:`'})")

    mirror = C.mirror_dir(n, mf["mode"])
    rel_mirror = mirror.relative_to(ROOT)
    if viper:
        n_md = len(list(mirror.rglob("*.md"))) if mirror.is_dir() else 0
        r.check(n_md >= 5, f"Mirror {rel_mirror}/ đã đóng băng (≥5 file .md — có {n_md})")
    else:
        n_f = len([f for f in mirror.rglob("*") if f.is_file() and f.name != ".gitkeep"]) \
            if mirror.is_dir() else 0
        r.check(n_f >= 1, f"Mirror {rel_mirror}/ đã đóng băng (≥1 file tài liệu bàn giao — có {n_f})")

    ho_live = C.read_live("context/HANDOVER.md")
    marker = re.search(r"^NGUỒN: VIPER — (.+)$" if viper else r"^NGUỒN: .+? — (.+)$",
                       ho_live, re.MULTILINE)
    truy_vet = len([c for c in C.table_rows(C.section(ho_live, "## Truy vết"))
                    if c and c[0] and C.UNFILLED not in c[0]])
    tv_min = 5 if viper else 3
    lo_hong = C.section(ho_live, "## Lỗ hổng")
    r.check(bool(marker) and C.UNFILLED not in (marker.group(1) if marker else ""),
            "HANDOVER.md mang marker " + ("`NGUỒN: VIPER — <path>`" if viper
                                          else "`NGUỒN: <tên nguồn> — <path>`"))
    r.check(truy_vet >= tv_min,
            f"Bảng `## Truy vết` nguồn → context ≥{tv_min} dòng (có {truy_vet})")
    r.check(bool(lo_hong.strip()) and C.UNFILLED not in lo_hong,
            "`## Lỗ hổng & cách xử` có nội dung thật")

    stg = C.strategy()
    if n == 1:
        stg_ok = stg["exists"] and C.UNFILLED not in stg["text"] and stg["chot_qc"]
        r.check(bool(stg_ok), "TEST-STRATEGY.md đủ mục, hết _CHƯA ĐIỀN_, có `Chốt bởi QC:`")
        if viper and vr:
            # ≥ chứ không =: _PROPOSAL.md chỉ tồn tại cho loop VIPER ĐÃ mở — chuỗi
            # release dự kiến (theo ROADMAP) được phép dài hơn phần VIPER đã chạy tới.
            expect = len(C.viper_loops_with_p(vr))
            r.check(expect > 0 and len(stg["release_rows"]) >= expect,
                    f"Chuỗi release §2 ({len(stg['release_rows'])} dòng) ≥ "
                    f"số loop đã khai P bên VIPER ({expect})")
        elif not viper:
            r.check(len(stg["release_rows"]) >= 1,
                    f"Chuỗi release §2 có ≥1 dòng (có {len(stg['release_rows'])})")
    else:
        p = C.plan(n)
        floor = st["release_mo"]
        ok = p["ra_lai"] and floor and p["ra_lai"] >= floor
        r.check(bool(ok), f"TEST-PLAN có `Rà lại chiến lược (release {n}): <ISO>` "
                          f"ngày ≥ Release mở ({floor or 'THIẾU MỐC — mở release bằng release.py'})")
        row = next((c for c in stg["release_rows"] if c[0].strip() == f"r{n}"), None)
        if viper:
            pv_manifest = f"l{mf['loop_a']}–l{mf['loop_b']}" if mf["loop_a"] else ""
        else:
            pv_manifest = mf["pham_vi"] or ""
        pv_stg = re.sub(r"\s", "", row[1]) if row and len(row) > 1 else ""
        if row and pv_manifest and re.sub(r"\s", "", pv_manifest) == pv_stg:
            r.ok(f"Phạm vi manifest khớp TEST-STRATEGY §2 dòng r{n}")
        else:
            has_log = bool(floor) and any(c[0] >= floor for c in stg["changelog"])
            r.check(has_log, f"Phạm vi lệch TEST-STRATEGY §2 dòng r{n} "
                             f"({pv_stg or 'không có dòng'} vs {pv_manifest}) — "
                             "cần dòng change log §11 ngày ≥ Release mở")

    p = C.plan(n)
    r.check(p["exists"] and p["pham_vi"] is not None and p["luot_max"] > 0,
            f"TEST-PLAN.md tồn tại, đủ 4 dòng đầu máy đọc ({C.plan_path(n)})")
    r.check(len(p["ac"]) >= 1, f"§1 có bảng AC mới ({len(p['ac'])} AC — VIPER giữ mã AC-n (l<i>))")
    ti_ok = len(p["ti"]) >= 3
    loai_hop_le = set(stg["loai"])
    ti_moicoi = [t[0] for t in p["ti"] if loai_hop_le and t[2] not in loai_hop_le]
    r.check(ti_ok, f"§2 có ≥3 hạng mục TI (có {len(p['ti'])})")
    r.check(not ti_moicoi,
            "Loại test của mọi TI thuộc ma trận TEST-STRATEGY §3"
            + (f" — mồ côi: {ti_moicoi}" if ti_moicoi else ""))
    r.check(bool(p["out_of_scope"].strip()) and C.UNFILLED not in p["out_of_scope"],
            "§3 out-of-scope tường minh")
    th = C.plan_thresholds(p)
    r.check(th["s1"] is not None and th["pct_pass"] is not None,
            "§4 bảng ngưỡng verdict CÓ SỐ (đọc được S1, tổng %)")
    r.check(n == 1 or bool(p["regression"]),
            "§5 regression scope (release ≥2 phải liệt kê TC-ID)")

    cov = C.read_live("context/COVERAGE-MAP.md")
    ti_thieu = [t[0] for t in p["ti"] if t[0] not in cov]
    r.check(bool(cov.strip()) and not ti_thieu,
            "Mọi TI có mặt ở COVERAGE-MAP.md" + (f" — thiếu: {ti_thieu}" if ti_thieu else ""))
    caps = {c[2].strip() for c in p["ac"] if len(c) > 2 and c[2].strip()}
    cap_thieu = [c for c in caps if c and c not in cov]
    r.check(not cap_thieu, "Mọi capability trong phạm vi có dòng ở COVERAGE-MAP"
            + (f" — thiếu: {cap_thieu}" if cap_thieu else ""))

    r.check(decisions_of_release(st) >= 2,
            f"≥2 quyết định DECISIONS của release này (đếm được {decisions_of_release(st)})")
    r.check(C.challenge_pass(st, "S"), "Challenge pha S PASS (ngày ≥ mốc)")
    r.check(bool(p["chot_qc"]), "TEST-PLAN có dòng `Chốt bởi QC: <ISO>`")
    r.check(st["scope_khoa"], "Scope khoá (STATE §Gate — tick tay sau khi QC chốt)")


def decisions_of_release(st: dict) -> int:
    """Số quyết định có ngày ISO dưới mốc release/lượt cuối (release 1: cả file)."""
    text = C.read_live("context/DECISIONS.md")
    lines = text.splitlines()
    marker_idx = 0
    if st["release"] >= 2 or st["ban_giao"] >= 2:
        pat = re.compile(r"^\|\s*\(release \d+( — bàn giao \d+)?\)\s*\|")
        found = [i for i, l in enumerate(lines) if pat.match(l.strip())]
        if not found:
            return 0  # fail-closed: không mở bằng release.py
        marker_idx = found[-1]
    floor = C.moc(st)
    count = 0
    for l in lines[marker_idx:]:
        m = re.match(r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|", l.strip())
        if m and (floor is None or m.group(1) >= floor):
            count += 1
    return count


# --- gate P ------------------------------------------------------------------

def gate_p(r: Report, st: dict) -> None:
    n = st["release"]
    r.check(C.challenge_pass(st, "P"), "Challenge pha P PASS (ngày ≥ mốc)")

    env = C.read_live("context/ENVIRONMENT.md")
    arch = C.read_live("context/ARCHITECTURE.md")
    env_url_rows = [c for c in C.table_rows(C.section(env, "## 1."))
                    + C.table_rows(C.section(env, "## 2."))
                    if c and c[0] and c[0] not in ("—", "-") and C.UNFILLED not in "|".join(c)]
    r.check(len(env_url_rows) >= 1, f"ENVIRONMENT §1–§2: có URL/bundle id ({len(env_url_rows)} dòng thật)")
    targets = C.inscope_targets()
    if targets:
        env_named = {c[0].strip("` ") for c in env_url_rows}
        thieu_env = [t for t in targets if t not in env_named]
        r.check(not thieu_env,
                f"Mỗi target trong phạm vi có dòng ở ENVIRONMENT §1–§2 ({len(targets)} target)"
                + (f" — thiếu: {thieu_env}" if thieu_env else ""))
        if thieu_env:
            r.note("Boundary nội bộ không expose ra ngoài vẫn phải có dòng — ghi "
                   "`— (nội bộ, chạm qua <gateway>)` để TC api biết đi đường vòng nào.")
    roles = matrix_roles()
    acc_sec = C.section(env, "## 3.")
    role_thieu = [ro for ro in roles if ro and ro not in acc_sec]
    r.check(bool(roles) and not role_thieu,
            "ENVIRONMENT §3: mỗi vai trong ma trận có tài khoản test"
            + (f" — thiếu: {role_thieu}" if role_thieu else f" ({len(roles)} vai)"))
    tenant = C.section(env, "## 4.")
    r.check(bool(tenant.strip()) and C.UNFILLED not in tenant, "ENVIRONMENT §4: tenant + cách ly đã chốt")
    seed = C.section(env, "## 5.")
    r.check("B0" in seed and "B1" in seed and C.UNFILLED not in seed,
            "ENVIRONMENT §5: hai mốc dữ liệu B0/B1 + đường seed")
    mob_rows = [c for c in C.table_rows(C.section(arch, "## 3."))
                if c and c[0] and c[0] != "—"]
    if mob_rows:
        dev = C.section(env, "## 6.")
        dev_rows = [c for c in C.table_rows(dev) if c and c[0] and c[0] != "—"]
        r.check(bool(dev_rows) and C.UNFILLED not in dev,
                "ENVIRONMENT §6: thiết bị mobile + build từ manifest (phạm vi có mobile)")
    else:
        r.ok("Không có mobile-experience — bỏ qua mục thiết bị")

    for t in ("doctor", "seed", "reset", "accounts", "devices", "smoke"):
        r.check(make_implemented(t), f"`make {t}` đã hiện thực")

    tcs = C.all_testcases()
    tcs_n = C.tcs_of_release(n, tcs)
    p = C.plan(n)
    bad_meta = [t["id"] for t in tcs_n
                if not all(t["meta"].get(k1) for k1 in ("Loại", "Tầng", "Mức", "Regression", "Release vào"))]
    r.check(bool(tcs_n) and not bad_meta,
            f"TC của release có dòng meta hợp lệ ({len(tcs_n)} TC)"
            + (f" — hỏng meta: {bad_meta}" if bad_meta else ""))

    ac_thieu = []
    for ac, loop, _cap in p["ac"]:
        needle = C.ac_needle(ac, loop)
        if not any(C.id_in(needle, re.sub(r"\s+", "", t["meta"].get("AC", "")))
                   for t in tcs):
            ac_thieu.append(ac)
    r.check(not ac_thieu, "Mỗi AC mới có ≥1 TC (khớp mã AC trọn vẹn — VIPER: AC-n(l<i>))"
            + (f" — thiếu: {ac_thieu}" if ac_thieu else ""))

    ti_thieu = []
    for ti, _ten, loai, nguon, _muc in p["ti"]:
        toks = re.findall(r"(CAP-[A-Za-z0-9-]+|AC-\d+)", nguon or "")
        def match(t):
            if t["meta"].get("Loại") != loai:
                return False
            if not toks:
                return True
            hay = t["file"] + " " + t["meta"].get("AC", "")
            return any(C.id_in(tok, hay) for tok in toks)
        if not any(match(t) for t in tcs):
            ti_thieu.append(ti)
    r.check(not ti_thieu, "Mỗi TI có ≥1 TC (khớp Loại + Nguồn)"
            + (f" — thiếu: {ti_thieu}" if ti_thieu else ""))

    x_cells = matrix_x_cells()
    tc_cells = {norm_cell(t["meta"]["Ô ma trận"]) for t in tcs if t["meta"].get("Ô ma trận")}
    cell_thieu = [c for c in x_cells if norm_cell(c) not in tc_cells]
    r.check(not cell_thieu,
            f"TC phân quyền phủ đủ ô ✗ ma trận — TỪNG Ô "
            f"({len(x_cells) - len(cell_thieu)}/{len(x_cells)} ô)"
            + (f" — thiếu: {cell_thieu}" if cell_thieu else ""))

    stg = C.strategy()
    oos_set = C.oos_types(p["out_of_scope"])
    reg_tcs = [t for t in tcs if t["id"] in p["regression"]]
    loai_thieu = []
    for loai in stg["loai_ticked"]:
        covered = any(t["meta"].get("Loại") == loai for t in tcs_n + reg_tcs)
        if not covered and C.norm_type(loai) not in oos_set:
            loai_thieu.append(loai)
    r.check(not loai_thieu,
            "Mỗi loại test tick trong ma trận có ≥1 TC (hoặc KHAI TÊN ở out-of-scope)"
            + (f" — thiếu: {loai_thieu}" if loai_thieu else ""))

    if n >= 2:
        reg_min = stg["regression_min"] or 0
        tc_ids = {t["id"] for t in tcs}
        reg_missing = [x for x in p["regression"] if x not in tc_ids]
        reg_untag = [x for x in p["regression"]
                     if x in tc_ids and next(t for t in tcs if t["id"] == x)["meta"].get("Regression") != "có"]
        r.check(len(p["regression"]) >= reg_min and not reg_missing and not reg_untag,
                f"Regression đã chọn ≥ tối thiểu ({len(p['regression'])}/{reg_min})"
                + (f" — không tồn tại: {reg_missing}" if reg_missing else "")
                + (f" — thiếu tag Regression: {reg_untag}" if reg_untag else ""))
    else:
        r.ok("Release 1 — chưa có regression để chọn")

    r.note("(người) `make doctor` xanh + `make seed` chạy không lỗi — tự chạy, gate không thay được")
    r.note(f"(người) Dry-run: meta tự tay một luồng lõi trên {C.moi_truong(st)} bằng tài khoản test")


def make_implemented(target: str) -> bool:
    text = C.read("Makefile")
    m = re.search(rf"^{target}:\s*$(.*?)(?=^\S|\Z)", text, re.MULTILINE | re.DOTALL)
    if not m:
        return False
    return "NOT_IMPLEMENTED" not in m.group(1)


def matrix_roles() -> list[str]:
    """Tên vai từ header ma trận PERSONAS §2 (bỏ cột đầu; giữ cả 'chưa đăng nhập')."""
    block = C.section(C.read_live("context/PERSONAS.md"), "## 2.")
    for line in block.splitlines():
        s = line.strip()
        if s.startswith("|") and "Hành động" in s:
            cells = [c.strip() for c in s.strip("|").split("|")][1:]
            out = []
            for c in cells:
                m = re.search(r"\(role[: ]*([^)]+)\)", c)
                out.append((m.group(1) if m else c).strip())
            return [c for c in out if c and C.UNFILLED not in c]
    return []


def matrix_x_cells() -> list[str]:
    """Từng ô ✗ của ma trận PERSONAS §2 dưới dạng `<hành động> × <vai>` — gate P đối
    chiếu TỪNG Ô với nhãn `Ô ma trận:` của TC phân quyền, không đếm tổng (8 TC cũ
    không được phép "gánh hộ" 8 ô mới)."""
    block = C.section(C.read_live("context/PERSONAS.md"), "## 2.")
    roles = matrix_roles()
    out: list[str] = []
    for cells in C.table_rows(block):
        if not cells or not cells[0].strip() or C.UNFILLED in cells[0]:
            continue
        action = re.sub(r"\s+", " ", cells[0]).strip()
        for role, val in zip(roles, cells[1:]):
            if "✗" in val:
                out.append(f"{action} × {role}")
    return out


def norm_cell(s: str) -> str:
    """Chuẩn hoá nhãn ô ma trận để so: bỏ đuôi `= ✗`, thống nhất khoảng quanh ×."""
    s = re.sub(r"\s*=\s*✗\s*$", "", s or "")
    s = re.sub(r"\s*×\s*", " × ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


# --- gate E ------------------------------------------------------------------

def gate_e(r: Report, st: dict) -> None:
    n, k = st["release"], max(st["ban_giao"], 1)
    problems = C.gate_e_missing(n, k)
    if problems:
        for msg in problems[:20]:
            r.no(msg)
        if len(problems) > 20:
            r.note(f"… và {len(problems) - 20} mục nữa")
    else:
        scope = C.scope_of_luot(n, k)
        r.ok(f"Lượt bàn giao {k}: đủ kết quả + bằng chứng + bug/blocker cho {len(scope)} TC")
    r.note("(người) Kết quả là thao tác thật — đã cho spec-evidence-auditor soi trước khi sang C")


# --- gate C ------------------------------------------------------------------

def gate_c(r: Report, st: dict) -> None:
    n, k = st["release"], max(st["ban_giao"], 1)
    p = C.plan(n)
    rl = C.runlog(n)
    sec1 = rl["sections"].get(1, {"rows": []})
    first_dates = [row["ngay"] for row in sec1["rows"] if row["ngay"]]
    earliest = min(first_dates) if first_dates else None
    r.check(bool(p["chot_qc"]) and bool(earliest) and p["chot_qc"] <= earliest,
            f"Ngưỡng chốt TRƯỚC khi chạy (Chốt bởi QC {p['chot_qc']} ≤ ngày chạy sớm nhất {earliest})")

    verdict, notes = C.compute_verdict(n, k)
    for note in notes:
        r.note(note)
    concl = C.report_conclusions(n).get(k, {})
    if verdict is None:
        r.no("Không tính được verdict máy — " + (notes[0] if notes else ""))
    else:
        r.check(concl.get("verdict") == verdict,
                f"Verdict trong REPORT (`{concl.get('verdict')}`) khớp verdict máy tính (`{verdict}`)")

    rep = C.read_live(C.report_path(n))
    for head, label in (("## 1.", "executive summary"), ("## 2.", "số liệu"),
                        ("## 3.", "so ngưỡng"), ("## 5.", "bàn giao lại cho dev")):
        sec = C.section(rep, head)
        # "đã điền" = có NỘI DUNG thật dưới heading: dòng văn xuôi, hoặc bảng có
        # ≥1 dòng dữ liệu không rỗng (bảng scaffold trống không tính).
        lines = sec.splitlines()
        body = "\n".join(lines[1:])
        data_rows = [row for row in C.table_rows(body) if any(c.strip() for c in row)]
        prose = [l for l in lines[1:] if l.strip() and not l.strip().startswith("|")]
        r.check(bool(sec.strip()) and C.UNFILLED not in sec and bool(data_rows or prose),
                f"REPORT {head[3:]} {label} đã điền (nội dung thật, không chỉ heading)")

    bad_status = []
    dec_text = C.read_live("context/DECISIONS.md")
    for b in C.bugs():
        if b["release"] != n:
            continue
        s = b["status"]
        if "chờ retest" in s:
            bad_status.append(f"{b['id']} còn `đã fix chờ retest`")
        elif (s.startswith("không sửa") or s.startswith("deferred")) \
                and not C.id_in(b["id"], dec_text):
            bad_status.append(f"{b['id']} `{s.split('(')[0].strip()}` nhưng thiếu dòng DECISIONS")
        elif not s.strip():
            bad_status.append(f"{b['id']} thiếu Trạng thái")
    r.check(not bad_status, "Mọi bug của release có trạng thái cuối hợp lệ"
            + (f" — {bad_status}" if bad_status else ""))

    mism = bugs_summary_mismatch()
    r.check(not mism, "Bảng `Tổng hợp` của BUGS.md khớp các khối bug"
            + (f" — {mism[:4]}" if mism else ""))

    floor = C.moc(st)
    ky = concl.get("ky_qc")
    r.check(bool(ky) and (floor is None or ky >= floor),
            f"`Ký bởi QC: <ISO>` trong mục Kết luận — bàn giao {k} (ngày ≥ mốc)")
    r.note("(người) COVERAGE-MAP cột Trạng thái đã cập nhật cho mọi TI")
    if concl.get("verdict") == "FAIL":
        r.note(f"FAIL → chờ QC thả RELEASE-{k+1}.md rồi chạy: python3 scripts/release.py --retest")
    else:
        r.note("PASS → đóng release: python3 scripts/release.py --go")


def bugs_summary_mismatch() -> list[str]:
    """So bảng `## Tổng hợp` của BUGS.md với con số đếm từ các khối bug (toàn dự án).
    Bảng là thứ QC đọc nhanh — lệch với khối là sổ sách không tin được."""
    STATUSES = ("Mở", "Chờ retest", "Đóng", "Không sửa", "Deferred")
    want = {s: dict.fromkeys(STATUSES, 0) for s in ("S1", "S2", "S3", "S4")}
    for b in C.bugs():
        if b["severity"] not in want:
            continue
        st_ = b["status"]
        col = ("Mở" if st_.startswith("mở") else
               "Chờ retest" if "chờ retest" in st_ else
               "Đóng" if st_.startswith("đóng") else
               "Không sửa" if st_.startswith("không sửa") else
               "Deferred" if st_.lower().startswith("deferred") else None)
        if col:
            want[b["severity"]][col] += 1
    mism: list[str] = []
    rows = C.table_rows(C.section(C.read_live("context/BUGS.md"), "## Tổng hợp"))
    seen = set()
    for cells in rows:
        sev = cells[0].strip() if cells else ""
        if sev not in want:
            continue
        seen.add(sev)
        got = cells[1:6] + [""] * max(0, 6 - len(cells))
        for label, g in zip(STATUSES, got):
            gi = int(g) if g.strip().isdigit() else -1
            if gi != want[sev][label]:
                mism.append(f"{sev} {label.lower()}: bảng ghi `{g.strip() or '?'}` "
                            f"≠ đếm từ khối ({want[sev][label]})")
    for sev in want:
        if sev not in seen and any(want[sev].values()):
            mism.append(f"{sev}: có bug trong khối nhưng bảng Tổng hợp thiếu dòng")
    return mism


# --- main --------------------------------------------------------------------

GATES = {"S": ("S — Scope", gate_s), "P": ("P — Prepare", gate_p),
         "E": ("E — Execute", gate_e), "C": ("C — Certify", gate_c)}


def main(argv: list[str]) -> int:
    st = C.state()
    pha = (argv[1].upper() if len(argv) > 1 else st.get("pha") or "")
    if pha not in GATES:
        print("Usage: python3 scripts/gate.py [S|P|E|C]  "
              f"(STATE đang ghi pha: {st.get('pha_raw') or 'không đọc được'})")
        return 2
    title, fn = GATES[pha]
    print(f"\nGate {title} — release {st['release']}, lượt bàn giao {st['ban_giao']}"
          + (f" (mốc: {C.moc(st)})" if C.moc(st) else ""))
    print("=" * 60)
    r = Report()
    fn(r, st)
    print("=" * 60)
    print(f"  {r.passed} ✓ · {r.failed} ✗"
          + ("  — gate CHƯA qua (mục (người) tự kiểm rồi tick STATE)" if r.failed else
             "  — phần máy XANH; mục (người) tự kiểm rồi tick STATE"))
    return 1 if r.failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
