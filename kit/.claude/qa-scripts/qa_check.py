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
    python3 .claude/qa-scripts/qa_check.py trace [--write]        ma trận truy vết REQ × VP × TC × kỹ thuật × kết quả × bug
    python3 .claude/qa-scripts/qa_check.py vp [REQ-…|<tính năng>] [--strict]
                                                                  soát quan điểm test (qa/viewpoints/): trường, trích dẫn, duyệt, phủ
    python3 .claude/qa-scripts/qa_check.py src [--strict] [--list]  soát nguồn: REQ/VP có nguồn + trích nguyên văn khớp tài liệu
    python3 .claude/qa-scripts/qa_check.py export <tc|vp> [--out <file.csv>] [--lang vi|en|ja]
                                                                  xuất CSV (UTF-8 BOM, mở bằng Excel); tiêu đề cột theo
                                                                  ngôn ngữ bàn giao (QA.md) — nội dung ô không tự dịch
    python3 .claude/qa-scripts/qa_check.py import <tc|vp> <file.csv> --feature <tính-năng>
                                                                  nhập CSV (Excel "Lưu thành CSV UTF-8") thành markdown để soát/review
    python3 .claude/qa-scripts/qa_check.py lessons [--brief] [--for <từ khoá>] [--archive]
                                                                  bài học: liệt kê · bản ngắn đầu phiên · lọc cho tester · cất dòng đã xong

