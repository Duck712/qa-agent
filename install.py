#!/usr/bin/env python3
"""install.py — cài bộ qa-agent vào một dự án bất kỳ (repo sản phẩm, hoặc thư mục QA riêng).

    python3 install.py <thư-mục-dự-án> [--name "Tên sản phẩm"] [--dry-run]
    python3 install.py <thư-mục-dự-án> --update      # cập nhật skill/agent/lệnh/script lên bản mới của repo này

Làm gì:
  1. Chép `kit/.claude/{commands,agents,skills,qa-scripts}` vào `<dự án>/.claude/` (chỉ file của qa-agent —
     tên bắt đầu `qa`; file khác của dự án không đụng).
  2. Tạo workspace `<dự án>/qa/` từ `kit/qa/` — file đã có thì GIỮ NGUYÊN (không bao giờ ghi đè dữ liệu QA).
  3. GỘP `kit/.claude/settings.qa.json` vào `<dự án>/.claude/settings.json` (thêm quyền + 2 hook, giữ phần có sẵn).
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
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT = HERE / "kit"
VERSION = "3.0.0"
PLAYWRIGHT_MCP_VERSION = "0.0.82"
MOBILE_MCP_VERSION = "1.0.4"
KIT_DIRS = ["commands", "agents", "skills", "qa-scripts"]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def render(text: str, ctx: dict) -> str:
    for k, v in ctx.items():
        text = text.replace("{{" + k + "}}", v)
    return text


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


def merge_settings(path: Path, ctx: dict, py: str, dry: bool, log: list) -> None:
    src = json.loads(render((KIT / ".claude" / "settings.qa.json").read_text(encoding="utf-8"), ctx))
    cur = {}
    if path.exists():
        try:
            cur = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            log.append(f"  ⚠ {path} không phải JSON hợp lệ — KHÔNG gộp, thêm tay theo kit/.claude/settings.qa.json")
            return
    perms = cur.setdefault("permissions", {})
    for k in ("allow", "ask", "deny"):
        merge_list(perms.setdefault(k, []), src["permissions"][k])
    hooks = cur.setdefault("hooks", {}).setdefault("PreToolUse", [])
    have = {json.dumps(h.get("args") or h.get("command")) for e in hooks for h in e.get("hooks", [])}
    for entry in src["hooks"]["PreToolUse"]:
        for h in entry["hooks"]:
            h["command"] = py
        if not any(json.dumps(h.get("args")) in have for h in entry["hooks"]):
            hooks.append(entry)
    if not dry:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(cur, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log.append(f"  ✓ gộp quyền + hook vào {path}")


def merge_mcp(path: Path, ctx: dict, dry: bool, log: list) -> None:
    src = json.loads(render((KIT / ".mcp.qa.json").read_text(encoding="utf-8"), ctx))
    cur = {}
    if path.exists():
        try:
            cur = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            log.append(f"  ⚠ {path} không phải JSON hợp lệ — KHÔNG gộp, thêm tay theo kit/.mcp.qa.json")
            return
    servers = cur.setdefault("mcpServers", {})
    for name, conf in src["mcpServers"].items():
        old = servers.get(name)
        ours = old and any(("@playwright/mcp" in a or "@mobilenext/mobile-mcp" in a) for a in old.get("args", []))
        if old and not ours:
            log.append(f"  ⚠ .mcp.json đã có server `{name}` khác của dự án — giữ nguyên; agent qa-tester vẫn có server riêng")
            continue
        servers[name] = conf
    if not dry:
        path.write_text(json.dumps(cur, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log.append(f"  ✓ gộp server browser + mobile vào {path} (Playwright MCP {PLAYWRIGHT_MCP_VERSION}, mobile-mcp {MOBILE_MCP_VERSION})")


def main() -> int:
    ap = argparse.ArgumentParser(description="Cài bộ qa-agent vào một dự án")
    ap.add_argument("project")
    ap.add_argument("--name", help="tên sản phẩm (mặc định: tên thư mục)")
    ap.add_argument("--update", action="store_true", help="cập nhật phần bộ công cụ, giữ nguyên dữ liệu qa/")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    proj = Path(a.project).expanduser().resolve()
    if not proj.is_dir():
        print(f"✗ {proj} không phải thư mục", file=sys.stderr)
        return 2
    if proj == HERE:
        print("✗ không cài vào chính repo qa-agent", file=sys.stderr)
        return 2
    manifest_path = proj / ".claude" / "qa-agent.json"
    old = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    if old and not a.update:
        print(f"Dự án đã cài qa-agent {old.get('version')} — dùng --update để cập nhật.", file=sys.stderr)
        return 1

    py = "python" if os.name == "nt" else "python3"
    ctx = {
        "PROJECT_NAME": a.name or old.get("name") or proj.name,
        "EVIDENCE_INBOX": str(proj / "qa" / "evidence" / "_inbox"),
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
        data = render(src.read_text(encoding="utf-8"), ctx).encode("utf-8") if src.suffix in (".md", ".py", ".json") \
            else src.read_bytes()
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

    # 3–4. cấu hình
    merge_settings(proj / ".claude" / "settings.json", ctx, py, a.dry_run, log)
    merge_mcp(proj / ".mcp.json", ctx, a.dry_run, log)

    # 5. manifest
    if not a.dry_run:
        manifest_path.write_text(json.dumps({
            "version": VERSION, "name": ctx["PROJECT_NAME"], "source": str(HERE),
            "installed": dt.datetime.now().isoformat(timespec="seconds"), "files": hashes,
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
