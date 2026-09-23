#!/usr/bin/env python3
"""qa_check.py — kiểm tra nhẹ cho workspace qa/ (Python chuẩn, không phụ thuộc).

    python3 .claude/qa-scripts/qa_check.py status               tình trạng: REQ, câu hỏi chờ, scope, TC, run, bug, bài học
    python3 .claude/qa-scripts/qa_check.py tc                   soát bộ TC (trường bắt buộc, normal+abnormal mỗi REQ, kỳ vọng mơ hồ)
    python3 .claude/qa-scripts/qa_check.py select <phạm vi>     in TC theo: all | smoke | regression | retest BUG-… | <tính năng> | TC-…
    python3 .claude/qa-scripts/qa_check.py new-run <loại> <phạm vi>   tạo qa/runs/<ngày>-<loại>/RUNLOG.md, mọi dòng CHƯA CHẠY
    python3 .claude/qa-scripts/qa_check.py run <run-id>         soát RUNLOG + bằng chứng, tính kết luận theo tiêu chí ghi trước

Không phải cổng chặn — chỉ báo. Exit 0 sạch · 1 có lỗi · 2 sai cách gọi.
"""

from __future__ import annotations

import datetime as dt
import os
import re
import sys
from pathlib import Path


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

RESULTS = {"PASS", "FAIL", "BLOCKED", "SKIP", "CHƯA CHẠY"}
KIEU = {"normal", "abnormal"}
MUC = {"R1", "R2", "R3"}
LOAI = {"chức năng", "biên", "phá-đầu-vào", "phân-quyền", "workflow", "api", "tích-hợp", "tương-thích",
        "hình-thức", "hiệu-năng", "bảo-mật", "khôi-phục", "cross-target", "khám-phá", "smoke"}
REQUIRED = ["REQ", "Target", "Loại", "Kiểu", "Mức", "Nguồn", "Bước", "Kỳ vọng", "Bằng chứng cần"]
VAGUE = ["hoạt động đúng", "hiển thị đúng", "chạy đúng", "hoạt động bình thường", "hợp lý", "như mong đợi",
         "đúng nghiệp vụ", "đúng yêu cầu", "đúng thiết kế", "xử lý đúng"]
TC_ID = r"TC-\w+(?:-\w+)*-\d{3}"
REQ_ID = r"REQ-[\w-]*\w"
OPEN_BUG = {"mở", "đã sửa"}
DEFAULT_CRITERIA = {"forbidden": {"S1", "S2"}, "min_pass": 95.0, "max_blocked": 5.0}


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return ""


def is_template_cell(cell: str) -> bool:
    return not cell or cell.startswith("<!--") or cell.startswith("<")


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
    """Các dòng dữ liệu của bảng markdown (bỏ header + dòng ---), mỗi dòng là list ô đã strip."""
    rows, header_seen = [], False
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            header_seen = False
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
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


# ---------------------------------------------------------------- dữ liệu

def load_tcs() -> tuple[dict[str, dict], list[str]]:
    tcs: dict[str, dict] = {}
    errors: list[str] = []
    d = QA / "testcases"
    for f in sorted(d.glob("*.md")) if d.is_dir() else []:
        if f.name.startswith("_"):
            continue
        text = read(f)
        for m in re.finditer(r"^##\s+(TC-\S*)", text, re.M):
            if not re.fullmatch(TC_ID, m.group(1)):
                errors.append(f"{f.name}: tiêu đề `## {m.group(1)}` sai định dạng ID (TC-<TÍNH-NĂNG>-<3 chữ số>) — TC này không được đếm")
        heads = list(re.finditer(rf"^##\s+({TC_ID})(?!\S)\s*[—-]?\s*(.*)$", text, re.M))
        for i, h in enumerate(heads):
            body = text[h.end(): heads[i + 1].start() if i + 1 < len(heads) else len(text)]
            tid = h.group(1)
            if tid in tcs:
                errors.append(f"{tid}: ID trùng ({tcs[tid]['file']} và {f.name})")
                continue
            tc = {"id": tid, "title": h.group(2).strip(), "file": f.name, "feature": f.stem, "body": body}
            for k in REQUIRED + ["Regression", "Tag", "Ticket"]:
                tc[k] = field(body, k)
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


def scope_reqs() -> list[str]:
    rows = table_rows(section(read(scope_file()), "2."))
    return [r[0] for r in rows if r and re.match(r"REQ-", r[0])]


