#!/usr/bin/env python3
"""Subagent statistics from your local Claude Code logs.

For one session: every subagent it started, how long it ran, how many API calls and
tool calls it made, and how many tokens it used. Next to it: the main thread, so you
can see what stayed out of your own context.

Where the data is (Claude Code 2.1.3xx):
  ~/.claude/projects/<project>/<session-id>.jsonl                      main thread
  ~/.claude/projects/<project>/<session-id>/subagents/agent-<id>.jsonl one file per subagent
  ~/.claude/projects/<project>/<session-id>/subagents/agent-<id>.meta.json  type, description

Usage:
  python3 tools/subagent_stats.py              newest session started in this folder (or below)
  python3 tools/subagent_stats.py --last 2     the 2 newest sessions here (e.g. run A and run B)
  python3 tools/subagent_stats.py <session-id> one session, anywhere (a prefix is enough)
  python3 tools/subagent_stats.py --root DIR   read logs from DIR instead of ~/.claude/projects

Python 3.10+, standard library only.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude")) / "projects"


def ts(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def read_jsonl(p: Path):
    try:
        with p.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        pass
    except OSError:
        return


def stats(p: Path) -> dict:
    """Token use, API calls, tool calls and wall time of one transcript file."""
    seen: set = set()
    s = dict(calls=0, tools=0, inp=0, cw=0, cw5=0, cw1h=0, cr=0, out=0, models={},
             first=None, last=None, last_ctx=0, max_ctx=0, cwd=None)
    tool_ids: set = set()
    for r in read_jsonl(p):
        t = ts(r.get("timestamp"))
        if t:
            s["first"] = t if s["first"] is None or t < s["first"] else s["first"]
            s["last"] = t if s["last"] is None or t > s["last"] else s["last"]
        if s["cwd"] is None and r.get("cwd"):
            s["cwd"] = r["cwd"]
        if r.get("type") != "assistant":
            continue
        m = r.get("message") or {}
        for c in m.get("content") or []:
            if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("id") not in tool_ids:
                tool_ids.add(c.get("id"))
                s["tools"] += 1
        u = m.get("usage")
        if not u:
            continue
        key = (m.get("id"), r.get("requestId"))
        if key in seen:  # one API call is written on 2-3 lines
            continue
        seen.add(key)
        model = m.get("model") or "?"
        if model == "<synthetic>":
            continue
        s["calls"] += 1
        s["models"][model] = s["models"].get(model, 0) + 1
        i, w, c, o = (u.get(k) or 0 for k in ("input_tokens", "cache_creation_input_tokens",
                                                "cache_read_input_tokens", "output_tokens"))
        s["inp"] += i; s["cw"] += w; s["cr"] += c; s["out"] += o
        cc = u.get("cache_creation") or {}
        s["cw5"] += cc.get("ephemeral_5m_input_tokens") or 0
        s["cw1h"] += cc.get("ephemeral_1h_input_tokens") or 0
        s["last_ctx"] = i + w + c
        s["max_ctx"] = max(s["max_ctx"], s["last_ctx"])
    s["tools"] = len(tool_ids)
    s["secs"] = (s["last"] - s["first"]).total_seconds() if s["first"] and s["last"] else 0.0
    return s


def k(n: float) -> str:
    return f"{n / 1e6:.2f}M" if n >= 1e6 else f"{n / 1e3:.1f}k" if n >= 1e3 else str(int(n))


def dur(sec: float) -> str:
    sec = int(round(sec))
    return f"{sec // 60}m{sec % 60:02d}s" if sec >= 60 else f"{sec}s"


def share(s: dict) -> str:
    tot = s["inp"] + s["cw"] + s["cr"]
    return f"{100 * s['cr'] / tot:.0f}%" if tot else "-"


def short_model(models: dict) -> str:
    if not models:
        return "-"
    names = sorted(models, key=models.get, reverse=True)
    return "+".join(n.replace("claude-", "") for n in names)


def subagents_of(main: Path) -> list[tuple[dict, dict]]:
    d = main.with_suffix("") / "subagents"
    out = []
    for f in sorted(d.glob("agent-*.jsonl")) if d.is_dir() else []:
        meta = {}
        mp = f.with_suffix(".meta.json")
        if mp.exists():
            try:
                meta = json.loads(mp.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass
        st = stats(f)
        if st["calls"]:
            out.append((meta, st))
    out.sort(key=lambda x: x[1]["first"] or datetime.max.astimezone())
    return out


def report(main: Path) -> None:
    ms = stats(main)
    subs = subagents_of(main)
    when = ms["first"].astimezone().strftime("%Y-%m-%d %H:%M") if ms["first"] else "?"
    print(f"\nSession {main.stem[:8]}  started {when}  in {ms['cwd'] or '?'}")
    if not subs:
        print("  No subagents in this session.")
    hdr = f"  {'#':>2}  {'type':<16} {'description':<30} {'model':<14} {'time':>6} {'calls':>5} {'tools':>5} " \
          f"{'input':>7} {'cache_write':>11} {'cache_read':>10} {'output':>7} {'cache_read%':>11}"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    tot = dict(calls=0, tools=0, inp=0, cw=0, cr=0, out=0, secs=0.0)
    for n, (meta, s) in enumerate(subs, 1):
        print(f"  {n:>2}  {(meta.get('agentType') or '?')[:16]:<16} {(meta.get('description') or '')[:30]:<30} "
              f"{short_model(s['models'])[:14]:<14} {dur(s['secs']):>6} {s['calls']:>5} {s['tools']:>5} "
              f"{k(s['inp']):>7} {k(s['cw']):>11} {k(s['cr']):>10} {k(s['out']):>7} {share(s):>11}")
        for key in tot:
            tot[key] += s[key]
    if subs:
        print("  " + "-" * (len(hdr) - 2))
        print(f"  {'':>2}  {'ALL SUBAGENTS':<16} {'':<30} {'':<14} {dur(tot['secs']):>6} {tot['calls']:>5} "
              f"{tot['tools']:>5} {k(tot['inp']):>7} {k(tot['cw']):>11} {k(tot['cr']):>10} {k(tot['out']):>7} "
              f"{share(tot):>11}")
    print(f"  {'':>2}  {'MAIN THREAD':<16} {'(you)':<30} {short_model(ms['models'])[:14]:<14} {dur(ms['secs']):>6} "
          f"{ms['calls']:>5} {ms['tools']:>5} {k(ms['inp']):>7} {k(ms['cw']):>11} {k(ms['cr']):>10} "
          f"{k(ms['out']):>7} {share(ms):>11}")
    if not subs:
        tok = ms["inp"] + ms["cw"] + ms["cr"] + ms["out"]
        print(f"\n  Tokens: {k(tok)}, all in the main thread.")
        print(f"  Your context at the end: {k(ms['last_ctx'])} tokens (peak {k(ms['max_ctx'])}).")
        return
    # Wall time actually spent in subagents (overlapping runs counted once) vs the sum.
    spans = sorted((s["first"], s["last"]) for _, s in subs if s["first"] and s["last"])
    wall, cur = 0.0, None
    for a, b in spans:
        if cur and a <= cur[1]:
            cur = (cur[0], max(cur[1], b))
        else:
            if cur:
                wall += (cur[1] - cur[0]).total_seconds()
            cur = (a, b)
    if cur:
        wall += (cur[1] - cur[0]).total_seconds()
    sub_tok = tot["inp"] + tot["cw"] + tot["cr"] + tot["out"]
    main_tok = ms["inp"] + ms["cw"] + ms["cr"] + ms["out"]
    longest = max(subs, key=lambda x: x[1]["secs"])
    cw5 = sum(s["cw5"] for _, s in subs); cw1h = sum(s["cw1h"] for _, s in subs)
    print()
    if wall:
        print(f"  Subagents ran {dur(tot['secs'])} in total, {dur(wall)} on the clock "
              f"({tot['secs'] / wall:.1f}x in parallel).")
    print(f"  Longest: #{subs.index(longest) + 1} {(longest[0].get('description') or '')[:40]} "
          f"({dur(longest[1]['secs'])}).")
    print(f"  Tokens: subagents {k(sub_tok)} vs main thread {k(main_tok)} "
          f"-> {100 * sub_tok / (sub_tok + main_tok):.0f}% of this session ran in subagents.")
    print(f"  Your context at the end: {k(ms['last_ctx'])} tokens (peak {k(ms['max_ctx'])}). "
          f"The subagents' reads are not in it.")
    if cw5 + cw1h:
        print(f"  Subagent cache writes: {100 * cw5 / (cw5 + cw1h):.0f}% are 5-minute cache "
              f"(the main thread usually writes 1-hour cache).")


def sessions(root: Path) -> list[Path]:
    return sorted((p for p in root.glob("*/*.jsonl")), key=lambda p: p.stat().st_mtime, reverse=True)


def in_cwd(p: Path, here: str) -> bool:
    for r in read_jsonl(p):
        c = r.get("cwd")
        if c:
            return c == here or c.startswith(here.rstrip(os.sep) + os.sep)
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("session", nargs="?", help="session id (prefix is fine)")
    ap.add_argument("--last", type=int, default=0, help="show the N newest sessions here")
    ap.add_argument("--root", type=Path, default=ROOT, help="log folder (default ~/.claude/projects)")
    a = ap.parse_args()
    if not a.root.is_dir():
        print(f"No Claude Code logs in {a.root}")
        return 1
    alls = sessions(a.root)
    if a.session:
        hit = [p for p in alls if p.stem.startswith(a.session)]
        if not hit:
            print(f"No session {a.session!r} under {a.root}")
            return 1
        report(hit[0])
        return 0
    here = os.getcwd()
    mine = [p for p in alls if in_cwd(p, here)]
    picked = mine[: max(a.last, 1)]
    if not picked:
        print(f"No Claude Code session started in {here} or below.\n"
              f"Run this from the folder where you started claude, or pass a session id.")
        return 1
    for p in reversed(picked):  # oldest first, so run A is printed above run B
        report(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
