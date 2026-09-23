#!/usr/bin/env python3
"""selftest.py — cài qa-agent vào một dự án nháp và kiểm từng mảnh. Chạy sau mỗi lần sửa kit/ hoặc install.py.

    python3 tests/selftest.py          # vài giây
    python3 tests/selftest.py --keep   # giữ thư mục nháp để soi
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OK, BAD = 0, 0


def check(cond: bool, msg: str, detail: str = "") -> None:
    global OK, BAD
    if cond:
        OK += 1
        print(f"  ✓ {msg}")
    else:
        BAD += 1
        print(f"  ✗ {msg}" + (f"\n      {detail[:600]}" if detail else ""))


def run(args: list[str], cwd: Path, env: dict | None = None, stdin: str | None = None) -> subprocess.CompletedProcess:
    e = dict(os.environ)
    e.pop("CLAUDE_PROJECT_DIR", None)
    if env:
        e.update(env)
    return subprocess.run(args, cwd=cwd, env=e, input=stdin, text=True, capture_output=True)


def hook(proj: Path, script: str, tool: str, ti: dict, cwd: Path | None = None) -> int:
    r = run([sys.executable, str(proj / ".claude/qa-scripts" / script)], cwd or proj,
            {"CLAUDE_PROJECT_DIR": str(proj)}, json.dumps({"tool_name": tool, "tool_input": ti}))
    return r.returncode


def qa(proj: Path, *args: str) -> subprocess.CompletedProcess:
    return run([sys.executable, ".claude/qa-scripts/qa_check.py", *args], proj, {"CLAUDE_PROJECT_DIR": str(proj)})


def main() -> int:
    keep = "--keep" in sys.argv
    tmp = Path(tempfile.mkdtemp(prefix="qa-agent-selftest-"))
    proj = tmp / "san-pham"
    (proj / ".claude").mkdir(parents=True)
    (proj / "src").mkdir()
    (proj / "src" / "app.js").write_text("console.log(1)\n")
    (proj / ".claude" / "settings.json").write_text(json.dumps({
        "permissions": {"allow": ["Bash(npm test:*)"]},
        "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "echo dev-hook"}]}]},
    }))
    (proj / ".mcp.json").write_text(json.dumps({"mcpServers": {"db": {"command": "db-mcp"}}}))

    print("[1] cài lần đầu")
    r = run([sys.executable, str(REPO / "install.py"), str(proj), "--name", "Sản phẩm thử"], tmp)
    check(r.returncode == 0, "install.py chạy xong", r.stderr + r.stdout)
    for p in ["qa/QA.md", "qa/SCOPE.md", "qa/LESSONS.md", "qa/testcases/_TEMPLATE.md", ".claude/agents/qa-tester.md",
              ".claude/commands/qa.md", ".claude/skills/qa/SKILL.md", ".claude/skills/qa-targets/ai.md",
              ".claude/qa-scripts/qa_check.py", ".claude/qa-agent.json", "qa/evidence/_inbox"]:
        check((proj / p).exists(), f"có {p}")
    check("Sản phẩm thử" in (proj / "qa/QA.md").read_text(), "thay tên sản phẩm vào QA.md")
    leftovers = [str(p) for p in (proj / ".claude").rglob("*.md") if "{{" in p.read_text()]
    check(not leftovers, "không còn placeholder {{…}} trong .claude/", ", ".join(leftovers))
    st = json.loads((proj / ".claude/settings.json").read_text())
    check("Bash(npm test:*)" in st["permissions"]["allow"] and "mcp__browser" in st["permissions"]["allow"],
          "settings.json: giữ quyền cũ + thêm quyền qa")
    cmds = json.dumps(st["hooks"])
    check("dev-hook" in cmds and "guard_evidence.py" in cmds and "guard_readonly.py" in cmds,
          "settings.json: giữ hook cũ + thêm 2 hook qa")
    mcp = json.loads((proj / ".mcp.json").read_text())
    args = mcp["mcpServers"]["browser"]["args"]
    od = args[args.index("--output-dir") + 1]
    check("db" in mcp["mcpServers"], ".mcp.json: giữ server cũ của dự án")
    check(Path(od).is_absolute() and od.startswith(str(proj / "qa/evidence/_inbox")),
          ".mcp.json: --output-dir tuyệt đối trong qa/evidence/_inbox", od)
    check(not any("@latest" in a for a in args), ".mcp.json: version MCP khoá cứng, không @latest")
    agent = (proj / ".claude/agents/qa-tester.md").read_text()
    check(str(proj / "qa/evidence/_inbox/tester") in agent and "@latest" not in agent,
          "qa-tester: output-dir tuyệt đối + version khoá")

    print("\n[2] cài lại / cập nhật")
    r = run([sys.executable, str(REPO / "install.py"), str(proj)], tmp)
    check(r.returncode == 1, "cài lại không có --update → từ chối")
    (proj / "qa/QA.md").write_text((proj / "qa/QA.md").read_text() + "\n<!-- dữ liệu của QA -->\n")
    edited = proj / ".claude/skills/qa-knowledge/bug-patterns.md"
    edited.write_text(edited.read_text() + "\n99. dòng dự án tự thêm\n")
    r = run([sys.executable, str(REPO / "install.py"), str(proj), "--update"], tmp)
    check(r.returncode == 0, "--update chạy xong", r.stderr + r.stdout)
    check("dữ liệu của QA" in (proj / "qa/QA.md").read_text(), "--update không ghi đè dữ liệu qa/")
    check("dòng dự án tự thêm" in edited.read_text() and "đã sửa tay" in r.stdout,
          "--update giữ file người dùng đã sửa tay và báo ra", r.stdout)
    st2 = json.loads((proj / ".claude/settings.json").read_text())
    n_hooks = sum(1 for e in st2["hooks"]["PreToolUse"] for h in e["hooks"] if "guard_" in json.dumps(h))
    check(n_hooks == 2, "--update không nhân đôi hook", str(n_hooks))

    print("\n[3] guard_evidence")
    ev = proj / "qa/evidence/r1/TC-A-001/01.png"
    check(hook(proj, "guard_evidence.py", "mcp__browser__browser_take_screenshot", {"filename": "/tmp/x.png"}) == 2,
          "chặn screenshot ra /tmp")
    check(hook(proj, "guard_evidence.py", "mcp__browser__browser_take_screenshot", {}) == 0,
          "cho screenshot không khai filename (dùng output-dir)")
    check(hook(proj, "guard_evidence.py", "mcp__browser__browser_take_screenshot", {"filename": str(ev)}) == 0,
          "cho đường dẫn tuyệt đối trong qa/evidence/")
    check(hook(proj, "guard_evidence.py", "mcp__browser__browser_take_screenshot", {"filename": "../../x.png"}) == 2,
          "chặn đường dẫn tương đối có ..")
    check(hook(proj, "guard_evidence.py", "mcp__mobile__mobile_start_screen_recording", {}) == 2,
          "chặn quay màn hình không khai output")
    check(hook(proj, "guard_evidence.py", "Bash", {"command": "cp qa/evidence/a.png ~/Desktop/a.png"}) == 2,
          "chặn Bash chép ảnh ra ngoài")
    check(hook(proj, "guard_evidence.py", "Bash", {"command": "mv qa/evidence/_inbox/tester/a.png qa/evidence/r1/TC-A-001/"}) == 0,
          "cho Bash chuyển ảnh trong qa/evidence")

    print("\n[4] guard_readonly")
    qa_md = proj / "qa/QA.md"
    qa_md.write_text(qa_md.read_text().replace("- Chỉ đọc: ", "- Chỉ đọc: src"))
    check(hook(proj, "guard_readonly.py", "Edit", {"file_path": str(proj / "src/app.js")}) == 2, "chặn Edit vào src/")
    check(hook(proj, "guard_readonly.py", "Write", {"file_path": str(proj / "qa/testcases/a.md")}) == 0, "cho ghi qa/")
    check(hook(proj, "guard_readonly.py", "Bash", {"command": "echo x >> src/app.js"}) == 2, "chặn Bash append vào src/")
    check(hook(proj, "guard_readonly.py", "Bash", {"command": "sed -i '' s/1/2/ src/app.js"}) == 2, "chặn sed -i vào src/")
    check(hook(proj, "guard_readonly.py", "Bash", {"command": "cp src/app.js qa/sandbox/"}) == 0, "cho cp LẤY từ src/")
    check(hook(proj, "guard_readonly.py", "Bash", {"command": "cat src/app.js | grep log"}) == 0, "cho đọc thuần")
    check(hook(proj, "guard_readonly.py", "Bash", {"command": "cd src && rm app.js"}) == 2, "chặn cd src && rm")

    print("\n[5] qa_check tc")
    scope = proj / "qa/SCOPE.md"
    scope.write_text(scope.read_text().replace("| | | | | |\n\n## 3.", "| REQ-DK-1 | Đăng ký | web | R1 | chức năng |\n\n## 3.", 1))
    tcf = proj / "qa/testcases/dang-ky.md"
    tc1 = """## TC-DK-001 — Đăng ký bằng email hợp lệ
