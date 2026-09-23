#!/usr/bin/env python3
"""install.py — cài bộ qa-agent vào một dự án bất kỳ (repo sản phẩm, hoặc thư mục QA riêng).

    python3 install.py <thư-mục-dự-án> [--name "Tên sản phẩm"] [--dry-run]
    python3 install.py <thư-mục-dự-án> --update      # cập nhật skill/agent/lệnh/script lên bản mới của repo này

Làm gì:
  1. Chép `kit/.claude/{commands,agents,skills,qa-scripts}` vào `<dự án>/.claude/` (chỉ file của qa-agent —
     tên bắt đầu `qa`; file khác của dự án không đụng).
  2. Tạo workspace `<dự án>/qa/` từ `kit/qa/` — file đã có thì GIỮ NGUYÊN (không bao giờ ghi đè dữ liệu QA).
  3. GỘP `kit/.claude/settings.qa.json` vào `<dự án>/.claude/settings.json` (thêm quyền + hook PreToolUse/SessionStart/
     UserPromptSubmit, giữ phần có sẵn).
     `--update` không thêm lại quyền/hook người dùng đã xoá, không ghi đè hook đã chỉnh tay; chuyển file settings chỉ
     gỡ quyền do qa-agent thêm (manifest ghi lại), không gỡ quyền người dùng tự có.
  4. GỘP server `browser` + `mobile` vào `<dự án>/.mcp.json` — version khoá cứng, `--output-dir` là đường dẫn
     TUYỆT ĐỐI tới `<dự án>/qa/evidence/_inbox/…` (ảnh không lạc sang thư mục khác dù mở phiên ở đâu).
  5. Ghi `<dự án>/.claude/qa-agent.json`: nguồn cài, version, băm từng file đã chép — `--update` dùng để
     KHÔNG ghi đè file người dùng đã sửa tay trong dự án (báo ra để tự gộp).

Chỉ dùng thư viện chuẩn Python 3.9+.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sys
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT = HERE / "kit"
VERSION = "3.0.0"
PLAYWRIGHT_MCP_VERSION = "0.0.82"
MOBILE_MCP_VERSION = "1.0.4"
KIT_DIRS = ["commands", "agents", "skills", "qa-scripts"]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def render(text: str, ctx: dict, as_json: bool = False) -> str:
    """Thay {{KHOÁ}}. as_json: escape giá trị để chèn an toàn vào chuỗi JSON/YAML (đường dẫn có \\ hoặc ")."""
    for k, v in ctx.items():
        text = text.replace("{{" + k + "}}", json.dumps(v)[1:-1] if as_json else v)
    return text


@lru_cache(maxsize=None)
def kit_hook_names() -> frozenset[str]:
    """Tên script hook của qa-agent (theo settings.qa.json) — hook khác trỏ vào .claude/qa-scripts/ (vd người dùng tự
    thêm `qa_check.py status` lúc mở phiên) KHÔNG phải của kit, không được gỡ/thay."""
    hooks = json.loads((KIT / ".claude" / "settings.qa.json").read_text(encoding="utf-8"))["hooks"]   # chỉ phần hook, không lấy quyền
    return frozenset(re.findall(r"qa-scripts/(\w+)\.py", json.dumps(hooks))) | {"guard_evidence", "guard_readonly"}


def hook_key(h: dict) -> str | None:
    m = re.search(r"\.claude/qa-scripts/(\w+)\.py", json.dumps(h))
    return m.group(1) if m and m.group(1) in kit_hook_names() else None


def event_lists(hooks) -> list:
    return [v for v in hooks.values() if isinstance(v, list)] if isinstance(hooks, dict) else []


def hook_sha(matcher, h: dict) -> str:
    return sha(json.dumps({"matcher": matcher, "hook": h}, sort_keys=True).encode())


def strip_qa(cur: dict, perms_ours: dict | None) -> None:
    """Gỡ quyền + hook của qa-agent khỏi một settings đã đọc (dùng khi chuyển giữa settings.json và settings.local.json).
    perms_ours: quyền qa-agent đã THÊM vào file này (theo manifest) — quyền người dùng tự có từ trước không bị gỡ.
    None = manifest bản cũ không ghi → gỡ theo danh sách của kit như trước."""
    if perms_ours is None:
        perms_ours = json.loads((KIT / ".claude" / "settings.qa.json").read_text(encoding="utf-8"))["permissions"]
    perms = cur.get("permissions") if isinstance(cur.get("permissions"), dict) else {}
    for k in ("allow", "ask", "deny"):
        if isinstance(perms.get(k), list):
            perms[k] = [x for x in perms[k] if x not in perms_ours.get(k, [])]
    for hooks in event_lists(cur.get("hooks")):
        for e in hooks:
            if isinstance(e, dict) and isinstance(e.get("hooks"), list):
                e["hooks"] = [h for h in e["hooks"] if not hook_key(h)]
        hooks[:] = [e for e in hooks if not isinstance(e, dict) or e.get("hooks")]
    if isinstance(cur.get("hooks"), dict):
        for ev in [k for k, v in cur["hooks"].items() if v == []]:
            del cur["hooks"][ev]


def migrate_notes(proj: Path) -> list[str]:
    """Workspace qa/ không bao giờ bị ghi đè — khuôn cũ thiếu phần của bản mới thì báo để người dùng tự gộp."""
    out = []
    qa = proj / "qa"
    an = qa / "ANALYSIS.md"
    if an.is_file() and "Trích nguyên văn" not in an.read_text(encoding="utf-8", errors="replace"):
        out.append("qa/ANALYSIS.md bản cũ: §3 chưa có cột `Trích nguyên văn` (qa_check.py src sẽ nhắc từng REQ) — thêm cột "
                   "cuối bảng §3 và mục `## 9. Thuật ngữ` theo kit/qa/ANALYSIS.md")
    tpl = qa / "testcases" / "_TEMPLATE.md"
    if tpl.is_file() and "- VP:" not in tpl.read_text(encoding="utf-8", errors="replace"):
        out.append("qa/testcases/_TEMPLATE.md bản cũ: chưa có dòng `- VP:` — chép lại từ kit/qa/testcases/_TEMPLATE.md")
    sc = qa / "SCOPE.md"
    if sc.is_file() and "Tiêu chí vào" not in sc.read_text(encoding="utf-8", errors="replace"):
        out.append("qa/SCOPE.md bản cũ: chưa có §9–§12 (vào/ra, lịch, bàn giao, rủi ro dự án) — thêm theo kit/qa/SCOPE.md khi lập đợt mới")
    les = qa / "LESSONS.md"
    if les.is_file() and "Phạm vi áp" not in les.read_text(encoding="utf-8", errors="replace"):
        out.append("qa/LESSONS.md bản cũ: chưa có cột `Phạm vi áp` (lessons --for coi mọi bài là chung) — thêm cột cuối bảng nếu cần")
    return out


def kit_files() -> list[Path]:
    out = []
    for d in KIT_DIRS:
        for p in sorted((KIT / ".claude" / d).rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
                out.append(p)
    return out


def merge_list(dst: list, src: list) -> list:
    for x in src:
        if x not in dst:
            dst.append(x)
    return dst


def merge_settings(path: Path, ctx: dict, py: str, dry: bool, log: list, rec: dict | None) -> dict | None:
    """Gộp quyền + hook vào `path`. rec = bản ghi lần cài trước cho CHÍNH file này ({perms, hooks}) hoặc {} khi là bản
    manifest cũ chưa ghi (coi quyền/hook có sẵn là của qa-agent), None khi cài mới vào file này.
    Không thêm lại quyền/hook người dùng đã xoá; không ghi đè hook người dùng đã sửa (matcher, timeout…).
    Trả về bản ghi mới để lưu manifest (None nếu không gộp được)."""
    src = json.loads(render((KIT / ".claude" / "settings.qa.json").read_text(encoding="utf-8"), ctx, as_json=True))
    cur = {}
    if path.exists():
        try:
            cur = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            log.append(f"  ⚠ {path} không phải JSON hợp lệ — KHÔNG gộp, thêm tay theo kit/.claude/settings.qa.json")
            return None
    events = list(src["hooks"])
    shape_ok = isinstance(cur, dict) and isinstance(cur.get("permissions", {}), dict) \
        and all(isinstance(cur.get("permissions", {}).get(k, []), list) for k in ("allow", "ask", "deny")) \
        and isinstance(cur.get("hooks", {}), dict) \
        and all(isinstance(cur.get("hooks", {}).get(ev, []), list) for ev in events) \
        and all(isinstance(e, dict) and isinstance(e.get("hooks", []), list) and all(isinstance(h, dict) for h in e.get("hooks", []))
                for ev in events for e in cur.get("hooks", {}).get(ev, []))
    if not shape_ok:
        log.append(f"  ⚠ {path} có cấu trúc lạ (permissions/hooks không đúng kiểu) — KHÔNG gộp, thêm tay theo kit/.claude/settings.qa.json")
        return None
    tracked = bool(rec) and "perms" in rec
    old_perms, old_hooks = (rec or {}).get("perms", {}), (rec or {}).get("hooks", {})
    perms = cur.setdefault("permissions", {})
    new_perms: dict = {}
    dropped: list[str] = []
    for k in ("allow", "ask", "deny"):
        lst, mine = perms.setdefault(k, []), []
        for x in src["permissions"][k]:
            if x in lst:
                if rec == {} or x in old_perms.get(k, []):   # có sẵn: của qa-agent nếu lần trước qa-agent thêm
                    mine.append(x)
            elif tracked and x in old_perms.get(k, []):
                dropped.append(x)                             # người dùng đã xoá → không thêm lại
                mine.append(x)                                # vẫn ghi vào manifest để lần --update sau còn nhớ
            else:
                lst.append(x)
                mine.append(x)
        new_perms[k] = mine
    if dropped:
        log.append(f"  ⚠ {path.name}: người dùng đã gỡ quyền {', '.join(dropped)} — không thêm lại")
    all_hooks = cur.setdefault("hooks", {})
    had = set(all_hooks)
    new_hooks: dict = {}
    present: set = set()
    kept: set = set()
    for ev in events:
        hooks = all_hooks.setdefault(ev, [])
        for e in hooks:                                       # hook qa-agent đang có: giữ bản đã sửa tay, gỡ bản nguyên gốc
            keep = []
            for h in e.get("hooks", []):
                key = hook_key(h)
                if not key:
                    keep.append(h)
                    continue
                present.add(key)
                if tracked and key in old_hooks and hook_sha(e.get("matcher"), h) != old_hooks[key] and key not in kept:
                    keep.append(h)
                    kept.add(key)
                    new_hooks[key] = old_hooks[key]
                    log.append(f"  ⚠ {path.name}: hook {key} đã được chỉnh tay — giữ nguyên; bản mới ở kit/.claude/settings.qa.json")
            e["hooks"] = keep
        hooks[:] = [e for e in hooks if e.get("hooks")]
    for ev in events:
        for entry in src["hooks"][ev]:
            for h in entry["hooks"]:
                h["command"] = py
            key = hook_key(entry)
            if key in kept:
                continue
            if tracked and key in old_hooks and key not in present:
                new_hooks[key] = old_hooks[key]
                log.append(f"  ⚠ {path.name}: người dùng đã gỡ hook {key} — không thêm lại (muốn bật lại: thêm tay theo "
                           f"kit/.claude/settings.qa.json)")
                continue
            all_hooks[ev].append(entry)
            for h in entry["hooks"]:
                new_hooks[key] = hook_sha(entry.get("matcher"), h)
    for ev in events:
        if not all_hooks.get(ev) and ev not in had:
            del all_hooks[ev]
    if not dry:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(cur, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log.append(f"  ✓ gộp quyền + hook vào {path}")
    return {"file": path.name, "perms": new_perms, "hooks": new_hooks}


def merge_mcp(path: Path, ctx: dict, dry: bool, log: list, old_mcp: dict) -> dict:
    """Thêm server browser/mobile. Server đã có mà KHÔNG phải bản qa-agent đã cài y nguyên (so băm lưu trong
    manifest) → giữ nguyên + báo, không ghi đè tinh chỉnh của người dùng. Trả về băm các server đã ghi."""
    src = json.loads(render((KIT / ".mcp.qa.json").read_text(encoding="utf-8"), ctx, as_json=True))
    cur = {}
    if path.exists():
        try:
            cur = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            log.append(f"  ⚠ {path} không phải JSON hợp lệ — KHÔNG gộp, thêm tay theo kit/.mcp.qa.json")
            return old_mcp
    if not isinstance(cur, dict) or not isinstance(cur.get("mcpServers", {}), dict):
        log.append(f"  ⚠ {path} có cấu trúc lạ (mcpServers không phải object) — KHÔNG gộp, thêm tay theo kit/.mcp.qa.json")
        return old_mcp
    servers = cur.setdefault("mcpServers", {})
    written: dict = {}
    for name, conf in src["mcpServers"].items():
        old = servers.get(name)
        if old is not None:
            untouched = old_mcp.get(name) == sha(json.dumps(old, sort_keys=True).encode())
            if not untouched:
                log.append(f"  ⚠ .mcp.json đã có server `{name}` (của dự án hoặc đã được chỉnh tay) — giữ nguyên; "
                           f"bản của qa-agent ở kit/.mcp.qa.json nếu muốn gộp tay")
                continue
        servers[name] = conf
        written[name] = sha(json.dumps(conf, sort_keys=True).encode())
    if not dry:
        path.write_text(json.dumps(cur, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if written:
        log.append(f"  ✓ ghi server {', '.join(written)} vào {path} (Playwright MCP {PLAYWRIGHT_MCP_VERSION}, mobile-mcp {MOBILE_MCP_VERSION})")
    return {**old_mcp, **written}


def main() -> int:
    ap = argparse.ArgumentParser(description="Cài bộ qa-agent vào một dự án")
    ap.add_argument("project")
    ap.add_argument("--name", help="tên sản phẩm (mặc định: tên thư mục)")
    ap.add_argument("--update", action="store_true", help="cập nhật phần bộ công cụ, giữ nguyên dữ liệu qa/")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--settings-shared", action="store_true",
                    help="chuyển quyền + hook về .claude/settings.json dùng chung (gỡ khỏi settings.local.json)")
    ap.add_argument("--settings-local", action="store_true",
                    help="ghi quyền + hook vào .claude/settings.local.json (không commit) thay cho settings.json dùng chung "
                         "— nên dùng khi cài vào repo sản phẩm mà dev khác cũng dùng Claude Code")
    a = ap.parse_args()

    proj = Path(a.project).expanduser().resolve()
    if not proj.is_dir():
        print(f"✗ {proj} không phải thư mục", file=sys.stderr)
        return 2
    if proj == HERE or HERE in proj.parents:
        print("✗ không cài vào chính repo qa-agent (hay thư mục con của nó)", file=sys.stderr)
        return 2
    manifest_path = proj / ".claude" / "qa-agent.json"
    old = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    if old and not a.update:
        print(f"Dự án đã cài qa-agent {old.get('version')} — dùng --update để cập nhật.", file=sys.stderr)
        return 1

    py = "python" if os.name == "nt" else "python3"
    ctx = {
        "PROJECT_NAME": a.name or old.get("name") or proj.name,
        "EVIDENCE_INBOX": (proj / "qa" / "evidence" / "_inbox").as_posix(),   # posix: an toàn trong JSON/YAML, kể cả Windows
        "PLAYWRIGHT_MCP_VERSION": PLAYWRIGHT_MCP_VERSION,
        "MOBILE_MCP_VERSION": MOBILE_MCP_VERSION,
        "DATE": dt.date.today().isoformat(),
    }
    log: list[str] = [f"qa-agent {VERSION} → {proj}" + (" (dry-run)" if a.dry_run else "")]
    hashes: dict[str, str] = {}
    old_hashes = old.get("files", {})

    # 1. bộ công cụ
    for src in kit_files():
        rel = src.relative_to(KIT)
        dst = proj / rel
        data = render(src.read_text(encoding="utf-8"), ctx, as_json=src.parent.name == "agents").encode("utf-8") \
            if src.suffix in (".md", ".py", ".json") else src.read_bytes()
        if os.name == "nt" and src.suffix == ".md":
            data = data.replace(b"python3 ", b"python ")
        h = sha(data)
        key = rel.as_posix()
        if dst.exists():
            cur = sha(dst.read_bytes())
            if cur == h:
                hashes[key] = h
                continue
            if key in old_hashes and cur != old_hashes[key]:
                log.append(f"  ⚠ {key}: đã sửa tay trong dự án — giữ bản của dự án, bản mới ở {src}")
                hashes[key] = old_hashes[key]
                continue
            if key not in old_hashes:
                log.append(f"  ⚠ {key}: đã có sẵn (không do qa-agent cài) — giữ nguyên")
                continue
        if not a.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)
            if src.suffix == ".py":
                dst.chmod(0o755)
        hashes[key] = h
    for key in sorted(set(old_hashes) - set(hashes)):
        log.append(f"  ⚠ {key}: không còn trong bản mới — tự xoá nếu không dùng")
    log.append(f"  ✓ skill/agent/lệnh/script: {len(hashes)} file")

    # 2. workspace qa/ — chỉ tạo file chưa có
    made = 0
    for src in sorted((KIT / "qa").rglob("*")):
        if not src.is_file():
            continue
        dst = proj / src.relative_to(KIT)
        if dst.exists():
            continue
        made += 1
        if not a.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(render(src.read_text(encoding="utf-8"), ctx), encoding="utf-8")
    for sub in ("evidence/_inbox", "sandbox"):
        if not a.dry_run:
            (proj / "qa" / sub).mkdir(parents=True, exist_ok=True)
    log.append(f"  ✓ workspace qa/: tạo {made} file mới (file đã có giữ nguyên)")
    for note in migrate_notes(proj):
        log.append(f"  ⚠ {note}")

    # 3–4. cấu hình
    local = False if a.settings_shared else (a.settings_local or old.get("settings_local", False))
    target_file = proj / ".claude" / ("settings.local.json" if local else "settings.json")
    other = proj / ".claude" / ("settings.json" if local else "settings.local.json")
    old_file = ("settings.local.json" if old.get("settings_local") else "settings.json") if old else None
    old_set = old.get("settings") if isinstance(old.get("settings"), dict) else None
    if old_set is None and old:                # manifest bản cũ: chưa ghi quyền/hook đã thêm
        old_set = {"file": old_file}
    if other.exists():                      # chuyển đích → gỡ bản qa-agent ở file kia, không để hook chạy hai lần
        try:
            o = json.loads(other.read_text(encoding="utf-8"))
            before = json.dumps(o, sort_keys=True)
            # chỉ gỡ quyền qa-agent đã thêm vào CHÍNH file này; manifest cũ (không ghi quyền) → danh sách của kit
            ours = old_set.get("perms") if old and old_set.get("file") == other.name else {}
            strip_qa(o, ours)
            if json.dumps(o, sort_keys=True) != before:
                if not a.dry_run:
                    other.write_text(json.dumps(o, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                log.append(f"  ✓ gỡ quyền + hook qa-agent khỏi {other.name} (chuyển sang {target_file.name})")
        except (json.JSONDecodeError, ValueError, AttributeError):
            log.append(f"  ⚠ {other} không đọc được — tự kiểm xem còn hook qa-agent ở đó không")
    rec_in = None
    if old_set is not None and old_set.get("file") == target_file.name:
        rec_in = {k: v for k, v in old_set.items() if k in ("perms", "hooks")}   # {} = manifest cũ
    set_rec = merge_settings(target_file, ctx, py, a.dry_run, log, rec_in)
    if set_rec is None:
        set_rec = old.get("settings") if isinstance(old.get("settings"), dict) else None
    mcp_hashes = merge_mcp(proj / ".mcp.json", ctx, a.dry_run, log, old.get("mcp", {}))

    # 5. manifest
    if not a.dry_run:
        manifest_path.write_text(json.dumps({
            "version": VERSION, "name": ctx["PROJECT_NAME"], "source": str(HERE),
            "installed": dt.datetime.now().isoformat(timespec="seconds"), "files": hashes,
            "mcp": mcp_hashes, "settings_local": local, "settings": set_rec,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log.append(f"  ✓ {manifest_path.relative_to(proj)} (nguồn: {HERE})")

    print("\n".join(log))
    if not a.update:
        print(f"""
Tiếp theo:
  cd {proj}
  claude                       # duyệt MCP server browser/mobile khi được hỏi
  /qa <việc cần làm>           # vd: /qa phân tích tài liệu docs/prd.md
  /qa-status                   # xem đang ở đâu
Điền qa/QA.md (tài liệu, target, môi trường, đường dẫn chỉ đọc) — hoặc để /qa-analyze hỏi dần.""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
