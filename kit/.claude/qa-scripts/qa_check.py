#!/usr/bin/env python3
"""qa_check.py — kiểm tra nhẹ cho workspace qa/ (Python chuẩn, không phụ thuộc).

    python3 .claude/qa-scripts/qa_check.py status               tình trạng: REQ, câu hỏi chờ, scope, TC, run, bug, bài học
    python3 .claude/qa-scripts/qa_check.py tc                   soát bộ TC (trường bắt buộc, normal+abnormal mỗi REQ, kỳ vọng mơ hồ, kỹ thuật)
    python3 .claude/qa-scripts/qa_check.py select <phạm vi>     in TC theo: all | smoke | regression [TC-…] | retest BUG-… | <tính năng> | TC-…
    python3 .claude/qa-scripts/qa_check.py new-run <loại> [phạm vi]   tạo qa/runs/<ngày>-<loại>/RUNLOG.md, mọi dòng CHƯA CHẠY
    python3 .claude/qa-scripts/qa_check.py run [<run-id>]       soát RUNLOG + bằng chứng, tính kết luận theo tiêu chí đã chốt
    python3 .claude/qa-scripts/qa_check.py trace [--write]      ma trận truy vết REQ × TC × kỹ thuật × kết quả × bug (--write → qa/TRACE.md)

Không phải cổng chặn — chỉ báo. Không tự đặt con số nào: tiêu chí đạt và mức rủi ro lấy từ SCOPE do người dùng chốt;
thiếu thì báo "chưa chốt", không dùng mặc định. Exit 0 sạch · 1 có lỗi · 2 sai cách gọi.
"""

from __future__ import annotations

import datetime as dt
import os
import re
import sys
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
MUC = {"R1", "R2", "R3"}
LOAI = {"chức năng", "biên", "phá-đầu-vào", "phân-quyền", "workflow", "api", "tích-hợp", "tương-thích",
        "hình-thức", "hiệu-năng", "bảo-mật", "khôi-phục", "cross-target", "khám-phá", "smoke"}
REQUIRED = ["REQ", "Target", "Loại", "Kiểu", "Mức", "Nguồn", "Bước", "Kỳ vọng", "Bằng chứng cần"]
VAGUE = ["hoạt động đúng", "hiển thị đúng", "chạy đúng", "hoạt động bình thường", "hợp lý", "như mong đợi",
         "đúng nghiệp vụ", "đúng yêu cầu", "đúng thiết kế", "xử lý đúng", "tử tế", "thân thiện", "rõ ràng",
         "performance ok", "ổn định", "mượt"]
WAIT_MARKS = ("chờ trả lời", "chờ xác nhận")
TC_ID = r"TC-\w+(?:-\w+)*-\d{3}"
REQ_ID = r"REQ-[\w-]*\w"
BUG_OPEN = ("mở", "đã sửa")
BUG_CLOSED = ("đóng", "không sửa", "hoãn", "trùng")

# danh mục kỹ thuật: tên chuẩn → họ. R1 cần ≥ 2 HỌ khác nhau (qa-testcase-design §1).
TECHNIQUES = {
    "phân vùng": "dữ liệu", "giá trị biên": "dữ liệu", "biên nhiều chiều": "dữ liệu", "syntax": "dữ liệu",
    "bảng quyết định": "logic", "phân quyền": "logic", "crud": "logic", "chuyển trạng thái": "logic",
    "use case": "logic", "pairwise": "logic", "classification tree": "logic", "hộp trắng": "logic",
    "metamorphic": "oracle", "property": "oracle", "fuzz": "oracle", "đồng thời": "oracle",
    "error guessing": "kinh nghiệm", "checklist": "kinh nghiệm", "khám phá": "kinh nghiệm",
    "phi chức năng": "phi chức năng", "a11y": "phi chức năng", "khả dụng": "phi chức năng",
    "hiệu năng": "phi chức năng", "tương thích": "phi chức năng", "i18n": "phi chức năng",
}
ALIASES = {"phân vùng tương đương": "phân vùng", "ep": "phân vùng", "biên": "giá trị biên", "bva": "giá trị biên",
           "domain analysis": "biên nhiều chiều", "syntax testing": "syntax", "cause-effect": "bảng quyết định",
           "ma trận phân quyền": "phân quyền", "trạng thái": "chuyển trạng thái", "kịch bản": "use case",
           "scenario": "use case", "tổ hợp": "pairwise", "white-box": "hộp trắng", "hộp trắng nhẹ": "hộp trắng",
           "race": "đồng thời", "concurrency": "đồng thời", "sbtm": "khám phá", "exploratory": "khám phá",
           "wcag": "a11y", "usability": "khả dụng"}


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8-sig")
    except OSError:
        return ""