def scope_status() -> str:
    return field(read(scope_file()), "Trạng thái")


def analysis_reqs() -> list[str]:
    rows = table_rows(section(read(QA / "ANALYSIS.md"), "3."))
    return [r[0] for r in rows if r and re.match(r"REQ-", r[0])]


def open_questions() -> list[str]:
    rows = table_rows(section(read(QA / "ANALYSIS.md"), "5."))
    out = []
    for r in rows:
        if len(r) >= 2 and not is_template_cell(r[1]) and (len(r) < 5 or not r[4]):
            out.append(f"#{r[0]} {r[1]}")
    return out


def targets() -> list[str]:
    rows = table_rows(section(read(QA / "QA.md"), "Target"))
    return [r[0] for r in rows if r and r[0]]


def load_bugs() -> dict[str, dict]:
    text = read(QA / "BUGS.md")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    bugs = {}
    heads = list(re.finditer(r"^##\s+(BUG-\d+)\b\s*[—-]?\s*(.*)$", text, re.M))
    for i, h in enumerate(heads):
        body = text[h.end(): heads[i + 1].start() if i + 1 < len(heads) else len(text)]
        bugs[h.group(1)] = {"id": h.group(1), "title": h.group(2).strip(),
                            "sev": field(body, "Severity").upper()[:2],
                            "status": field(body, "Trạng thái").lower(),
                            "tc": re.findall(TC_ID, field(body, "TC")),
                            "run": field(body, "Run")}
    return bugs


def parse_criteria(text: str) -> dict | None:
    f = field(text, "Bug mở không được phép")
    p = field(text, "Tỉ lệ PASS tối thiểu")
    b = field(text, "Tỉ lệ BLOCKED tối đa")
    if not (f or p or b):
        return None
    num = lambda s, d: float(re.search(r"[\d.]+", s).group()) if re.search(r"[\d.]+", s or "") else d
    forb = set(re.findall(r"S[1-4]", f)) if f else DEFAULT_CRITERIA["forbidden"]
    return {"forbidden": forb, "min_pass": num(p, DEFAULT_CRITERIA["min_pass"]),
            "max_blocked": num(b, DEFAULT_CRITERIA["max_blocked"])}


# ---------------------------------------------------------------- lệnh: tc

def cmd_tc() -> int:
    tcs, errors = load_tcs()
    warns: list[str] = []
    tg = set(targets())
    for t in tcs.values():
        miss = [k for k in REQUIRED if not t[k] and not (k == "Bước" and t["steps"]) and not (k == "Kỳ vọng" and t["expects"])]
        if miss:
            errors.append(f"{t['id']} ({t['file']}): thiếu {', '.join(miss)}")
        if t["Kiểu"] and t["Kiểu"].lower() not in KIEU:
            errors.append(f"{t['id']}: `Kiểu: {t['Kiểu']}` — phải là normal hoặc abnormal")
        if t["Mức"] and t["Mức"].upper() not in MUC:
            errors.append(f"{t['id']}: `Mức: {t['Mức']}` — phải là R1/R2/R3")
        if t["Loại"] and t["Loại"].lower() not in LOAI:
            warns.append(f"{t['id']}: loại `{t['Loại']}` ngoài danh mục qa-targets §2 (được, nếu có chủ đích)")
        if tg and t["Target"] and t["Target"] not in tg:
            warns.append(f"{t['id']}: target `{t['Target']}` không có trong QA.md §Target")
        if "chờ trả lời" in t["body"]:
            warns.append(f"{t['id']}: còn `(chờ trả lời)` — hỏi người dùng trước khi đưa vào run")
        for e in t["expects"]:
            for v in VAGUE:
                if v in e.lower():
                    errors.append(f"{t['id']}: kỳ vọng mơ hồ \"{e[:60]}\" — viết điều quan sát được")
                    break
    reqs = scope_reqs() or analysis_reqs()
    by_req: dict[str, set] = {}
    for t in tcs.values():
        for r in re.findall(REQ_ID, t["REQ"]):
            by_req.setdefault(r, set()).add(t["Kiểu"].lower())
    for r in reqs:
        k = by_req.get(r, set())
        if not k:
            errors.append(f"{r}: chưa có TC nào")
        else:
            for need in ("normal", "abnormal"):
                if need not in k:
                    errors.append(f"{r}: thiếu TC `Kiểu: {need}`")
    orphan = sorted(set(by_req) - set(reqs)) if reqs else []
    for r in orphan:
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