Không phải cổng chặn — chỉ báo. Không tự đặt con số nào: tiêu chí đạt, mức rủi ro, N lần chạy AI lấy từ SCOPE do
người dùng chốt; thiếu hoặc không đọc được thì báo "chưa chốt", không dùng mặc định. Exit 0 sạch · 1 có lỗi · 2 sai cách gọi.
"""

from __future__ import annotations

import csv
import datetime as dt
import io
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
OPTIONAL = ["VP", "Regression", "Tag", "Ticket", "Kỹ thuật", "Tiền điều kiện", "Dữ liệu", "Ô ma trận", "Thực hiện"]
# `Thực hiện:` trống/agent = agent chạy · người = người chạy tay, agent ghi kết quả + bằng chứng họ gửi (skill qa §7)
BY_HUMAN = ("người", "thủ công", "manual", "human")
BY_AGENT = ("", "agent", "tự động", "auto")
HUMAN_NOTE = "nguoi-thuc-hien.md"     # trong thư mục bằng chứng của TC chạy tay: ai làm, lúc nào, bằng chứng nhận qua đâu
VAGUE = ["hoạt động đúng", "hiển thị đúng", "chạy đúng", "hoạt động bình thường", "hợp lý", "như mong đợi",
         "đúng nghiệp vụ", "đúng yêu cầu", "đúng thiết kế", "xử lý đúng", "tử tế", "thân thiện", "rõ ràng",
         "performance ok", "ổn định", "mượt"]
WAIT_RE = re.compile(r"\([^()]*chờ trả lời[^()]*\)", re.I)       # nhãn chờ duy nhất: (chờ trả lời #n)
PLACEHOLDER_RE = re.compile(r"<(?!\s)(?![A-Za-z][\w-]*\s+[\w:-]+\s*=)(?=[^<>\n]*(?:\s|[^\x00-\x7f]))[^<>\n]{1,80}(?<!\s)>")
# ↑ <điền gì đó>; không phải <b>, "< 100 và >", hay thẻ HTML có thuộc tính (<svg onload=…>, <img src=x onerror=…>) trong TC
TC_ID = r"TC-\w+(?:-\w+)*-\d{3}"
REQ_ID = r"REQ-[\w.-]*\w"
VP_ID = r"VP-\w+(?:-\w+)*-\d{3}"
BUG_CLOSED = ("đóng", "đã đóng", "closed", "không sửa", "wontfix", "hoãn", "deferred", "trùng", "duplicate")
BUG_OPEN = ("mở", "open", "đã sửa", "fixed", "mở lại", "reopened")

# danh mục kỹ thuật: tên chuẩn → họ. R1 cần ≥ 2 HỌ khác nhau (qa-testcase-design §1).
TECHNIQUES = {
    "phân vùng": "dữ liệu", "giá trị biên": "dữ liệu", "biên nhiều chiều": "dữ liệu", "syntax": "dữ liệu",
    "bảng quyết định": "logic", "phân quyền": "logic", "crud": "logic", "chuyển trạng thái": "logic",
    "use case": "logic", "pairwise": "logic", "classification tree": "logic", "hộp trắng": "logic",
    "metamorphic": "oracle", "property": "oracle", "fuzz": "oracle", "đồng thời": "oracle", "rubric": "oracle",
    "mốc hành vi": "oracle", "so sánh song song": "oracle", "đối soát dữ liệu": "oracle",
    "error guessing": "kinh nghiệm", "checklist": "kinh nghiệm", "khám phá": "kinh nghiệm",
    "phi chức năng": "phi chức năng", "a11y": "phi chức năng", "khả dụng": "phi chức năng",
    "hiệu năng": "phi chức năng", "tương thích": "phi chức năng", "i18n": "phi chức năng",
}
ALIASES = {"phân vùng tương đương": "phân vùng", "ep": "phân vùng", "biên": "giá trị biên", "bva": "giá trị biên",
           "domain analysis": "biên nhiều chiều", "syntax testing": "syntax", "cause-effect": "bảng quyết định",
           "ma trận phân quyền": "phân quyền", "trạng thái": "chuyển trạng thái", "kịch bản": "use case",
           "scenario": "use case", "tổ hợp": "pairwise", "white-box": "hộp trắng", "hộp trắng nhẹ": "hộp trắng",
           "race": "đồng thời", "concurrency": "đồng thời", "sbtm": "khám phá", "exploratory": "khám phá",
           "wcag": "a11y", "usability": "khả dụng", "characterization": "mốc hành vi", "golden master": "mốc hành vi",
           "back-to-back": "so sánh song song", "differential": "so sánh song song", "parallel run": "so sánh song song",
           "so sánh cũ mới": "so sánh song song", "reconciliation": "đối soát dữ liệu", "đối soát": "đối soát dữ liệu"}


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
            for k in ("Kiểu", "Mức", "Loại", "Regression", "Tag", "Thực hiện"):
                tc[k] = no_paren(plain(tc[k]))
            tc["human"] = tc["Thực hiện"].lower() in BY_HUMAN
            tc["reqs"] = req_ids(tc["REQ"])
            tc["vps"] = [x.upper() for x in re.findall(VP_ID, tc["VP"], re.I)]
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
    """REQ → mức R người dùng đã xác nhận ở SCOPE §2 (cột `Mức`, đọc theo tên). REQ không có trong SCOPE hiện tại → tìm ở
    SCOPE-<đợt>.md cũ (REQ đã phát hành, còn regression). Không suy từ TC."""
    out: dict[str, str] = {}
    files = [scope_file()] + (sorted(QA.glob("SCOPE-*.md"), key=lambda p: p.stat().st_mtime, reverse=True) if include_old else [])
    for f in files:
        for r in table_dicts(section(read(f), "2."), "REQ"):
            m = re.search(r"\bR[1-3]\b", col(r, "mức").upper())
            if m:
                for req in req_ids(r.get("req", "")):
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
    """Câu hỏi ANALYSIS §5 chưa có Trả lời — đọc cột theo tên (bảng thêm cột, vd `Ưu tiên`, vẫn đúng)."""
    rows = table_dicts(re.sub(r"<!--.*?-->", "", section(read(QA / "ANALYSIS.md"), "5."), flags=re.S), "#")
    out = []
    for r in rows:
        q = col(r, "điểm chưa rõ", "câu hỏi")
        if q and not q.startswith("<") and not plain(col(r, "trả lời")):
            out.append(f"#{r.get('#', '')} {q}")
    return out


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


# ---------------------------------------------------------------- bảng có tên cột

def table_dicts(text: str, first: str) -> list[dict]:
    """Các dòng của MỌI bảng có cột đầu tên `first` (không phân biệt hoa thường), khoá = tên cột viết thường.
    Tên cột đọc theo tiêu đề nên bảng cũ thiếu cột mới vẫn đọc được."""
    out: list[dict] = []
    head: list[str] | None = None
    sep_seen = False
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            head, sep_seen = None, False
            continue
        cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", s.strip("|"))]
        if head is None:
            names = [plain(c).lower() for c in cells]
            head = names if names and names[0] == first.lower() else []
            continue
        if not sep_seen:
            sep_seen = all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c)
            if sep_seen:
                continue
        if head and any(cells):
            out.append({head[i]: (cells[i] if i < len(cells) else "") for i in range(len(head))})
    return out


def col(row: dict, *prefixes: str) -> str:
    """Giá trị cột đầu tiên có tên bắt đầu bằng một trong các tiền tố (viết thường)."""
    for p in prefixes:
        for k, v in row.items():
            if k.startswith(p):
                return v
    return ""


# ---------------------------------------------------------------- nguồn & trích dẫn

BINARY_EXT = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".png", ".jpg", ".jpeg", ".gif", ".webp",
              ".fig", ".sketch", ".zip", ".odt", ".ods"}
_doc_cache: dict[Path, str] = {}


def norm_text(s: str) -> str:
    """So trích dẫn: bỏ định dạng markdown, nháy cong, khoảng trắng thừa; không phân biệt hoa thường."""
    s = unicodedata.normalize("NFC", s or "")
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'").replace(" ", " ")
    s = re.sub(r"<br\s*/?>", " ", s, flags=re.I)
    s = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", s)              # [chữ](link) → chữ
    s = re.sub(r"\\([\\`*_{}\[\]()#+\-.!|>~])", r"\1", s)       # \* \_ \| … → ký tự thường
    s = re.sub(r"[*_`>#|]", " ", s)
    s = re.sub(r"^\s*(?:[-+]|\d+[.)])\s+", " ", s, flags=re.M)
    return re.sub(r"\s+", " ", s).strip().casefold()


def quote_parts(q: str) -> list[str]:
    q = (q or "").strip().strip('"“”\'‘’').strip()
    parts = re.split(r"\s*(?:…|\.\.\.|\[\.\.\.\]|\[…\])\s*", q)
    return [norm_text(p).strip('"\' ') for p in parts if norm_text(p).strip('"\' ')]


def source_files(src: str) -> tuple[list[Path], list[str]]:
    """→ (file cục bộ đọc được, phần nguồn không kiểm được bằng máy: URL, pdf/docx, file không có)."""
    files, other = [], []
    raw = re.sub(r"\[([^\]]*)\]\(([^)]+)\)", r" `\2` ", src or "")
    whole = [t.strip() for t in re.findall(r"`([^`]+)`", raw)]            # `docs/Đặc tả v2.md` — giữ dấu cách
    raw = re.sub(r"`[^`]+`", " ", raw)
    head = re.split(r"\s*(?:§|,|;|·|:\d)", raw.strip(), maxsplit=1)[0].strip()
    if " " in head and re.search(r"\.\w{1,8}$", head) and (ROOT / head).is_file():
        whole.append(head)                                                    # docs/Đặc tả v2.md §2 (không backtick)
        raw = raw.replace(head, " ", 1)
    for tok in whole + re.split(r"[\s,;·]+", raw):
        t = tok.strip("`*()[]\"'")
        if not t or t.startswith("§") or t.lower() in ("mục", "dòng", "trang"):
            continue
        if re.match(r"https?://", t):
            other.append(t)
            continue
        t = re.sub(r"(?::\d+(?:-\d+)?|#.*)$", "", t)
        if not re.search(r"\.\w{1,8}$", t) and "/" not in t:
            continue
        p = Path(t).expanduser()
        p = p if p.is_absolute() else ROOT / p
        if p.suffix.lower() in BINARY_EXT:
            other.append(t)
        elif p.is_file():
            files.append(p)
        else:
            other.append(t + " (không thấy file)")
    return files, other


def verify_quote(src: str, quote: str) -> tuple[str, str]:
    """→ (trạng thái, ghi chú). Trạng thái: khớp · lệch · thiếu-nguồn · thiếu-trích · không-kiểm-máy."""
    if not plain(src) or PLACEHOLDER_RE.search(src):
        return "thiếu-nguồn", "cột Nguồn trống"
    parts = quote_parts(quote)
    if not parts:
        return "thiếu-trích", "chưa trích nguyên văn câu trong tài liệu"
    files, other = source_files(src)
    if not files:
        return "không-kiểm-máy", ("nguồn " + ", ".join(other) if other else "không nhận ra đường dẫn file trong Nguồn") \
            + " — máy không mở được, cần qa-source-check đối chiếu"
    docs = []
    for f in files:
        if f not in _doc_cache:
            _doc_cache[f] = norm_text(read(f))
        docs.append(_doc_cache[f])
    short = [x for x in parts if len(x.split()) < (2 if len(parts) > 1 else 3)]
    if short:
        return "thiếu-trích", f"trích dẫn quá ngắn để đối chiếu (\"{short[0]}\") — chép nguyên câu, mỗi đoạn quanh `…` ≥ 2 từ"
    where = ", ".join(str(f.relative_to(ROOT)) if ROOT in f.parents else str(f) for f in files)
    for d in docs:                                   # mọi đoạn phải có trong CÙNG một file, đúng thứ tự
        pos, ok = 0, True
        for part in parts:
            i = d.find(part, pos)
            if i < 0:
                ok = False
                break
            pos = i + len(part)
        if ok:
            return "khớp", ""
    for part in parts:
        if not any(part in d for d in docs):
            return "lệch", f"không tìm thấy \"{part[:70]}\" trong {where}"
    return "lệch", f"các đoạn quanh `…` có trong {where} nhưng không đúng thứ tự / không cùng một file"


# ---------------------------------------------------------------- quan điểm test

VP_OK = ("duyệt", "đã duyệt")
VP_STATES = ("nháp", "duyệt", "đã duyệt", "bỏ")
OUTSIDE_RE = re.compile(r"ngoài đặc tả", re.I)


def vp_state(v: dict) -> str:
    s = re.sub(r"\s+", " ", no_paren(plain(v.get("Trạng thái", ""))).lower()).strip()
    return "duyệt" if s in VP_OK else s


def vp_usable(v: dict | None) -> bool:
    """VP dùng được để viết/chạy TC: đã duyệt, không còn chờ trả lời."""
    return bool(v) and vp_state(v) == "duyệt" and not waiting(" ".join(str(x) for x in v.values() if isinstance(x, str)))


def load_vps() -> tuple[dict[str, dict], list[str]]:
    vps: dict[str, dict] = {}
    errors: list[str] = []
    d = QA / "viewpoints"
    for f in sorted(d.glob("*.md")) if d.is_dir() else []:
        if f.name.startswith("_"):
            continue
        text = read(f)
        approver = field(text, "Duyệt bởi")
        for row in table_dicts(re.sub(r"<!--.*?-->", "", text, flags=re.S), "VP"):
            first = plain(row.get("vp", ""))
            if not first:
                continue
            m = re.fullmatch(VP_ID, first, re.I)
            if not m:
                if first.upper().startswith("VP-"):
                    errors.append(f"{f.name}: mã `{first}` không đúng khuôn VP-<TÍNH-NĂNG>-<3 chữ số> — dòng không được đếm")
                continue
            vid = first.upper()
            if vid in vps:
                errors.append(f"{vid}: mã trùng ({vps[vid]['file']} và {f.name})")
                continue
            v = {"id": vid, "file": f.name, "feature": f.stem, "approver": approver,
                 "REQ": col(row, "req"), "Hạng mục": col(row, "hạng mục"), "Quan điểm": col(row, "quan điểm"),
                 "Kiểu": no_paren(plain(col(row, "kiểu"))), "Kỹ thuật": col(row, "kỹ thuật"),
                 "Mức": no_paren(plain(col(row, "mức"))), "Nguồn": col(row, "nguồn"),
                 "Trích": col(row, "trích"), "Trạng thái": col(row, "trạng thái")}
            v["reqs"] = req_ids(v["REQ"])
            v["outside"] = bool(OUTSIDE_RE.search(" ".join(str(x) for x in row.values())))   # ghi nhầm cột vẫn tính
            v["outside_misplaced"] = v["outside"] and not OUTSIDE_RE.search(v["Nguồn"])
            vps[vid] = v
    return vps, errors


def analysis_rows() -> list[dict]:
    """Dòng REQ ở ANALYSIS §3 (đọc theo tên cột — bản cũ không có cột Trích nguyên văn vẫn đọc được)."""
    return [r for r in table_dicts(section(read(QA / "ANALYSIS.md"), "3."), "REQ") if req_ids(r.get("req", ""))]


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
    vps, _ = load_vps()
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
        if t["Thực hiện"].lower() not in BY_HUMAN + BY_AGENT:
            errors.append(f"{t['id']}: `Thực hiện: {t['Thực hiện']}` — phải là `agent` (mặc định, để trống được) hoặc `người`")
        if vps:                                   # dự án đã dùng lớp quan điểm test → TC phải đi ra từ quan điểm đã duyệt
            if not t["vps"]:
                if plain(t["VP"]) and plain(t["VP"]) not in ("—", "-"):
                    errors.append(f"{t['id']}: trường VP `{t['VP']}` không đọc được mã VP-<TÍNH-NĂNG>-<3 chữ số>")
                elif not re.search(r"BUG-\d+", t["Nguồn"]):
                    (errors if strict else warns).append(f"{t['id']}: chưa trỏ quan điểm test (`VP:`) — TC phải đi ra từ quan điểm đã duyệt")
            for vid in t["vps"]:
                v = vps.get(vid)
                if not v:
                    errors.append(f"{t['id']}: {vid} không có trong qa/viewpoints/")
                elif not vp_usable(v):
                    errors.append(f"{t['id']}: {vid} chưa `duyệt` hoặc còn chờ trả lời — chưa được viết/chạy TC từ quan điểm này")
                else:
                    if t["reqs"] and v["reqs"] and not set(t["reqs"]) <= set(v["reqs"]):
                        warns.append(f"{t['id']}: REQ {', '.join(t['reqs'])} không khớp REQ của {vid} ({', '.join(v['reqs'])})")
                    if t["Kiểu"] and v["Kiểu"] and t["Kiểu"].lower() != v["Kiểu"].lower():
                        warns.append(f"{t['id']}: Kiểu {t['Kiểu']} khác kiểu {v['Kiểu']} của {vid}")
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
    """Bỏ TC còn nhãn chờ, trỏ tới REQ còn chờ xác nhận, hoặc trỏ tới quan điểm test chưa duyệt — chưa được đưa vào run."""
    tcs, _ = load_tcs()
    wreq = waiting_reqs()
    vps, _ = load_vps()
    w = [i for i in ids if waiting(tcs.get(i, {}).get("body", "")) or set(tcs.get(i, {}).get("reqs", [])) & wreq
         or any(not vp_usable(vps.get(v)) for v in tcs.get(i, {}).get("vps", []))]
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
    para_ai = field_any(scope_text, "Test AI — số cách diễn đạt mỗi ca (kiểm ổn định)", "Test AI — số cách diễn đạt mỗi ca")
    ai_lines = (f"  - Test AI — N mỗi ca: {n_ai}\n  - Test AI — ngưỡng đạt mỗi ca: {thr_ai}\n"
                + (f"  - Test AI — số cách diễn đạt mỗi ca: {para_ai}\n" if para_ai else "")) if (n_ai or thr_ai) else ""
    day = dt.date.today().isoformat()
    run_id, n = f"{day}-{kind}", 2
    while (QA / "runs" / run_id).exists():
        run_id, n = f"{day}-{kind}-{n}", n + 1
    d = QA / "runs" / run_id
    d.mkdir(parents=True)
    rows = "\n".join(f"| {i} | CHƯA CHẠY | | | |" for i in ids)
    tcs_all, _ = load_tcs()
    human = [i for i in ids if tcs_all.get(i, {}).get("human")]
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
        + (f"- TC do người thực hiện (giao cho người dùng; bằng chứng họ gửi + `{HUMAN_NOTE}`): {', '.join(human)}\n" if human else "")
        + f"- Scope lúc tạo run: {st}\n"
        f"- Tiêu chí ({src}; không sửa sau khi đã chạy):\n{crit_lines}{ai_lines}\n"
        "| TC | Kết quả | Ngày | Bằng chứng | Bug / Lý do |\n|---|---|---|---|---|\n"
        f"{rows}\n\n## Nhật ký\n", encoding="utf-8")
    (QA / "evidence" / run_id).mkdir(parents=True, exist_ok=True)
    print(f"run-id: {run_id}")
    print(f"RUNLOG: {d.relative_to(ROOT)}/RUNLOG.md · {len(ids)} TC ({how})")
    if human:
        print(f"TC do người thực hiện: {len(human)} — {', '.join(human)} → giao danh sách + bước cho người dùng (skill qa §7)")
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
    human_done = 0
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
            if tcs.get(tid, {}).get("human"):
                human_done += 1
                if not (QA / "evidence" / run_id / tid / HUMAN_NOTE).is_file():
                    errors.append(f"{tid}: TC do người thực hiện nhưng thiếu `{HUMAN_NOTE}` trong bằng chứng "
                                  "(ai làm, lúc nào, trên môi trường/bản nào, bằng chứng nhận qua đâu)")
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
              + (f" · khám phá {explore}" if explore else "") + (f" · người thực hiện {human_done}" if human_done else ""))
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
            reasons.append(f"tiêu chí đóng băng trong RUNLOG {', '.join(diff_crit)} khác SCOPE hiện tại — hỏi người dùng: tạo lại run bằng new-run (chép tiêu chí hiện tại) rồi chạy lại, hoặc chốt lại SCOPE §6 theo tiêu chí cũ (ghi DECISIONS)")
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
    vps, _ = load_vps()
    live_vps = {k: v for k, v in vps.items() if vp_state(v) != "bỏ"}
    extra = sorted({r for t in tcs.values() for r in t["reqs"]} - set(reqs))
    lines = ["| REQ | Mức (SCOPE) | Quan điểm (duyệt/tổng) | TC normal | TC abnormal | Kỹ thuật | Kết quả gần nhất | Bug mở |",
             "|---|---|---|---|---|---|---|---|"]
    gaps = 0
    for r in reqs + extra:
        rv = [v for v in live_vps.values() if r in v["reqs"]]
        vcell = f"{', '.join(v['id'] for v in rv)} ({sum(vp_usable(v) for v in rv)}/{len(rv)})" if rv else ("**—**" if live_vps else "—")
        no_vp_r = bool(live_vps) and not rv and r in reqs
        mine = [t for t in tcs.values() if r in t["reqs"]]
        nor = [t["id"] for t in mine if t["Kiểu"].lower() == "normal"]
        abn = [t["id"] for t in mine if t["Kiểu"].lower() == "abnormal"]
        tech = sorted(set().union(*[techniques(t) for t in mine] or [set()]))
        cnt: dict[str, int] = {}
        for t in mine:
            k = res.get(t["id"], ("chưa chạy", ""))[0]
            cnt[k] = cnt.get(k, 0) + 1
        ob = sorted({b["id"] + f" ({b['sev']})" for b in bugs.values() if b["open"] and set(b["tc"]) & {t["id"] for t in mine}})
        if not nor or not abn or no_vp_r:
            gaps += 1
        mark = "" if r in reqs else (" (regression)" if mine and all(t["Regression"].lower().startswith("có") for t in mine) else " ⚠ ngoài phạm vi")
        lines.append(f"| {r}{mark} | {levels.get(r, '— chưa chốt')} | {vcell} | {', '.join(nor) or '**—**'} | {', '.join(abn) or '**—**'} | "
                     f"{', '.join(tech) or '—'} | {' · '.join(f'{k} {v}' for k, v in sorted(cnt.items())) or '—'} | "
                     f"{', '.join(ob) or '—'} |")
    no_req = sorted(t["id"] for t in tcs.values() if not t["reqs"])
    vp_lines, vp_gaps = [], []
    if live_vps:
        vp_lines = ["", "| Quan điểm | REQ | Kiểu | Trạng thái | Nguồn | TC |", "|---|---|---|---|---|---|"]
        for v in live_vps.values():
            vt = [t["id"] for t in tcs.values() if v["id"] in t["vps"]]
            if vp_usable(v) and not vt:
                vp_gaps.append(v["id"])
            vp_lines.append(f"| {v['id']} | {', '.join(v['reqs']) or '—'} | {v['Kiểu'] or '—'} | {vp_state(v) or '—'} | "
                            f"{'ngoài đặc tả' if v['outside'] else 'đặc tả'} | {', '.join(vt) or '**—**'} |")
    no_vp = sorted(t["id"] for t in tcs.values() if live_vps and not t["vps"] and not re.search(r"BUG-\d+", t["Nguồn"]))
    summary = (f"REQ: {len(reqs)} ({'SCOPE' if scope_reqs() else 'ANALYSIS'}) · "
               + (f"quan điểm: {len(live_vps)} · " if live_vps else "") + f"TC: {len(tcs)} · "
               f"REQ thiếu quan điểm/normal/abnormal: {gaps}" + (f" · TC không trỏ REQ: {', '.join(no_req)}" if no_req else "")
               + (f" · quan điểm đã duyệt chưa có TC: {', '.join(vp_gaps)}" if vp_gaps else "")
               + (f" · TC không trỏ quan điểm: {', '.join(no_vp)}" if no_vp else ""))
    gaps += len(vp_gaps)
    out = "\n".join(lines + vp_lines) + "\n\n" + summary + "\n"
    if "--write" in args:
        (QA / "TRACE.md").write_text(
            f"# TRACE — ma trận truy vết\n\n> Sinh bởi `qa_check.py trace --write` lúc {dt.datetime.now():%Y-%m-%d %H:%M}. "
            "Không sửa tay — chạy lại lệnh.\n\n" + out, encoding="utf-8")
        print(f"Đã ghi {(QA / 'TRACE.md').relative_to(ROOT)}")
    print(out)
    return 1 if gaps else 0


# ---------------------------------------------------------------- lệnh: vp

def cmd_vp(args: list[str]) -> int:
    strict = "--strict" in args
    focus = [a for a in args if a != "--strict"]
    vps, errors = load_vps()
    warns: list[str] = []
    levels = scope_levels()
    known_reqs = set(scope_reqs()) | set(analysis_reqs())
    wreq = waiting_reqs()
    reqs_all = scope_reqs() or analysis_reqs()
    focus_reqs = [r for a in focus for r in req_ids(a)]
    focus_feat = [a for a in focus if not req_ids(a)]
    if focus:
        view = {k: v for k, v in vps.items() if set(v["reqs"]) & set(focus_reqs) or v["feature"] in focus_feat}
        reqs = focus_reqs + [r for v in view.values() for r in v["reqs"] if r not in focus_reqs]
        feats = {v["feature"] for v in vps.values()}
        for f_ in focus_feat:
            if f_ not in feats:
                errors.append(f"phạm vi `{f_}` không phải REQ-… hay tính năng nào trong qa/viewpoints/ (có: {', '.join(sorted(feats)) or '—'})")
    else:
        view, reqs = vps, reqs_all
    for v in view.values():
        vid, st = v["id"], vp_state(v)
        if st == "bỏ":
            continue
        miss = [k for k in ("REQ", "Quan điểm", "Kiểu", "Nguồn", "Trạng thái") if not plain(v[k])]
        if miss:
            errors.append(f"{vid} ({v['file']}): thiếu {', '.join(miss)}")
        if v["REQ"] and not v["reqs"]:
            errors.append(f"{vid}: cột REQ `{v['REQ']}` không đọc được mã REQ-…")
        for r in v["reqs"]:
            if known_reqs and r not in known_reqs:
                errors.append(f"{vid}: {r} không có trong ANALYSIS §3 / SCOPE §2 — quan điểm phải bám một yêu cầu đã phân tích")
            if r in wreq and not waiting(" ".join(str(x) for x in v.values() if isinstance(x, str))):
                warns.append(f"{vid}: {r} còn `(chờ trả lời)` ở ANALYSIS — quan điểm này cũng phải chờ, chưa duyệt được")
        if v["Kiểu"] and v["Kiểu"].lower() not in KIEU:
            errors.append(f"{vid}: `Kiểu: {v['Kiểu']}` — phải là normal hoặc abnormal")
        if st and st not in VP_STATES:
            errors.append(f"{vid}: trạng thái `{v['Trạng thái']}` lạ — dùng nháp · duyệt · bỏ")
        if v["Mức"]:
            if v["Mức"].upper() not in MUC:
                errors.append(f"{vid}: `Mức: {v['Mức']}` — phải là R1/R2/R3")
            for r in v["reqs"]:
                if r in levels and v["Mức"].upper() != levels[r]:
                    warns.append(f"{vid}: mức {v['Mức']} khác mức {levels[r]} người dùng chốt cho {r} ở SCOPE §2")
        for k in ("REQ", "Quan điểm", "Nguồn", "Trích"):
            m = PLACEHOLDER_RE.search(re.sub(r"`[^`]*`", "", v[k] or ""))
            if m:
                errors.append(f"{vid}: `{k}` còn chỗ trống `{m.group()}` — điền theo tài liệu hoặc hỏi")
        for w in VAGUE:
            if w in (v["Quan điểm"] or "").lower():
                warns.append(f"{vid}: quan điểm có từ mơ hồ `{w}` — nêu điều cụ thể cần kiểm")
                break
        tech = re.sub(r"<[^>]*>", "", v["Kỹ thuật"])
        for k in {norm_technique(x) for x in re.split(r"[,;·+/]", tech) if x.strip()} - set(TECHNIQUES):
            warns.append(f"{vid}: kỹ thuật `{k}` không có trong danh mục qa-testcase-design §1 — dùng tên chuẩn")
        if v["outside_misplaced"]:
            errors.append(f"{vid}: có chữ `ngoài đặc tả` nhưng không ở cột Nguồn — ghi `Nguồn: ngoài đặc tả — <lý do>` để "
                          "không lẫn với quan điểm bám đặc tả")
        if v["outside"]:
            if st == "duyệt" and not re.search(r"DECISIONS\s*#?\d+|#\d+", " ".join([v["Nguồn"], v["Trạng thái"]])):
                errors.append(f"{vid}: quan điểm ngoài đặc tả đã `duyệt` nhưng không trỏ dòng DECISIONS người dùng đồng ý")
            elif st != "duyệt":
                warns.append(f"{vid}: quan điểm NGOÀI đặc tả — trình người dùng, chỉ viết TC khi được duyệt (ghi DECISIONS)")
        else:
            state, why = verify_quote(v["Nguồn"], v["Trích"])
            if state in ("lệch", "thiếu-nguồn", "thiếu-trích"):
                errors.append(f"{vid}: {why} — quan điểm phải trích nguyên văn câu trong đặc tả (không có thì là điểm hỏi)")
            elif state == "không-kiểm-máy":
                warns.append(f"{vid}: {why}")
        if waiting(" ".join(str(x) for x in v.values() if isinstance(x, str))):
            warns.append(f"{vid}: còn `(chờ trả lời #n)` — hỏi người dùng; chưa viết TC từ quan điểm này")
        if st == "duyệt" and not plain(v["approver"]):
            warns.append(f"{vid}: `duyệt` nhưng {v['file']} chưa ghi `- Duyệt bởi:` — ai duyệt?")
    by_req: dict[str, set] = {}
    for v in vps.values():
        if vp_state(v) != "bỏ":
            for r in v["reqs"]:
                by_req.setdefault(r, set()).add(v["Kiểu"].lower())
    for r in reqs:
        k = by_req.get(r, set())
        if not k:
            (errors if strict or r in focus_reqs else warns).append(f"{r}: chưa có quan điểm test nào")
        else:
            for need in ("normal", "abnormal"):
                if need not in k:
                    errors.append(f"{r}: thiếu quan điểm `Kiểu: {need}`")
    n_ok = sum(1 for v in view.values() if vp_usable(v))
    print(f"Quan điểm test: {len(view)}{' (phạm vi: ' + ' '.join(focus) + ')' if focus else ''} · đã duyệt dùng được {n_ok}"
          f" · REQ đang xét: {len(reqs)}{' · --strict' if strict else ''}")
    for e in errors:
        print(f"  ✗ {e}")
    for w in warns:
        print(f"  ⚠ {w}")
    if not errors:
        print("  ✓ bộ quan điểm sạch")
    return 1 if errors else 0


# ---------------------------------------------------------------- lệnh: src

def cmd_src(args: list[str]) -> int:
    """Mọi REQ (ANALYSIS §3) và quan điểm test có nguồn; trích nguyên văn có thật trong tài liệu nguồn."""
    strict, listing = "--strict" in args, "--list" in args
    errors: list[str] = []
    warns: list[str] = []
    manual: list[tuple[str, str, str]] = []
    rows = analysis_rows()
    for r in rows:
        rid = ", ".join(req_ids(r.get("req", "")))
        src, quote = col(r, "nguồn"), col(r, "trích")
        state, why = verify_quote(src, quote)
        if state == "thiếu-nguồn":
            errors.append(f"{rid}: {why} — REQ phải trỏ về tài liệu/code cụ thể")
        elif state == "thiếu-trích":
            (errors if strict else warns).append(f"{rid}: {why} (cột `Trích nguyên văn` ở ANALYSIS §3)")
        elif state == "lệch":
            errors.append(f"{rid}: {why} — sửa trích dẫn cho đúng nguyên văn, hoặc đây là điều tài liệu không nói → ANALYSIS §5")
        elif state == "không-kiểm-máy":
            manual.append((rid, src, quote))
    vps, _ = load_vps()
    for v in vps.values():
        if vp_state(v) == "bỏ" or v["outside"]:
            continue
        state, why = verify_quote(v["Nguồn"], v["Trích"])
        if state in ("thiếu-nguồn", "thiếu-trích", "lệch"):
            errors.append(f"{v['id']}: {why}")
        elif state == "không-kiểm-máy":
            manual.append((v["id"], v["Nguồn"], v["Trích"]))
    outside = [v["id"] for v in vps.values() if v["outside"] and vp_state(v) != "bỏ"]
    print(f"Nguồn: {len(rows)} REQ · {len(vps)} quan điểm · máy không mở được nguồn: {len(manual)}"
          + (f" · quan điểm ngoài đặc tả: {', '.join(outside)}" if outside else ""))
    for e in errors:
        print(f"  ✗ {e}")
    for w in warns:
        print(f"  ⚠ {w}")
    if manual:
        print(f"  ⚠ {len(manual)} mục nguồn là URL/pdf/docx/file không có — spawn `qa-source-check` để đối chiếu bằng mắt"
              + ("" if listing else " (thêm --list để in danh sách)"))
        if listing:
            print("| Mục | Nguồn | Trích nguyên văn |\n|---|---|---|")
            for m in manual:
                print(f"| {m[0]} | {m[1]} | {m[2] or '—'} |")
    if not errors:
        print("  ✓ mọi trích dẫn máy mở được đều khớp tài liệu")
    return 1 if errors else 0


# ---------------------------------------------------------------- lệnh: export / import

TC_COLS = ["ID", "Tiêu đề", "REQ", "VP", "Target", "Loại", "Kiểu", "Mức", "Kỹ thuật", "Nguồn", "Regression", "Tag",
           "Ticket", "Tiền điều kiện", "Dữ liệu", "Ô ma trận", "Thực hiện", "Bước", "Kỳ vọng", "Bằng chứng cần"]
TC_FIELDS = TC_COLS[2:17]            # REQ … Thực hiện: một dòng `- Khoá: giá trị`
SPARSE = ("Ô ma trận", "Thực hiện")  # trường tuỳ chọn hiếm dùng: nhập CSV không ghi dòng trống
VP_COLS = ["VP", "Tính năng", "REQ", "Hạng mục", "Quan điểm test", "Kiểu", "Kỹ thuật dự kiến", "Mức", "Nguồn",
           "Trích nguyên văn", "Trạng thái"]
ALIASES_COMMON = {
    "requirement": "REQ", "yêu cầu": "REQ", "mức rủi ro": "Mức", "priority": "Mức", "type": "Kiểu",
    "source": "Nguồn", "status": "Trạng thái",
}
ALIASES_TC = {  # tên cột hay gặp trong file Excel của đội → tên trường của kit
    "mã tc": "ID", "tc": "ID", "tc id": "ID", "test case id": "ID", "id": "ID", "mã": "ID",
    "tên tc": "Tiêu đề", "title": "Tiêu đề", "tên": "Tiêu đề", "mô tả": "Tiêu đề",
    "viewpoint": "VP", "quan điểm": "VP", "mã vp": "VP", "vp id": "VP",
    "precondition": "Tiền điều kiện", "pre-condition": "Tiền điều kiện", "test data": "Dữ liệu",
    "steps": "Bước", "các bước": "Bước", "bước thực hiện": "Bước", "expected": "Kỳ vọng",
    "expected result": "Kỳ vọng", "kết quả mong đợi": "Kỳ vọng", "kết quả mong muốn": "Kỳ vọng",
    "evidence": "Bằng chứng cần",
}
ALIASES_VP = {
    "mã vp": "VP", "vp id": "VP", "viewpoint id": "VP", "id": "VP", "mã": "VP",
    "category": "Hạng mục", "check item": "Quan điểm test", "nội dung kiểm tra": "Quan điểm test",
    "quan điểm": "Quan điểm test", "viewpoint": "Quan điểm test", "kỹ thuật": "Kỹ thuật dự kiến",
    "quote": "Trích nguyên văn", "trích dẫn": "Trích nguyên văn",
}
FORMULA = ("=", "+", "-", "@", "\t", "\r")

# Ngôn ngữ bàn giao (`QA.md` dòng `- Ngôn ngữ bàn giao:` hoặc `export … --lang`): CHỈ đổi tiêu đề cột của file xuất.
# File trong qa/ vẫn tiếng Việt (qa_check đọc tên trường tiếng Việt); nội dung ô do agent dịch khi được nhờ (skill qa §1.8).
LANGS = {"vi": "vi", "tiếng việt": "vi", "vietnamese": "vi", "en": "en", "tiếng anh": "en", "english": "en",
         "ja": "ja", "tiếng nhật": "ja", "japanese": "ja", "日本語": "ja"}
HEAD_TR = {
    "en": {"ID": "ID", "Tiêu đề": "Title", "REQ": "Requirement ID", "VP": "Viewpoint ID", "Target": "Target",
           "Loại": "Test type", "Kiểu": "Kind (normal/abnormal)", "Mức": "Risk level", "Kỹ thuật": "Technique",
           "Nguồn": "Source", "Regression": "Regression", "Tag": "Tag", "Ticket": "Ticket", "Tiền điều kiện": "Precondition",
           "Dữ liệu": "Test data", "Ô ma trận": "Matrix cell", "Thực hiện": "Executed by (agent/human)", "Bước": "Steps",
           "Kỳ vọng": "Expected result", "Bằng chứng cần": "Required evidence", "Tính năng": "Feature",
           "Hạng mục": "Category", "Quan điểm test": "Test viewpoint", "Kỹ thuật dự kiến": "Planned technique",
           "Trích nguyên văn": "Verbatim quote (source language)", "Trạng thái": "Status"},
    "ja": {"ID": "ID", "Tiêu đề": "タイトル", "REQ": "要件ID", "VP": "観点ID", "Target": "対象", "Loại": "テスト種別",
           "Kiểu": "区分（正常系/異常系）", "Mức": "リスクレベル", "Kỹ thuật": "技法", "Nguồn": "根拠", "Regression": "回帰対象",
           "Tag": "タグ", "Ticket": "チケット", "Tiền điều kiện": "前提条件", "Dữ liệu": "テストデータ", "Ô ma trận": "マトリクスセル",
           "Thực hiện": "実施者（エージェント/人）", "Bước": "手順", "Kỳ vọng": "期待結果", "Bằng chứng cần": "必要なエビデンス",
           "Tính năng": "機能", "Hạng mục": "分類", "Quan điểm test": "テスト観点", "Kỹ thuật dự kiến": "想定技法",
           "Trích nguyên văn": "原文引用（原語のまま）", "Trạng thái": "ステータス"},
}
HEAD_BACK = {label.lower(): canon for tr in HEAD_TR.values() for canon, label in tr.items()}   # nhập lại file đã xuất


def export_lang(args: list[str]) -> tuple[str, str]:
    """(mã ngôn ngữ, lỗi). --lang thắng dòng QA.md; trống → vi."""
    raw = args[args.index("--lang") + 1] if "--lang" in args and args.index("--lang") + 1 < len(args) \
        else no_paren(plain(field(read(QA / "QA.md"), "Ngôn ngữ bàn giao")))
    code = LANGS.get(raw.strip().lower(), "") if raw.strip() else "vi"
    return code, ("" if code else f"ngôn ngữ bàn giao `{raw}` chưa hỗ trợ — dùng vi / en / ja")


def csv_safe(c: str) -> str:
    """Chống chèn công thức khi mở bằng Excel (TC phá-đầu-vào hay chứa `=HYPERLINK(…)`): thêm `'` phía trước."""
    c = re.sub(r"<br\s*/?>", "\n", c or "")
    return "'" + c if c.startswith(FORMULA) else c


def csv_unsafe(c: str) -> str:
    return c[1:] if c.startswith("'") and c[1:2] in FORMULA else c


def cmd_export(args: list[str]) -> int:
    kind = args[0].lower() if args else ""
    if kind not in ("tc", "vp"):
        print("cách gọi: export <tc|vp> [--out <file.csv>] [--lang vi|en|ja]", file=sys.stderr)
        return 2
    lang, bad_lang = export_lang(args)
    if bad_lang:
        print(f"✗ {bad_lang}", file=sys.stderr)
        return 2
    out = Path(args[args.index("--out") + 1]) if "--out" in args and args.index("--out") + 1 < len(args) \
        else QA / "export" / f"{kind}-{dt.date.today().isoformat()}{'' if lang == 'vi' else '-' + lang}.csv"
    out = out if out.is_absolute() else ROOT / out
    rows: list[list[str]] = []
    if kind == "tc":
        tcs, _ = load_tcs()
        num = lambda xs: "\n".join(f"{i}. {x}" for i, x in enumerate(xs, 1))
        for t in tcs.values():                       # giá trị nguyên văn (kể cả chú thích trong ngoặc), không phải bản đã chuẩn hoá
            rows.append([t["id"], t["title"]] + [field(t["body"], k) for k in TC_FIELDS]
                        + [num(t["steps"]), num(t["expects"]), field(t["body"], "Bằng chứng cần")])
        cols = TC_COLS
    else:
        vps, _ = load_vps()
        rows = [[v["id"], v["feature"], v["REQ"], v["Hạng mục"], v["Quan điểm"], v["Kiểu"], v["Kỹ thuật"], v["Mức"],
                 v["Nguồn"], v["Trích"], v["Trạng thái"]] for v in vps.values()]
        cols = VP_COLS
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([HEAD_TR.get(lang, {}).get(c, c) for c in cols])
        w.writerows([[csv_safe(c) for c in r] for r in rows])
    print(f"Đã xuất {len(rows)} {'TC' if kind == 'tc' else 'quan điểm'} → {out}"
          + ("" if lang == "vi" else f" (tiêu đề cột: {lang})"))
    if lang != "vi":
        print(f"  ⚠ nội dung ô vẫn là tiếng Việt — bàn giao bằng `{lang}` thì dịch file này (skill qa §1.8): giữ nguyên mã "
              "ID/REQ/VP, giá trị chuẩn (normal/abnormal, R1–R3), và cột trích nguyên văn")
    return 0


def read_csv(path: Path, kind: str) -> list[dict]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    rows = list(csv.reader(io.StringIO(text, newline=""), dialect))
    if not rows:
        return []
    canon = set(TC_COLS if kind == "tc" else VP_COLS)
    aliases = {**{k: v for k, v in HEAD_BACK.items() if v in canon}, **ALIASES_COMMON, **(ALIASES_TC if kind == "tc" else ALIASES_VP)}
    raw = [unicodedata.normalize("NFC", h).strip() for h in rows[0]]
    exact = {h for h in raw if h in canon}
    head = []
    for h in raw:                                   # tên đúng của kit thắng; bí danh không đè cột đã có tên đúng
        k = h if h in canon else aliases.get(h.lower(), h)
        head.append(k if k == h or k not in exact and k not in head else h)
    return [dict(zip(head, [csv_unsafe(unicodedata.normalize("NFC", c).strip()) for c in r]))
            for r in rows[1:] if any(c.strip() for c in r)]


def one_line(s: str) -> str:
    return " ".join((s or "").split())


def cmd_import(args: list[str]) -> int:
    if len(args) < 2 or args[0].lower() not in ("tc", "vp") or "--feature" not in args or args.index("--feature") + 1 >= len(args):
        print("cách gọi: import <tc|vp> <file.csv> --feature <tính-năng>   (Excel: Lưu thành → CSV UTF-8)", file=sys.stderr)
        return 2
    kind, src = args[0].lower(), Path(args[1])
    feat = args[args.index("--feature") + 1]
    if src.suffix.lower() in (".xlsx", ".xls"):
        print("✗ chưa đọc thẳng .xlsx — mở bằng Excel/Sheets, Lưu thành → CSV UTF-8, rồi nhập file .csv", file=sys.stderr)
        return 2
    src = src if src.is_absolute() else Path.cwd() / src
    if not src.is_file():
        print(f"✗ không thấy file {src}", file=sys.stderr)
        return 2
    rows = read_csv(src, kind)
    if not rows:
        print(f"✗ {src} rỗng hoặc không đọc được", file=sys.stderr)
        return 1
    problems: list[str] = []
    seen: set[str] = set()
    if kind == "tc":
        out = QA / "testcases" / f"{feat}.md"
        have, _ = load_tcs()
        blocks = []
        items = lambda s: [re.sub(r"^\s*(?:\d+[.)]|-)\s*", "", x) for x in re.split(r"\r?\n", s or "") if x.strip()]
        for i, r in enumerate(rows, 2):
            tid = plain(r.get("ID", "")).upper()
            if not re.fullmatch(TC_ID, tid):
                problems.append(f"dòng {i}: mã `{one_line(r.get('ID', ''))}` không đúng khuôn TC-<TÍNH-NĂNG>-<3 chữ số> — không nhập (không tự đặt mã)")
                continue
            if tid in have or tid in seen:
                problems.append(f"dòng {i}: {tid} đã có ({have[tid]['file'] if tid in have else 'trùng trong chính file CSV'}) — bỏ qua")
                continue
            seen.add(tid)
            lines = [f"## {tid} — {one_line(r.get('Tiêu đề', ''))}".rstrip(" —")]
            lines += [f"- {k}: {one_line(r.get(k))}" for k in TC_FIELDS if k not in SPARSE or r.get(k)]
            for k in ("Bước", "Kỳ vọng"):
                lines.append(f"- {k}:")
                lines += [f"  {n}. {x}" for n, x in enumerate(items(r.get(k, "")), 1)]
            lines.append(f"- Bằng chứng cần: {one_line(r.get('Bằng chứng cần'))}")
            blocks.append("\n".join(lines) + "\n")
        if blocks:
            existing = read(out)
            head = existing.rstrip() if existing else (f"# Test case — {feat}\n\n> Nhập từ {src.name} lúc {dt.datetime.now():%Y-%m-%d %H:%M}"
                                                       " — bản sao định dạng để soát; trường trống giữ trống, không tự điền.")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(head + "\n\n" + "\n".join(blocks), encoding="utf-8")
        print(f"Đã nhập {len(blocks)} TC vào {out.relative_to(ROOT)} — chạy `qa_check.py tc {feat}` để soát")
    else:
        out = QA / "viewpoints" / f"{feat}.md"
        have, _ = load_vps()
        lines = []
        for i, r in enumerate(rows, 2):
            vid = plain(r.get("VP", "")).upper()
            if not re.fullmatch(VP_ID, vid):
                problems.append(f"dòng {i}: mã `{one_line(r.get('VP', ''))}` không đúng khuôn VP-<TÍNH-NĂNG>-<3 chữ số> — không nhập (không tự đặt mã)")
                continue
            if vid in have or vid in seen:
                problems.append(f"dòng {i}: {vid} đã có ({have[vid]['file'] if vid in have else 'trùng trong chính file CSV'}) — bỏ qua")
                continue
            seen.add(vid)
            lines.append("| " + " | ".join([vid] + [one_line(r.get(k)).replace("|", "\\|") for k in VP_COLS[2:]]) + " |")
        existing = read(out)
        if lines and existing:
            problems.append(f"{out.name} đã có — {len(lines)} dòng mới in dưới, tự chép vào đúng bảng:")
            problems += lines
            lines = []
        elif lines:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(f"# Quan điểm test — {feat}\n\n> Nhập từ {src.name} lúc {dt.datetime.now():%Y-%m-%d %H:%M} — bản sao "
                           "định dạng để soát; trường trống giữ trống, không tự điền.\n\n- Duyệt bởi: \n- Ngày duyệt: \n\n"
                           "| " + " | ".join(["VP"] + VP_COLS[2:]) + " |\n|" + "---|" * (len(VP_COLS) - 1) + "\n"
                           + "\n".join(lines) + "\n", encoding="utf-8")
        print(f"Đã nhập {len(lines)} quan điểm vào {out.relative_to(ROOT)} — chạy `qa_check.py vp {feat}` để soát")
    for p in problems:
        print(f"  ⚠ {p}")
    return 0


# ---------------------------------------------------------------- lệnh: lessons

LESSON_DONE = ("đã nâng", "bỏ")
LESSON_HEAD = "| Ngày | Loại | Bài học | Nguồn | Trạng thái | Phạm vi áp |\n|---|---|---|---|---|---|\n"


def split_cells(line: str) -> list[str]:
    return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def lesson_lines(text: str) -> list[tuple[int, dict]]:
    """(số dòng, bài học) cho từng dòng dữ liệu của bảng bài học — giữ số dòng để cất đúng dòng, không so theo chữ."""
    out, head, sep = [], None, False
    lines = text.splitlines()
    in_comment = False
    for n, line in enumerate(lines):
        if "<!--" in line and "-->" not in line:
            in_comment = True
        if in_comment:
            in_comment = "-->" not in line
            continue
        s = line.strip()
        if not s.startswith("|"):
            head, sep = None, False
            continue
        cells = [c.replace("\\|", "|") for c in split_cells(s)]
        if head is None:
            names = [plain(c).lower() for c in cells]
            head = names if names and names[0] == "ngày" else []
            continue
        if not sep:
            sep = all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c)
            if sep:
                continue
        if head:
            r = {head[i]: (cells[i] if i < len(cells) else "") for i in range(len(head))}
            if plain(col(r, "bài học")):
                out.append((n, {"day": plain(col(r, "ngày")), "kind": plain(col(r, "loại")).lower(), "text": col(r, "bài học"),
                                "src": col(r, "nguồn"), "scope": col(r, "phạm vi"),
                                "state": no_paren(plain(col(r, "trạng thái"))).lower()}))
    return out


def lesson_rows(text: str | None = None) -> list[dict]:
    return [r for _, r in lesson_lines(read(QA / "LESSONS.md") if text is None else text)]


def fold_key(s: str) -> str:
    return re.sub(r"[\s_\-–—/]+", " ", unicodedata.normalize("NFC", s or "").casefold()).strip()


def lessons_brief(limit: int = 30) -> str:
    rows = [r for r in lesson_rows() if not r["state"].startswith(LESSON_DONE)]
    if not rows:
        return ""
    rows = sorted(rows, key=lambda r: r["day"], reverse=True)
    lines = [f"- [{r['kind'] or '?'}{' · ' + r['scope'] if r['scope'] else ''}] {r['text']} ({r['state'] or '?'})" for r in rows[:limit]]
    more = f"\n… còn {len(rows) - limit} bài học cũ hơn — `qa_check.py lessons` để xem hết" if len(rows) > limit else ""
    return "\n".join(lines) + more


def cmd_lessons(args: list[str]) -> int:
    path = QA / "LESSONS.md"
    if not path.is_file():
        print("chưa có qa/LESSONS.md", file=sys.stderr)
        return 1
    if "--brief" in args:
        b = lessons_brief()
        print(b or "(chưa có bài học đang hiệu lực)")
        return 0
    rows = lesson_rows()
    if "--for" in args:
        i = args.index("--for")
        keys = [fold_key(k) for k in args[i + 1:] if not k.startswith("--")]
        sel = [r for r in rows if not r["state"].startswith(LESSON_DONE)
               and (not plain(r["scope"]) or any(k and k in fold_key(r["scope"] + " " + r["text"]) for k in keys))]
        print(f"# bài học áp cho {' '.join(keys) or '(chung)'}: {len(sel)} — dán vào prompt tester")
        for r in sel:
            print(f"- [{r['kind']}] {r['text']} (nguồn: {plain(r['src']) or '—'})")
        return 0
    if "--archive" in args:
        text = read(path)
        done = [(n, r) for n, r in lesson_lines(text) if r["state"].startswith(LESSON_DONE)]
        if not done:
            print("không có dòng `đã nâng`/`bỏ` để cất")
            return 0
        arch = QA / "LESSONS-archive.md"
        atext = read(arch) or ("# LESSONS — lưu trữ\n\n> Dòng `đã nâng`/`bỏ` cất từ LESSONS.md bằng `qa_check.py lessons --archive`. "
                               "Không nạp đầu phiên; tra khi cần.\n\n" + LESSON_HEAD)
        esc = lambda s: (s or "").replace("|", "\\|")
        atext = atext.rstrip("\n") + "\n" + "".join(
            f"| {r['day']} | {r['kind']} | {esc(r['text'])} | {esc(r['src'])} | {r['state']} | {esc(r['scope'])} |\n" for _, r in done)
        drop = {n for n, _ in done}
        kept = [l for n, l in enumerate(text.splitlines(keepends=True)) if n not in drop]
        arch.write_text(atext, encoding="utf-8")
        path.write_text("".join(kept), encoding="utf-8")
        print(f"Đã cất {len(done)} dòng sang {arch.relative_to(ROOT)}")
        return 0
    by: dict[str, int] = {}
    for r in rows:
        by[r["state"] or "?"] = by.get(r["state"] or "?", 0) + 1
    print(f"Bài học: {len(rows)} ({', '.join(f'{k} {v}' for k, v in sorted(by.items())) or '—'})")
    seen: dict[str, str] = {}
    for r in rows:
        k = norm_text(r["text"])
        if k in seen:
            print(f"  ⚠ trùng: \"{r['text'][:60]}\" ({seen[k]} và {r['day']}) — gộp thành một dòng")
        seen[k] = r["day"]
    active = [r for r in rows if not r["state"].startswith(LESSON_DONE)]
    if len(active) > 40:
        print(f"  ⚠ {len(active)} bài học đang hiệu lực — gộp bài na ná, đánh `bỏ` bài hết hiệu lực, rồi `lessons --archive`")
    for r in active:
        print(f"  - {r['day']} [{r['kind']}] {r['text'][:100]} ({r['state']})")
    return 0

# ---------------------------------------------------------------- lệnh: status

def cmd_status() -> int:
    if not (QA / "QA.md").is_file():
        print(f"Chưa có workspace qa/ ở {ROOT} — cài bộ qa-agent (python3 <repo qa-agent>/install.py <dự án>).")
        return 1
    tcs, _ = load_tcs()
    bugs = load_bugs()
    lessons = [r for r in lesson_rows() if r["state"] == "mới"]
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
    vps, _ = load_vps()
    if vps:
        vs: dict[str, int] = {}
        for v in vps.values():
            vs[vp_state(v) or "?"] = vs.get(vp_state(v) or "?", 0) + 1
        covered = {r for v in vps.values() if vp_state(v) != "bỏ" for r in v["reqs"]}
        no_vp = [r for r in (scope_reqs() or analysis_reqs()) if r not in covered]
        print(f"Quan điểm test: {len(vps)} ({', '.join(f'{k} {n}' for k, n in sorted(vs.items()))})"
              + (f" · REQ chưa có quan điểm: {len(no_vp)}" if no_vp else ""))
    else:
        print("Quan điểm test: chưa có (qa/viewpoints/ — /qa-viewpoint)")
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
    if cmd == "vp":
        return cmd_vp(args)
    if cmd == "src":
        return cmd_src(args)
    if cmd == "export":
        return cmd_export(args)
    if cmd == "import":
        return cmd_import(args)
    if cmd == "lessons":
        return cmd_lessons(args)
    print(f"lệnh lạ `{cmd}`\n{__doc__}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
