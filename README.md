# Claude Code like a pro — practice repo

TSW Academy workshop, Thursday 19 November 2026, 09:00–12:00 CET.
Everything here is plain Python 3 (standard library only) so it runs on any laptop.

## Before Thursday (5 minutes)

1. `git --version` and `python3 --version` (3.10 or newer) work in your terminal.
   Windows: use WSL or Git Bash.
2. Claude Code is installed: `claude --version` ([setup guide](https://code.claude.com/docs/en/setup)).
3. You are logged in: start `claude`, run `/status`. A Pro, Max, Team or Enterprise
   subscription, or an Anthropic API key, all work.
4. Clone this repo and check the meter runs:
   ```
   git clone <repo-url> claude-code-like-a-pro
   cd claude-code-like-a-pro
   python3 tools/cc_meter.py --days --all
   ```
   You should see a table of your past Claude Code usage (or "No session logs" if you are new; that is fine).

## What is in here

| Folder | Practice | What you do |
|---|---|---|
| `exercises/01-setup` | 1 · 09:35 | Get running, look at `/context` before you type anything |
| `exercises/02-context` | 1–2 · 09:35 / 10:20 | Read a 4,300-row usage export, ask questions, watch the cache in the log |
| `exercises/03-hooks` | 3 · 10:55 | Make the agent build a cron parser and stop it from weakening the tests |
| `exercises/04-meter` | 4 · 11:20 | Build your own meter for your own Claude Code logs |
| `exercises/bonus-bugfix` | spare | A small bug-fix task if you finish early |
| `tools/cc_meter.py` | 2–4 | Our ready meter: turn-by-turn token use from your local logs |
| `hook-pack/` | take home | The hooks from block 3 + an example `settings.json` |
| `CLAUDE.md` | take home | A short CLAUDE.md template |

## Keep your limit safe

The exercises are sized for a Pro plan. Use **Sonnet 5.5** for them (`/model sonnet`).
Do not switch models in the middle of a session; you will see why in block 2.