def select(args: list[str]) -> tuple[list[str], str]:
    tcs, _ = load_tcs()
    if not args:
        return [], "thiếu phạm vi"
    mode = args[0].lower()
    if mode == "all":
        reqs = set(scope_reqs())
        ids = [t for t, v in tcs.items() if not reqs or set(re.findall(REQ_ID, v["REQ"])) & reqs]
        return ids, "mọi TC của REQ trong SCOPE" if reqs else "mọi TC (SCOPE chưa có REQ)"
    if mode == "smoke":
        ids = [t for t, v in tcs.items() if "smoke" in v["Tag"].lower()]
        if ids:
            return ids, "TC có Tag: smoke"
        return [t for t, v in tcs.items() if v["Mức"].upper() == "R1" and v["Kiểu"].lower() == "normal"], \
            "chưa TC nào gắn smoke → TC R1 normal"
    if mode in ("regression", "reg"):
        return [t for t, v in tcs.items() if v["Regression"].lower().startswith("có")], "TC Regression: có"
    if mode == "retest":
        bugs = load_bugs()
        ids = []
        for b in args[1:]:
            ids += bugs.get(b.upper(), {}).get("tc", [])
        return sorted(set(ids)), f"TC của {' '.join(args[1:])}"
    if all(re.match(r"TC-", a) for a in args):
        return [a for a in args if a in tcs], "TC chỉ định"
    ids = [t for t, v in tcs.items() if v["feature"] == args[0] or args[0].lower() in v["feature"].lower()]
    return ids, f"TC của tính năng `{args[0]}`"


def cmd_select(args: list[str]) -> int:
    ids, how = select(args)
    tcs, _ = load_tcs()
    waiting = [i for i in ids if "chờ trả lời" in tcs.get(i, {}).get("body", "")]
    if waiting:
        print(f"# bỏ {len(waiting)} TC còn (chờ trả lời): {', '.join(waiting)}", file=sys.stderr)
        ids = [i for i in ids if i not in waiting]
    print(f"# {how}: {len(ids)} TC")
    for i in ids:
        print(i)
    missing = [a for a in args if re.match(r"TC-", a)]
    tcs, _ = load_tcs()
    bad = [a for a in missing if a not in tcs]
    for b in bad:
        print(f"  ✗ {b} không có trong qa/testcases/", file=sys.stderr)
    return 1 if bad or not ids else 0


# ---------------------------------------------------------------- lệnh: new-run

def cmd_new_run(args: list[str]) -> int:
    if len(args) < 1:
        print("cách gọi: new-run <loại> [phạm vi…]  (loại: full, smoke, reg, retest, explore, …)", file=sys.stderr)
        return 2
    kind = re.sub(r"[^a-z0-9-]", "-", args[0].lower())
    rest = args[1:]
    if kind == "explore":
        ids, how = [], "test khám phá — thêm dòng EXPLORE-<n> khi chạy"
    else:
        if kind == "retest":
            sel = ["retest", *rest]
        elif rest:
            sel = rest
        else:
            sel = [kind] if kind in ("smoke", "regression", "reg") else ["all"]
        ids, how = select(sel)
        tcs_all, _ = load_tcs()
        waiting = [i for i in ids if "chờ trả lời" in tcs_all.get(i, {}).get("body", "")]
        if waiting:
            print(f"⚠ bỏ {len(waiting)} TC còn (chờ trả lời): {', '.join(waiting)} — hỏi người dùng rồi thêm vào run", file=sys.stderr)
            ids = [i for i in ids if i not in waiting]
        if not ids:
            print(f"✗ phạm vi `{' '.join(sel)}` không chọn được TC nào — kiểm lại (qa_check.py select …)", file=sys.stderr)
            return 1
    crit = parse_criteria(read(scope_file())) or DEFAULT_CRITERIA
    crit_src = "SCOPE §6" if parse_criteria(read(scope_file())) else "mặc định (SCOPE chưa có tiêu chí)"
    day = dt.date.today().isoformat()
    run_id, n = f"{day}-{kind}", 2
    while (QA / "runs" / run_id).exists():
        run_id, n = f"{day}-{kind}-{n}", n + 1
    d = QA / "runs" / run_id
    d.mkdir(parents=True)
    rows = "\n".join(f"| {i} | CHƯA CHẠY | | | |" for i in ids)
    (d / "RUNLOG.md").write_text(
        f"# RUNLOG — {run_id}\n\n"
        "> Kết quả: `PASS` · `FAIL` (cột cuối ghi BUG-…) · `BLOCKED` (cột cuối ghi lý do/câu hỏi) · `SKIP` (cột cuối ghi dòng DECISIONS) · `CHƯA CHẠY`.\n"
        f"> Bằng chứng: `qa/evidence/{run_id}/<TC-ID>/` — phải tồn tại và không rỗng với PASS/FAIL.\n\n"
        "- Bản đang kiểm: \n- Môi trường: \n"
        f"- Bắt đầu: {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"- Phạm vi: {how}\n"
        f"- Scope lúc tạo run: {scope_status() or '(chưa có)'}\n"
        f"- Tiêu chí (chép từ {crit_src} lúc tạo run — không sửa sau khi đã chạy):\n"
        f"  - Bug mở không được phép: {', '.join(sorted(crit['forbidden'])) or 'không'}\n"
        f"  - Tỉ lệ PASS tối thiểu: {crit['min_pass']:g}%\n"
        f"  - Tỉ lệ BLOCKED tối đa: {crit['max_blocked']:g}%\n\n"
        "| TC | Kết quả | Ngày | Bằng chứng | Bug / Lý do |\n|---|---|---|---|---|\n"
        f"{rows}\n\n## Nhật ký\n", encoding="utf-8")
    (QA / "evidence" / run_id).mkdir(parents=True, exist_ok=True)
    print(f"run-id: {run_id}")
    print(f"RUNLOG: {d.relative_to(ROOT)}/RUNLOG.md · {len(ids)} TC ({how})")
    return 0


