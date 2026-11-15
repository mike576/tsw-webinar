#!/usr/bin/env python3
"""PostToolUse hook (Edit|Write): strip trailing whitespace from the edited file.
A stand-in for your real formatter (ruff format, prettier, gofmt ...). Costs zero context."""
import json
import sys
from pathlib import Path

data = json.load(sys.stdin)
path = Path((data.get("tool_input") or {}).get("file_path", ""))
if path.suffix in {".py", ".md", ".txt", ".json", ".toml", ".yaml", ".yml"} and path.is_file():
    text = path.read_text(encoding="utf-8")
    clean = "\n".join(line.rstrip() for line in text.splitlines()) + ("\n" if text.endswith("\n") else "")
    if clean != text:
        path.write_text(clean, encoding="utf-8")
sys.exit(0)
