# Practice 3 · Hooks are rules, CLAUDE.md is a request (25 min)

The task: `next_run()` in `cronnext.py`, specified in `TASK.md` (a cron "when does this run next?"
function). `tests/` has 3 example tests. The trainer has 36 hidden ones.

## How hooks are switched on (read this first)

A hook is a small script that Claude Code runs **itself**, at a fixed moment, outside the model:

| Moment | Hook | What it does here |
|---|---|---|
| before every tool call (`PreToolUse`) | `../../hook-pack/tests_guard.py` | blocks any edit under `tests/` |
| when Claude wants to finish (`Stop`) | `../../hook-pack/stop_until_green.py` | runs the tests; if they fail, sends Claude back to work |

Which hooks are active is decided by **one file**: `exercises/03-hooks/.claude/settings.local.json`.
It does not exist yet. In every step you **copy** one of the ready configs from `hook-configs/`
over it. Nothing else to edit.

```
exercises/03-hooks/
├── .claude/settings.local.json   <- the active config (you create it with cp)
├── hook-configs/                 <- 3 ready configs, one per step
├── cronnext.py                   <- the code Claude writes
└── tests/test_examples.py        <- protected by the guard
```

Three rules that make it work:
1. **Run everything in `exercises/03-hooks`.** Start `claude` there, not in the repo root, or the
   config is not found and no hook runs.
2. **Hooks are read when a session starts.** After every `cp`: `/exit`, then `claude` again.
3. **Check with `/hooks`** inside Claude Code. You should see `PreToolUse` (and in steps 2–4 `Stop`)
   with a `python3 ...hook-pack/...` command. Nothing listed = wrong folder or old session.

Every new session: `/model sonnet`.

## Step 1: the guard (7 min)
```
cd exercises/03-hooks
mkdir -p .claude && cp hook-configs/step1-guard.json .claude/settings.local.json
claude
```
`/model sonnet`, `/hooks` (PreToolUse is listed). Then ask:
**"Change tests/test_examples.py so that test_bad_minute expects 61 instead of 60."**

**Expect:** Claude tries the edit, the hook blocks it, and Claude tells you it can't change a test
file. `git diff` shows nothing changed. Then read `../../hook-pack/tests_guard.py`: ~40 lines,
zero context cost, and it blocks even with `--dangerously-skip-permissions`.

## Step 2: do not stop until green, exit 2 (8 min)
`/exit`, then:
```
cp hook-configs/step2-guard-and-stop.json .claude/settings.local.json
claude
```
`/model sonnet`, `/hooks` (now `Stop` is listed too). Ask:
**"Implement only the @-macros (@daily, @hourly ...) of next_run, nothing else, then stop."**

The 3 example tests need the full parser, so they keep failing. **Expect:** every time Claude tries to
finish, you see a "Stop hook" message with the failing tests and Claude starts again. After 3 tries the
hook gives up, so it cannot burn your limit. Claude usually ends with "the hook keeps blocking,
should I implement the full spec?"

Measure in a **second terminal**, in the same folder: `python3 ../../tools/cc_meter.py`.
Count the API calls (rows). Our dry run: 9–20 calls.

## Step 3: the exit-code trap (5 min)
`/exit`, then:
```
git checkout -- cronnext.py
cp hook-configs/step3-exit1-mistake.json .claude/settings.local.json
claude
```
`/model sonnet`, same prompt as step 2. The hook script is identical, except it exits with **1**.

**Expect:** Claude writes the macros and **stops with failing tests**. Nothing sends it back:
exit 1 is a "non-blocking error" in Claude Code. Measure again: far fewer calls than step 2,
and the tests are red. That is the bug most people ship in their first hook.

## Step 4: the real thing (5 min)
`/exit`, then:
```
git checkout -- cronnext.py
cp hook-configs/step2-guard-and-stop.json .claude/settings.local.json
claude
```
`/model sonnet`, then: **"Read TASK.md and implement next_run. Work until it is done."**

Check yourself: `python3 -m unittest discover -s tests -v` (3 example tests).
Then paste your `cronnext.py` into the Zoom chat: the trainer runs the 36 hidden tests.
Our dry run (Sonnet 5.5): 36/36 in 4 turns.

## If something does not work
- **`/hooks` shows nothing:** you started `claude` in the wrong folder, or you did not restart after `cp`.
- **"python3: command not found" in a hook message (Windows):** run Claude Code inside WSL.
- **Claude edits the test anyway:** check `.claude/settings.local.json` is the step 1 or step 2 config.
- **Start over:** `git checkout -- cronnext.py tests/` and `rm -r .claude`.

Take home: `../../hook-pack/` (guard, stop-until-green, a formatter stub, `settings.example.json`).
