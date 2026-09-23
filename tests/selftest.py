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
    check(Path(od).is_absolute() and od.startswith((proj.resolve() / "qa/evidence/_inbox").as_posix()),
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
    check(r.returncode == 1 and "kỳ vọng có từ mơ hồ" in r.stdout, "bắt kỳ vọng mơ hồ", r.stdout)
    tcf.write_text(tcf.read_text().replace("Hệ thống hoạt động đúng", 'Hiện lỗi "Email không hợp lệ", không tạo tài khoản'))
    r = qa(proj, "tc")
    check(r.returncode == 0 and "bộ TC sạch" in r.stdout, "bộ TC sạch khi đủ normal + abnormal", r.stdout)
    r = qa(proj, "select", "smoke")
    check("TC-DK-001" in r.stdout and "TC-DK-002" not in r.stdout, "select smoke theo Tag", r.stdout)

    print("\n[6] qa_check new-run + run")
    r = qa(proj, "new-run", "full", "all")
    rid0 = r.stdout.split("run-id: ")[1].split()[0] if "run-id: " in r.stdout else ""
    r0 = qa(proj, "run", rid0)
    check("chưa có tiêu chí đạt được người dùng chốt" in r0.stdout and "CHƯA KẾT LUẬN" in r0.stdout,
          "SCOPE chưa chốt tiêu chí → run không kết luận (không có con số mặc định)", r0.stdout)
    check("chưa có tiêu chí" in r.stderr, "new-run cảnh báo tiêu chí chưa chốt", r.stderr)
    shutil.rmtree(proj / "qa/runs" / rid0)
    scope.write_text(scope.read_text().replace("- Bug mở không được phép: \n", "- Bug mở không được phép: S1, S2\n")
                     .replace("- Tỉ lệ PASS tối thiểu: \n", "- Tỉ lệ PASS tối thiểu: 95%\n")
                     .replace("- Tỉ lệ BLOCKED tối đa: \n", "- Tỉ lệ BLOCKED tối đa: 5%\n")
                     .replace("- Trạng thái: NHÁP", "- Trạng thái: CHỐT"))
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
         "--target", "web", "--req", "REQ-DK-1", "--muc", "R1", "--out", str(out)]
    r = run(g, proj)
    check(r.returncode == 0 and out.read_text().count("## TC-QUYEN-") == 3, "sinh 1 TC mỗi ô ✗ (3 ô)", r.stdout + r.stderr)
    r = run(g, proj)
    check(out.read_text().count("## TC-QUYEN-") == 3 and "bỏ qua 3" in r.stdout, "chạy lại không sinh trùng", r.stdout)

    print("\n[8] các ca đã từng hỏng (review v3)")
    tcf.write_text(tcf.read_text() + "\n## TC-ĐK-9 — ID sai định dạng\n- REQ: REQ-DK-1\n")
    r = qa(proj, "tc")
    check("không đúng khuôn" in r.stdout, "tiêu đề TC sai định dạng bị báo, không lặng lẽ bỏ qua", r.stdout)
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
    check("REQ-DK-1: mức R1 nhưng TC mới thuộc" in r.stdout, "cảnh báo REQ R1 chưa đủ 2 họ kỹ thuật", r.stdout)
    t = tcf.read_text().replace("- Mức: R1\n- Nguồn: REQ-DK-1", "- Mức: R1\n- Kỹ thuật: phân vùng, giá trị biên\n- Nguồn: REQ-DK-1", 1)
    tcf.write_text(t)
    r = qa(proj, "tc")
    pq = proj / "qa/testcases/phan-quyen.md"; pq_txt = pq.read_text(); pq.unlink()   # TC phân quyền (họ logic) tạm tách ra
    r = qa(proj, "tc")
    check("REQ-DK-1: mức R1 nhưng TC mới thuộc 1 họ" in r.stdout, "phân vùng + giá trị biên cùng một họ → R1 vẫn chưa đủ", r.stdout)
    pq.write_text(pq_txt)
    tcf.write_text(t.replace("- Kỹ thuật: phân vùng, giá trị biên", "- Kỹ thuật: giá trị biên, chuyển trạng thái", 1))
    r = qa(proj, "tc")
    check("REQ-DK-1: mức R1 nhưng" not in r.stdout, "hết cảnh báo khi R1 có kỹ thuật thuộc ≥ 2 họ", r.stdout)
    tcf.write_text(tcf.read_text().replace("- Kỹ thuật: giá trị biên, chuyển trạng thái", "- Kỹ thuật: gia tri bien", 1))
    r = qa(proj, "tc")
    check("kỹ thuật `gia tri bien` không có trong danh mục" in r.stdout, "tên kỹ thuật lạ bị cảnh báo", r.stdout)
    tcf.write_text(tcf.read_text().replace("- Kỹ thuật: gia tri bien", "- Kỹ thuật: giá trị biên, chuyển trạng thái", 1))
    scope.write_text(sc.replace("| REQ-DK-1 | Đăng ký | web | R1 | chức năng |", "| REQ-DK-1 | Đăng ký | web | | chức năng |"))
    r = qa(proj, "tc")
    check("REQ-DK-1: chưa có mức R người dùng xác nhận" in r.stdout,
          "SCOPE không ghi mức → nhắc hỏi người dùng, không tự suy mức từ TC", r.stdout)
    scope.write_text(sc)
    for f in ["ky-thuat/use-case.md", "ky-thuat/to-hop.md", "ky-thuat/oracle.md", "ky-thuat/review-tc.md", "ky-thuat/hop-trang.md"]:
        check((proj / ".claude/skills/qa-testcase-design" / f).exists(), f"cài kèm {f}")
    check((proj / ".claude/skills/qa-knowledge/analysis-review.md").exists() and (proj / "qa/runs/_EXPLORE-TEMPLATE.md").exists(),
          "cài kèm analysis-review.md + khuôn phiên khám phá")

    print("\n[10] tham chiếu file/skill/lệnh/§ ở mọi công đoạn (cài mới)")
    fresh = tmp / "cai-moi"
    fresh.mkdir()
    run([sys.executable, str(REPO / "install.py"), str(fresh)], tmp)
    rc = run([sys.executable, str(REPO / "tests/refcheck.py"), str(fresh)], tmp)
    check(rc.returncode == 0, "mọi tham chiếu trong lệnh/agent/skill/khuôn trỏ tới thứ có thật", rc.stdout + rc.stderr)
    broken = fresh / ".claude/commands/qa-tmp.md"
    broken.write_text("Nạp skill `qa-khong-co` · xem `ky-thuat/khong-co.md` · chạy `/qa-khong-co` · ANALYSIS §99\n")
    rc = run([sys.executable, str(REPO / "tests/refcheck.py"), str(fresh)], tmp)
    check(rc.returncode == 1 and rc.stdout.count("qa-tmp.md") >= 4, "refcheck bắt được skill/file/lệnh/mục không tồn tại", rc.stdout)
    broken.unlink()

    print("\n[11] các lỗi review cuối (script, hook, cài đặt)")
    bugs.write_text(bugs.read_text().replace("- Trạng thái: mở", "- Trạng thái: đã sửa (chờ test lại)"))
    r = qa(proj, "status")
    check("Bug mở: 1" in r.stdout, "bug 'đã sửa (chờ test lại)' vẫn tính là còn mở", r.stdout)
    bugs.write_text(bugs.read_text().replace("- Trạng thái: đã sửa (chờ test lại)", "- Trạng thái: mở"))
    r = qa(proj, "new-run", "full", "TC-DK-001")
    rid3 = r.stdout.split("run-id: ")[1].split()[0]
    l3 = proj / "qa/runs" / rid3 / "RUNLOG.md"
    (proj / "qa/evidence" / rid3 / "TC-DK-001").mkdir(parents=True, exist_ok=True)
    (proj / "qa/evidence" / rid3 / "TC-DK-001" / "a.txt").write_text("x")
    l3.write_text(l3.read_text().replace("| TC-DK-001 | CHƯA CHẠY | | | |", "| TC-DK-001 | PASS | 2026-09-23 | qa/evidence/ | |"))
    r = qa(proj, "run", rid3)
    check("không nằm trong qa/evidence/" in r.stdout, "ô bằng chứng trỏ thư mục chung → không được tính", r.stdout)
    l3.write_text(l3.read_text().replace("| qa/evidence/ |", f"| [ảnh](qa/evidence/{rid3}/TC-DK-001/a.txt) |"))
    r = qa(proj, "run", rid3)
    check("TC-DK-001: PASS nhưng" not in r.stdout, "ô bằng chứng dạng link markdown được hiểu đúng", r.stdout)
    for name, at in (("2026-09-23-full-9", "23:50"), ("2026-09-23-full-10", "23:55")):
        d = proj / "qa/runs" / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "RUNLOG.md").write_text(f"- Bắt đầu: 2099-01-01 {at}\n")
    r = qa(proj, "run")
    check("2026-09-23-full-10" in r.stdout or "full-10" in r.stdout, "run mới nhất chọn theo thời điểm bắt đầu, không theo chữ cái", r.stdout + r.stderr)
    for name in ("2026-09-23-full-10", "2026-09-23-full-9"):
        shutil.rmtree(proj / "qa/runs" / name)
    sc2 = scope.read_text()
    scope.write_text(sc2.replace("| REQ-DK-1 | Đăng ký | web | R1 | chức năng |", "| REQ-DK-1, REQ-DK-2 | Đăng ký \\| đăng nhập | web | R1 | chức năng |"))
    r = qa(proj, "trace")
    check("| REQ-DK-2 |" in r.stdout and "REQ-DK-1, REQ-DK-2" not in r.stdout, "nhiều REQ một ô được tách đúng", r.stdout)
    r = qa(proj, "tc")
    check("REQ-DK-1: SCOPE §2 chưa có mức" not in r.stdout, "ô có \\| không làm lệch cột Mức", r.stdout)
    scope.write_text(sc2)
    bom = proj / "qa/testcases/bom.md"
    bom.write_text("\ufeff" + tc1.replace("TC-DK-001", "TC-BOM-001"), encoding="utf-8")
    (proj / "qa/testcases/h3.md").write_text("### TC-H3-001 — tiêu đề cấp 3\n- REQ: REQ-DK-1\n")
    r = qa(proj, "select", "TC-BOM-001")
    check("TC-BOM-001" in r.stdout, "file TC có BOM vẫn đếm TC đầu tiên", r.stdout + r.stderr)
    r = qa(proj, "tc")
    check("### TC-H3-001" in r.stdout, "tiêu đề `### TC-…` bị báo, không lặng lẽ bỏ qua", r.stdout)
    bom.unlink(); (proj / "qa/testcases/h3.md").unlink()
    an = proj / "qa/ANALYSIS.md"
    an0 = an.read_text()
    an.write_text(an0.replace("| | | | | |\n\n## 4.", "| REQ-DK-1 | Đăng ký | từ code: email bắt buộc (chờ trả lời #9) | web | app.js:1 |\n\n## 4.", 1))
    r = qa(proj, "new-run", "full", "TC-DK-001")
    check(r.returncode == 1 and "chờ trả lời" in r.stderr, "TC dựa trên REQ còn chờ xác nhận không được đưa vào run", r.stdout + r.stderr)
    an.write_text(an0)
    mx = proj / "qa/mx.md"
    mx.write_text("| Hành động | admin | khách |\n|---|---|---|\n| Xoá | ✓ | ✗ (403) |\n| Sửa | ✓ | ✖️ |\n| Xem | ✓ | ? |\n")
    g2 = run([sys.executable, ".claude/qa-scripts/gen_matrix_tc.py", "qa/mx.md", "--feature", "ĐƠN", "--target", "web",
              "--req", "REQ-DK-1", "--muc", "R2"], proj)
    check(g2.stdout.count("## TC-ĐƠN-") == 2 and "ô không nhận ra" in g2.stderr,
          "gen_matrix: ô `✗ (403)`/`✖️` sinh TC, tên tính năng tiếng Việt giữ nguyên, ô lạ bị báo", g2.stdout[:300] + g2.stderr)
    import time
    args12 = [f"Q{i}=" + ",".join(f"{c}{i}" for c in "abcde") for i in range(12)]
    t0 = time.time()
    pw2 = run([sys.executable, ".claude/qa-scripts/pairwise.py", *args12, "--khong", "a0&a1", "--khong", "b2&b3"], proj)
    check(pw2.returncode == 0 and time.time() - t0 < 5, f"pairwise 12 tham số × 5 giá trị chạy nhanh ({time.time() - t0:.2f}s)", pw2.stderr)
    check(hook(proj, "guard_evidence.py", "mcp__browser__browser_take_screenshot", {"filename": "01.png"}) == 2,
          "chặn tên file trần (Playwright ghi ra gốc dự án)")
    check(hook(proj, "guard_evidence.py", "mcp__browser-tester__browser_take_screenshot", {"filename": "/tmp/x.png"}) == 2,
          "hook áp cả server riêng của tester")
    check(hook(proj, "guard_evidence.py", "Bash", {"command": "cp logo.png src/assets/logo.png"}) == 0,
          "không chặn việc thường của dev (chép ảnh vào src)")
    check(hook(proj, "guard_evidence.py", "Bash", {"command": "cp qa/evidence/r1/TC-A-001/01.png ~/Desktop/"}) == 2,
          "chặn chép bằng chứng ra thư mục ngoài dự án")
    qa_md.write_text(qa_md.read_text().replace("- Chỉ đọc: src", "- Chỉ đọc: .."))
    check(hook(proj, "guard_readonly.py", "Write", {"file_path": str(proj / "qa/testcases/x.md")}) == 0, "`Chỉ đọc: ..` vẫn ghi được qa/")
    qa_md.write_text(qa_md.read_text().replace("- Chỉ đọc: ..", "- Chỉ đọc: src"))
    check(hook(proj, "guard_readonly.py", "Bash", {"command": 'cd src && grep -rn "=>" .'}) == 0, "grep có `=>` trong chuỗi không bị chặn nhầm")
    check(hook(proj, "guard_readonly.py", "Bash", {"command": "git -C src branch"}) == 0, "git branch (liệt kê) không bị chặn")
    check(hook(proj, "guard_readonly.py", "Bash", {"command": "(cd src && rm app.js)"}) == 2, "chặn rm trong subshell")
    st3 = json.loads((proj / ".claude/settings.json").read_text())
    wrap = [h for e in st3["hooks"]["PreToolUse"] for h in e["hooks"] if "guard_readonly" in json.dumps(h)][0]
    miss = run([wrap["command"], *[a.replace("${CLAUDE_PROJECT_DIR}", str(tmp / "khong-co")) for a in wrap["args"]]], tmp,
               stdin=json.dumps({"tool_name": "Write", "tool_input": {"file_path": "/x"}}))
    check(miss.returncode == 0, "thiếu file script thì hook cho qua, không chặn mọi thao tác", miss.stderr)
    mj = proj / ".mcp.json"
    m = json.loads(mj.read_text()); m["mcpServers"]["browser"]["args"].append("--user-data-dir=/tmp/x"); mj.write_text(json.dumps(m))
    r = run([sys.executable, str(REPO / "install.py"), str(proj), "--update"], tmp)
    check("--user-data-dir=/tmp/x" in mj.read_text() and "giữ nguyên" in r.stdout, "--update không ghi đè server browser đã chỉnh tay", r.stdout)
    r = run([sys.executable, str(REPO / "install.py"), str(REPO / "kit")], tmp)
    check(r.returncode == 2, "không cho cài vào thư mục con của repo qa-agent", r.stderr)
    py39 = Path("/usr/bin/python3")
    if py39.exists():
        rc = run([str(py39), str(REPO / "tests/refcheck.py"), str(fresh)], tmp)
        check(rc.returncode == 0, "refcheck chạy được trên Python hệ thống (3.9)", rc.stdout + rc.stderr)


    print("\n[12] review lần 3: kết luận sai, parse, hook đa dòng, release")
    def mkrun(rows, crit, listed=None, name="2099-01-01-t", bug_md=None, extra=""):
        d = proj / "qa/runs" / name
        shutil.rmtree(d, ignore_errors=True); d.mkdir(parents=True)
        ids = listed if listed is not None else [r[0] for r in rows]
        body = (f"- Bắt đầu: 2099-01-01 00:00\n- Danh sách TC lúc tạo run: {', '.join(ids)}\n- Tiêu chí (test):\n{crit}{extra}\n"
                "| TC | Kết quả | Ngày | Bằng chứng | Bug / Lý do |\n|---|---|---|---|---|\n")
        for tid, res, note in rows:
            e = proj / "qa/evidence" / name / tid
            e.mkdir(parents=True, exist_ok=True); (e / "a.txt").write_text("x")
            body += f"| {tid} | {res} | 2099-01-01 | qa/evidence/{name}/{tid}/ | {note} |\n"
        (d / "RUNLOG.md").write_text(body)
        return name
    good = "  - Bug mở không được phép: S1, S2\n  - Tỉ lệ PASS tối thiểu: 95%\n  - Tỉ lệ BLOCKED tối đa: 5%\n"
    rid = mkrun([("TC-DK-001", "PASS", "")], good.replace("95%", "R1: 100%, R2: 95%"))
    r = qa(proj, "run", rid)
    check("CHƯA KẾT LUẬN" in r.stdout and "không đọc được" not in r.stdout.lower() or "cần đúng một số" in r.stdout,
          "`Tỉ lệ PASS tối thiểu: R1: 100%…` không bị đọc thành 1%", r.stdout)
    rid = mkrun([("TC-DK-001", "PASS", ""), ("TC-DK-002", "PASS", "")], good.replace("S1, S2", "S1–S3"))
    bugs0 = bugs.read_text()
    bugs.write_text(bugs0 + "\n## BUG-077 — lỗi S2 chỉ ghi ở RUNLOG\n- Severity: S2\n- Trạng thái: mở\n")
    rid = mkrun([("TC-DK-001", "PASS", ""), ("TC-DK-002", "FAIL", "BUG-077")], good.replace("S1, S2", "S1–S3"))
    r = qa(proj, "run", rid)
    check("KHÔNG ĐẠT" in r.stdout and "BUG-077" in r.stdout, "khoảng S1–S3 gồm S2; bug chỉ nhắc trong RUNLOG vẫn được xét", r.stdout)
    bugs.write_text(bugs0)
    rid = mkrun([("**TC-DK-001**", "PASS", "")], good, listed=["TC-DK-001", "TC-DK-002"])
    r = qa(proj, "run", rid)
    check("TC-DK-002: có trong danh sách lúc tạo run nhưng không còn dòng" in r.stdout and "CHƯA KẾT LUẬN" in r.stdout,
          "xoá dòng TC khỏi RUNLOG bị phát hiện; ID in đậm vẫn được đọc", r.stdout)
    rid = mkrun([("TC-DK-001", "PASS", ""), ("TC-DK-002", "SKIP", "không kịp")], good)
    r = qa(proj, "run", rid)
    check("SKIP phải trỏ dòng DECISIONS" in r.stdout, "SKIP không trỏ DECISIONS bị báo", r.stdout)
    shutil.rmtree(proj / "qa/runs" / "2099-01-01-t", ignore_errors=True)
    st_tc = proj / "qa/testcases/trang-thai.md"
    st_tc.write_text(tc1.replace("TC-DK-001", "TC-TT-001").replace('Hiện "Kiểm tra hộp thư"', 'Đơn hiện trạng thái "Chờ xác nhận"'))
    r = qa(proj, "select", "TC-TT-001")
    check("TC-TT-001" in r.stdout and "bỏ" not in r.stderr, "trạng thái nghiệp vụ \"Chờ xác nhận\" không bị coi là nhãn chờ", r.stdout + r.stderr)
    st_tc.write_text(tc1.replace("TC-DK-001", "TC-TT-001").replace("- REQ: REQ-DK-1", "- REQ: REQ-DK-1.2")
                     .replace("Ô email nhận giá trị", "Nhập <email của người dùng thật>"))
    r = qa(proj, "tc", "REQ-DK-1.2")
    check("chỗ trống `<email" in r.stdout, "TC còn chỗ trống <…> bị chặn", r.stdout)
    r2 = qa(proj, "trace")
    check("REQ-DK-1.2" in r2.stdout, "mã REQ có dấu chấm (REQ-DK-1.2) không bị cắt", r2.stdout)
    st_tc.unlink()
    r = qa(proj, "tc", "REQ-DK-1")
    check("REQ đang xét" in r.stdout and "(phạm vi: REQ-DK-1)" in r.stdout, "tc soát được theo phạm vi REQ", r.stdout)
    ids_all = qa(proj, "select", "all").stdout.split("\n")[1:]
    rid = mkrun([(t, "PASS", "") for t in ids_all if t.startswith("TC-")], good, name="2099-01-01-full")
    bugs.write_text(bugs0.replace("- Trạng thái: mở", "- Trạng thái: đóng") + "\n## BUG-088 — S1 ở chỗ khác\n- Severity: S1\n- Trạng thái: mở\n- TC: TC-KHAC-001\n")
    rr = mkrun([("TC-DK-001", "PASS", "")], good, name="2099-01-02-retest")
    r = qa(proj, "run", rr)
    check("NGOÀI phạm vi run này: BUG-088" in r.stdout and "chỉ trong phạm vi run này" in r.stdout,
          "run retest ĐẠT nhưng cảnh báo bug S1 ở ngoài phạm vi", r.stdout)
    sc_now = scope.read_text()
    scope.write_text(sc_now.replace("- Trạng thái: NHÁP", "- Trạng thái: CHỐT"))
    r = qa(proj, "release", rid, rr)
    check("KẾT LUẬN PHÁT HÀNH: KHÔNG ĐẠT" in r.stdout and "BUG-088" in r.stdout, "release gộp nhiều run và xét mọi bug mở mức cấm", r.stdout)
    scope.write_text(sc_now); bugs.write_text(bugs0)
    for n in (rid, rr):
        shutil.rmtree(proj / "qa/runs" / n, ignore_errors=True)
    check(hook(proj, "guard_readonly.py", "Bash", {"command": "echo ok\nrm src/app.js"}) == 2, "hook chặn lệnh ghi ở dòng thứ hai")
    check(hook(proj, "guard_readonly.py", "Bash", {"command": "git -c user.name=a -C src commit -am x"}) == 2, "chặn git -c … -C src commit")
    check(hook(proj, "guard_readonly.py", "Bash", {"command": "git -C src branch --show-current"}) == 0, "git branch --show-current không bị chặn")
    check(hook(proj, "guard_readonly.py", "Bash", {"command": "python3 -c \"open('src/x','w').write('1')\""}) == 2, "chặn python -c ghi file")
    check(hook(proj, "guard_readonly.py", "Bash", {"command": "grep -rl a src | xargs sed -i s/a/b/"}) == 2, "chặn xargs sed -i")
    check(hook(proj, "guard_readonly.py", "Bash", {"command": 'git commit -m "sửa; rm src/x"'}) == 0, "dấu ; trong nháy không bị tách nhầm")
    check(hook(proj, "guard_evidence.py", "Bash", {"command": "echo x\ncp qa/evidence/r1/TC-A-001/01.png /tmp/"}) == 2, "hook bằng chứng tách lệnh nhiều dòng")
    check(hook(proj, "guard_evidence.py", "Bash", {"command": "adb shell screencap -p /sdcard/s.png"}) == 0, "adb shell screencap (trên thiết bị) đi qua")
    check(hook(proj, "guard_evidence.py", "mcp__browser__browser_network_requests", {"filename": "/tmp/net.txt"}) == 2, "chặn log mạng ghi ra /tmp")
    pwu = run([sys.executable, ".claude/qa-scripts/pairwise.py", "X=1,2", "Y=a,b", "Z=p,q", "--khong", "X=1&Y=a", "--khong", "X=1&Y=b"], proj)
    check("X=1" in pwu.stderr, "pairwise báo giá trị bị ràng buộc loại hết", pwu.stderr)
    mx2 = proj / "qa/mx2.md"
    mx2.write_text("| Hành động | admin | khách |\n|---|---|---|\n| Sửa | ✓ | |\n")
    g3 = run([sys.executable, ".claude/qa-scripts/gen_matrix_tc.py", str(mx2), "--feature", "Q", "--target", "web", "--req", "REQ-DK-1"], proj)
    check(g3.returncode != 0, "gen_matrix bắt buộc --muc (mức người dùng chốt)", g3.stderr)
    g4 = run([sys.executable, ".claude/qa-scripts/gen_matrix_tc.py", str(mx2), "--feature", "Q", "--target", "web", "--req", "REQ-DK-1", "--muc", "R1"], proj)
    check("(trống)" in g4.stderr, "ô trống trong ma trận bị báo, không coi là cho phép", g4.stderr)
    stl = proj / ".claude/settings.json"
    r = run([sys.executable, str(REPO / "install.py"), str(proj), "--update", "--settings-local"], tmp)
    shared_guards = json.dumps(json.loads(stl.read_text())).count("guard_")
    local_guards = json.dumps(json.loads((proj / ".claude/settings.local.json").read_text())).count("guard_")
    check(shared_guards == 0 and local_guards == 2, "--settings-local chuyển hook sang settings.local.json, không nhân đôi", f"{shared_guards} {local_guards} {r.stdout}")
    run([sys.executable, str(REPO / "install.py"), str(proj), "--update", "--settings-shared"], tmp)
    check(json.dumps(json.loads(stl.read_text())).count("guard_") == 2, "--settings-shared chuyển về lại")
    bad = tmp / "bad-shape"; (bad / ".claude").mkdir(parents=True)
    (bad / ".claude/settings.json").write_text(json.dumps({"hooks": {"PreToolUse": {"x": 1}}}))
    r = run([sys.executable, str(REPO / "install.py"), str(bad)], tmp)
    check(r.returncode == 0 and "cấu trúc lạ" in r.stdout, "settings.json sai hình dạng → báo, không crash giữa chừng", r.stdout + r.stderr)

    print("\n[13] review lần 4: release, SCOPE nháp, tiêu chí lệch khuôn, mức theo SCOPE, lượt AI, hook")
    bugs0, sc0, qa0 = bugs.read_text(), scope.read_text(), (proj / "qa/QA.md").read_text()
    chot = sc0.replace("- Trạng thái: NHÁP", "- Trạng thái: CHỐT")
    scope.write_text(chot)
    rid = mkrun([("tc-dk-001", "PASS", "")], good, listed=["TC-DK-001"], name="2099-02-01-full",
                extra="")
    r = qa(proj, "run", rid)
    check("không có trong qa/testcases" not in r.stdout, "ID viết thường khớp đúng TC thật", r.stdout)
    rid = mkrun([("TC-DK-001", "PASS", "")], good, name="2099-02-01-full")
    lg = proj / "qa/runs" / rid / "RUNLOG.md"
    lg.write_text(lg.read_text().replace("- Tiêu chí (test):", "- Scope lúc tạo run: NHÁP\n- Tiêu chí (test):"))
    r = qa(proj, "run", rid)
    check("CHƯA KẾT LUẬN" in r.stdout and "NHÁP" in r.stdout, "run tạo khi SCOPE còn NHÁP → không kết luận", r.stdout)
    rid = mkrun([("TC-DK-001", "PASS", "")], good + "  - Tỉ lệ PASS tối thiểu (R1): 100%\n", name="2099-02-01-full")
    r = qa(proj, "run", rid)
    check("không đúng khuôn" in r.stdout and "CHƯA KẾT LUẬN" in r.stdout, "dòng tiêu chí lệch khuôn bị báo, không bỏ qua im lặng", r.stdout)
    rid = mkrun([("TC-DK-001", "PASS", ""), ("TC-DK-002", "FAIL", "BUG-099")], good.replace("S1, S2", "S1") + "  - Tỉ lệ PASS tối thiểu R1: 100%\n",
                name="2099-02-01-full")
    bugs.write_text(bugs0 + "\n## BUG-099 — x\n- Severity: S3\n- Trạng thái: mở\n- TC: TC-DK-002\n")
    t2 = tcf.read_text()
    tcf.write_text(t2.replace("- Mức: R1", "- Mức: R3"))
    r = qa(proj, "run", rid)
    check("tỉ lệ PASS R1 50.0% < 100%" in r.stdout, "tỉ lệ theo mức tính theo mức SCOPE đã chốt, không theo trường Mức của TC", r.stdout)
    tcf.write_text(t2); bugs.write_text(bugs0)
    ev = proj / "qa/evidence" / rid / "TC-DK-001"
    (ev / "buoc 1.png").write_text("x")
    lg = proj / "qa/runs" / rid / "RUNLOG.md"
    lg.write_text(lg.read_text().replace(f"| qa/evidence/{rid}/TC-DK-001/ |", f"| `qa/evidence/{rid}/TC-DK-001/buoc 1.png` |"))
    r = qa(proj, "run", rid)
    check("TC-DK-001: PASS nhưng" not in r.stdout, "tên file bằng chứng có dấu cách (trong backtick) được hiểu đúng", r.stdout)
    shutil.rmtree(proj / "qa/runs" / rid, ignore_errors=True)
    old = proj / "qa/SCOPE-dot1.md"
    old.write_text("## 2. Trong phạm vi\n| REQ | Mô tả | Target | Mức | Loại |\n|---|---|---|---|---|\n| REQ-OLD-1 | cũ | web | R2 | x |\n")
    (proj / "qa/testcases/cu.md").write_text(tc1.replace("TC-DK-001", "TC-OLD-001").replace("REQ-DK-1", "REQ-OLD-1").replace("- Tag: smoke\n", "")
                                             .replace("- Mức: R1", "- Mức: R2"))
    ids_all = [t for t in qa(proj, "select", "all").stdout.split("\n")[1:] if t.startswith("TC-")]
    ra = mkrun([(t, "PASS", "") for t in ids_all], good, name="2099-03-01-full")
    rg = mkrun([("TC-OLD-001", "FAIL", "BUG-098")], good, name="2099-03-02-reg")
    bugs.write_text(bugs0 + "\n## BUG-098 — hồi quy\n- Severity: S3\n- Trạng thái: mở\n- TC: TC-OLD-001\n")
    r = qa(proj, "release", ra, rg)
    check("KẾT LUẬN PHÁT HÀNH: KHÔNG ĐẠT" in r.stdout and f"{len(ids_all) + 1} TC" in r.stdout,
          "release tính cả TC regression của REQ cũ (FAIL làm tụt tỉ lệ)", r.stdout)
    lg = proj / "qa/runs" / ra / "RUNLOG.md"
    lg.write_text(lg.read_text().replace("Tỉ lệ PASS tối thiểu: 95%", "Tỉ lệ PASS tối thiểu: 100%"))
    r = qa(proj, "release", ra, rg)
    check("khác SCOPE hiện tại" in r.stdout, "release báo khi tiêu chí đóng băng trong RUNLOG khác SCOPE", r.stdout)
    for n in (ra, rg):
        shutil.rmtree(proj / "qa/runs" / n, ignore_errors=True)
    old.unlink(); (proj / "qa/testcases/cu.md").unlink(); bugs.write_text(bugs0)
    rs = mkrun([("TC-DK-001", "PASS", "")], good, name="2099-04-01-smoke")
    r = qa(proj, "run", rs)
    check("chỉ trong phạm vi run này" in r.stdout, "run chỉ phủ một phần SCOPE → ĐẠT kèm \"chỉ trong phạm vi run\"", r.stdout)
    shutil.rmtree(proj / "qa/runs" / rs, ignore_errors=True)
    (proj / "qa/QA.md").write_text(qa0.replace("| | | | |\n\n## Môi trường", "| bot | ai | https://x | |\n\n## Môi trường", 1))
    ai_tc = proj / "qa/testcases/bot.md"
    ai_tc.write_text(tc1.replace("TC-DK-001", "TC-BOT-001").replace("- Target: web", "- Target: bot"))
    ra = mkrun([("TC-BOT-001", "PASS", "")], good + "  - Test AI — N mỗi ca: 3\n", name="2099-05-01-full")
    e = proj / "qa/evidence" / ra / "TC-BOT-001"
    (e / "01-luot-1.txt").write_text("x"); (e / "01-luot-1.png").write_text("x"); (e / "cham-cac-luot.md").write_text("x")
    r = qa(proj, "run", ra)
    check("cần 3 lượt, bằng chứng mới có 1" in r.stdout, "đếm lượt AI theo số k khác nhau của transcript, không đếm ảnh/file chấm", r.stdout)
    (e / "02-lượt-2.md").write_text("x"); (e / "03-LUOT-3.txt").write_text("x")
    r = qa(proj, "run", ra)
    check("TC AI cần" not in r.stdout, "nhận cả `lượt`/`LUOT` khi đủ N", r.stdout)
    shutil.rmtree(proj / "qa/runs" / ra, ignore_errors=True); ai_tc.unlink(); (proj / "qa/QA.md").write_text(qa0)
    ph = proj / "qa/testcases/ph.md"
    ph.write_text(tc1.replace("TC-DK-001", "TC-PH-001").replace("Ô email nhận giá trị", "Hiện chữ đậm <b>OK</b>, tổng < 100 và > 0"))
    r = qa(proj, "tc", "ph")
    check("chỗ trống" not in r.stdout, "không báo nhầm <b> hay \"< 100 và >\" là chỗ trống", r.stdout)
    ph.unlink()
    r = qa(proj, "tc", "khong-co-tinh-nang")
    check(r.returncode == 1 and "không phải REQ" in r.stdout, "tc với phạm vi gõ sai → báo lỗi, không \"sạch\"", r.stdout)
    scope.write_text(sc0)
    bad2 = tmp / "bad-shape2"; (bad2 / ".claude").mkdir(parents=True)
    (bad2 / ".claude/settings.json").write_text(json.dumps({"hooks": {"PreToolUse": ["echo x"]}}))
    r = run([sys.executable, str(REPO / "install.py"), str(bad2)], tmp)
    check(r.returncode == 0 and "cấu trúc lạ" in r.stdout, "PreToolUse chứa chuỗi → báo, không crash", r.stdout + r.stderr)
    mx3 = proj / "qa/mx3.md"
    mx3.write_text("| Hành động | admin | khách |\n|---|---|---|\n| Sửa | ✓ (chỉ của mình) | Có điều kiện |\n")
    g5 = run([sys.executable, ".claude/qa-scripts/gen_matrix_tc.py", str(mx3), "--feature", "Q", "--target", "web", "--req", "REQ-DK-1", "--muc", "R1"], proj)
    check(g5.stderr.count("ô không nhận ra") == 2, "ô có điều kiện (\"✓ (chỉ của mình)\", \"Có điều kiện\") bị báo để hỏi", g5.stderr)
    pw3 = run([sys.executable, ".claude/qa-scripts/pairwise.py", "A=1,2", "A=3,4"], proj)
    check(pw3.returncode != 0 and "trùng" in (pw3.stderr + pw3.stdout), "pairwise từ chối tên tham số trùng", pw3.stderr)
    HOOK_CASES = [
        (0, "guard_readonly.py", "cd src && npm test 2>&1 | tail -20"), (0, "guard_readonly.py", "cd src && make >&2"),
        (2, "guard_readonly.py", "echo x >| src/a"), (2, "guard_readonly.py", "perl -pi -e s/a/b/ src/a"),
        (2, "guard_readonly.py", "sed -Ei s/a/b/ src/a"), (2, "guard_readonly.py", "sed --in-place s/a/b/ src/a"),
        (2, "guard_readonly.py", "git checkout ."), (2, "guard_readonly.py", "git reset --hard"),
        (2, "guard_readonly.py", "git clean -fdx"), (2, "guard_readonly.py", "git stash"),
        (0, "guard_readonly.py", "git status && git log --oneline -3 && git diff"),
        (0, "guard_readonly.py", "git add qa/testcases && git commit -m 'thêm TC'"),
        (2, "guard_readonly.py", "find . -name '*.orig' -delete"), (2, "guard_readonly.py", "for f in a; do rm src/app.js; done"),
        (2, "guard_readonly.py", "if true; then rm src/app.js; fi"), (2, "guard_readonly.py", "true & rm src/app.js"),
        (2, "guard_readonly.py", "echo x |& tee src/a"), (2, "guard_readonly.py", "export F=src/a; rm $F"),
        (2, "guard_readonly.py", "rm ${F:-src/a}"), (2, "guard_readonly.py", "env FOO=1 rm src/app.js"),
        (2, "guard_readonly.py", "sudo -u me rm src/app.js"), (2, "guard_readonly.py", "timeout 5 rm src/app.js"),
        (2, "guard_readonly.py", "bash -lc 'rm src/app.js'"), (2, "guard_readonly.py", "echo $(rm src/app.js)"),
        (2, "guard_readonly.py", "cp -rt src a.txt"), (2, "guard_readonly.py", "curl -sSo src/x http://x"),
        (2, "guard_readonly.py", "cat > qa/n.md <<'EOF'\nIt's\nEOF\nrm src/app.js"),
        (0, "guard_readonly.py", "cat > qa/n.md <<'EOF'\nrm src/app.js\nEOF"), (2, "guard_readonly.py", "rm s*/app.js"),
        (0, "guard_readonly.py", "ls qa | xargs -I{} cp src/{} qa/sandbox/"), (0, "guard_readonly.py", "git -C src clean -nd"),
        (0, "guard_readonly.py", "git -C src tag --contains HEAD"), (0, "guard_readonly.py", "cd src; popd; rm qa/x"),
        (0, "guard_readonly.py", "pytest -q && cat src/app.js && grep -rn x src"),
        (0, "guard_evidence.py", "ls qa/evidence 2>/dev/null"), (0, "guard_evidence.py", "ls qa/evidence > /tmp/list.txt"),
        (0, "guard_evidence.py", "cat > qa/notes.md <<'EOF'\ncp qa/evidence/r1 /tmp/\nEOF"),
        (2, "guard_evidence.py", "tar -C qa -czf /tmp/ev.tgz evidence"), (2, "guard_evidence.py", "ffmpeg -i qa/evidence/r1/v.mp4 /tmp/x.gif"),
        (2, "guard_evidence.py", "xcrun simctl io booted screenshot /tmp/a"),
    ]
    wrong = [f"{g} `{c}` → {hook(proj, g, 'Bash', {'command': c})} (cần {e_})" for e_, g, c in HOOK_CASES
             if hook(proj, g, "Bash", {"command": c}) != e_]
    check(not wrong, f"{len(HOOK_CASES)} ca đối kháng của hook (lọt + chặn nhầm) đều đúng", "\n".join(wrong))

    print("\n[14] review lần 5: hook chặn nhầm việc thường, batch mobile, cờ dài, payload HTML, ID chữ thường")
    ev_abs = str(proj / "qa/evidence/r1/TC-A-001")
    MCP_CASES = [
        (0, "mcp__mobile__mobile_install_app", {"device": "x", "path": "/tmp/build/app.apk"}),
        (2, "mcp__mobile__mobile_batch_commands", {"steps": [{"name": "mobile_save_screenshot", "arguments": {"saveTo": "/tmp/a.png"}}]}),
        (2, "mcp__mobile__mobile_batch_commands", {"steps": [{"name": "mobile_start_screen_recording", "arguments": {}}]}),
        (0, "mcp__mobile__mobile_batch_commands", {"steps": [{"name": "mobile_save_screenshot", "arguments": {"saveTo": ev_abs + "/01.png"}},
                                                             {"name": "mobile_install_app", "arguments": {"path": "/tmp/app.apk"}}]}),
        (2, "mcp__mobile__mobile_save_screenshot", {"saveTo": "/tmp/a.png"}),
    ]
    wrong = [f"{t} {ti} → {hook(proj, 'guard_evidence.py', t, ti)} (cần {e_})" for e_, t, ti in MCP_CASES
             if hook(proj, "guard_evidence.py", t, ti) != e_]
    check(not wrong, "cài app mobile (path là đầu vào) đi qua; từng bước mobile_batch_commands được soi", "\n".join(wrong))
    CASES5 = [
        (0, "guard_readonly.py", "git checkout -b qa/tc-moi"), (0, "guard_readonly.py", "git switch -c qa/tc-moi"),
        (2, "guard_readonly.py", "git checkout -b x origin/main"), (2, "guard_readonly.py", "git pull --rebase"),
        (0, "guard_readonly.py", "(cd src && ls); touch qa/x"), (2, "guard_readonly.py", "(cd qa && ls); rm src/app.js"),
        (2, "guard_readonly.py", "(cd src && rm app.js)"), (0, "guard_readonly.py", "echo $(cd src; ls) > qa/list.txt"),
        (0, "guard_readonly.py", "tee qa/x < src/app.js"), (0, "guard_readonly.py", "wc -l < src/app.js > qa/n.txt"),
        (2, "guard_evidence.py", "tar --file=/tmp/e.tgz -c qa/evidence/r1"), (2, "guard_evidence.py", "tar -c --file /tmp/e.tgz qa/evidence/r1"),
        (2, "guard_evidence.py", "cp --target-directory=/tmp qa/evidence/r1/TC-A-001/01.png"),
        (0, "guard_evidence.py", "(cd qa && cp evidence/r1/TC-A-001/01.png evidence/r2/)"),
        (0, "guard_evidence.py", "cp qa/sandbox/a/out.json qa/evidence/r/T/01-out.json 2>/dev/null"),
        (2, "guard_evidence.py", "cp qa/evidence/r1/TC-A-001/01.png /tmp/ 2>/dev/null"),
        (2, "guard_readonly.py", "rm src/app.js 2>/dev/null"), (2, "guard_readonly.py", "npm test 2> src/err.log"),
        (0, "guard_readonly.py", "cp src/app.js qa/sandbox/ 2>&1"),
        (2, "guard_evidence.py", "cat < qa/evidence/r1/TC-A-001/01.png > /tmp/o"),
        (2, "guard_evidence.py", "base64 < qa/evidence/r1/TC-A-001/01.png > /tmp/o"),
        (2, "guard_evidence.py", "(cat qa/evidence/r1/TC-A-001/01.png) > /tmp/o.png"),
        (2, "guard_evidence.py", "(cd qa/evidence/r1/TC-A-001 && cat 01.png) > /tmp/o.png"),
        (2, "guard_evidence.py", "(cd qa && tar czf - evidence) > /tmp/ev.tgz"),
        (0, "guard_evidence.py", "(cd qa && ls evidence) > /tmp/list.txt"),
        (2, "guard_evidence.py", "for d in a; do (cd /tmp && ls); done; cp qa/evidence/r1/TC-A-001/01.png /tmp/o.png"),
        (0, "guard_evidence.py", "mv qa/evidence/r1/TC-A-001/a.png qa/evidence/r1/TC-A-001/b.png 2>/dev/null"),
        (0, "guard_readonly.py", "for d in a b; do (cd src && ls); done; touch notes.txt"),
        (0, "guard_readonly.py", "if [ -d src ]; then (cd src && ls); fi; echo hi > out.txt"),
        (0, "guard_readonly.py", "time (cd src && make); echo done > build.log"),
        (0, "guard_readonly.py", "! (cd src && grep -q x a); echo $? > rc.txt"),
        (0, "guard_readonly.py", "{ (cd src && ls); } ; touch x"),
        (2, "guard_readonly.py", "cp qa/x src/a 2>/dev/null"), (2, "guard_readonly.py", "rsync -a out/ src/ 2>err.log"),
        (0, "guard_readonly.py", "V=$(cd src && git rev-parse HEAD); echo $V > qa/v.txt"),
        (0, "guard_readonly.py", "V=$(cd src && git log -1 --format=%h); echo \"$V\" > notes.txt"),
        (2, "guard_readonly.py", "echo $(rm src/app.js)"), (2, "guard_readonly.py", "x=$(echo $(rm src/app.js))"),
        (2, "guard_readonly.py", "cd src && git checkout -b feat"), (2, "guard_readonly.py", "git -C src switch -c feat"),
        (0, "guard_readonly.py", "a=(x y); echo ${a[0]} > qa/a.txt"), (0, "guard_readonly.py", "echo $((1+2)) > qa/n.txt"),
    ]
    wrong = [f"{g} `{c}` → {hook(proj, g, 'Bash', {'command': c})} (cần {e_})" for e_, g, c in CASES5
             if hook(proj, g, "Bash", {"command": c}) != e_]
    check(not wrong, "tạo nhánh, subshell ( cd … ), `<` đầu vào, cờ dài --file=/--target-directory= xử lý đúng", "\n".join(wrong))
    (proj / "src/.git").mkdir()
    wrong = [c for c in ("git pull --rebase", "git stash", "git checkout main") if hook(proj, "guard_readonly.py", "Bash", {"command": c}) != 0]
    wrong += [c for c in ("git -C src reset --hard",) if hook(proj, "guard_readonly.py", "Bash", {"command": c}) != 2]
    check(not wrong, "vùng chỉ đọc là repo git riêng lồng bên trong: lệnh git của repo ngoài đi qua, lệnh vào chính nó vẫn chặn",
          ", ".join(wrong))
    (proj / "src/.git").rmdir()
    ph = proj / "qa/testcases/xss.md"
    ph.write_text(tc1.replace("TC-DK-001", "TC-XSS-001").replace("Ô email nhận giá trị",
                                                                 "Nhập <svg onload=alert(1)> và <img src=x onerror=alert(1)> — hiện nguyên văn"))
    r = qa(proj, "tc", "xss")
    check("chỗ trống" not in r.stdout, "payload XSS dạng thẻ HTML không bị báo nhầm là chỗ trống", r.stdout)
    ph.unlink()
    ids_all = [t for t in qa(proj, "select", "all").stdout.split("\n")[1:] if t.startswith("TC-")]
    ra = mkrun([(t, "PASS", "") for t in ids_all], good, name="2099-06-01-full")
    lg = proj / "qa/runs" / ra / "RUNLOG.md"
    txt = lg.read_text()
    for t in ids_all:
        txt = txt.replace(f"| {t} | PASS", f"| {t.lower()} | PASS")
    lg.write_text(txt)
    r = qa(proj, "release", ra)
    check("chưa có kết quả 0" in r.stdout, "release nhận ID TC viết thường trong RUNLOG", r.stdout)
    r = qa(proj, "trace")
    check(f"PASS {len(ids_all)}" in r.stdout, "trace nhận ID TC viết thường", r.stdout)
    shutil.rmtree(proj / "qa/runs" / ra, ignore_errors=True)
    # installer: không gỡ quyền người dùng tự có, không thêm lại thứ người dùng đã xoá, không ghi đè hook đã chỉnh
    ip = tmp / "inst5"; (ip / ".claude").mkdir(parents=True)
    (ip / ".claude/settings.local.json").write_text(json.dumps({"permissions": {"allow": ["mcp__browser"]}}))
    run([sys.executable, str(REPO / "install.py"), str(ip)], tmp)
    run([sys.executable, str(REPO / "install.py"), str(ip), "--update", "--settings-local"], tmp)
    run([sys.executable, str(REPO / "install.py"), str(ip), "--update", "--settings-shared"], tmp)
    loc = json.loads((ip / ".claude/settings.local.json").read_text())
    check("mcp__browser" in loc["permissions"]["allow"], "chuyển settings qua lại không gỡ quyền người dùng tự có từ trước", json.dumps(loc))
    sp = ip / ".claude/settings.json"
    st = json.loads(sp.read_text())
    st["permissions"]["ask"].remove("Bash(psql:*)")
    for e in st["hooks"]["PreToolUse"]:
        if "guard_evidence" in json.dumps(e):
            e["hooks"][0]["timeout"] = 30
        if "guard_readonly" in json.dumps(e):
            e["hooks"] = []
    st["hooks"]["PreToolUse"] = [e for e in st["hooks"]["PreToolUse"] if e["hooks"]]
    sp.write_text(json.dumps(st))
    r = run([sys.executable, str(REPO / "install.py"), str(ip), "--update"], tmp)
    st = json.loads(sp.read_text())
    ev_h = [h for e in st["hooks"]["PreToolUse"] for h in e["hooks"] if "guard_evidence" in json.dumps(h)]
    ro_h = [h for e in st["hooks"]["PreToolUse"] for h in e["hooks"] if "guard_readonly" in json.dumps(h)]
    run([sys.executable, str(REPO / "install.py"), str(ip), "--update"], tmp)
    st2 = json.loads(sp.read_text())
    check("Bash(psql:*)" not in st2["permissions"]["ask"], "quyền người dùng đã xoá không quay lại ở lần --update thứ hai", json.dumps(st2))
    check("Bash(psql:*)" not in st["permissions"]["ask"] and len(ev_h) == 1 and ev_h[0].get("timeout") == 30 and not ro_h
          and "đã được chỉnh tay" in r.stdout and "đã gỡ hook" in r.stdout,
          "--update không thêm lại quyền/hook người dùng đã xoá, giữ hook đã chỉnh tay", r.stdout + json.dumps(st))

    print(f"\n{'=' * 50}\n  {OK} ✓ · {BAD} ✗")
    if keep:
        print(f"  giữ thư mục nháp: {tmp}")
    else:
        shutil.rmtree(tmp, ignore_errors=True)
    return 1 if BAD else 0


if __name__ == "__main__":
    sys.exit(main())