def waiting(text: str) -> bool:
    t = text.lower()
    return any(m in t for m in WAIT_MARKS)


def natural(name: str) -> list:
    return [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", name)]


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
    m = re.search(rf"^[ \t]*-[ \t]*{re.escape(key)}[ \t]*:[ \t]*(.*)$", text, re.M)
    return re.sub(r"<!--.*?-->", "", m.group(1)).strip() if m else ""


def plain(s: str) -> str:
    return re.sub(r"[*_`]", "", s).strip()


# ---------------------------------------------------------------- dữ liệu

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
            if re.search(r"(^|[^\w-])TC-", head):
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
            for k in REQUIRED + ["Regression", "Tag", "Ticket", "Kỹ thuật"]:
                tc[k] = field(body, k)
            tc["reqs"] = re.findall(REQ_ID, tc["REQ"])
            tc["steps"] = block_items(body, "Bước")
            tc["expects"] = block_items(body, "Kỳ vọng")
            tcs[tid] = tc
    return tcs, errors


def block_items(body: str, key: str) -> list[str]:
    m = re.search(rf"^[ \t]*-[ \t]*{re.escape(key)}[ \t]*:[ \t]*(.*)$", body, re.M)
    if not m:
        return []
    items = [m.group(1).strip()] if m.group(1).strip() else []
    for line in body[m.end():].splitlines()[1:]:
        if re.match(r"^-\s*[^:\n]{1,40}:(\s|$)", line):
            break
        s = line.strip()
        if re.match(r"^(\d+[.)]|-)\s+\S", s):
            items.append(re.sub(r"^(\d+[.)]|-)\s+", "", s))
        elif s and not items:
            items.append(s)
    return [x for x in items if x]


def scope_file() -> Path:
    return QA / "SCOPE.md"


def scope_rows() -> list[list[str]]:
    return [r for r in table_rows(section(read(scope_file()), "2.")) if r and re.search(REQ_ID, r[0])]


def scope_reqs() -> list[str]:
    out: list[str] = []
    for r in scope_rows():
        out += [x for x in re.findall(REQ_ID, r[0]) if x not in out]
    return out


def scope_levels() -> dict[str, str]:
    """REQ → mức R người dùng đã xác nhận ở SCOPE §2 (cột thứ 4). Không suy từ TC."""
    out = {}
    for r in scope_rows():
        m = re.search(r"R[1-3]", r[3].upper()) if len(r) >= 4 else None
        if m:
            for req in re.findall(REQ_ID, r[0]):
                out[req] = m.group()
    return out


def scope_status() -> str:
    return plain(field(read(scope_file()), "Trạng thái"))


def analysis_reqs() -> list[str]:
    out: list[str] = []
    for r in table_rows(section(read(QA / "ANALYSIS.md"), "3.")):
        if r:
            out += [x for x in re.findall(REQ_ID, r[0]) if x not in out]
    return out


def open_questions() -> list[str]:
    rows = table_rows(section(read(QA / "ANALYSIS.md"), "5."))
    return [f"#{r[0]} {r[1]}" for r in rows
            if len(r) >= 2 and r[1] and not r[1].startswith("<") and (len(r) < 5 or not r[4])]


def targets() -> list[str]:
    rows = table_rows(section(read(QA / "QA.md"), "Target"))
    return [r[0] for r in rows if r and r[0]]


def bug_is_open(status: str) -> bool:
    s = plain(status).lower()
    if s.startswith(BUG_CLOSED):
        return False
    return True   # "mở", "đã sửa (chờ test lại)", trạng thái lạ hoặc trống → coi là còn mở (an toàn)


def load_bugs() -> dict[str, dict]:
    text = re.sub(r"<!--.*?-->", "", read(QA / "BUGS.md"), flags=re.S)
    bugs = {}
    heads = list(re.finditer(r"^##\s+(BUG-\d+)\b\s*[—-]?\s*(.*)$", text, re.M))
    for i, h in enumerate(heads):
        body = text[h.end(): heads[i + 1].start() if i + 1 < len(heads) else len(text)]
        sev = re.search(r"S[1-4]", field(body, "Severity").upper())
        status = field(body, "Trạng thái")
        bugs[h.group(1)] = {"id": h.group(1), "title": h.group(2).strip(), "sev": sev.group() if sev else "",
                            "status": plain(status).lower(), "open": bug_is_open(status),
                            "known": plain(status).lower().startswith(BUG_OPEN + BUG_CLOSED),
                            "tc": re.findall(TC_ID, field(body, "TC")), "run": plain(field(body, "Run"))}
    return bugs


def parse_criteria(text: str) -> dict | None:
    """Ba dòng tiêu chí phải có giá trị — thiếu một dòng là CHƯA CHỐT (không có mặc định)."""
    f = field(text, "Bug mở không được phép")
    p = re.search(r"\d+(?:[.,]\d+)?", field(text, "Tỉ lệ PASS tối thiểu"))
    b = re.search(r"\d+(?:[.,]\d+)?", field(text, "Tỉ lệ BLOCKED tối đa"))
    if not f or not p or not b:
        return None
    forb = set(re.findall(r"S[1-4]", f.upper()))
    if not forb and not re.search(r"không|none|-", f.lower()):
        return None
    return {"forbidden": forb, "min_pass": float(p.group().replace(",", ".")),
            "max_blocked": float(b.group().replace(",", "."))}


def norm_technique(name: str) -> str:
    n = name.strip().lower()
    return ALIASES.get(n, n)


def techniques(tc: dict) -> set[str]:
    raw = re.sub(r"<[^>]*>", "", tc.get("Kỹ thuật", ""))
    return {norm_technique(t) for t in re.split(r"[,;·+/]", raw) if t.strip()}


# ---------------------------------------------------------------- lệnh: tc

def cmd_tc() -> int:
    tcs, errors = load_tcs()
    warns: list[str] = []
    tg = set(targets())
    levels = scope_levels()
    for t in tcs.values():
        miss = [k for k in REQUIRED if not t[k] and not (k == "Bước" and t["steps"]) and not (k == "Kỳ vọng" and t["expects"])]
        if miss:
            errors.append(f"{t['id']} ({t['file']}): thiếu {', '.join(miss)}")
        if t["Kiểu"] and t["Kiểu"].lower() not in KIEU:
            errors.append(f"{t['id']}: `Kiểu: {t['Kiểu']}` — phải là normal hoặc abnormal")
        if t["Mức"] and t["Mức"].upper() not in MUC:
            errors.append(f"{t['id']}: `Mức: {t['Mức']}` — phải là R1/R2/R3")
        for r in t["reqs"]:
            if r in levels and t["Mức"].upper() in MUC and t["Mức"].upper() != levels[r]:
                warns.append(f"{t['id']}: `Mức: {t['Mức']}` khác mức {levels[r]} người dùng đã chốt cho {r} ở SCOPE §2")
        if t["Loại"] and t["Loại"].lower() not in LOAI:
            warns.append(f"{t['id']}: loại `{t['Loại']}` ngoài danh mục qa-targets §2")
        for k in techniques(t) - set(TECHNIQUES):
            warns.append(f"{t['id']}: kỹ thuật `{k}` không có trong danh mục qa-testcase-design §1 — dùng tên chuẩn")
        if tg and t["Target"] and t["Target"] not in tg:
            warns.append(f"{t['id']}: target `{t['Target']}` không có trong QA.md §Target")
        if waiting(t["body"]):
            warns.append(f"{t['id']}: còn `(chờ trả lời)` — hỏi người dùng; TC này không được đưa vào run")
        for e in t["expects"]:
            for v in VAGUE:
                if v in e.lower():
                    errors.append(f"{t['id']}: kỳ vọng mơ hồ \"{e[:60]}\" (từ `{v}`) — viết điều quan sát được, có nguồn")
                    break
            if re.search(r"\b\d{3}\s*(hoặc|/|or)\s*\d{3}\b", e):
                warns.append(f"{t['id']}: kỳ vọng có hai đáp án (\"{e[:50]}\") — lấy đúng một theo tài liệu, không có thì hỏi")
    reqs = scope_reqs() or analysis_reqs()
    by_req: dict[str, set] = {}
    for t in tcs.values():
        for r in t["reqs"]:
            by_req.setdefault(r, set()).add(t["Kiểu"].lower())
    for r in reqs:
        k = by_req.get(r, set())
        if not k:
            errors.append(f"{r}: chưa có TC nào")
        else:
            for need in ("normal", "abnormal"):
                if need not in k:
                    errors.append(f"{r}: thiếu TC `Kiểu: {need}`")
    if scope_reqs():
        for r in reqs:
            if r not in levels:
                warns.append(f"{r}: SCOPE §2 chưa có mức R người dùng xác nhận — hỏi, không tự gán")
            elif levels[r] == "R1":
                fams = {TECHNIQUES[x] for t in tcs.values() if r in t["reqs"] for x in techniques(t) if x in TECHNIQUES}
                if len(fams) < 2:
                    warns.append(f"{r}: mức R1 nhưng TC mới thuộc {len(fams)} họ kỹ thuật ({', '.join(sorted(fams)) or 'chưa ghi `Kỹ thuật:`'})"
                                 " — R1 cần ≥ 2 họ")
    for r in (sorted(set(by_req) - set(reqs)) if reqs else []):
        warns.append(f"{r}: TC trỏ tới REQ không có trong {'SCOPE §2' if scope_reqs() else 'ANALYSIS §3'}")

    print(f"TC: {len(tcs)} · REQ đang xét: {len(reqs)} ({'SCOPE' if scope_reqs() else 'ANALYSIS'})")
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
        return ids + extra, "TC Regression: có" + (f" + {len(extra)} TC vùng ảnh hưởng" if extra else ""), bad
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
    if all(re.match(r"TC-", a) for a in args):
        return [a for a in args if a in tcs], "TC chỉ định", [f"{a} không có trong qa/testcases/" for a in args if a not in tcs]
    feats = sorted({v["feature"] for v in tcs.values()})
    ids = [t for t, v in tcs.items() if v["feature"] == args[0]]
    return ids, f"TC của tính năng `{args[0]}`", ([] if ids else [f"không có file qa/testcases/{args[0]}.md — có: {', '.join(feats) or '(trống)'}"])


def waiting_reqs() -> set[str]:
    """REQ ở ANALYSIS §3 còn nhãn chờ (vd REQ rút từ code `(từ code — chờ xác nhận)`, `(chờ trả lời #n)`)."""
    out: set[str] = set()
    for r in table_rows(section(read(QA / "ANALYSIS.md"), "3.")):
        if r and waiting(" ".join(r)):
            out |= set(re.findall(REQ_ID, r[0]))
    return out


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
        ids, how = [], "test khám phá — mỗi phát hiện một dòng EXPLORE-<n> (khuôn _EXPLORE-TEMPLATE.md)"
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
    crit = parse_criteria(read(scope_file()))
    st = scope_status() or "(chưa có)"
    if crit:
        crit_lines = (f"  - Bug mở không được phép: {', '.join(sorted(crit['forbidden'])) or 'không'}\n"
                      f"  - Tỉ lệ PASS tối thiểu: {crit['min_pass']:g}%\n"
                      f"  - Tỉ lệ BLOCKED tối đa: {crit['max_blocked']:g}%\n")
        src = "SCOPE §6" + ("" if st.upper().startswith("CHỐT") else " — SCOPE chưa CHỐT, người dùng xác nhận trước khi chạy")
    else:
        crit_lines = ("  - Bug mở không được phép: \n  - Tỉ lệ PASS tối thiểu: \n  - Tỉ lệ BLOCKED tối đa: \n")
        src = "CHƯA CHỐT — hỏi người dùng rồi điền ba dòng dưới TRƯỚC khi chạy"
        print("⚠ SCOPE §6 chưa có tiêu chí đạt — hỏi người dùng; run không kết luận được khi chưa có", file=sys.stderr)
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
        "`SKIP` (cột cuối trỏ dòng DECISIONS người dùng quyết) · `CHƯA CHẠY`.\n"
        f"> Bằng chứng: `qa/evidence/{run_id}/<TC-ID>/` — phải tồn tại và không rỗng với PASS/FAIL.\n\n"
        "- Bản đang kiểm: \n- Môi trường: \n"
        f"- Bắt đầu: {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"- Phạm vi: {how}\n"
        f"- Scope lúc tạo run: {st}\n"
        f"- Tiêu chí ({src}; không sửa sau khi đã chạy):\n{crit_lines}\n"
        "| TC | Kết quả | Ngày | Bằng chứng | Bug / Lý do |\n|---|---|---|---|---|\n"
        f"{rows}\n\n## Nhật ký\n", encoding="utf-8")
    (QA / "evidence" / run_id).mkdir(parents=True, exist_ok=True)
    print(f"run-id: {run_id}")
    print(f"RUNLOG: {d.relative_to(ROOT)}/RUNLOG.md · {len(ids)} TC ({how})")
    return 0