- REQ: REQ-DK-1
- Target: web
- Loại: chức năng
- Kiểu: normal
- Mức: R1
- Nguồn: REQ-DK-1
- Tag: smoke
- Regression: có
- Bước:
  1. Mở trang đăng ký, nhập QA-x@example.test
  2. Bấm Đăng ký
- Kỳ vọng:
  1. Ô email nhận giá trị
  2. Hiện "Kiểm tra hộp thư", tài khoản ở trạng thái chờ kích hoạt
- Bằng chứng cần: ảnh bước 2 + Page URL
"""
    tcf.write_text("# TC — Đăng ký\n\n" + tc1)
    r = qa(proj, "tc")
    check(r.returncode == 1 and "REQ-DK-1: thiếu TC `Kiểu: abnormal`" in r.stdout, "bắt REQ thiếu ca abnormal", r.stdout)
    tc2 = tc1.replace("TC-DK-001 — Đăng ký bằng email hợp lệ", "TC-DK-002 — Email sai định dạng bị từ chối") \
             .replace("Kiểu: normal", "Kiểu: abnormal").replace("- Tag: smoke\n", "") \
             .replace('Hiện "Kiểm tra hộp thư", tài khoản ở trạng thái chờ kích hoạt', "Hệ thống hoạt động đúng")
    tcf.write_text(tcf.read_text() + "\n" + tc2)
    r = qa(proj, "tc")
    check(r.returncode == 1 and "kỳ vọng mơ hồ" in r.stdout, "bắt kỳ vọng mơ hồ", r.stdout)
    tcf.write_text(tcf.read_text().replace("Hệ thống hoạt động đúng", 'Hiện lỗi "Email không hợp lệ", không tạo tài khoản'))
    r = qa(proj, "tc")
    check(r.returncode == 0 and "bộ TC sạch" in r.stdout, "bộ TC sạch khi đủ normal + abnormal", r.stdout)
    r = qa(proj, "select", "smoke")
    check("TC-DK-001" in r.stdout and "TC-DK-002" not in r.stdout, "select smoke theo Tag", r.stdout)

    print("\n[6] qa_check new-run + run")
    r = qa(proj, "new-run", "full", "all")
    run_id = r.stdout.split("run-id: ")[1].split()[0] if "run-id: " in r.stdout else ""
    check(r.returncode == 0 and run_id, "new-run tạo run", r.stdout + r.stderr)
    log = proj / "qa/runs" / run_id / "RUNLOG.md"
    r = qa(proj, "run", run_id)
    check("CHƯA KẾT LUẬN" in r.stdout, "TC chưa chạy → CHƯA KẾT LUẬN", r.stdout)
    t = log.read_text()
    t = t.replace("| TC-DK-001 | CHƯA CHẠY | | | |", f"| TC-DK-001 | PASS | 2026-09-23 | qa/evidence/{run_id}/TC-DK-001/ | |")
    t = t.replace("| TC-DK-002 | CHƯA CHẠY | | | |", f"| TC-DK-002 | PASS | 2026-09-23 | qa/evidence/{run_id}/TC-DK-002/ | |")
    log.write_text(t)
    r = qa(proj, "run", run_id)
    check(r.returncode == 1 and "không tồn tại" in r.stdout, "PASS không có bằng chứng → lỗi", r.stdout)
    for tid in ("TC-DK-001", "TC-DK-002"):
        d = proj / "qa/evidence" / run_id / tid
        d.mkdir(parents=True, exist_ok=True)
        (d / "01.txt").write_text("Page URL: https://staging.example.test/dang-ky\n")
    r = qa(proj, "run", run_id)
    check(r.returncode == 0 and "KẾT LUẬN: ĐẠT" in r.stdout, "đủ bằng chứng, 100% PASS → ĐẠT", r.stdout)
    log.write_text(log.read_text().replace(f"| TC-DK-002 | PASS | 2026-09-23 | qa/evidence/{run_id}/TC-DK-002/ | |",
                                           f"| TC-DK-002 | FAIL | 2026-09-23 | qa/evidence/{run_id}/TC-DK-002/ | BUG-001 |"))
    r = qa(proj, "run", run_id)
    check(r.returncode == 1 and "BUG-001 không có trong BUGS.md" in r.stdout, "FAIL trỏ bug không tồn tại → lỗi", r.stdout)
    bugs = proj / "qa/BUGS.md"
    bugs.write_text(bugs.read_text() + f"""
