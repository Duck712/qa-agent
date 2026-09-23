#!/usr/bin/env python3
"""qa_check.py — kiểm tra nhẹ cho workspace qa/ (Python chuẩn, không phụ thuộc).

    python3 .claude/qa-scripts/qa_check.py status                 tình trạng: REQ, câu hỏi chờ, scope, TC, run, bug, bài học
    python3 .claude/qa-scripts/qa_check.py tc [REQ-…|<tính năng>] [--strict]
                                                                  soát TC (trường, normal+abnormal, kỳ vọng, kỹ thuật, chỗ trống)
    python3 .claude/qa-scripts/qa_check.py select <phạm vi>       in TC theo: all | smoke | regression [TC-…] | retest BUG-… | <tính năng> | TC-…
    python3 .claude/qa-scripts/qa_check.py new-run <loại> [phạm vi]   tạo qa/runs/<ngày>-<loại>/RUNLOG.md, mọi dòng CHƯA CHẠY
    python3 .claude/qa-scripts/qa_check.py run [<run-id>]         soát RUNLOG + bằng chứng, kết luận theo tiêu chí đóng băng trong RUNLOG
    python3 .claude/qa-scripts/qa_check.py release <run-id> [<run-id>…]
                                                                  "phát hành được chưa": gộp kết quả mới nhất của mọi TC trong SCOPE
                                                                  qua các run, xét MỌI bug mở mức cấm
    python3 .claude/qa-scripts/qa_check.py trace [--write]        ma trận truy vết REQ × TC × kỹ thuật × kết quả × bug

Không phải cổng chặn — chỉ báo. Không tự đặt con số nào: tiêu chí đạt, mức rủi ro, N lần chạy AI lấy từ SCOPE do
người dùng chốt; thiếu hoặc không đọc được thì báo "chưa chốt", không dùng mặc định. Exit 0 sạch · 1 có lỗi · 2 sai cách gọi.
"""

from __future__ import annotations

import datetime as dt
import os
import re
import sys
import unicodedata
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


# ---------------------------------------------------------------- tìm workspace

def find_root() -> Path:
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env and (Path(env) / "qa").is_dir():
        return Path(env)
    here = Path.cwd().resolve()
    for p in [here, *here.parents]:
        if (p / "qa" / "QA.md").is_file():
            return p
    return Path(__file__).resolve().parents[2]


ROOT = find_root()
QA = ROOT / "qa"

RESULTS = ["CHƯA CHẠY", "BLOCKED", "PASS", "FAIL", "SKIP"]
KIEU = {"normal", "abnormal"}
MUC = ("R1", "R2", "R3")
LOAI = {"chức năng", "biên", "phá-đầu-vào", "phân-quyền", "workflow", "api", "tích-hợp", "tương-thích",
        "hình-thức", "hiệu-năng", "bảo-mật", "khôi-phục", "cross-target", "khám-phá", "smoke"}
REQUIRED = ["REQ", "Target", "Loại", "Kiểu", "Mức", "Nguồn", "Bước", "Kỳ vọng", "Bằng chứng cần"]
OPTIONAL = ["Regression", "Tag", "Ticket", "Kỹ thuật", "Tiền điều kiện", "Dữ liệu", "Ô ma trận"]
VAGUE = ["hoạt động đúng", "hiển thị đúng", "chạy đúng", "hoạt động bình thường", "hợp lý", "như mong đợi",
         "đúng nghiệp vụ", "đúng yêu cầu", "đúng thiết kế", "xử lý đúng", "tử tế", "thân thiện", "rõ ràng",
         "performance ok", "ổn định", "mượt"]
WAIT_RE = re.compile(r"\([^()]*chờ trả lời[^()]*\)", re.I)       # nhãn chờ duy nhất: (chờ trả lời #n)
PLACEHOLDER_RE = re.compile(r"<(?!\s)(?![A-Za-z][\w-]*\s+[\w:-]+\s*=)(?=[^<>\n]*(?:\s|[^\x00-\x7f]))[^<>\n]{1,80}(?<!\s)>")
# ↑ <điền gì đó>; không phải <b>, "< 100 và >", hay thẻ HTML có thuộc tính (<svg onload=…>, <img src=x onerror=…>) trong TC
TC_ID = r"TC-\w+(?:-\w+)*-\d{3}"
REQ_ID = r"REQ-[\w.-]*\w"
BUG_CLOSED = ("đóng", "đã đóng", "closed", "không sửa", "wontfix", "hoãn", "deferred", "trùng", "duplicate")
BUG_OPEN = ("mở", "open", "đã sửa", "fixed", "mở lại", "reopened")

# danh mục kỹ thuật: tên chuẩn → họ. R1 cần ≥ 2 HỌ khác nhau (qa-testcase-design §1).
TECHNIQUES = {
    "phân vùng": "dữ liệu", "giá trị biên": "dữ liệu", "biên nhiều chiều": "dữ liệu", "syntax": "dữ liệu",
    "bảng quyết định": "logic", "phân quyền": "logic", "crud": "logic", "chuyển trạng thái": "logic",
    "use case": "logic", "pairwise": "logic", "classification tree": "logic", "hộp trắng": "logic",
    "metamorphic": "oracle", "property": "oracle", "fuzz": "oracle", "đồng thời": "oracle", "rubric": "oracle",
    "mốc hành vi": "oracle",
    "error guessing": "kinh nghiệm", "checklist": "kinh nghiệm", "khám phá": "kinh nghiệm",
    "phi chức năng": "phi chức năng", "a11y": "phi chức năng", "khả dụng": "phi chức năng",
    "hiệu năng": "phi chức năng", "tương thích": "phi chức năng", "i18n": "phi chức năng",
}
ALIASES = {"phân vùng tương đương": "phân vùng", "ep": "phân vùng", "biên": "giá trị biên", "bva": "giá trị biên",
           "domain analysis": "biên nhiều chiều", "syntax testing": "syntax", "cause-effect": "bảng quyết định",
           "ma trận phân quyền": "phân quyền", "trạng thái": "chuyển trạng thái", "kịch bản": "use case",
           "scenario": "use case", "tổ hợp": "pairwise", "white-box": "hộp trắng", "hộp trắng nhẹ": "hộp trắng",
           "race": "đồng thời", "concurrency": "đồng thời", "sbtm": "khám phá", "exploratory": "khám phá",
           "wcag": "a11y", "usability": "khả dụng", "characterization": "mốc hành vi", "golden master": "mốc hành vi"}


def read(p: Path) -> str:
    try:
        return unicodedata.normalize("NFC", p.read_text(encoding="utf-8-sig", errors="replace"))
    except OSError:
        return ""


def waiting(text: str) -> bool:
    return bool(WAIT_RE.search(text or ""))