# ---------------------------------------------------------------- lệnh: run

def evidence_ok(path: str) -> tuple[bool, str]:
    raw = path.strip("` ")
    if not raw:
        return False, "thiếu đường dẫn bằng chứng"
    p = (ROOT / raw).resolve() if not Path(raw).is_absolute() else Path(raw).resolve()
    ev = (QA / "evidence").resolve()
    if ev != p and ev not in p.parents:
        return False, f"`{raw}` nằm ngoài qa/evidence/"
    if not p.exists():
        return False, f"`{raw}` không tồn tại"
    files = [f for f in (p.rglob("*") if p.is_dir() else [p]) if f.is_file()]
    if not files:
        return False, f"`{raw}` rỗng"
    if all(f.stat().st_size == 0 for f in files):
        return False, f"`{raw}` chỉ có file 0 byte"
    return True, ""


def cmd_run(args: list[str], quiet: bool = False) -> tuple[int, dict]:
    if not args:
        runs = sorted(p.name for p in (QA / "runs").glob("*") if p.is_dir())
        if not runs:
            print("chưa có run nào", file=sys.stderr)
            return 2, {}
        args = [runs[-1]]
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
        if len(r) < 5:
            r = r + [""] * (5 - len(r))
        tid, res, day, ev, note = r[:5]
        if not re.match(r"(TC-|EXPLORE-)", tid):
            continue
        # cho phép chú thích sau kết quả, vd "BLOCKED (chờ trả lời #2)" — phần chú thích tính như lý do
        res_u = next((k for k in sorted(RESULTS, key=len, reverse=True) if res.upper().startswith(k)), res)
        if res_u != res and res_u in RESULTS:
            note = (note + " " + res[len(res_u):]).strip()
        if res_u not in RESULTS:
            errors.append(f"{tid}: kết quả `{res}` không hợp lệ")
            continue
        run_tcs.append(tid)
        if tid.startswith("EXPLORE-"):
            explore += 1          # phát hiện khám phá: kiểm bằng chứng nhưng không tính vào tỉ lệ
        else:
            counts[res_u] += 1
        if tid.startswith("TC-") and tid not in tcs:
            errors.append(f"{tid}: không có trong qa/testcases/")
        if res_u in ("PASS", "FAIL"):
            if not re.match(r"\d{4}-\d{2}-\d{2}", day):
                errors.append(f"{tid}: thiếu ngày chạy (YYYY-MM-DD)")
            ok, why = evidence_ok(ev)
            if not ok:
                errors.append(f"{tid}: {res_u} nhưng {why}")
        if res_u == "FAIL":
            ids = re.findall(r"BUG-\d+", note)
            if not ids:
                errors.append(f"{tid}: FAIL không ghi BUG-…")
            for b in ids:
                if b not in bugs:
                    errors.append(f"{tid}: {b} không có trong BUGS.md")
                elif not bugs[b]["sev"].startswith("S"):
                    errors.append(f"{b}: thiếu Severity")
        if res_u in ("BLOCKED", "SKIP") and not note:
            errors.append(f"{tid}: {res_u} không ghi lý do")

    crit = parse_criteria(text) or parse_criteria(read(scope_file())) or DEFAULT_CRITERIA
    total = sum(counts.values())
    base = total - counts["SKIP"]
    pass_rate = 100.0 * counts["PASS"] / base if base else 0.0
    blocked_rate = 100.0 * counts["BLOCKED"] / base if base else 0.0
    related = [b for b in bugs.values()
               if b["status"] in OPEN_BUG and (b["run"] == run_id or set(b["tc"]) & set(run_tcs))]
    forbidden = [b for b in related if b["sev"] in crit["forbidden"]]

    reasons = []
    if counts["CHƯA CHẠY"] or errors or not (total or explore):
        verdict = "CHƯA KẾT LUẬN"
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

    if not total and explore and verdict != "CHƯA KẾT LUẬN":
        verdict = "KHÔNG ĐẠT" if forbidden else "KHÔNG ÁP DỤNG (chỉ khám phá)"
    info = {"run": run_id, "verdict": verdict, "counts": counts, "pass_rate": pass_rate}
    if not quiet:
        print(f"Run {run_id}: {total} dòng · PASS {counts['PASS']} · FAIL {counts['FAIL']} · BLOCKED {counts['BLOCKED']}"
              f" · SKIP {counts['SKIP']} · CHƯA CHẠY {counts['CHƯA CHẠY']} · tỉ lệ PASS {pass_rate:.1f}%"
              + (f" · khám phá {explore}" if explore else ""))
        print(f"Tiêu chí: bug mở cấm {'/'.join(sorted(crit['forbidden'])) or '—'} · PASS ≥ {crit['min_pass']:g}%"
              f" · BLOCKED ≤ {crit['max_blocked']:g}%")
        for e in errors:
            print(f"  ✗ {e}")
        print(f"KẾT LUẬN: {verdict}" + (f" — {'; '.join(reasons)}" if reasons else ""))
    return (1 if errors else 0), info


