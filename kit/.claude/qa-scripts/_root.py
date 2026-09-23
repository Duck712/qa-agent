"""Tìm thư mục dự án (nơi có qa/) cho các hook — dùng chung."""
from __future__ import annotations

import os
from pathlib import Path


def project_root() -> Path:
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parents[2]   # <dự án>/.claude/qa-scripts/_root.py
