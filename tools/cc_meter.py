#!/usr/bin/env python3
"""cc_meter: what did my Claude Code sessions really use?

Reads the session logs Claude Code already writes on your machine
(~/.claude/projects/**/*.jsonl, or $CLAUDE_CONFIG_DIR/projects) and prints
token use per turn, per session or per day. No account, no API key, no packages.

  python3 tools/cc_meter.py                 # last session started in this folder, turn by turn
  python3 tools/cc_meter.py --sessions      # every session started in this folder
  python3 tools/cc_meter.py --days --all    # all your sessions, per day and model
  python3 tools/cc_meter.py --file x.jsonl  # one log file (e.g. the sample log)

Columns: input = fresh input (not cached; ~2 per call is normal), cache_write = new input
written to cache, cache_read = input read back from cache, output = output.
"cache_read share" = cache_read / (input + cache_write + cache_read): how much of what
was sent came from the cache.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from pathlib import Path

FIELDS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")


def log_root() -> Path:
    base = os.environ.get("CLAUDE_CONFIG_DIR") or str(Path.home() / ".claude")
    return Path(base).expanduser() / "projects"


def project_dir(cwd: Path) -> Path:
    # Claude Code names the folder after the path, with every non-alphanumeric char as "-".
    name = "".join(c if c.isalnum() else "-" for c in str(cwd.resolve()))
    return log_root() / name


def read_turns(path: Path) -> list[dict]:
    """One row per API call. A call is logged once per content block, so we dedupe."""
    seen, turns = set(), []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = rec.get("message") or {}
            usage = msg.get("usage")
            if rec.get("type") != "assistant" or not usage:
                continue
            key = (msg.get("id"), rec.get("requestId"))
            if key in seen:
                continue
            seen.add(key)
            row = {f: int(usage.get(f) or 0) for f in FIELDS}
            row.update(
                t=rec.get("timestamp", ""),
                model=msg.get("model", "?"),
                session=rec.get("sessionId", path.stem),
                sidechain=bool(rec.get("isSidechain")),
            )
            turns.append(row)
    return turns


def share(rows: list[dict]) -> float:
    sent = sum(r["input_tokens"] + r["cache_creation_input_tokens"] + r["cache_read_input_tokens"] for r in rows)
    return sum(r["cache_read_input_tokens"] for r in rows) / sent if sent else 0.0


def k(n: int) -> str:
    return f"{n / 1000:,.1f}k" if n >= 1000 else str(n)


def table(header: list[str], rows: list[list[str]]) -> None:
    w = [max(len(h), *(len(r[i]) for r in rows)) if rows else len(h) for i, h in enumerate(header)]
    print("  ".join(h.rjust(w[i]) for i, h in enumerate(header)))
    for r in rows:
        print("  ".join(c.rjust(w[i]) for i, c in enumerate(r)))


def sums(rows: list[dict]) -> list[str]:
    return [k(sum(r[f] for r in rows)) for f in FIELDS] + [f"{share(rows):.1%}"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", type=Path, help="read this .jsonl file only")
    ap.add_argument("--all", action="store_true", help="all projects, not just this folder")
    ap.add_argument("--sessions", action="store_true", help="one line per session")
    ap.add_argument("--days", action="store_true", help="one line per day and model")
    args = ap.parse_args()

    if args.file:
        files = [args.file]
    else:
        root = log_root() if args.all else project_dir(Path.cwd())
        files = sorted(root.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime)
        if not files:
            raise SystemExit(f"No session logs under {root}. Start claude in this folder first.")

    if not (args.sessions or args.days):  # turn by turn, latest session
        turns = read_turns(files[-1])
        print(f"session {files[-1].stem}  ({len(turns)} API calls)\n")
        rows = [[str(i), r["t"][11:19], r["model"].replace("claude-", ""), *(k(r[f]) for f in FIELDS)]
                for i, r in enumerate(turns, 1)]
        rows.append(["", "", "TOTAL", *sums(turns)[:4]])
        table(["#", "time", "model", "input", "cache_write", "cache_read", "output"], rows)
        print(f"\ncache_read share: {share(turns):.1%}")
        return

    all_turns = [t for f in files for t in read_turns(f)]
    if args.sessions:
        by = defaultdict(list)
        for t in all_turns:
            by[t["session"]].append(t)
        rows = [[s[:8], min(r["t"] for r in ts)[:16].replace("T", " "), str(len(ts)), *sums(ts)]
                for s, ts in sorted(by.items(), key=lambda kv: min(r["t"] for r in kv[1]))]
        table(["session", "started", "calls", "input", "cache_write", "cache_read", "output", "cache_read share"], rows)
    else:
        by = defaultdict(list)
        for t in all_turns:
            by[(t["t"][:10], t["model"])].append(t)
        rows = [[d, m.replace("claude-", ""), str(len(ts)), *sums(ts)] for (d, m), ts in sorted(by.items())]
        table(["day", "model", "calls", "input", "cache_write", "cache_read", "output", "cache_read share"], rows)
    print(f"\nall: {len(all_turns)} API calls, cache_read share {share(all_turns):.1%}")


if __name__ == "__main__":
    main()
