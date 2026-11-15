#!/usr/bin/env python3
"""PreToolUse hook: the agent may not edit anything under tests/.

Why: an agent that is told "make the tests pass" can also make them pass by
weakening the tests. A line in CLAUDE.md asks it not to; this hook makes it impossible.
Exit code 2 = block, and stderr goes back to Claude as the reason. (Exit 1 would NOT block.)
"""
import json
import re
import sys

PROTECTED = re.compile(r"""(^|[/\s"'=])tests?/""")
data = json.load(sys.stdin)
tool = data.get("tool_name", "")
inp = data.get("tool_input") or {}

if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
    path = inp.get("file_path") or inp.get("notebook_path") or ""
    if PROTECTED.search(path.replace("\\", "/")):
        print(f"Blocked by tests_guard: {path} is a test file. Fix the code, not the tests.", file=sys.stderr)
        sys.exit(2)

if tool == "Bash":
    cmd = inp.get("command", "")
    # best effort: shell writes into tests/ (redirects, sed -i, rm, mv, cp, tee)
    if PROTECTED.search(cmd) and re.search(r"(>|\bsed\s+-i|\brm\b|\bmv\b|\bcp\b|\btee\b|\btruncate\b)", cmd):
        print("Blocked by tests_guard: shell command would change files under tests/.", file=sys.stderr)
        sys.exit(2)

sys.exit(0)