## BUG-001 — Email sai định dạng vẫn tạo được tài khoản
- Severity: S2
- Trạng thái: mở
- TC: TC-DK-002
- Run: {run_id}
""")
    r = qa(proj, "run", run_id)
    check("KẾT LUẬN: KHÔNG ĐẠT" in r.stdout and "BUG-001 (S2)" in r.stdout, "bug S2 mở → KHÔNG ĐẠT", r.stdout)
    r = qa(proj, "status")
    check(r.returncode == 0 and "Bug mở: 1" in r.stdout and "Test case: 2" in r.stdout, "status tóm tắt đúng", r.stdout)

    print("\n[7] gen_matrix_tc")
    m = proj / "qa/ANALYSIS.md"
    m.write_text(m.read_text() + "\n| Hành động | owner | member | khách |\n|---|---|---|---|\n| Sửa đơn | ✓ | ✗ | ✗ |\n| Xem đơn | ✓ | ✓ | ✗ |\n")
    out = proj / "qa/testcases/phan-quyen.md"
    g = [sys.executable, ".claude/qa-scripts/gen_matrix_tc.py", "qa/ANALYSIS.md", "--feature", "QUYEN",
         "--target", "web", "--req", "REQ-DK-1", "--out", str(out)]
    r = run(g, proj)
    check(r.returncode == 0 and out.read_text().count("## TC-QUYEN-") == 3, "sinh 1 TC mỗi ô ✗ (3 ô)", r.stdout + r.stderr)
    r = run(g, proj)
    check(out.read_text().count("## TC-QUYEN-") == 3 and "bỏ qua 3" in r.stdout, "chạy lại không sinh trùng", r.stdout)

    print("\n[8] các ca đã từng hỏng (review v3)")
    tcf.write_text(tcf.read_text() + "\n## TC-ĐK-9 — ID sai định dạng\n- REQ: REQ-DK-1\n")
    r = qa(proj, "tc")
    check("sai định dạng ID" in r.stdout, "tiêu đề TC sai định dạng bị báo, không lặng lẽ bỏ qua", r.stdout)
    tcf.write_text(tcf.read_text().replace("\n## TC-ĐK-9 — ID sai định dạng\n- REQ: REQ-DK-1\n", ""))
    viet = tc1.replace("TC-DK-001", "TC-ĐĂNGKÝ-001").replace("Ô email nhận giá trị", "Console không có lỗi JS")
    (proj / "qa/testcases/tieng-viet.md").write_text(viet)
    r = qa(proj, "tc")
    sel = qa(proj, "select", "TC-ĐĂNGKÝ-001")
    check("TC-ĐĂNGKÝ-001" in sel.stdout and "mơ hồ" not in r.stdout,
          "ID có chữ tiếng Việt được đếm; 'không có lỗi JS' không bị coi là mơ hồ", r.stdout + sel.stdout)
    (proj / "qa/testcases/tieng-viet.md").unlink()
    r = qa(proj, "new-run", "retest", "BUG-001")
    rid = r.stdout.split("run-id: ")[1].split()[0] if "run-id: " in r.stdout else ""
    rl = (proj / "qa/runs" / rid / "RUNLOG.md").read_text() if rid else ""
    check("| TC-DK-002 | CHƯA CHẠY" in rl and "TC-DK-001" not in rl, "new-run retest BUG-… chọn đúng TC của bug", r.stdout + r.stderr)
    check("Tỉ lệ PASS tối thiểu: 95%" in rl, "new-run chép tiêu chí đạt vào RUNLOG (đóng băng)", rl[:400])
    sc = scope.read_text()
    scope.write_text(sc.replace("Tỉ lệ PASS tối thiểu: 95%", "Tỉ lệ PASS tối thiểu: 10%"))
    (proj / "qa/runs" / rid / "RUNLOG.md").write_text(rl.replace("| TC-DK-002 | CHƯA CHẠY | | | |",
        f"| TC-DK-002 | BLOCKED | | | thiếu tài khoản |"))
    r = qa(proj, "run", rid)
    check("PASS ≥ 95%" in r.stdout, "sửa SCOPE sau khi tạo run không đổi tiêu chí của run", r.stdout)
    scope.write_text(sc)
    r = qa(proj, "new-run", "full", "khong-ton-tai")
    check(r.returncode == 1, "new-run với phạm vi không chọn được TC → báo lỗi, không tạo run rỗng", r.stdout + r.stderr)
    check(hook(proj, "guard_evidence.py", "Bash", {"command": "cp ~/Pictures/mau.png qa/sandbox/upload.png"}) == 0,
          "cho chép ảnh mẫu vào qa/sandbox (test upload)")
    check(hook(proj, "guard_readonly.py", "Bash", {"command": "git -C src commit -am x"}) == 2, "chặn git -C src commit")
    check(hook(proj, "guard_readonly.py", "Bash", {"command": "git -C src log --oneline"}) == 0, "cho git -C src log (đọc)")
    agent = (proj / ".claude/agents/qa-tester.md").read_text()
    check("mobile-mcp" not in agent, "qa-tester không tự khai server mobile riêng (tôn trọng cấu hình máy)")
    check('"--browser","chromium"' in agent, "qa-tester dùng chromium như phiên chính")
    tpl = (proj / "qa/testcases/_TEMPLATE.md").read_text()
    check("- Tag: \n" in tpl and "- Regression: không" in tpl, "khuôn TC không mặc định smoke/regression")

    r = qa(proj, "status")
    check("Quy trình: (chưa ghi)" in r.stdout, "trường để trống không bị đọc trượt sang dòng sau", r.stdout)
    wait = tc1.replace("TC-DK-001", "TC-DK-050").replace("- Tag: smoke\n", "").replace(
        'Hiện "Kiểm tra hộp thư", tài khoản ở trạng thái chờ kích hoạt', "(chờ trả lời #3)")
    tcf.write_text(tcf.read_text() + "\n" + wait)
    r = qa(proj, "new-run", "full", "all")
    rid2 = r.stdout.split("run-id: ")[1].split()[0] if "run-id: " in r.stdout else ""
    rl2 = (proj / "qa/runs" / rid2 / "RUNLOG.md").read_text() if rid2 else ""
    check("TC-DK-050" not in rl2 and "chờ trả lời" in r.stderr, "TC còn (chờ trả lời) không được đưa vào run", r.stdout + r.stderr)

    rl3 = (proj / "qa/runs" / rid / "RUNLOG.md").read_text().replace("| TC-DK-002 | BLOCKED | | | thiếu tài khoản |",
                                                                     "| TC-DK-002 | BLOCKED (chờ trả lời #2) | | | |")
    (proj / "qa/runs" / rid / "RUNLOG.md").write_text(rl3)
    r = qa(proj, "run", rid)
    check("không hợp lệ" not in r.stdout and "không ghi lý do" not in r.stdout,
          "kết quả có chú thích `BLOCKED (chờ trả lời #2)` được hiểu đúng", r.stdout)

    print("\n[9] kỹ thuật: pairwise · trace · R1 ≥ 2 kỹ thuật")
    import itertools
    pw = run([sys.executable, ".claude/qa-scripts/pairwise.py", "B=Chrome,Firefox,Safari,Edge", "OS=Windows,macOS,Linux",
              "Vai=admin,member,guest", "L=vi,en", "--khong", "Safari&Windows", "--khong", "Safari&Linux"], proj)
    rows = [l.strip("|").split("|")[1:] for l in pw.stdout.splitlines() if l.startswith("| ") and not l.startswith("| #")]
    rows = [[c.strip() for c in r] for r in rows]
    vals = [["Chrome", "Firefox", "Safari", "Edge"], ["Windows", "macOS", "Linux"], ["admin", "member", "guest"], ["vi", "en"]]
    need = {(i, a, j, b) for i, j in itertools.combinations(range(4), 2) for a in vals[i] for b in vals[j]
            if not ({a, b} in ({"Safari", "Windows"}, {"Safari", "Linux"}))}
    got = {(i, r[i], j, r[j]) for r in rows for i, j in itertools.combinations(range(4), 2)}
    check(pw.returncode == 0 and need <= got, "pairwise phủ mọi cặp hợp lệ", pw.stdout + pw.stderr)
    check(not any(r[0] == "Safari" and r[1] in ("Windows", "Linux") for r in rows), "pairwise tôn trọng ràng buộc --khong")
    check(0 < len(rows) < 30, f"pairwise gọn hơn tích đầy đủ ({len(rows)} dòng < 60)")
    full = run([sys.executable, ".claude/qa-scripts/pairwise.py", "A=1,2", "B=x,y", "--khong", "2&y", "--tat-ca"], proj)
    check("Tích đầy đủ: 3 dòng" in full.stdout, "pairwise --tat-ca bỏ tổ hợp cấm", full.stdout)
    r = qa(proj, "trace", "--write")
    check((proj / "qa/TRACE.md").exists() and "| REQ-DK-1 |" in r.stdout and "TC-DK-001" in r.stdout,
          "trace --write sinh ma trận truy vết", r.stdout)
    r = qa(proj, "tc")
    check("REQ-DK-1: mức R1 nhưng TC mới dùng" in r.stdout, "cảnh báo REQ R1 dùng < 2 kỹ thuật", r.stdout)
    t = tcf.read_text().replace("- Mức: R1\n- Nguồn: REQ-DK-1", "- Mức: R1\n- Kỹ thuật: phân vùng, giá trị biên\n- Nguồn: REQ-DK-1", 1)
    tcf.write_text(t)
    r = qa(proj, "tc")
    check("REQ-DK-1: mức R1 nhưng" not in r.stdout, "hết cảnh báo khi R1 có ≥ 2 kỹ thuật", r.stdout)
    for f in ["ky-thuat/use-case.md", "ky-thuat/to-hop.md", "ky-thuat/oracle.md", "ky-thuat/review-tc.md", "ky-thuat/hop-trang.md"]:
        check((proj / ".claude/skills/qa-testcase-design" / f).exists(), f"cài kèm {f}")
    check((proj / ".claude/skills/qa-knowledge/analysis-review.md").exists() and (proj / "qa/runs/_EXPLORE-TEMPLATE.md").exists(),
          "cài kèm analysis-review.md + khuôn phiên khám phá")

    print(f"\n{'=' * 50}\n  {OK} ✓ · {BAD} ✗")
    if keep:
        print(f"  giữ thư mục nháp: {tmp}")
    else:
        shutil.rmtree(tmp, ignore_errors=True)
    return 1 if BAD else 0


if __name__ == "__main__":
    sys.exit(main())
