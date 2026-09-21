#!/usr/bin/env python3
"""_counts.py — module đếm dùng chung của SPEC.

VÌ SAO CÓ FILE NÀY
    gate.py (chỉ báo) và guard_verdict.py (chặn cứng) phải nhìn sổ sách BẰNG CÙNG MỘT
    CON MẮT — hai bản parse riêng thì sớm muộn lệch nhau, và hook sẽ chặn thứ gate cho
    qua (hoặc ngược lại). Mọi phép đọc STATE / manifest / TEST-PLAN / testcases / RUNLOG
    / BUGS / REPORT / TEST-STRATEGY nằm ở đây; gate và hook chỉ gọi.

    Mọi hàm đọc file đều chịu được file thiếu/hỏng: trả về giá trị rỗng có cấu trúc,
    không traceback — người gọi tự quyết fail-open (hook) hay fail-closed (gate).
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UNFILLED = "_CHƯA ĐIỀN_"
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
ISO = re.compile(r"\d{4}-\d{2}-\d{2}")
RESULTS = ("PASS", "FAIL", "BLOCKED", "SKIP")


# --- đọc file ----------------------------------------------------------------

def read(rel_or_path) -> str:
    p = Path(rel_or_path)
    if not p.is_absolute():
        p = ROOT / p
    try:
        return p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def read_live(rel_or_path) -> str:
    """Nội dung thật, đã bỏ khối <!-- --> — ví dụ trong template không được đếm."""
    return COMMENT.sub("", read(rel_or_path))


def filled(rel_or_path) -> bool:
    text = read(rel_or_path)
    return bool(text.strip()) and UNFILLED not in text


def section(text: str, header_prefix: str) -> str:
    """Một mục '## …' của văn bản (đã bỏ comment trước khi gọi), tính tới '## ' kế tiếp."""
    m = re.search(rf"^{re.escape(header_prefix)}.*$", text, re.MULTILINE)
    if not m:
        return ""
    start = m.start()
    nxt = text.find("\n## ", m.end())
    return text[start: nxt if nxt > 0 else len(text)]


def table_rows(block: str) -> list[list[str]]:
    """Dòng dữ liệu của các bảng markdown trong block (bỏ tiêu đề + phân cách)."""
    rows: list[list[str]] = []
    header_seen = False
    for line in block.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            header_seen = False
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
            header_seen = True
            continue
        if header_seen:
            rows.append(cells)
    return rows


# --- so khớp ID và tên loại — KHÔNG dùng substring trần -----------------------

def id_in(needle: str, hay: str) -> bool:
    """ID (AC-/TC-/BUG-…) có mặt TRỌN VẸN trong hay — không nhận khi needle chỉ là
    tiền tố của ID dài hơn (AC-1 vs AC-10, TC-…-001 vs TC-…-0010). Mọi phép
    "có nhắc tới ID này không" của gate/hook đi qua đây, không dùng `in` trần."""
    if not needle:
        return False
    return re.search(r"(?<![\w-])" + re.escape(needle) + r"(?!\d)", hay or "") is not None


def ac_needle(ac: str, loop: str) -> str:
    """Khoá so khớp AC. Chế độ VIPER: mã AC đánh số THEO LOOP (AC-1 của l2 khác AC-1 của
    l4) nên khoá gồm cả loop: `AC-1` + `l2` → `AC-1(l2)` — so với meta `AC:` đã bỏ khoảng
    trắng. Chế độ tổng quát: cột thứ hai của bảng AC là "Nguồn" (tài liệu/mục) — KHÔNG phải
    loop, nên chỉ ghép khi nó đúng dạng `l<số>`; còn lại so mã trần bằng id_in (có biên)."""
    ac = (ac or "").strip()
    loop = (loop or "").strip()
    if loop and re.fullmatch(r"l\d+", loop):
        return re.sub(r"\s+", "", f"{ac}({loop})")
    return ac


def norm_type(s: str) -> str:
    """Chuẩn hoá tên loại test để so bằng đẳng thức: gộp gạch nối/khoảng trắng,
    thường hoá — `tương-thích-ngược` ≡ `tương thích ngược`."""
    return re.sub(r"[-\s]+", " ", s or "").strip().lower()


def oos_types(oos_section: str) -> set[str]:
    """Tên loại test khai TƯỜNG MINH ở TEST-PLAN §3: mỗi dòng lấy phần trước dấu
    `—`/`:` rồi tách bằng ,/;/·, chuẩn hoá qua norm_type. Nhắc tên loại trong văn
    xuôi hay URL (`/api/…`) KHÔNG tính là bỏ loại đó khỏi phạm vi."""
    out: set[str] = set()
    for line in (oos_section or "").splitlines()[1:]:
        s = line.strip().lstrip("-*·").strip()
        if not s:
            continue
        s = re.split(r"[—–:]", s, 1)[0]
        for tok in re.split(r"[,;·]", s):
            tok = norm_type(tok)
            if tok:
                out.add(tok)
    return out


# --- lệnh Bash có ghi vào một đường dẫn không --------------------------------

WRITE_GIT = re.compile(r"\bgit\b[^|;&]*\s(commit|checkout|reset|clean|rm|mv|push|restore|stash|am|apply|merge|rebase)\b")


def bash_writes_into(command: str, target: str, aliases: tuple[str, ...] = ()) -> bool:
    """Lệnh Bash có GHI vào target không — xét theo TỪNG lệnh đơn trong chuỗi ghép,
    để lệnh đọc thuần (cat/grep/git log) và `cp <target> <nơi khác>` đi qua.
    Dùng chung cho guard_readonly (target = repo nguồn) và guard_frozen/guard_verdict
    (target = tên file bị khoá). `aliases`: các dạng viết khác của cùng đường dẫn."""
    forms = tuple(x for x in (target,) + aliases if x)
    if not any(f in command for f in forms):
        return False
    for seg in re.split(r"&&|\|\||;|\|", command):
        hit = next((f for f in forms if f in seg), "")
        if not hit:
            continue
        # redirect / tee với ĐÍCH chứa target
        for m in re.finditer(r"(?:>>?|\btee\b(?:\s+-a)?)\s*(\S+)", seg):
            if hit in m.group(1):
                return True
        toks = seg.strip().split()
        # bỏ tiền tố env VAR=x và sudo-như (deny đã chặn sudo, nhưng cứ phòng)
        while toks and ("=" in toks[0] or toks[0] in ("env", "command")):
            toks = toks[1:]
        if not toks:
            continue
        head = toks[0]
        args = toks[1:]
        if head == "git" and WRITE_GIT.search(seg):
            return True
        if head in ("rm", "rmdir", "mv", "ln", "touch", "mkdir", "chmod", "chown", "truncate"):
            if any(hit in a for a in args):
                return True
        if head == "cp":
            plain = [a for a in args if not a.startswith("-")]
            if plain and hit in plain[-1]:  # chỉ chặn khi ĐÍCH chứa target
                return True
        if head == "sed" and "-i" in args and any(hit in a for a in args):
            return True
        if head in ("python", "python3", "node", "npm", "npx") and any(hit in a for a in args):
            # script chạy VỚI đường dẫn làm tham số — không đoán được đọc hay ghi; cho qua
            # (fail-open có chủ đích — kẻ cố tình lách thì hook nào cũng thua, luật + review
            # của QC mới là lưới cuối).
            continue
    return False


# --- STATE -------------------------------------------------------------------

def state() -> dict:
    """Trạng thái sống. Thiếu file → dict rỗng có khoá đầy đủ."""
    text = read("STATE.md")
    def grab(pat):
        m = re.search(pat, text)
        return m.group(1) if m else None
    return {
        "pha": grab(r"Pha hiện tại\s*:\s*(S|P|E|C)\b"),
        "pha_raw": grab(r"Pha hiện tại\s*:\s*(\S+)"),
        "release": int(grab(r"Release\s*:\s*(\d+)") or 0),
        "ban_giao": int(grab(r"Lần bàn giao\s*:\s*(\d+)") or 0),
        "release_mo": grab(r"Release mở\s*:\s*(\d{4}-\d{2}-\d{2})"),
        "ban_giao_mo": grab(r"Bàn giao mở\s*:\s*(\d{4}-\d{2}-\d{2})"),
        "scope_khoa": bool(re.search(r"^- \[x\] \*\*Scope khoá\*\*", text, re.MULTILINE)),
        "raw": text,
    }


def moc(st: dict) -> str | None:
    """Mốc đếm của lượt hiện tại: max(Release mở, Bàn giao mở) — ISO so chuỗi được."""
    dates = [d for d in (st.get("release_mo"), st.get("ban_giao_mo")) if d]
    return max(dates) if dates else None


def challenge_pass(st: dict, pha: str) -> bool:
    """Có dòng challenge PASS của pha, ngày ≥ mốc, trong STATE §Challenge log."""
    block = section(read_live("STATE.md"), "## Challenge log")
    floor = moc(st)
    for cells in table_rows(block):
        if len(cells) >= 4 and cells[1].strip() == pha and "PASS" in cells[3].upper():
            d = ISO.search(cells[0])
            if d and (floor is None or d.group(0) >= floor):
                return True
    return False


def blocker_ids(text_needle: str) -> bool:
    """text_needle (vd một TC id) có xuất hiện TRỌN VẸN trong bảng §Blocker của STATE không."""
    return id_in(text_needle, section(read_live("STATE.md"), "## Blocker"))


# --- manifest & repo nguồn ---------------------------------------------------
#
# Hai chế độ (SPEC.md §1.3):
#   VIPER    — `Quy trình dev: VIPER` HOẶC manifest có dòng `Repo VIPER:` (định dạng cũ).
#              Giữ nguyên mọi đối chiếu loop / _PROPOSAL.md / mirror viper/.
#   tổng quát — mọi quy trình dev khác. Đầu vào là `Repo nguồn:` (repo code HOẶC thư mục
#              tài liệu bàn giao), `Phạm vi:` + `Bản deploy:` là văn bản tự do.
# Hai chế độ dùng CHUNG: hook chỉ-đọc, bảng URL, lượt bàn giao, mục bug đã fix.

ENVIRONMENTS = ("production", "staging")

def manifest_path(n: int, k: int) -> Path | None:
    """File manifest của lượt k (k=1: RELEASE.md · k≥2: RELEASE-<k>.md). None nếu thiếu."""
    d = ROOT / "intake" / "releases" / f"r{n}"
    p = d / ("RELEASE.md" if k <= 1 else f"RELEASE-{k}.md")
    return p if p.is_file() else None


def parse_manifest(path: Path | None) -> dict:
    text = read(path) if path else ""
    live = COMMENT.sub("", text)
    def grab(pat):
        m = re.search(pat, live, re.MULTILINE)
        return m.group(1).strip() if m else None
    quy_trinh = grab(r"^Quy trình dev\s*:\s*(.+)$")
    repo_viper = grab(r"^Repo VIPER\s*:\s*(.+)$")
    is_viper = bool(repo_viper) or bool(quy_trinh and re.match(r"viper\b", quy_trinh, re.I))
    pham_vi = grab(r"^Phạm vi loop\s*:\s*(.+)$") or grab(r"^Phạm vi\s*:\s*(.+)$")
    pv = re.match(r"l?(\d+)\s*[–—-]\s*l?(\d+)", pham_vi or "")
    ban_deploy = grab(r"^Loop deploy\s*:\s*(.+)$") or grab(r"^Bản deploy\s*:\s*(.+)$")
    ld = re.match(r"l?(\d+)\s*$", ban_deploy or "")
    moi_truong = (grab(r"^Môi trường\s*:\s*(\S+)") or "production").lower()
    fixed_sec = section(live, "## Dev đã fix") or section(live, "## VIPER đã fix")
    fixed = re.findall(r"^\s*-\s*(BUG-r\d+-\d+)", fixed_sec, re.MULTILINE)
    return {
        "text": text,
        "ok": bool(text.strip()) and "{{" not in text,
        "mode": "viper" if is_viper else "tong-quat",
        "quy_trinh": quy_trinh or ("VIPER" if repo_viper else None),
        "repo": repo_viper or grab(r"^Repo nguồn\s*:\s*(.+)$"),
        "release": int(grab(r"^Release\s*:\s*(\d+)") or 0),
        "pham_vi": pham_vi,
        "ban_deploy": ban_deploy,
        "moi_truong": moi_truong,
        "loop_a": int(pv.group(1)) if (pv and is_viper) else None,
        "loop_b": int(pv.group(2)) if (pv and is_viper) else None,
        "loop_deploy": int(ld.group(1)) if (ld and is_viper) else 0,
        "url": grab(r"^Điểm vào chính\s*:\s*(\S+)") or grab(r"^URL production\s*:\s*(\S+)"),
        "urls": manifest_urls(text),
        "ban_giao": int(grab(r"^Lần bàn giao\s*:\s*(\d+)") or 0),
        "build_mobile": grab(r"^Build\s*:\s*(.+)$"),
        "fixed_bugs": fixed,
    }


def manifest_urls(text: str) -> list[dict]:
    """Bảng `## URL theo target` của manifest — hệ nhiều microservice khai từng endpoint
    ở đây; một app thì một dòng. Bỏ dòng mẫu/placeholder."""
    out: list[dict] = []
    for cells in table_rows(section(text, "## URL theo target")):
        if len(cells) < 3:
            continue
        target = cells[0].strip("` ")
        if not target or target in ("—", "-") or "{{" in "|".join(cells) or UNFILLED in target:
            continue
        out.append({
            "target": target,
            "loai": cells[1].strip(),
            "url": cells[2].strip("` "),
            "health": cells[3].strip() if len(cells) > 3 else "",
            "ghi_chu": cells[4].strip() if len(cells) > 4 else "",
        })
    return out


def inscope_targets() -> list[str]:
    """Target (boundary/experience) khai `Trong phạm vi` = có ở context/ARCHITECTURE §1–§3.
    Đây là danh sách mà manifest phải khai URL và ENVIRONMENT phải dựng được."""
    text = read_live("context/ARCHITECTURE.md")
    out: list[str] = []
    for head in ("## 1.", "## 2.", "## 3."):
        for cells in table_rows(section(text, head)):
            if not cells or len(cells) < 2:
                continue
            name = cells[0].strip("` ")
            if not name or name in ("—", "-") or UNFILLED in name:
                continue
            last = cells[-1].strip().lower()
            if last.startswith("có") or last in ("✓", "x", "yes"):
                out.append(name)
    return out


def current_manifest(st: dict | None = None) -> dict:
    """Manifest của lượt hiện tại theo STATE — nếu file lượt k thiếu, lùi về bản k lớn
    nhất đang có (để hook lấy được đường dẫn repo nguồn ngay cả khi QC chưa thả bản mới)."""
    st = st or state()
    n = st.get("release") or 0
    for k in range(max(st.get("ban_giao") or 1, 1), 0, -1):
        p = manifest_path(n, k)
        if p:
            return parse_manifest(p)
    return parse_manifest(None)


def mirror_dir(n: int, mode: str) -> Path:
    """Bản chụp đóng băng tài liệu bàn giao: VIPER → intake/releases/r<N>/viper/,
    tổng quát → intake/releases/r<N>/nguon/."""
    return ROOT / "intake" / "releases" / f"r{n}" / ("viper" if mode == "viper" else "nguon")


def moi_truong(st: dict | None = None) -> str:
    """Môi trường test khai trong manifest lượt hiện tại — `production` | `staging`.
    Thiếu dòng → `production` (mặc định của SPEC gốc: luật cách ly đầy đủ)."""
    return current_manifest(st).get("moi_truong") or "production"


def source_root(st: dict | None = None) -> Path | None:
    """Đường dẫn repo nguồn (`Repo nguồn:` / `Repo VIPER:`) từ manifest, LUÔN resolve (theo symlink) — hook so chuỗi
    đường dẫn với `Path(...).resolve()` của phía kia, không resolve cả hai bên thì
    /var vs /private/var trên macOS làm phép so trượt và hook mở toang."""
    repo = current_manifest(st).get("repo")
    if not repo:
        return None
    p = Path(repo)
    if not p.is_absolute():
        p = ROOT / repo
    try:
        p = p.resolve()
    except OSError:
        return None
    return p if p.is_dir() else None


viper_root = source_root  # tên cũ — giữ cho script/dự án đời trước


def viper_loops_with_p(root: Path) -> list[int]:
    """Các loop bên repo VIPER có `P` trong dòng `Pha vòng này` của _PROPOSAL.md."""
    out = []
    for prop in sorted(root.glob("intake/loops/l*/_PROPOSAL.md")):
        m = re.search(r"l(\d+)", prop.parent.name)
        line = re.search(r"^Pha vòng này\s*:\s*(.+)$", read(prop), re.MULTILINE)
        if m and line and re.search(r"(?<![A-Za-z])P(?![A-Za-z0-9])", line.group(1)):
            out.append(int(m.group(1)))
    return out


# --- TEST-PLAN ---------------------------------------------------------------

def plan_path(n: int) -> str:
    return f"context/releases/r{n}/TEST-PLAN.md"


def plan(n: int) -> dict:
    text = read_live(plan_path(n))
    def grab(pat):
        m = re.search(pat, text, re.MULTILINE)
        return m.group(1).strip() if m else None
    ac_rows = [c for c in table_rows(section(text, "## 1."))
               if c and re.match(r"AC-\d+", c[0])]
    ti_rows = [c for c in table_rows(section(text, "## 2."))
               if c and re.match(r"TI-\d+", c[0])]
    reg_rows = [c for c in table_rows(section(text, "## 5."))
                if c and c[0] and not c[0].startswith("—")]
    return {
        "exists": bool(text.strip()),
        "text": text,
        "pham_vi": grab(r"^Phạm vi loop\s*:\s*(.+)$") or grab(r"^Phạm vi\s*:\s*(.+)$"),
        "luot_max": int(grab(r"^Lượt bàn giao tối đa\s*:\s*(\d+)") or 0),
        "ra_lai": grab(r"^Rà lại chiến lược \(release \d+\)\s*:\s*(\d{4}-\d{2}-\d{2})"),
        "chot_qc": grab(r"^Chốt bởi QC\s*:\s*(\d{4}-\d{2}-\d{2})"),
        # (mã AC, loop|nguồn, capability) — cột 2 là `Loop` (VIPER) hoặc `Nguồn` (tổng quát)
        "ac": [(c[0], c[1] if len(c) > 1 else "", c[2] if len(c) > 2 else "")
               for c in ac_rows],
        # (mã TI, tên, loại, nguồn, mức)
        "ti": [(c[0], *(c[1:5] + [""] * (4 - len(c[1:5])))) for c in ti_rows],
        "out_of_scope": section(text, "## 3."),
        "nguong": section(text, "## 4."),
        "regression": [c[0].strip("` ") for c in reg_rows if re.match(r"TC-", c[0].strip("` "))],
    }


def plan_thresholds(p: dict) -> dict:
    """Đọc bảng ngưỡng §4 theo nhãn dòng. Không đọc được ô nào → None ở ô đó."""
    s1 = s2_pass = s2_cond = pct = None
    for cells in table_rows(p.get("nguong", "")):
        if len(cells) < 2:
            continue
        label, val = cells[0], cells[1]
        if "S1" in label:
            m = re.search(r"\d+", val)
            s1 = int(m.group(0)) if m else None
        elif "S2" in label:
            m = re.search(r"(\d+)", val)
            s2_pass = int(m.group(1)) if m else None
            mc = re.search(r"≤\s*(\d+)", val)
            s2_cond = int(mc.group(1)) if mc else None
        elif "Tổng TC" in label:
            m = re.search(r"(\d+)\s*%", val)
            pct = int(m.group(1)) if m else None
    return {"s1": s1, "s2_pass": s2_pass, "s2_cond": s2_cond, "pct_pass": pct}


# --- testcases ---------------------------------------------------------------

TC_HEAD = re.compile(r"^### (TC-[A-Za-z0-9ĐđÀ-ỹ_-]+-\d+)\s*[—–-]\s*(.+)$", re.MULTILINE)


def all_testcases() -> list[dict]:
    """Mọi TC sống trong context/testcases/ — kèm dòng meta đã tách nhãn."""
    out: list[dict] = []
    tc_dir = ROOT / "context" / "testcases"
    if not tc_dir.is_dir():
        return out
    for f in sorted(tc_dir.glob("*.md")):
        if f.name.startswith("_TC-TEMPLATE"):
            continue
        text = read_live(f)
        heads = list(TC_HEAD.finditer(text))
        for i, h in enumerate(heads):
            end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
            block = text[h.end():end]
            meta_line = next((l.strip() for l in block.splitlines() if l.strip()), "")
            meta: dict[str, str] = {}
            for part in meta_line.split("·"):
                if ":" in part:
                    key, val = part.split(":", 1)
                    meta[key.strip()] = val.strip()
            out.append({
                "id": h.group(1), "title": h.group(2).strip(), "file": f.name,
                "meta": meta, "removed": "đã gỡ" in h.group(2),
            })
    return out


def tcs_of_release(n: int, tcs: list[dict] | None = None) -> list[dict]:
    tcs = tcs if tcs is not None else all_testcases()
    return [t for t in tcs
            if not t["removed"] and t["meta"].get("Release vào") == str(n)]


# --- RUNLOG ------------------------------------------------------------------

def runlog_path(n: int) -> str:
    return f"context/releases/r{n}/RUNLOG.md"


def runlog(n: int) -> dict:
    """Các mục lượt chạy: {k: {"retest": [tc...], "rows": [dict...]}}."""
    text = read_live(runlog_path(n))
    sections: dict[int, dict] = {}
    heads = list(re.finditer(r"^## Lượt chạy — bàn giao (\d+)", text, re.MULTILINE))
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        body = text[h.start():end]
        retest = [c[0].strip("` ") for c in table_rows(section(body, "### Phạm vi retest"))
                  if c and c[0].strip("` ").startswith("TC-")]
        rows = []
        for c in table_rows(section(body, "### Kết quả chạy")):
            if len(c) >= 5 and c[2].strip("` ").startswith("TC-"):
                rows.append({
                    "ngay": (ISO.search(c[0]).group(0) if ISO.search(c[0]) else None),
                    "dot": c[1], "tc": c[2].strip("` "), "agent": c[3],
                    "kq": c[4].strip().upper(),
                    "evidence": c[5].strip("` ") if len(c) > 5 else "",
                    "bug": c[6].strip("` ") if len(c) > 6 else "",
                })
        sections[int(h.group(1))] = {"retest": retest, "rows": rows}
    return {"exists": bool(text.strip()), "sections": sections, "text": text}


def scope_of_luot(n: int, k: int, rl: dict | None = None,
                  p: dict | None = None) -> list[str]:
    """Danh sách TC phải chạy trong lượt k: lượt 1 = TC mới + regression đã chọn;
    lượt ≥2 = bảng Phạm vi retest của mục lượt đó."""
    rl = rl or runlog(n)
    if k >= 2:
        return rl["sections"].get(k, {}).get("retest", [])
    p = p or plan(n)
    new_ids = [t["id"] for t in tcs_of_release(n)]
    return sorted(set(new_ids + p.get("regression", [])))


def final_results(n: int, upto_k: int, rl: dict | None = None) -> dict[str, dict]:
    """Kết quả CUỐI của từng TC qua các lượt ≤ upto_k (dòng sau đè dòng trước)."""
    rl = rl or runlog(n)
    out: dict[str, dict] = {}
    for k in sorted(rl["sections"]):
        if k > upto_k:
            continue
        for row in rl["sections"][k]["rows"]:
            out[row["tc"]] = row
    return out


# --- BUGS --------------------------------------------------------------------

BUG_HEAD = re.compile(r"^### (BUG-r(\d+)-\d+)\b.*$", re.MULTILINE)


def bugs() -> list[dict]:
    text = read_live("context/BUGS.md")
    heads = list(BUG_HEAD.finditer(text))
    out = []
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        block = text[h.start():end]
        sev = re.search(r"\|\s*Severity\s*\|\s*(S[1-4])", block)
        stt = re.search(r"\|\s*Trạng thái\s*\|\s*([^|]+)\|?", block)
        out.append({
            "id": h.group(1), "release": int(h.group(2)),
            "severity": sev.group(1) if sev else None,
            "status": (stt.group(1).strip() if stt else ""),
            "block": block,
        })
    return out


def bug_is_open(b: dict) -> bool:
    s = b["status"]
    return s.startswith("mở") or "chờ retest" in s


def open_bugs_by_sev(n: int, bug_list: list[dict] | None = None) -> dict[str, int]:
    """Bug 'mở' / 'đã fix chờ retest' đếm theo severity — TÍNH CẢ bug các release
    trước còn mở (cam kết của PASS-có-điều-kiện không tự biến mất khi sang release
    mới; muốn thôi đếm phải `đóng` / `không sửa` / `deferred` có vết)."""
    counts = {"S1": 0, "S2": 0, "S3": 0, "S4": 0}
    for b in (bug_list if bug_list is not None else bugs()):
        if b["release"] > n:
            continue
        if bug_is_open(b) and b["severity"] in counts:
            counts[b["severity"]] += 1
    return counts


# --- REPORT ------------------------------------------------------------------

def report_path(n: int) -> str:
    return f"context/releases/r{n}/REPORT.md"


def report_conclusions(n: int) -> dict[int, dict]:
    text = read_live(report_path(n))
    out: dict[int, dict] = {}
    heads = list(re.finditer(r"^## Kết luận — bàn giao (\d+)", text, re.MULTILINE))
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        body = text[h.start():end]
        v = re.search(r"Verdict\s*:\s*(PASS-có-điều-kiện|PASS|FAIL)", body)
        ky = re.search(r"Ký bởi QC\s*:\s*(\d{4}-\d{2}-\d{2})", body)
        out[int(h.group(1))] = {
            "verdict": v.group(1) if v else None,
            "ky_qc": ky.group(1) if ky else None,
        }
    return out


# --- TEST-STRATEGY -----------------------------------------------------------

def strategy() -> dict:
    text = read_live("context/TEST-STRATEGY.md")
    chot = re.search(r"^Chốt bởi QC\s*:\s*(\d{4}-\d{2}-\d{2})", text, re.MULTILINE)
    rel_rows = [c for c in table_rows(section(text, "## 2."))
                if c and re.match(r"r\d+", c[0])]
    matrix = section(text, "## 3.")
    loai: list[str] = []
    ticks: dict[str, bool] = {}
    for line in matrix.splitlines():
        s = line.strip()
        if s.startswith("| Target"):
            loai = [c.strip() for c in s.strip("|").split("|")][1:]
            ticks = {name: False for name in loai if name}
        elif loai and s.startswith("|") and not re.match(r"\|[\s|:-]+\|$", s):
            cells = [c.strip() for c in s.strip("|").split("|")]
            for name, cell in zip(loai, cells[1:]):
                if name and "✓" in cell:
                    ticks[name] = True
    reg_min = re.search(r"Số TC regression tối thiểu[^|]*\|\s*(\d+)", text)
    changelog = [c for c in table_rows(section(text, "## 11."))
                 if c and ISO.search(c[0] or "")]
    return {
        "exists": bool(text.strip()),
        "text": text,
        "chot_qc": chot.group(1) if chot else None,
        "release_rows": rel_rows,          # [r<N>, phạm vi, bản deploy, …]
        "loai": [n for n in loai if n],
        "loai_ticked": [n for n, t in ticks.items() if t],
        "regression_min": int(reg_min.group(1)) if reg_min else None,
        "changelog": changelog,
    }


# --- gate E: ba phép đếm dùng chung với guard_verdict ------------------------

def gate_e_missing(n: int, k: int) -> list[str]:
    """Danh sách thiếu sót khiến pha E chưa xong. Rỗng = gate E xanh (phần máy).
    guard_verdict chặn ghi REPORT khi danh sách này chưa rỗng."""
    problems: list[str] = []
    rl = runlog(n)
    if not rl["exists"]:
        return [f"chưa có {runlog_path(n)}"]
    if k not in rl["sections"]:
        return [f"RUNLOG chưa có mục `## Lượt chạy — bàn giao {k}` (fail-closed — "
                f"lượt ≥2 mở bằng `release.py --retest`)"]
    st = state()
    floor = moc(st)
    sec = rl["sections"][k]
    scope = scope_of_luot(n, k, rl)
    if not scope:
        problems.append("phạm vi lượt rỗng — chưa có TC nào của release "
                        f"(Release vào: {n}) và chưa chọn regression" if k == 1
                        else "bảng `### Phạm vi retest` của lượt này rỗng")
    have = {}
    for row in sec["rows"]:
        if row["kq"] in RESULTS:
            have[row["tc"]] = row
    for tc in scope:
        row = have.get(tc)
        if row is None:
            problems.append(f"{tc}: chưa có dòng kết quả trong lượt {k}")
            continue
        if floor and (not row["ngay"] or row["ngay"] < floor):
            problems.append(f"{tc}: dòng kết quả thiếu ngày hoặc ngày < mốc lượt ({floor})")
    bug_ids = {b["id"]: b for b in bugs()}
    vr = source_root(st)
    for row in sec["rows"]:
        tc, kq = row["tc"], row["kq"]
        if kq == "PASS":
            ev = row["evidence"]
            if not ev or not ev.startswith("evidence/"):
                problems.append(f"{tc}: PASS nhưng cột Bằng chứng không trỏ evidence/…")
            else:
                ep = (ROOT / ev).resolve()
                if not ep.exists():
                    problems.append(f"{tc}: bằng chứng `{ev}` không tồn tại trên đĩa")
                elif vr and str(ep).startswith(str(vr)):
                    problems.append(f"{tc}: bằng chứng trỏ vào repo nguồn — vi phạm luật #5")
        elif kq == "FAIL":
            bug_m = re.search(r"BUG-r\d+-\d+", row["bug"] or "")
            b = bug_ids.get(bug_m.group(0)) if bug_m else None
            if b is None:
                problems.append(f"{tc}: FAIL nhưng cột Bug không trỏ BUG-r{n}-… có thật")
            elif b["severity"] not in ("S1", "S2", "S3", "S4"):
                problems.append(f"{tc}: bug {row['bug']} thiếu Severity S1–S4")
        elif kq == "BLOCKED":
            if not blocker_ids(tc):
                problems.append(f"{tc}: BLOCKED nhưng không thấy trong STATE.md §Blocker")
        elif kq == "SKIP":
            if not id_in(tc, read_live("context/DECISIONS.md")):
                problems.append(f"{tc}: SKIP nhưng không có dòng DECISIONS nhắc tới nó")
    if k >= 2:
        mf = parse_manifest(manifest_path(n, k))
        luot_text = rl["text"].split(f"## Lượt chạy — bàn giao {k}")[-1]
        for bug_id in mf.get("fixed_bugs", []):
            if not id_in(bug_id, luot_text):
                problems.append(f"{bug_id}: manifest khai đã fix nhưng lượt {k} chưa có vết retest")
    return problems


# --- verdict máy tính --------------------------------------------------------

def compute_verdict(n: int, k: int) -> tuple[str | None, list[str]]:
    """Verdict đề xuất từ số liệu, so bảng ngưỡng TEST-PLAN §4. (None, [lý do]) khi
    thiếu dữ liệu để tính."""
    p = plan(n)
    th = plan_thresholds(p)
    notes: list[str] = []
    if th["s1"] is None or th["pct_pass"] is None:
        return None, ["bảng ngưỡng TEST-PLAN §4 không đọc được (thiếu số) — điền số thật"]
    rl = runlog(n)
    fin = final_results(n, k, rl)
    bl = bugs()
    sev = open_bugs_by_sev(n, bl)
    # AC mới có ≥1 TC PASS — so khoá AC-n(l<i>) trọn vẹn, KHÔNG substring (AC-1 ≠ AC-10)
    tcs = all_testcases()
    ac_missing = []
    for ac, loop, _cap in p["ac"]:
        needle = ac_needle(ac, loop)
        ok = False
        for t in tcs:
            meta_ac = re.sub(r"\s+", "", t["meta"].get("AC", ""))
            if id_in(needle, meta_ac) and fin.get(t["id"], {}).get("kq") == "PASS":
                ok = True
                break
        if not ok:
            ac_missing.append(ac)
    # regression R1
    reg_r1_fail = []
    tc_by_id = {t["id"]: t for t in tcs}
    for tc_id in p["regression"]:
        t = tc_by_id.get(tc_id)
        if t and t["meta"].get("Mức") == "R1":
            if fin.get(tc_id, {}).get("kq") != "PASS":
                reg_r1_fail.append(tc_id)
    # tổng pass
    scope = scope_of_luot(n, 1, rl, p) if k == 1 else sorted(
        set(scope_of_luot(n, 1, rl, p)) | set(scope_of_luot(n, k, rl, p)))
    ran = [fin[t]["kq"] for t in scope if t in fin]
    pct = round(100 * sum(1 for r in ran if r == "PASS") / len(ran), 1) if ran else 0.0
    # bug còn mở mang sang từ release trước + cam kết DECISIONS cho từng S2 mở
    carried = [b["id"] for b in bl if b["release"] < n and bug_is_open(b)]
    dec_text = read_live("context/DECISIONS.md")
    s2_open = [b["id"] for b in bl
               if b["release"] <= n and b["severity"] == "S2" and bug_is_open(b)]
    s2_uncommitted = [i for i in s2_open if not id_in(i, dec_text)]
    notes.append(f"bug mở: S1={sev['S1']} S2={sev['S2']} S3={sev['S3']} S4={sev['S4']}"
                 + (f" (mang sang từ release trước: {carried})" if carried else ""))
    notes.append(f"AC mới thiếu PASS: {ac_missing or '—'}")
    notes.append(f"regression R1 chưa PASS: {reg_r1_fail or '—'}")
    notes.append(f"tổng TC PASS: {pct}% (ngưỡng ≥ {th['pct_pass']}%)")
    if s2_open:
        notes.append(f"S2 mở thiếu dòng DECISIONS cam kết: {s2_uncommitted or '—'}")
    luot_max = p["luot_max"] or 99
    if sev["S1"] > (th["s1"] or 0) or ac_missing or k > luot_max:
        return "FAIL", notes
    if sev["S2"] <= (th["s2_pass"] or 0) and not reg_r1_fail and pct >= th["pct_pass"]:
        return "PASS", notes
    # PASS-có-điều-kiện KHÔNG phải cửa thoát ngưỡng: các điều kiện PASS còn lại
    # (tổng TC PASS, regression R1, AC — đã chặn ở FAIL) vẫn phải đạt, và TỪNG S2 mở
    # phải có dòng DECISIONS cam kết (khuôn TEST-STRATEGY §10).
    if (th["s2_cond"] is not None and sev["S2"] <= th["s2_cond"] and not reg_r1_fail
            and pct >= th["pct_pass"] and not s2_uncommitted):
        return "PASS-có-điều-kiện", notes
    return "FAIL", notes