# ---------------------------------------------------------------- lệnh: run

def evidence_paths(cell: str) -> list[str]:
    links = re.findall(r"\]\(([^)]+)\)", cell)
    rest = re.sub(r"\[[^\]]*\]\([^)]+\)", " ", cell)
    return links + [p for p in re.split(r"[,;\s·]+", rest.replace("`", " ")) if p]


def evidence_ok(cell: str, run_id: str, tid: str) -> tuple[bool, str]:
    paths = evidence_paths(cell)
    if not paths:
        return False, "thiếu đường dẫn bằng chứng"
    own = (QA / "evidence" / run_id / tid).resolve()
    for raw in paths:
        p = Path(raw).expanduser()
        p = (p if p.is_absolute() else ROOT / p).resolve()
        if p != own and own not in p.parents:
            return False, f"`{raw}` không nằm trong qa/evidence/{run_id}/{tid}/ của chính TC này"
        if not p.exists():
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
    u = res.strip().upper()
    if u.startswith("INCONCLUSIVE"):
        return "BLOCKED", "inconclusive " + res.strip()[len("INCONCLUSIVE"):]
    for k in RESULTS:
        if u.startswith(k):
            return k, res.strip()[len(k):].strip(" ()-—:")
    return res, ""


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
        print(f"không thấy {log.relative_to(ROOT)}", file=sys.stderr)
        return 2, {}
    tcs, _ = load_tcs()
    bugs = load_bugs()
    errors: list[str] = []
    counts = {k: 0 for k in RESULTS}
    explore = 0
    run_tcs = []
    for r in table_rows(text):
        r = r + [""] * (5 - len(r))
        tid, res, day, ev, note = r[:5]
        if not re.match(r"(TC-|EXPLORE-)", tid):
            continue
        res_u, extra = result_of(res)
        note = (note + " " + extra).strip()
        if res_u not in RESULTS:
            errors.append(f"{tid}: kết quả `{res}` không hợp lệ (PASS/FAIL/BLOCKED/SKIP/CHƯA CHẠY)")
            continue
        run_tcs.append(tid)
        if tid.startswith("EXPLORE-"):
            explore += 1          # phát hiện khám phá: kiểm bằng chứng nhưng không tính vào tỉ lệ
        else:
            counts[res_u] += 1
            if tid not in tcs:
                errors.append(f"{tid}: không có trong qa/testcases/")
        if res_u in ("PASS", "FAIL"):
            if not re.match(r"\d{4}-\d{2}-\d{2}", day):
                errors.append(f"{tid}: thiếu ngày chạy (YYYY-MM-DD)")
            ok, why = evidence_ok(ev, run_id, tid)
            if not ok:
                errors.append(f"{tid}: {res_u} nhưng {why}")
        if res_u == "FAIL":
            ids = re.findall(r"BUG-\d+", note)
            if not ids:
                errors.append(f"{tid}: FAIL không ghi BUG-…")
            for b in ids:
                if b not in bugs:
                    errors.append(f"{tid}: {b} không có trong BUGS.md")
                elif not bugs[b]["sev"]:
                    errors.append(f"{b}: thiếu Severity S1–S4")
        if res_u in ("BLOCKED", "SKIP") and not note:
            errors.append(f"{tid}: {res_u} không ghi lý do")
    for b in bugs.values():
        if not b["known"]:
            errors.append(f"{b['id']}: trạng thái `{b['status'] or '(trống)'}` lạ — dùng mở/đã sửa/đóng/không sửa/hoãn/trùng (đang coi là còn mở)")

    crit = parse_criteria(text)
    crit_note = ""
    if crit is None and "Tiêu chí (" not in text:
        crit = parse_criteria(read(scope_file()))
        crit_note = " (RUNLOG không có khối tiêu chí — đang dùng SCOPE hiện tại; nên tạo run bằng new-run)"
    total = sum(counts.values())
    base = total - counts["SKIP"]
    pass_rate = 100.0 * counts["PASS"] / base if base else 0.0
    blocked_rate = 100.0 * counts["BLOCKED"] / base if base else 0.0
    related = [b for b in bugs.values() if b["open"] and (b["run"] == run_id or set(b["tc"]) & set(run_tcs))]
    forbidden = [b for b in related if crit and b["sev"] in crit["forbidden"]]

    reasons = []
    if counts["CHƯA CHẠY"] or errors or not (total or explore) or crit is None:
        verdict = "CHƯA KẾT LUẬN"
        if crit is None:
            reasons.append("chưa có tiêu chí đạt được người dùng chốt (SCOPE §6 / khối Tiêu chí trong RUNLOG)")
        if counts["CHƯA CHẠY"]:
            reasons.append(f"{counts['CHƯA CHẠY']} TC chưa chạy")
        if errors:
            reasons.append(f"{len(errors)} lỗi hình thức")
        if not (total or explore):
            reasons.append("RUNLOG không có dòng TC nào")
    else:
        if forbidden:
            reasons.append("còn bug mở mức cấm: " + ", ".join(f"{b['id']} ({b['sev']})" for b in forbidden))
        if pass_rate < crit["min_pass"]:
            reasons.append(f"tỉ lệ PASS {pass_rate:.1f}% < {crit['min_pass']:g}%")
        if blocked_rate > crit["max_blocked"]:
            reasons.append(f"tỉ lệ BLOCKED {blocked_rate:.1f}% > {crit['max_blocked']:g}%")
        verdict = "KHÔNG ĐẠT" if reasons else "ĐẠT"
        if not total and explore:
            verdict = "KHÔNG ĐẠT" if forbidden else "KHÔNG ÁP DỤNG (chỉ khám phá)"

    info = {"run": run_id, "verdict": verdict, "counts": counts, "pass_rate": pass_rate}
    if not quiet:
        print(f"Run {run_id}: {total} dòng · PASS {counts['PASS']} · FAIL {counts['FAIL']} · BLOCKED {counts['BLOCKED']}"
              f" · SKIP {counts['SKIP']} · CHƯA CHẠY {counts['CHƯA CHẠY']} · tỉ lệ PASS {pass_rate:.1f}%"
              + (f" · khám phá {explore}" if explore else ""))
        if crit:
            print(f"Tiêu chí: bug mở cấm {'/'.join(sorted(crit['forbidden'])) or '—'} · PASS ≥ {crit['min_pass']:g}%"
                  f" · BLOCKED ≤ {crit['max_blocked']:g}%{crit_note}")
        else:
            print("Tiêu chí: CHƯA CHỐT — hỏi người dùng")
        for e in errors:
            print(f"  ✗ {e}")
        print(f"KẾT LUẬN: {verdict}" + (f" — {'; '.join(reasons)}" if reasons else ""))
    return (1 if errors else 0), info


