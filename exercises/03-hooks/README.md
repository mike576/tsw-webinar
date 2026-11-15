# Block 3 · Hooks are rules, CLAUDE.md is a request (10:40–11:20)

The task: `next_run()` in `cronnext.py`, specified in `TASK.md`.
`tests/` has 3 example tests. The trainer has 36 hidden ones.

Hooks are switched on by copying a config to `.claude/settings.local.json` in this folder.
After every copy, start a **new** session (`claude`), `/model sonnet`, and check with `/hooks`.

## Step 1: the guard (7 min)
```
mkdir -p .claude && cp hook-configs/step1-guard.json .claude/settings.local.json
```
Ask: **"Change tests/test_examples.py so that test_bad_minute expects 61 instead of 60."**
The hook stops the edit, and Claude tells you why. Read `../../hook-pack/tests_guard.py`:
30 lines, zero context cost, and it blocks even with `--dangerously-skip-permissions`.

## Step 2: do not stop until green (8 min)
```
cp hook-configs/step2-guard-and-stop.json .claude/settings.local.json
```
Ask: **"Implement only the @-macros (@daily, @hourly ...) of next_run, nothing else, then stop."**
The example tests need the full parser, so they fail. Each time Claude tries to stop, the Stop
hook runs the tests and sends it back (exit 2). It gives up after 3 tries, so it cannot burn your limit.
Measure: `python3 ../../tools/cc_meter.py`. How many API calls?

## Step 3: the exit-code trap (5 min)
```
git checkout -- cronnext.py
cp hook-configs/step3-exit1-mistake.json .claude/settings.local.json
```
New session, same prompt. The hook is identical, except that it exits with **1**.
Claude stops with failing tests, and nothing tells it otherwise. Exit 1 is a non-blocking error
in Claude Code. Measure again and compare.

## Step 4: the real thing (5 min)
`git checkout -- cronnext.py`, step 2 config, new session:
**"Read TASK.md and implement next_run. Work until it is done."**
Then paste your `cronnext.py` to the trainer: we run the 36 hidden tests.

Take home: `../../hook-pack/` (guard, stop-until-green, a formatter stub, `settings.example.json`).
