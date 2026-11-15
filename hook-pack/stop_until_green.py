#!/usr/bin/env python3
"""Stop hook: Claude may not finish while the visible tests fail.

Exit 2 + stderr = "keep working, here is why". To cap the cost, it blocks at most
MAX_BLOCKS times per session, then lets Claude stop (a hook can burn your limit too).
"""
import json
import os
import subprocess
import sys
import tempfile

MAX_BLOCKS = 3
TEST_CMD = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"]

data = json.load(sys.stdin)
counter = os.path.join(tempfile.gettempdir(), f"stop-hook-{data.get('session_id', 'x')}.count")
blocks = int(open(counter).read()) if os.path.exists(counter) else 0
if blocks >= MAX_BLOCKS:
    print(f"stop_until_green: gave up after {MAX_BLOCKS} attempts", file=sys.stderr)
    sys.exit(0)

cwd = os.environ.get("CLAUDE_PROJECT_DIR", data.get("cwd", "."))
res = subprocess.run(TEST_CMD, cwd=cwd, capture_output=True, text=True, timeout=120)
if res.returncode == 0:
    sys.exit(0)

open(counter, "w").write(str(blocks + 1))
tail = (res.stdout + res.stderr)[-2500:]
print(f"The tests are failing, do not stop yet. Fix the code (not the tests).\n{tail}", file=sys.stderr)
sys.exit(2)