# ---------------------------------------------------------------- lệnh: status

def cmd_status() -> int:
    if not (QA / "QA.md").is_file():
        print(f"Chưa có workspace qa/ ở {ROOT} — chạy install.py của bộ qa-agent.")
        return 1
    tcs, _ = load_tcs()
    scope = read(scope_file())
    bugs = load_bugs()
    lessons = [r for r in table_rows(read(QA / "LESSONS.md")) if len(r) >= 5 and r[4].lower() == "mới"]
    print(f"Workspace: {QA}")
    print(f"Quy trình: {field(read(QA / 'QA.md'), 'Quy trình') or '(chưa ghi)'} · "
          f"Việc tiếp theo: {field(read(QA / 'QA.md'), 'Việc tiếp theo') or '(chưa ghi)'}")
    print(f"Target: {', '.join(targets()) or '(chưa khai)'}")
    print(f"Phân tích: {len(analysis_reqs())} REQ · câu hỏi chờ trả lời: {len(open_questions())}")
    for q in open_questions()[:10]:
        print(f"    ? {q}")
    st = field(scope, "Trạng thái") or "(chưa có)"
    print(f"Scope: {st} · {len(scope_reqs())} REQ trong phạm vi")
    kinds = {}
    for t in tcs.values():
        kinds[t["Kiểu"].lower() or "?"] = kinds.get(t["Kiểu"].lower() or "?", 0) + 1
    print(f"Test case: {len(tcs)} ({', '.join(f'{k} {v}' for k, v in sorted(kinds.items())) or '—'})")
    runs = sorted(p.name for p in (QA / "runs").glob("*") if p.is_dir())
    for r in runs[-5:]:
        _, info = cmd_run([r], quiet=True)
        if info:
            c = info["counts"]
            print(f"Run {r}: {info['verdict']} · PASS {c['PASS']} FAIL {c['FAIL']} BLOCKED {c['BLOCKED']} "
                  f"CHƯA CHẠY {c['CHƯA CHẠY']}")
    if not runs:
        print("Run: chưa có")
    ob = [b for b in bugs.values() if b["status"] in OPEN_BUG]
    by = {}
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
    print(f"lệnh lạ `{cmd}`\n{__doc__}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