def natural(name: str) -> list:
    return [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", name)]


def plain(s: str) -> str:
    return re.sub(r"[*_`]", "", s or "").strip()


def no_paren(s: str) -> str:
    return re.sub(r"\([^()]*\)", "", s or "").strip()


# ---------------------------------------------------------------- markdown nhỏ

def section(text: str, prefix: str) -> str:
    """Nội dung dưới heading `## <prefix>…` tới heading ## kế tiếp."""
    m = re.search(rf"^##\s+{re.escape(prefix)}.*$", text, re.M)
    if not m:
        return ""
    rest = text[m.end():]
    n = re.search(r"^##\s", rest, re.M)
    return rest[: n.start()] if n else rest


def table_rows(text: str) -> list[list[str]]:
    """Các dòng dữ liệu của bảng markdown (bỏ header + dòng ---); hiểu `\\|` là ký tự | trong ô."""
    rows, header_seen = [], False
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            header_seen = False
            continue
        cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", s.strip("|"))]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            header_seen = True
            continue
        if not header_seen:
            continue  # dòng header
        if any(cells):
            rows.append(cells)
    return rows


def field(text: str, key: str) -> str:
    """Giá trị của dòng `- Khoá: giá trị` (chấp nhận khoá in đậm `- **Khoá**:`)."""
    m = re.search(rf"^[ \t]*-[ \t]*\*{{0,2}}{re.escape(key)}\*{{0,2}}[ \t]*:\*{{0,2}}[ \t]*(.*)$", text, re.M)
    if not m:
        return ""
    v = re.sub(r"<!--.*?-->", "", m.group(1)).strip()
    return re.sub(r"^\*{1,2}|\*{1,2}$", "", v).strip()


def field_any(text: str, *keys: str) -> str:
    for k in keys:
        v = field(text, k)
        if v:
            return v
    return ""


# ---------------------------------------------------------------- dữ liệu

KNOWN_KEYS = "|".join(re.escape(k) for k in REQUIRED + OPTIONAL)


def block_items(body: str, key: str) -> list[str]:
    m = re.search(rf"^[ \t]*-[ \t]*\*{{0,2}}{re.escape(key)}\*{{0,2}}[ \t]*:\*{{0,2}}[ \t]*(.*)$", body, re.M)
    if not m:
        return []
    items = [m.group(1).strip()] if m.group(1).strip() else []
    for line in body[m.end():].splitlines()[1:]:
        if re.match(rf"^-[ \t]*\*{{0,2}}({KNOWN_KEYS})\*{{0,2}}[ \t]*:", line):   # chỉ dừng ở trường TC khác
            break
        s = line.strip()
        if re.match(r"^(\d+[.)]|-)\s+\S", s):
            items.append(re.sub(r"^(\d+[.)]|-)\s+", "", s))
        elif s and not items:
            items.append(s)
    return [x for x in items if x]


def load_tcs() -> tuple[dict[str, dict], list[str]]:
    tcs: dict[str, dict] = {}
    errors: list[str] = []
    d = QA / "testcases"
    for f in sorted(d.glob("*.md")) if d.is_dir() else []:
        if f.name.startswith("_"):
            continue
        text = read(f)
        for m in re.finditer(r"^(#{1,6})\s+(.*)$", text, re.M):
            head = m.group(2)
            if re.search(r"(^|[^\w-])TC-", head, re.I):
                ok = m.group(1) == "##" and re.match(rf"({TC_ID})(?!\S)", head)
                if not ok:
                    errors.append(f"{f.name}: tiêu đề `{m.group(0)[:60]}` không đúng khuôn `## TC-<TÍNH-NĂNG>-<3 chữ số> — …`"
                                  " — TC này không được đếm")
        heads = list(re.finditer(rf"^##\s+({TC_ID})(?!\S)\s*[—-]?\s*(.*)$", text, re.M))
        for i, h in enumerate(heads):
            body = text[h.end(): heads[i + 1].start() if i + 1 < len(heads) else len(text)]
            tid = h.group(1)
            if tid in tcs:
                errors.append(f"{tid}: ID trùng ({tcs[tid]['file']} và {f.name})")
                continue
            tc = {"id": tid, "title": h.group(2).strip(), "file": f.name, "feature": f.stem, "body": body}
            for k in REQUIRED + OPTIONAL:
                tc[k] = field(body, k)
            for k in ("Kiểu", "Mức", "Loại", "Regression", "Tag"):
                tc[k] = no_paren(plain(tc[k]))
            tc["reqs"] = req_ids(tc["REQ"])
            tc["steps"] = block_items(body, "Bước")
            tc["expects"] = block_items(body, "Kỳ vọng")
            tcs[tid] = tc
    return tcs, errors


def scope_file() -> Path:
    return QA / "SCOPE.md"


def req_ids(cell: str) -> list[str]:
    return [r.upper() for r in re.findall(REQ_ID, cell or "", re.I)]


def scope_rows(text: str | None = None) -> list[list[str]]:
    text = read(scope_file()) if text is None else text
    return [r for r in table_rows(section(text, "2.")) if r and re.search(REQ_ID, r[0], re.I)]


def scope_reqs() -> list[str]:
    out: list[str] = []
    for r in scope_rows():
        out += [x for x in req_ids(r[0]) if x not in out]
    return out


def scope_levels(include_old: bool = True) -> dict[str, str]:
    """REQ → mức R người dùng đã xác nhận ở SCOPE §2 (cột 4). REQ không có trong SCOPE hiện tại → tìm ở SCOPE-<đợt>.md
    cũ (REQ đã phát hành, còn regression). Không suy từ TC."""
    out: dict[str, str] = {}
    files = [scope_file()] + (sorted(QA.glob("SCOPE-*.md"), key=lambda p: p.stat().st_mtime, reverse=True) if include_old else [])
    for f in files:
        for r in scope_rows(read(f)):
            m = re.search(r"\bR[1-3]\b", r[3].upper()) if len(r) >= 4 else None
            if m:
                for req in req_ids(r[0]):
                    out.setdefault(req, m.group())
    return out


def scope_status() -> str:
    return plain(field(read(scope_file()), "Trạng thái"))


def analysis_reqs() -> list[str]:
    out: list[str] = []
    for r in table_rows(section(read(QA / "ANALYSIS.md"), "3.")):
        if r:
            out += [x for x in req_ids(r[0]) if x not in out]
    return out


def waiting_reqs() -> set[str]:
    """REQ ở ANALYSIS §3 còn nhãn `(chờ trả lời #n)` (kể cả REQ rút từ code chưa được người dùng xác nhận)."""
    out: set[str] = set()
    for r in table_rows(section(read(QA / "ANALYSIS.md"), "3.")):
        if r and waiting(" ".join(r)):
            out |= set(req_ids(r[0]))
    return out


def open_questions() -> list[str]:
    rows = table_rows(section(read(QA / "ANALYSIS.md"), "5."))
    return [f"#{r[0]} {r[1]}" for r in rows
            if len(r) >= 2 and r[1] and not r[1].startswith("<") and (len(r) < 5 or not r[4])]


def target_types() -> dict[str, str]:
    rows = table_rows(section(read(QA / "QA.md"), "Target"))
    return {r[0]: (plain(r[1]).lower() if len(r) > 1 else "") for r in rows if r and r[0]}


def bug_state(status: str) -> tuple[bool, bool]:
    """(còn mở, trạng thái có nhận ra). Trạng thái lạ/trống → coi là còn mở (an toàn)."""
    s = plain(status).lower()
    if s.startswith(BUG_CLOSED):
        return False, True
    return True, s.startswith(BUG_OPEN)


def load_bugs() -> dict[str, dict]:
    text = re.sub(r"<!--.*?-->", "", read(QA / "BUGS.md"), flags=re.S)
    bugs = {}
    heads = list(re.finditer(r"^##\s+(BUG-\d+)\b\s*[—-]?\s*(.*)$", text, re.M))
    for i, h in enumerate(heads):
        body = text[h.end(): heads[i + 1].start() if i + 1 < len(heads) else len(text)]
        sev = re.search(r"S[1-4]", field(body, "Severity").upper())
        status = field(body, "Trạng thái")
        is_open, known = bug_state(status)
        run = Path(plain(field(body, "Run")).rstrip("/")).name
        bugs[h.group(1)] = {"id": h.group(1), "title": h.group(2).strip(), "sev": sev.group() if sev else "",
                            "status": plain(status).lower(), "open": is_open, "known": known,
                            "tc": re.findall(TC_ID, field(body, "TC")), "run": run}
    return bugs


# ---------------------------------------------------------------- tiêu chí đạt

def parse_pct(line: str) -> float | None:
    """Đúng MỘT con số có dấu % và không có số trần nào khác; có nhắc R1–R3 → không đọc (dùng dòng riêng theo mức)."""
    if not line or re.search(r"\bR[1-3]\b", line, re.I):
        return None
    pct = re.findall(r"(\d+(?:[.,]\d+)?)\s*%", line)
    bare = re.findall(r"\d+(?:[.,]\d+)?", line)
    if len(pct) != 1 or len(bare) != 1:
        return None
    return float(pct[0].replace(",", "."))


def parse_sev(line: str) -> set[str] | None:
    t = plain(line).upper().strip()
    if not t:
        return None
    if re.fullmatch(r"(KHÔNG|KHONG|NONE|-|—)", t):
        return set()
    m = re.fullmatch(r"S([1-4])\s*[–—-]\s*S([1-4])", t)
    if m:
        a, b = sorted((int(m.group(1)), int(m.group(2))))
        return {f"S{i}" for i in range(a, b + 1)}
    m = re.fullmatch(r"(?:MỌI BUG\s+)?S([1-4])\s*(?:TRỞ LÊN|\+|VÀ NẶNG HƠN)", t)
    if m:
        return {f"S{i}" for i in range(1, int(m.group(1)) + 1)}
    if re.fullmatch(r"S[1-4](\s*[,;/]\s*S[1-4]|\s+VÀ\s+S[1-4])*", t):
        return set(re.findall(r"S[1-4]", t))
    return None


CRIT_KEYS = {"tỉ lệ pass tối thiểu", "tỉ lệ blocked tối đa", "tỉ lệ pass tối thiểu r1", "tỉ lệ pass tối thiểu r2",
             "tỉ lệ pass tối thiểu r3", "bug mở không được phép", "soi bằng chứng — tỉ lệ bốc mẫu pass"}


def crit_block(text: str) -> str:
    """Phần tiêu chí: khối `- Tiêu chí (…):` của RUNLOG, hoặc §6 của SCOPE, hoặc cả văn bản."""
    m = re.search(r"^- Tiêu chí \(.*$", text, re.M)
    if m:
        rest = text[m.end():]
        end = re.search(r"^(?!\s+- )", rest[1:], re.M)
        return text[m.start(): m.end() + 1 + (end.start() if end else len(rest))]
    sec = section(text, "6.")
    return sec or text


def parse_criteria(text: str) -> tuple[dict | None, list[str]]:
    """→ (tiêu chí, lý do không đọc được). Thiếu/không đọc được một dòng → None (CHƯA CHỐT, không có mặc định)."""
    block = crit_block(text)
    strip = lambda v: no_paren(v).replace("—", " ").strip()      # "95% (chốt sau khi chạy — DECISIONS #3)" → "95%"
    f = strip(field(block, "Bug mở không được phép"))
    p_line = strip(field_any(block, "Tỉ lệ PASS tối thiểu", "Tỷ lệ PASS tối thiểu"))
    b_line = strip(field_any(block, "Tỉ lệ BLOCKED tối đa", "Tỷ lệ BLOCKED tối đa"))
    odd = [m.group(0).strip() for m in re.finditer(r"^[ \t]*-[ \t]*\**[ \t]*(?:Tỉ|Tỷ) lệ[^\n]*$", block, re.M | re.I)
           if re.sub(r"\s+", " ", re.sub(r"[*`]", "", m.group(0).split(":", 1)[0]).strip(" -").replace("Tỷ", "Tỉ")).lower()
           not in CRIT_KEYS]
    if not (f or p_line or b_line or odd):
        return None, []
    bad = [f"dòng tiêu chí không đúng khuôn `{o}` — dùng `Tỉ lệ PASS tối thiểu R1: <số>%`" for o in odd]
    forb, p, b = parse_sev(f), parse_pct(p_line), parse_pct(b_line)
    if forb is None:
        bad.append(f"`Bug mở không được phép: {f}` — viết S1, S2 · S1–S3 · S2 trở lên · không")
    if p is None:
        bad.append(f"`Tỉ lệ PASS tối thiểu: {p_line}` — cần đúng một số có %, vd 95% (tiêu chí theo mức → dòng riêng `Tỉ lệ PASS tối thiểu R1: …%`)")
    if b is None:
        bad.append(f"`Tỉ lệ BLOCKED tối đa: {b_line}` — cần đúng một số có %")
    per = {}
    for lv in MUC:
        v = strip(field_any(block, f"Tỉ lệ PASS tối thiểu {lv}", f"Tỷ lệ PASS tối thiểu {lv}"))
        if v:
            x = parse_pct(v.replace(lv, ""))
            if x is None:
                bad.append(f"`Tỉ lệ PASS tối thiểu {lv}: {v}` — cần đúng một số có %")
            else:
                per[lv] = x
    if bad:
        return None, bad
    return {"forbidden": forb, "min_pass": p, "max_blocked": b, "per_level": per,
            "late": bool(re.search(r"\(\s*chốt sau khi chạy", text, re.I))}, []


def ai_n(text: str) -> tuple[dict[str, int] | int | None, str]:
    """N lần chạy mỗi ca AI: `12` hoặc `R1: 10, R2: 5, R3: 5`."""
    v = field_any(text, "Test AI — N mỗi ca", "Test AI - N mỗi ca", "Test AI — N mỗi ca (R1/R2/R3)")
    if not v:
        return None, ""
    lv = dict((k.upper(), int(n)) for k, n in re.findall(r"\b(R[1-3])\s*[:=]\s*(\d+)", v, re.I))
    base = re.findall(r"\d+", re.sub(r"\bR[1-3]\s*[:=]\s*\d+", "", v, flags=re.I))   # "3 lượt (R1: 5)" → 3 cho mức khác
    if lv:
        if len(base) == 1:
            lv["*"] = int(base[0])
        return lv, v
    return (int(base[0]) if len(base) == 1 else None), v


def ai_turns(d: Path) -> int:
    """Số lượt AI khác nhau có transcript: file `NN-luot-<k>.txt|md|json` (không phân biệt hoa thường, nhận `lượt`)."""
    ks = set()
    for f in d.rglob("*") if d.is_dir() else []:
        m = re.search(r"(?i)(?:luot|lượt)[-_ ]?(\d+)\.(txt|md|json)$", unicodedata.normalize("NFC", f.name))
        if f.is_file() and m:
            ks.add(int(m.group(1)))
    return len(ks)


# ---------------------------------------------------------------- kỹ thuật

def tc_level(tc: dict, levels: dict[str, str]) -> str:
    ls = sorted(levels[r] for r in tc.get("reqs", []) if r in levels)
    return ls[0] if ls else (tc.get("Mức", "").upper() if tc.get("Mức", "").upper() in MUC else "")


def norm_technique(name: str) -> str:
    n = no_paren(name).strip().lower()
    n = ALIASES.get(n, n)
    if n in TECHNIQUES:
        return n
    for k in sorted(list(TECHNIQUES) + list(ALIASES), key=len, reverse=True):   # "use case UC-DON 3a" → use case
        if n.startswith(k + " "):
            return ALIASES.get(k, k)
    return n


def techniques(tc: dict) -> set[str]:
    raw = re.sub(r"<[^>]*>", "", tc.get("Kỹ thuật", ""))
    return {norm_technique(t) for t in re.split(r"[,;·+/]", raw) if t.strip()}


# ---------------------------------------------------------------- lệnh: tc

def cmd_tc(args: list[str]) -> int:
    strict = "--strict" in args
    focus = [a for a in args if a != "--strict"]
    tcs, errors = load_tcs()
    warns: list[str] = []
    tg = set(target_types())
    levels = scope_levels()
    reqs_all = scope_reqs() or analysis_reqs()
    focus_reqs = [r for a in focus for r in req_ids(a)]
    focus_feat = [a for a in focus if not req_ids(a)]
    if focus:
        sel = {t for t, v in tcs.items() if set(v["reqs"]) & set(focus_reqs) or v["feature"] in focus_feat}
        feats = {v["feature"] for v in tcs.values()}
        for f_ in focus_feat:
            if f_ not in feats:
                errors.append(f"phạm vi `{f_}` không phải REQ-… hay tính năng nào trong qa/testcases/ (có: {', '.join(sorted(feats)) or '—'})")
        reqs = focus_reqs + [r for t in sel for r in tcs[t]["reqs"] if r not in focus_reqs]
        view = {t: tcs[t] for t in sel}
    else:
        reqs, view = reqs_all, tcs
    for t in view.values():
        miss = [k for k in REQUIRED if not t[k] and not (k == "Bước" and t["steps"]) and not (k == "Kỳ vọng" and t["expects"])]
        if miss:
            errors.append(f"{t['id']} ({t['file']}): thiếu {', '.join(miss)}")
        if t["REQ"] and not t["reqs"]:
            errors.append(f"{t['id']}: trường REQ `{t['REQ']}` không đọc được mã REQ-…")
        if t["Kiểu"] and t["Kiểu"].lower() not in KIEU:
            errors.append(f"{t['id']}: `Kiểu: {t['Kiểu']}` — phải là normal hoặc abnormal")
        if t["Mức"] and t["Mức"].upper() not in MUC:
            errors.append(f"{t['id']}: `Mức: {t['Mức']}` — phải là R1/R2/R3 (mức người dùng chốt ở SCOPE §2)")
        for r in t["reqs"]:
            if r in levels and t["Mức"].upper() in MUC and t["Mức"].upper() != levels[r]:
                (errors if strict else warns).append(f"{t['id']}: `Mức: {t['Mức']}` khác mức {levels[r]} người dùng đã chốt cho {r} — kết luận theo mức SCOPE")
        hole = lambda v: PLACEHOLDER_RE.search(re.sub(r"`[^`]*`", "", re.sub(r"<run(?:-id)?>", "RUN", v or "")))
        for k in ("REQ", "Target", "Tiền điều kiện", "Dữ liệu", "Nguồn", "Bằng chứng cần"):
            if hole(t[k]):
                errors.append(f"{t['id']}: `{k}` còn chỗ trống `{hole(t[k]).group()}` — điền theo sản phẩm hoặc hỏi")
        for s in t["steps"] + t["expects"]:
            m = hole(s)
            if m:
                errors.append(f"{t['id']}: Bước/Kỳ vọng còn chỗ trống `{m.group()}` — điền theo sản phẩm hoặc hỏi")
                break
        if t["Loại"] and t["Loại"].lower() not in LOAI:
            warns.append(f"{t['id']}: loại `{t['Loại']}` ngoài danh mục qa-targets §2")
        for k in techniques(t) - set(TECHNIQUES):
            warns.append(f"{t['id']}: kỹ thuật `{k}` không có trong danh mục qa-testcase-design §1 — dùng tên chuẩn (mã quy tắc/luồng ghi ở Nguồn)")
        if tg and t["Target"] and t["Target"] not in tg:
            warns.append(f"{t['id']}: target `{t['Target']}` không có trong QA.md §Target")
        if waiting(t["body"]):
            warns.append(f"{t['id']}: còn `(chờ trả lời #n)` — hỏi người dùng; TC này không được đưa vào run")
        for e in t["expects"]:
            for v in VAGUE:
                if v in e.lower():
                    concrete = re.search(r"\d|\"[^\"]+\"|“[^”]+”|'[^']+'", e)
                    msg = f"{t['id']}: kỳ vọng có từ mơ hồ `{v}` (\"{e[:60]}\") — viết điều quan sát được, có nguồn"
                    (warns if concrete else errors).append(msg)
                    break
            if re.search(r"\b\d{3}\s*(hoặc|/|or)\s*\d{3}\b", e):
                warns.append(f"{t['id']}: kỳ vọng có hai đáp án (\"{e[:50]}\") — lấy đúng một theo tài liệu, không có thì hỏi")
    by_req: dict[str, set] = {}
    for t in tcs.values():
        for r in t["reqs"]:
            by_req.setdefault(r, set()).add(t["Kiểu"].lower())
    for r in reqs:
        k = by_req.get(r, set())
        hard = strict or r in focus_reqs
        if not k:
            (errors if hard else warns).append(f"{r}: chưa có TC nào")
        else:
            for need in ("normal", "abnormal"):
                if need not in k:
                    errors.append(f"{r}: thiếu TC `Kiểu: {need}`")
    if scope_reqs():
        for r in reqs:
            if r not in levels:
                warns.append(f"{r}: chưa có mức R người dùng xác nhận (SCOPE §2) — hỏi, không tự gán")
            elif levels[r] == "R1":
                fams = {TECHNIQUES[x] for t in tcs.values() if r in t["reqs"] for x in techniques(t) if x in TECHNIQUES}
                if len(fams) < 2:
                    warns.append(f"{r}: mức R1 nhưng TC mới thuộc {len(fams)} họ kỹ thuật ({', '.join(sorted(fams)) or 'chưa ghi `Kỹ thuật:`'})"
                                 " — R1 cần ≥ 2 họ")
    if reqs_all and not focus:
        for r in sorted(set(by_req) - set(reqs_all)):
            if not all(t["Regression"].lower().startswith("có") for t in tcs.values() if r in t["reqs"]):
                warns.append(f"{r}: TC trỏ tới REQ không có trong {'SCOPE §2' if scope_reqs() else 'ANALYSIS §3'}")

    print(f"TC: {len(view)}{' (phạm vi: ' + ' '.join(focus) + ')' if focus else ''} · REQ đang xét: {len(reqs)} "
          f"({'SCOPE' if scope_reqs() else 'ANALYSIS'}){' · --strict' if strict else ''}")
    for e in errors:
        print(f"  ✗ {e}")
    for w in warns:
        print(f"  ⚠ {w}")
    if not errors:
        print("  ✓ bộ TC sạch")
    return 1 if errors else 0


# ---------------------------------------------------------------- lệnh: select

def select(args: list[str]) -> tuple[list[str], str, list[str]]:
    """→ (TC-ID, mô tả, lỗi)."""
    tcs, _ = load_tcs()
    if not args:
        return [], "thiếu phạm vi", ["thiếu phạm vi"]
    mode = args[0].lower()
    if mode == "all":
        reqs = set(scope_reqs())
        ids = [t for t, v in tcs.items() if not reqs or set(v["reqs"]) & reqs]
        return ids, "mọi TC của REQ trong SCOPE" if reqs else "mọi TC (SCOPE chưa có REQ)", []
    if mode == "smoke":
        ids = [t for t, v in tcs.items() if "smoke" in v["Tag"].lower()]
        if ids:
            return ids, "TC có Tag: smoke", []
        return ([t for t, v in tcs.items() if v["Mức"].upper() == "R1" and v["Kiểu"].lower() == "normal"],
                "chưa TC nào gắn smoke → đề xuất TC R1 normal (người dùng xác nhận)", [])
    if mode in ("regression", "reg"):
        ids = [t for t, v in tcs.items() if v["Regression"].lower().startswith("có")]
        extra = [a for a in args[1:] if a in tcs and a not in ids]
        bad = [f"{a} không có trong qa/testcases/" for a in args[1:] if a not in tcs]
        return ids + extra, "mọi TC Regression: có" + (f" + {len(extra)} TC truyền thêm" if extra else ""), bad
    if mode == "retest":
        bugs = load_bugs()
        ids, bad = [], []
        for b in args[1:]:
            bug = bugs.get(b.upper())
            if not bug:
                bad.append(f"{b} không có trong BUGS.md")
            elif not bug["tc"]:
                bad.append(f"{b} chưa có TC tái hiện — viết TC (Nguồn: {b}), người dùng duyệt, rồi mới retest")
            ids += bug["tc"] if bug else []
        return sorted(set(ids)), f"TC của {' '.join(args[1:])}", bad
    if all(re.match(r"TC-", a, re.I) for a in args):
        up = [a.upper() if a.upper() in tcs else a for a in args]
        return [a for a in up if a in tcs], "TC chỉ định", [f"{a} không có trong qa/testcases/" for a in up if a not in tcs]
    feats = sorted({v["feature"] for v in tcs.values()})
    ids = [t for t, v in tcs.items() if v["feature"] == args[0]]
    return ids, f"TC của tính năng `{args[0]}`", ([] if ids else [f"không có file qa/testcases/{args[0]}.md — có: {', '.join(feats) or '(trống)'}"])


def drop_waiting(ids: list[str]) -> tuple[list[str], list[str]]:
    """Bỏ TC còn nhãn chờ, hoặc trỏ tới REQ còn chờ xác nhận — chưa được đưa vào run."""
    tcs, _ = load_tcs()
    wreq = waiting_reqs()
    w = [i for i in ids if waiting(tcs.get(i, {}).get("body", "")) or set(tcs.get(i, {}).get("reqs", [])) & wreq]
    return [i for i in ids if i not in w], w


def cmd_select(args: list[str]) -> int:
    ids, how, bad = select(args)
    ids, w = drop_waiting(ids)
    if w:
        print(f"# bỏ {len(w)} TC còn (chờ trả lời): {', '.join(w)}", file=sys.stderr)
    print(f"# {how}: {len(ids)} TC")
    for i in ids:
        print(i)
    for b in bad:
        print(f"  ✗ {b}", file=sys.stderr)
    return 1 if bad or not ids else 0


# ---------------------------------------------------------------- lệnh: new-run

def cmd_new_run(args: list[str]) -> int:
    if not args:
        print("cách gọi: new-run <loại> [phạm vi…]  (loại: full, smoke, reg, retest, explore, …)", file=sys.stderr)
        return 2
    kind = re.sub(r"[^a-z0-9-]", "-", args[0].lower())
    rest = args[1:]
    if kind == "explore":
        ids, how = [], "test khám phá — mỗi phiên một dòng EXPLORE-<n> (khuôn _EXPLORE-TEMPLATE.md)"
    else:
        if kind in ("retest", "reg", "regression"):
            sel = [kind, *rest]
        elif rest:
            sel = rest
        else:
            sel = ["smoke"] if kind == "smoke" else ["all"]
        ids, how, bad = select(sel)
        ids, w = drop_waiting(ids)
        if w:
            print(f"⚠ bỏ {len(w)} TC còn (chờ trả lời): {', '.join(w)} — hỏi người dùng rồi thêm vào run", file=sys.stderr)
        for b in bad:
            print(f"✗ {b}", file=sys.stderr)
        if bad or not ids:
            if not ids:
                print(f"✗ phạm vi `{' '.join(sel)}` không chọn được TC nào — kiểm lại (qa_check.py select …)", file=sys.stderr)
            return 1
    scope_text = read(scope_file())
    crit, bad_crit = parse_criteria(scope_text)
    st = scope_status() or "(chưa có)"
    if crit:
        per = "".join(f"  - Tỉ lệ PASS tối thiểu {lv}: {v:g}%\n" for lv, v in crit["per_level"].items())
        crit_lines = (f"  - Bug mở không được phép: {', '.join(sorted(crit['forbidden'])) or 'không'}\n"
                      f"  - Tỉ lệ PASS tối thiểu: {crit['min_pass']:g}%\n{per}"
                      f"  - Tỉ lệ BLOCKED tối đa: {crit['max_blocked']:g}%\n")
        src = "SCOPE §6" + ("" if st.upper().startswith("CHỐT") else " — SCOPE chưa CHỐT, người dùng xác nhận trước khi chạy")
    else:
        crit_lines = "  - Bug mở không được phép: \n  - Tỉ lệ PASS tối thiểu: \n  - Tỉ lệ BLOCKED tối đa: \n"
        src = "CHƯA CHỐT — hỏi người dùng; chốt trước khi chạy, hoặc (người dùng đã bảo chạy luôn) điền sau theo skill qa §2"
        for b in bad_crit:
            print(f"⚠ tiêu chí không đọc được: {b}", file=sys.stderr)
        print("⚠ SCOPE §6 chưa có tiêu chí đạt đọc được — hỏi người dùng; run không kết luận được khi chưa có", file=sys.stderr)
    n_ai = field_any(scope_text, "Test AI — N mỗi ca", "Test AI — N mỗi ca (R1/R2/R3)")
    thr_ai = field(scope_text, "Test AI — ngưỡng đạt mỗi ca")
    ai_lines = (f"  - Test AI — N mỗi ca: {n_ai}\n  - Test AI — ngưỡng đạt mỗi ca: {thr_ai}\n") if (n_ai or thr_ai) else ""
    day = dt.date.today().isoformat()
    run_id, n = f"{day}-{kind}", 2
    while (QA / "runs" / run_id).exists():
        run_id, n = f"{day}-{kind}-{n}", n + 1
    d = QA / "runs" / run_id
    d.mkdir(parents=True)
    rows = "\n".join(f"| {i} | CHƯA CHẠY | | | |" for i in ids)
    (d / "RUNLOG.md").write_text(
        f"# RUNLOG — {run_id}\n\n"
        "> Kết quả: `PASS` · `FAIL` (cột cuối ghi BUG-…) · `BLOCKED` (cột cuối ghi lý do / `chờ trả lời #n`) · "
        "`SKIP` (cột cuối trỏ dòng DECISIONS người dùng quyết, vd `DECISIONS #3`) · `CHƯA CHẠY`.\n"
        f"> Bằng chứng: `qa/evidence/{run_id}/<TC-ID>/` — phải tồn tại và không rỗng với PASS/FAIL.\n"
        "> Không xoá/thêm dòng TC: danh sách dưới được đối chiếu khi soát run.\n\n"
        "- Bản đang kiểm: \n- Môi trường: \n"
        f"- Bắt đầu: {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"- Phạm vi: {how}\n"
        f"- Danh sách TC lúc tạo run: {', '.join(ids) or '(khám phá)'}\n"
        f"- Scope lúc tạo run: {st}\n"
        f"- Tiêu chí ({src}; không sửa sau khi đã chạy):\n{crit_lines}{ai_lines}\n"
        "| TC | Kết quả | Ngày | Bằng chứng | Bug / Lý do |\n|---|---|---|---|---|\n"
        f"{rows}\n\n## Nhật ký\n", encoding="utf-8")
    (QA / "evidence" / run_id).mkdir(parents=True, exist_ok=True)
    print(f"run-id: {run_id}")
    print(f"RUNLOG: {d.relative_to(ROOT)}/RUNLOG.md · {len(ids)} TC ({how})")
    return 0


# ---------------------------------------------------------------- lệnh: run

def evidence_paths(cell: str) -> list[str]:
    links = [l.strip().strip("<>") for l in re.findall(r"\]\(([^)]+)\)", cell)]
    rest = re.sub(r"\[[^\]]*\]\([^)]+\)", " ", cell)
    ticks = re.findall(r"`([^`]+)`", rest)                      # `…/a b.png` — giữ nguyên dấu cách
    rest = re.sub(r"`[^`]+`", " ", rest)
    rest = re.sub(r"\([^()]*\)", " ", rest)
    whole = rest.strip()
    if whole and " " in whole and (ROOT / whole).exists():     # cả ô là một đường dẫn có dấu cách
        return links + ticks + [whole]
    toks = [p for p in re.split(r"[,;\s·]+", rest) if p]
    return links + ticks + [t for t in toks if "/" in t or re.search(r"\.\w{2,5}$", t)]


def evidence_ok(cell: str, run_id: str, tid: str, log_dir: Path) -> tuple[bool, str]:
    paths = evidence_paths(cell)
    if not paths:
        return False, "thiếu đường dẫn bằng chứng"
    own = (QA / "evidence" / run_id / tid).resolve()
    for raw in paths:
        cands = [Path(raw).expanduser()] if Path(raw).expanduser().is_absolute() else [ROOT / raw, log_dir / raw]
        found = [c.resolve() for c in cands if c.resolve() == own or own in c.resolve().parents]
        if not found:
            return False, f"`{raw}` không nằm trong qa/evidence/{run_id}/{tid}/ của chính TC này"
        if not any(c.exists() for c in found):
            return False, f"`{raw}` không tồn tại"
    files = [f for f in own.rglob("*") if f.is_file()] if own.is_dir() else []
    if not files:
        return False, f"qa/evidence/{run_id}/{tid}/ rỗng"
    if all(f.stat().st_size == 0 for f in files):
        return False, f"qa/evidence/{run_id}/{tid}/ chỉ có file 0 byte"
    return True, ""


def run_dirs() -> list[Path]:
    """Các run theo thứ tự tạo: dòng `Bắt đầu:` trong RUNLOG, rồi tên (so số tự nhiên)."""
    ds = [p for p in (QA / "runs").glob("*") if p.is_dir()]
    def key(p: Path):
        started = field(read(p / "RUNLOG.md"), "Bắt đầu")
        return (started or "0000", natural(p.name))
    return sorted(ds, key=key)


def result_of(res: str) -> tuple[str, str]:
    """(kết quả chuẩn, phần chú thích). INCONCLUSIVE (từ qa-security) = BLOCKED."""
    u = plain(res).upper()
    if u.startswith("INCONCLUSIVE"):
        return "BLOCKED", "inconclusive " + plain(res)[len("INCONCLUSIVE"):]
    for k in RESULTS:
        if u.startswith(k):
            return k, plain(res)[len(k):].strip(" ()-—:")
    return res, ""


def row_id(cell: str) -> tuple[str, bool]:
    """(ID chuẩn hoá, ô có trông như ID TC/EXPLORE không). Bỏ **, `, link markdown; nhận chữ thường."""
    c = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", cell)
    c = plain(c)
    m = re.match(r"(?i)(tc-\w+(?:-\w+)*-\d{3}|explore-\d+)$", c)
    if m:
        v = m.group(1)
        return (v[:3].upper() + v[3:] if v.lower().startswith("tc-") else "EXPLORE-" + v.split("-", 1)[1]), True
    return c, bool(re.search(r"(?i)\b(tc|explore)-", c))


def parse_day(s: str) -> bool:
    s = plain(s)
    return bool(re.match(r"\d{4}-\d{2}-\d{2}", s) or re.match(r"\d{1,2}/\d{1,2}/\d{4}", s))


def cmd_run(args: list[str], quiet: bool = False) -> tuple[int, dict]:
    if not args:
        runs = run_dirs()
        if not runs:
            print("chưa có run nào", file=sys.stderr)
            return 2, {}
        args = [runs[-1].name]
    run_id = args[0]
    log = QA / "runs" / run_id / "RUNLOG.md"
    text = read(log)
    if not text:
        if not quiet:
            print(f"không thấy {log.relative_to(ROOT)}", file=sys.stderr)
        return 2, {}
    tcs, _ = load_tcs()
    tc_case = {t.lower(): t for t in tcs}
    levels = scope_levels()
    bugs = load_bugs()
    ttype = target_types()
    errors: list[str] = []
    warns: list[str] = []
    counts = {k: 0 for k in RESULTS}
    per_level: dict[str, list[int]] = {}
    explore = 0
    run_tcs: list[str] = []
    noted_bugs: set[str] = set()
    for r in table_rows(text):
        r = r + [""] * (5 - len(r))
        tid, looks = row_id(r[0])
        tid = tc_case.get(tid.lower(), tid)
        _, res, day, ev, note = r[:5]
        if not re.match(r"(TC-|EXPLORE-)", tid):
            if looks:
                errors.append(f"dòng `{r[0]}`: ID không đúng khuôn TC-<TÍNH-NĂNG>-<3 chữ số> / EXPLORE-<n> — dòng không được đếm")
            continue
        res_u, extra = result_of(res)
        note = (note + " " + extra).strip()
        if res_u not in RESULTS:
            errors.append(f"{tid}: kết quả `{res}` không hợp lệ (PASS/FAIL/BLOCKED/SKIP/CHƯA CHẠY)")
            continue
        if tid in run_tcs:
            errors.append(f"{tid}: có hơn một dòng — mỗi TC một dòng; chạy lại thì sửa dòng đó hoặc tạo run mới")
            continue
        run_tcs.append(tid)
        noted_bugs |= set(re.findall(r"BUG-\d+", note))
        if tid.startswith("EXPLORE-"):
            explore += 1          # phát hiện khám phá: kiểm bằng chứng nhưng không tính vào tỉ lệ
        else:
            counts[res_u] += 1
            if tid not in tcs:
                errors.append(f"{tid}: không có trong qa/testcases/")
            else:
                lv = tc_level(tcs[tid], levels)
                if lv and tcs[tid]["Mức"].upper() in MUC and tcs[tid]["Mức"].upper() != lv:
                    warns.append(f"{tid}: `Mức: {tcs[tid]['Mức']}` khác mức {lv} đã chốt ở SCOPE — tính theo {lv}")
                if lv in MUC and res_u != "SKIP":
                    per_level.setdefault(lv, [0, 0])
                    per_level[lv][1] += 1
                    per_level[lv][0] += res_u == "PASS"
        if res_u in ("PASS", "FAIL"):
            if not parse_day(day):
                errors.append(f"{tid}: thiếu ngày chạy (YYYY-MM-DD hoặc DD/MM/YYYY)")
            ok, why = evidence_ok(ev, run_id, tid, log.parent)
            if not ok:
                errors.append(f"{tid}: {res_u} nhưng {why}")
            if tid in tcs and re.match(r"ai\b", ttype.get(tcs[tid]["Target"], "")):
                n_ai, _raw = ai_n(text)
                lv = tc_level(tcs[tid], levels)
                need = (n_ai.get(lv) or n_ai.get("*")) if isinstance(n_ai, dict) else n_ai
                got = ai_turns(QA / "evidence" / run_id / tid)
                if not need:
                    errors.append(f"{tid}: TC AI (mức {lv or '?'}) nhưng RUNLOG chưa có `Test AI — N mỗi ca` người dùng chốt cho mức này")
                elif got < need:
                    errors.append(f"{tid}: TC AI cần {need} lượt, bằng chứng mới có {got} transcript `NN-luot-<k>.txt`")
        if res_u == "FAIL":
            ids = re.findall(r"BUG-\d+", note)
            if not ids:
                errors.append(f"{tid}: FAIL không ghi BUG-…")
            for b in ids:
                if b not in bugs:
                    errors.append(f"{tid}: {b} không có trong BUGS.md")
                elif not bugs[b]["sev"]:
                    errors.append(f"{b}: thiếu Severity S1–S4")
        if res_u == "BLOCKED" and not note:
            errors.append(f"{tid}: BLOCKED không ghi lý do")
        if res_u == "SKIP" and not re.search(r"DECISIONS|#\d+", note):
            errors.append(f"{tid}: SKIP phải trỏ dòng DECISIONS người dùng quyết (vd `DECISIONS #3`)")
    listed_raw = field(text, "Danh sách TC lúc tạo run")
    listed = re.findall(TC_ID, listed_raw)
    if listed:
        for t in listed:
            if t not in run_tcs:
                errors.append(f"{t}: có trong danh sách lúc tạo run nhưng không còn dòng trong RUNLOG")
        for t in run_tcs:
            if t.startswith("TC-") and t not in listed:
                warns.append(f"{t}: không có trong danh sách lúc tạo run — thêm TC giữa chừng phải được người dùng đồng ý")
    elif "(khám phá)" not in listed_raw:
        warns.append("RUNLOG không có dòng `Danh sách TC lúc tạo run` — không đối chiếu được dòng bị xoá; nên tạo run bằng new-run")
    for b in bugs.values():
        if not b["known"]:
            errors.append(f"{b['id']}: trạng thái `{b['status'] or '(trống)'}` lạ — dùng mở/đã sửa/đóng/không sửa/hoãn/trùng (đang coi là còn mở)")

    crit, bad = parse_criteria(text)
    crit_note = ""
    if crit is None and not bad and "Tiêu chí (" not in text:
        crit, bad = parse_criteria(read(scope_file()))
        crit_note = " (RUNLOG không có khối tiêu chí — đang dùng SCOPE hiện tại; nên tạo run bằng new-run)"
    if crit and crit["late"]:
        warns.append("tiêu chí được chốt SAU khi đã chạy (DECISIONS) — báo cáo phải nêu rõ")
    scope_at = plain(field(text, "Scope lúc tạo run"))
    draft = scope_at and not scope_at.upper().startswith("CHỐT") and not (crit and crit["late"])
    total = sum(counts.values())
    base = total - counts["SKIP"]
    pass_rate = 100.0 * counts["PASS"] / base if base else 0.0
    blocked_rate = 100.0 * counts["BLOCKED"] / base if base else 0.0
    related = [b for b in bugs.values() if b["open"] and (b["run"] == run_id or set(b["tc"]) & set(run_tcs) or b["id"] in noted_bugs)]
    forbidden = [b for b in related if crit and b["sev"] in crit["forbidden"]]
    outside = [b for b in bugs.values() if b["open"] and crit and b["sev"] in crit["forbidden"] and b not in related]
    kind = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", run_id)

    reasons = []
    if counts["CHƯA CHẠY"] or errors or not (total or explore) or crit is None or draft:
        verdict = "CHƯA KẾT LUẬN"
        if draft and crit is not None:
            reasons.append(f"SCOPE lúc tạo run là `{scope_at}` — tiêu chí chưa được người dùng chốt (chốt rồi tạo run mới, hoặc ghi theo skill qa §2)")
        if crit is None:
            reasons.append("chưa có tiêu chí đạt được người dùng chốt" + (f" ({'; '.join(bad)})" if bad else ""))
        if counts["CHƯA CHẠY"]:
            reasons.append(f"{counts['CHƯA CHẠY']} TC chưa chạy")
        if errors:
            reasons.append(f"{len(errors)} lỗi hình thức")
        if not (total or explore):
            reasons.append("RUNLOG không có dòng TC nào")
    else:
        if forbidden:
            reasons.append("còn bug mở mức cấm: " + ", ".join(f"{b['id']} ({b['sev']})" for b in forbidden))
        if total:
            if pass_rate < crit["min_pass"]:
                reasons.append(f"tỉ lệ PASS {pass_rate:.1f}% < {crit['min_pass']:g}%")
            if blocked_rate > crit["max_blocked"]:
                reasons.append(f"tỉ lệ BLOCKED {blocked_rate:.1f}% > {crit['max_blocked']:g}%")
            for lv, need in crit["per_level"].items():
                ok_n, all_n = per_level.get(lv, [0, 0])
                if all_n and 100.0 * ok_n / all_n < need:
                    reasons.append(f"tỉ lệ PASS {lv} {100.0 * ok_n / all_n:.1f}% < {need:g}%")
        verdict = "KHÔNG ĐẠT" if reasons else "ĐẠT"
        if not total and explore and not forbidden:
            verdict = "KHÔNG ÁP DỤNG (chỉ khám phá)"
        scope_all, _h, _b = select(["all"]) if scope_reqs() else ([], "", [])
        partial = kind.startswith(("retest", "reg")) or bool(set(drop_waiting(scope_all)[0]) - set(run_tcs))
        if verdict == "ĐẠT" and partial:
            verdict = "ĐẠT (chỉ trong phạm vi run này — hỏi 'phát hành được chưa' thì dùng `release`)"
    if outside:
        warns.append("còn bug mở mức cấm NGOÀI phạm vi run này: " + ", ".join(f"{b['id']} ({b['sev']})" for b in outside))

    info = {"run": run_id, "verdict": verdict, "counts": counts, "pass_rate": pass_rate, "errors": len(errors)}
    if not quiet:
        print(f"Run {run_id}: {total} dòng · PASS {counts['PASS']} · FAIL {counts['FAIL']} · BLOCKED {counts['BLOCKED']}"
              f" · SKIP {counts['SKIP']} · CHƯA CHẠY {counts['CHƯA CHẠY']} · tỉ lệ PASS {pass_rate:.1f}%"
              + (f" · khám phá {explore}" if explore else ""))
        if crit:
            per = "".join(f" · PASS {lv} ≥ {v:g}%" for lv, v in crit["per_level"].items())
            print(f"Tiêu chí: bug mở cấm {'/'.join(sorted(crit['forbidden'])) or '—'} · PASS ≥ {crit['min_pass']:g}%{per}"
                  f" · BLOCKED ≤ {crit['max_blocked']:g}%{crit_note}")
        else:
            print("Tiêu chí: CHƯA CHỐT — hỏi người dùng")
        for e in errors:
            print(f"  ✗ {e}")
        for w in warns:
            print(f"  ⚠ {w}")
        print(f"KẾT LUẬN: {verdict}" + (f" — {'; '.join(reasons)}" if reasons else ""))
    return (0 if verdict.startswith(("ĐẠT", "KHÔNG ÁP DỤNG")) and not errors else 1), info


# ---------------------------------------------------------------- lệnh: release

def cmd_release(args: list[str]) -> int:
    """Kết luận cấp phát hành: kết quả MỚI NHẤT của từng TC trong SCOPE qua các run được liệt kê (theo thứ tự tạo),
    tiêu chí của SCOPE hiện tại (phải CHỐT), bug mở mức cấm xét trên TOÀN BỘ BUGS.md."""
    if not args:
        print("cách gọi: release <run-id> [<run-id>…]  (run gốc + retest + regression)", file=sys.stderr)
        return 2
    order = {d.name: i for i, d in enumerate(run_dirs())}
    missing = [a for a in args if a not in order]
    if missing:
        print(f"✗ không thấy run: {', '.join(missing)}", file=sys.stderr)
        return 2
    errs = [a for a in args if cmd_run([a], quiet=True)[1].get("errors")]   # lỗi hình thức, không phải KHÔNG ĐẠT
    tcs, _ = load_tcs()
    scope_tc, _how, _b = select(["all"])
    scope_tc, wait = drop_waiting(scope_tc)
    levels = scope_levels()
    latest: dict[str, tuple[str, str]] = {}
    tc_case = {t.lower(): t for t in tcs}
    for rid in sorted(args, key=lambda a: order[a]):
        for r in table_rows(read(QA / "runs" / rid / "RUNLOG.md")):
            tid, _ = row_id(r[0]) if r else ("", False)
            tid = tc_case.get(tid.lower(), tid)
            if tid.startswith("TC-") and len(r) >= 2:
                latest[tid] = (result_of(r[1])[0], rid)
    crit, bad = parse_criteria(read(scope_file()))
    in_runs = [t for t in latest if t not in scope_tc]          # TC regression của REQ cũ, TC truyền thêm…
    scope_tc = scope_tc + in_runs
    diff_crit = []
    for rid in args:
        rc, _ = parse_criteria(read(QA / "runs" / rid / "RUNLOG.md"))
        if rc and crit and (rc["forbidden"], rc["min_pass"], rc["max_blocked"], rc["per_level"]) != \
                (crit["forbidden"], crit["min_pass"], crit["max_blocked"], crit["per_level"]):
            diff_crit.append(rid)
    counts = {k: 0 for k in RESULTS}
    not_run = []
    for t in scope_tc:
        res = latest.get(t, ("CHƯA CHẠY", ""))[0]
        counts[res if res in counts else "CHƯA CHẠY"] += 1
        if res == "CHƯA CHẠY":
            not_run.append(t)
    bugs = load_bugs()
    forb = [b for b in bugs.values() if b["open"] and crit and b["sev"] in crit["forbidden"]]
    base = len(scope_tc) - counts["SKIP"]
    pr = 100.0 * counts["PASS"] / base if base else 0.0
    br = 100.0 * counts["BLOCKED"] / base if base else 0.0
    reasons = []
    if crit is None or not scope_status().upper().startswith("CHỐT"):
        verdict = "CHƯA KẾT LUẬN"
        reasons.append("SCOPE chưa CHỐT hoặc chưa có tiêu chí đạt đọc được" + (f" ({'; '.join(bad)})" if bad else ""))
    elif errs or not_run or diff_crit:
        verdict = "CHƯA KẾT LUẬN"
        if diff_crit:
            reasons.append(f"tiêu chí đóng băng trong RUNLOG {', '.join(diff_crit)} khác SCOPE hiện tại — người dùng xác nhận (DECISIONS) tiêu chí nào áp dụng")
        if errs:
            reasons.append(f"run còn lỗi hình thức: {', '.join(errs)}")
        if not_run:
            reasons.append(f"{len(not_run)} TC trong SCOPE chưa có kết quả ở các run đã liệt kê: {', '.join(not_run[:10])}")
    else:
        if forb:
            reasons.append("còn bug mở mức cấm: " + ", ".join(f"{b['id']} ({b['sev']})" for b in forb))
        if pr < crit["min_pass"]:
            reasons.append(f"tỉ lệ PASS {pr:.1f}% < {crit['min_pass']:g}%")
        if br > crit["max_blocked"]:
            reasons.append(f"tỉ lệ BLOCKED {br:.1f}% > {crit['max_blocked']:g}%")
        for lv, need in crit["per_level"].items():
            ids = [t for t in scope_tc if t in tcs and tc_level(tcs[t], levels) == lv and latest.get(t, ("",))[0] != "SKIP"]
            ok = [t for t in ids if latest.get(t, ("",))[0] == "PASS"]
            if ids and 100.0 * len(ok) / len(ids) < need:
                reasons.append(f"tỉ lệ PASS {lv} {100.0 * len(ok) / len(ids):.1f}% < {need:g}%")
        verdict = "KHÔNG ĐẠT" if reasons else "ĐẠT"
    print(f"Phát hành — gộp {len(args)} run ({', '.join(args)}) · {len(scope_tc)} TC trong SCOPE"
          + (f" · bỏ {len(wait)} TC còn chờ trả lời" if wait else ""))
    print(f"PASS {counts['PASS']} · FAIL {counts['FAIL']} · BLOCKED {counts['BLOCKED']} · SKIP {counts['SKIP']} · "
          f"chưa có kết quả {len(not_run)} · tỉ lệ PASS {pr:.1f}%")
    print(f"KẾT LUẬN PHÁT HÀNH: {verdict}" + (f" — {'; '.join(reasons)}" if reasons else ""))
    return 0 if verdict == "ĐẠT" else 1


# ---------------------------------------------------------------- lệnh: trace

def latest_results() -> dict[str, tuple[str, str]]:
    """TC → (kết quả, run-id) ở run gần nhất có TC đó."""
    out: dict[str, tuple[str, str]] = {}
    tc_case = {t.lower(): t for t in load_tcs()[0]}
    for d in run_dirs():
        for r in table_rows(read(d / "RUNLOG.md")):
            tid, _ = row_id(r[0]) if r else ("", False)
            tid = tc_case.get(tid.lower(), tid)
            if tid.startswith("TC-") and len(r) >= 2:
                out[tid] = (result_of(r[1])[0], d.name)
    return out


def cmd_trace(args: list[str]) -> int:
    tcs, _ = load_tcs()
    bugs = load_bugs()
    res = latest_results()
    levels = scope_levels()
    reqs = scope_reqs() or analysis_reqs()
    extra = sorted({r for t in tcs.values() for r in t["reqs"]} - set(reqs))
    lines = ["| REQ | Mức (SCOPE) | TC normal | TC abnormal | Kỹ thuật | Kết quả gần nhất | Bug mở |",
             "|---|---|---|---|---|---|---|"]
    gaps = 0
    for r in reqs + extra:
        mine = [t for t in tcs.values() if r in t["reqs"]]
        nor = [t["id"] for t in mine if t["Kiểu"].lower() == "normal"]
        abn = [t["id"] for t in mine if t["Kiểu"].lower() == "abnormal"]
        tech = sorted(set().union(*[techniques(t) for t in mine] or [set()]))
        cnt: dict[str, int] = {}
        for t in mine:
            k = res.get(t["id"], ("chưa chạy", ""))[0]
            cnt[k] = cnt.get(k, 0) + 1
        ob = sorted({b["id"] + f" ({b['sev']})" for b in bugs.values() if b["open"] and set(b["tc"]) & {t["id"] for t in mine}})
        if not nor or not abn:
            gaps += 1
        mark = "" if r in reqs else (" (regression)" if mine and all(t["Regression"].lower().startswith("có") for t in mine) else " ⚠ ngoài phạm vi")
        lines.append(f"| {r}{mark} | {levels.get(r, '— chưa chốt')} | {', '.join(nor) or '**—**'} | {', '.join(abn) or '**—**'} | "
                     f"{', '.join(tech) or '—'} | {' · '.join(f'{k} {v}' for k, v in sorted(cnt.items())) or '—'} | "
                     f"{', '.join(ob) or '—'} |")
    no_req = sorted(t["id"] for t in tcs.values() if not t["reqs"])
    summary = (f"REQ: {len(reqs)} ({'SCOPE' if scope_reqs() else 'ANALYSIS'}) · TC: {len(tcs)} · "
               f"REQ thiếu normal hoặc abnormal: {gaps}" + (f" · TC không trỏ REQ: {', '.join(no_req)}" if no_req else ""))
    out = "\n".join(lines) + "\n\n" + summary + "\n"
    if "--write" in args:
        (QA / "TRACE.md").write_text(
            f"# TRACE — ma trận truy vết\n\n> Sinh bởi `qa_check.py trace --write` lúc {dt.datetime.now():%Y-%m-%d %H:%M}. "
            "Không sửa tay — chạy lại lệnh.\n\n" + out, encoding="utf-8")
        print(f"Đã ghi {(QA / 'TRACE.md').relative_to(ROOT)}")
    print(out)
    return 1 if gaps else 0


# ---------------------------------------------------------------- lệnh: status

def cmd_status() -> int:
    if not (QA / "QA.md").is_file():
        print(f"Chưa có workspace qa/ ở {ROOT} — cài bộ qa-agent (python3 <repo qa-agent>/install.py <dự án>).")
        return 1
    tcs, _ = load_tcs()
    bugs = load_bugs()
    lessons = [r for r in table_rows(read(QA / "LESSONS.md")) if len(r) >= 5 and plain(r[4]).lower() == "mới"]
    qa_md = read(QA / "QA.md")
    print(f"Workspace: {QA}")
    print(f"Quy trình: {field(qa_md, 'Quy trình') or '(chưa ghi)'} · Việc tiếp theo: {field(qa_md, 'Việc tiếp theo') or '(chưa ghi)'}")
    print(f"Target: {', '.join(target_types()) or '(chưa khai)'}")
    qs = open_questions()
    print(f"Phân tích: {len(analysis_reqs())} REQ · câu hỏi chờ trả lời: {len(qs)}")
    for q in qs[:10]:
        print(f"    ? {q}")
    crit, bad = parse_criteria(read(scope_file()))
    print(f"Scope: {scope_status() or '(chưa có)'} · {len(scope_reqs())} REQ trong phạm vi · "
          f"tiêu chí đạt: {'đã có' if crit else ('KHÔNG ĐỌC ĐƯỢC' if bad else 'CHƯA CHỐT')} · REQ chưa có mức: "
          f"{len([r for r in scope_reqs() if r not in scope_levels()])}")
    kinds: dict[str, int] = {}
    for t in tcs.values():
        kinds[t["Kiểu"].lower() or "?"] = kinds.get(t["Kiểu"].lower() or "?", 0) + 1
    wait_tc = [t for t in tcs.values() if waiting(t["body"])]
    print(f"Test case: {len(tcs)} ({', '.join(f'{k} {v}' for k, v in sorted(kinds.items())) or '—'})"
          + (f" · chờ trả lời: {len(wait_tc)}" if wait_tc else ""))
    runs = run_dirs()
    for d in runs[-5:]:
        _, info = cmd_run([d.name], quiet=True)
        if info:
            c = info["counts"]
            print(f"Run {d.name}: {info['verdict']} · PASS {c['PASS']} FAIL {c['FAIL']} BLOCKED {c['BLOCKED']} CHƯA CHẠY {c['CHƯA CHẠY']}")
    if not runs:
        print("Run: chưa có")
    ob = [b for b in bugs.values() if b["open"]]
    by: dict[str, int] = {}
    for b in ob:
        by[b["sev"] or "?"] = by.get(b["sev"] or "?", 0) + 1
    print(f"Bug mở: {len(ob)} ({', '.join(f'{k} {v}' for k, v in sorted(by.items())) or '—'}) · tổng {len(bugs)}")
    print(f"Bài học mới chưa áp: {len(lessons)}")
    return 0


# ---------------------------------------------------------------- main

def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv else 2
    cmd, args = argv[0], argv[1:]
    if cmd == "status":
        return cmd_status()
    if cmd == "tc":
        return cmd_tc(args)
    if cmd == "select":
        return cmd_select(args)
    if cmd == "new-run":
        return cmd_new_run(args)
    if cmd == "run":
        return cmd_run(args)[0]
    if cmd == "release":
        return cmd_release(args)
    if cmd == "trace":
        return cmd_trace(args)
    print(f"lệnh lạ `{cmd}`\n{__doc__}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
