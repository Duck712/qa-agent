#!/usr/bin/env python3
"""refcheck.py — kiểm mọi tham chiếu trong bộ qa-agent ĐÃ CÀI vào một dự án có trỏ tới thứ có thật.

    python3 tests/refcheck.py <thư-mục-dự-án-đã-cài>

Quét lệnh, agent, skill và khuôn qa/*.md; kiểm:
  · đường dẫn file (`qa/…`, `.claude/…`, `ky-thuat/…`, `checklists/…`, tên file skill/workspace trần) tồn tại
  · tên skill/agent được gọi (Nạp skill / spawn <tên>) có thật
  · lệnh `/qa…` có thật · lệnh con của qa_check.py có thật
  · tham chiếu mục `<file> §n` tới file có đánh số mục (ANALYSIS, SCOPE, analysis-review, techniques-judgement,
    skill qa, qa-targets, qa-evidence) trỏ tới mục có thật
Exit 0 sạch · 1 có tham chiếu hỏng.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# tên xuất hiện như VÍ DỤ đầu ra lúc chạy — không phải file của bộ công cụ
RUNTIME = {"qa/TRACE.md", "TRACE.md", "qa/.env", "qa/API-SURFACE.md", "cham.md", "ghi-chu.md", "out.json", "RUNLOG.md",
           "REPORT.md", "SKILL.md", "qa/testcases/phan-quyen.md", "qa/evidence/_inbox/tester/"}
WORKSPACE = {"QA.md", "ANALYSIS.md", "SCOPE.md", "BUGS.md", "DECISIONS.md", "LESSONS.md", "TRACE.md"}
SCRIPTS = {"qa_check.py", "pairwise.py", "gen_matrix_tc.py", "guard_evidence.py", "guard_readonly.py"}
QA_CHECK_CMDS = {"status", "tc", "select", "new-run", "run", "trace"}


def sections(path: Path) -> set[str]:
    return set(re.findall(r"^##\s+(\d+[a-z]?)\.", path.read_text(encoding="utf-8"), re.M)) if path.exists() else set()


def main() -> int:
    proj = Path(sys.argv[1]).resolve()
    cl = proj / ".claude"
    skills = cl / "skills"
    skill_names = {p.name for p in skills.iterdir() if p.is_dir()}
    agent_names = {p.stem for p in (cl / "agents").glob("*.md")}
    cmd_names = {p.stem for p in (cl / "commands").glob("*.md")}
    sec_files = {
        "ANALYSIS": proj / "qa/ANALYSIS.md", "SCOPE": proj / "qa/SCOPE.md",
        "analysis-review": skills / "qa-knowledge/analysis-review.md",
        "techniques-judgement": skills / "qa-knowledge/techniques-judgement.md",
        "skill `qa`": skills / "qa/SKILL.md", "qa-targets": skills / "qa-targets/SKILL.md",
        "qa-evidence": skills / "qa-evidence/SKILL.md",
        "qa-testcase-design": skills / "qa-testcase-design/SKILL.md",
        **{f.stem + ".md": f for f in (skills / "qa-testcase-design/ky-thuat").glob("*.md")},
    }
    sec_of = {k: sections(v) for k, v in sec_files.items()}
    files = [*(cl / "commands").glob("*.md"), *(cl / "agents").glob("*.md"), *skills.rglob("*.md"),
             *[p for p in (proj / "qa").glob("*.md")], *(proj / "qa/runs").glob("_*.md"), *(proj / "qa/testcases").glob("_*.md")]
    bad: list[str] = []

    def exists(part: str, here: Path) -> bool:
        if part in RUNTIME:
            return True
        name = part.rstrip("/")
        cands = [proj / name, here.parent / name, skills / name, *[skills / s / name for s in skill_names]]
        if name in WORKSPACE:
            cands.append(proj / "qa" / name)
        if name in SCRIPTS:
            cands.append(cl / "qa-scripts" / name)
        if name.startswith(("ky-thuat/",)):
            cands.append(skills / "qa-testcase-design" / name)
        if name.startswith(("_EXPLORE", "_RUNLOG", "_REPORT")):
            cands.append(proj / "qa/runs" / name)
        return any(c.exists() for c in cands)

    for f in files:
        rel = f.relative_to(proj)
        text = f.read_text(encoding="utf-8")
        for m in re.finditer(r"`([^`\n]+)`", text):
            for part in m.group(1).split():
                part = part.strip("(),;:'\"")
                if re.search(r"[<>*{}$…]", part) or part.startswith(("http", "-", "/", "~")):
                    continue
                looks_path = re.search(r"\.(md|py|json)/?$", part) or part.startswith(("qa/", ".claude/", "ky-thuat/", "checklists/"))
                if not looks_path or part.startswith("kit/"):
                    continue
                if re.match(r"qa/(evidence|runs|sandbox|automation|scripts)/(?!_)", part) or part.endswith((".py",)) and part not in SCRIPTS and not part.startswith(".claude/"):
                    continue   # đường dẫn sinh lúc chạy / script mẫu của người dùng
                if not exists(part, f):
                    bad.append(f"{rel}: file `{part}` không tồn tại")
        # tham chiếu trần sang skill khác: agent đang ở skill/lệnh khác sẽ tìm sai thư mục
        owner = {"ky-thuat/": "qa-testcase-design", "analysis-review.md": "qa-knowledge",
                 "techniques-judgement": "qa-knowledge", "bug-patterns.md": "qa-knowledge", "checklists/": "qa-knowledge"}
        for m in re.finditer(r"`(ky-thuat/|analysis-review\.md|techniques-judgement|bug-patterns\.md|checklists/)", text):
            if owner[m.group(1)] not in f.parts:
                bad.append(f"{rel}: `{m.group(1)}…` thiếu tên skill phía trước (`{owner[m.group(1)]}/{m.group(1)}…`)")
        for m in re.finditer(r"(?:skill|agent|spawn|Nạp)\s+`(qa[a-z-]*)`", text):
            if m.group(1) not in skill_names | agent_names:
                bad.append(f"{rel}: skill/agent `{m.group(1)}` không tồn tại")
        for m in re.finditer(r"`/(qa[a-z-]*)", text):
            if m.group(1) not in cmd_names:
                bad.append(f"{rel}: lệnh `/{m.group(1)}` không tồn tại")
        for m in re.finditer(r"qa_check\.py\s+([a-z-]+)", text):
            if m.group(1) not in QA_CHECK_CMDS:
                bad.append(f"{rel}: `qa_check.py {m.group(1)}` không có lệnh con này")
        for key, secs in sec_of.items():
            pat = re.escape(key) + (r"`?" if key.endswith(".md") else r"(?:\.md)?`?") + r"\s*§\s*(\d+[a-z]?)(?:\s*[–-]\s*§?(\d+))?"
            for m in re.finditer(pat, text):
                for n in filter(None, m.groups()):
                    if n not in secs:
                        have = ", ".join(sorted(secs, key=lambda x: int(re.sub(r"\D", "", x) or 0)))
                        bad.append(f"{rel}: `{key} §{n}` — mục không tồn tại (có: {have})")
    for b in sorted(set(bad)):
        print(f"  ✗ {b}")
    print(f"refcheck: quét {len(files)} file · {len(set(bad))} tham chiếu hỏng")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