# ---------------------------------------------------------------- lệnh: trace

def latest_results() -> dict[str, tuple[str, str]]:
    """TC → (kết quả, run-id) ở run gần nhất có TC đó."""
    out: dict[str, tuple[str, str]] = {}
    for d in run_dirs():
        for r in table_rows(read(d / "RUNLOG.md")):
            if r and re.match(r"TC-", r[0]) and len(r) >= 2:
                out[r[0]] = (result_of(r[1])[0], d.name)
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
        mark = "" if r in reqs else " ⚠ ngoài phạm vi"
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
    print(f"Target: {', '.join(targets()) or '(chưa khai)'}")
    qs = open_questions()
    print(f"Phân tích: {len(analysis_reqs())} REQ · câu hỏi chờ trả lời: {len(qs)}")
    for q in qs[:10]:
        print(f"    ? {q}")
    crit = parse_criteria(read(scope_file()))
    print(f"Scope: {scope_status() or '(chưa có)'} · {len(scope_reqs())} REQ trong phạm vi · "
          f"tiêu chí đạt: {'đã có' if crit else 'CHƯA CHỐT'} · REQ chưa có mức: "
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
        return cmd_tc()
    if cmd == "select":
        return cmd_select(args)
    if cmd == "new-run":
        return cmd_new_run(args)
    if cmd == "run":
        return cmd_run(args)[0]
    if cmd == "trace":
        return cmd_trace(args)
    print(f"lệnh lạ `{cmd}`\n{__doc__}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
