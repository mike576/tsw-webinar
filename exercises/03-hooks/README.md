# Block 3 · Hooks are rules, CLAUDE.md is a request (10:40–11:20)

The task: implement `next_run()` in `cronnext.py` from the spec in `TASK.md`.
`tests/` has 3 example tests. The trainer has 36 hidden ones.

Hooks are switched on by copying a config to `.claude/settings.local.json` in this folder.
After copying, start a **new** session (`claude`), `/model sonnet`, and check with `/hooks`.

## Step 1: the guard (8 min)
```
mkdir -p .claude && cp hook-configs/step1-guard.json .claude/settings.local.json
```
Ask Claude: **"Change tests/test_examples.py so that test_bad_minute expects 61 instead of 60."**
Watch the hook stop it. Read `../../hook-pack/tests_guard.py`: 30 lines, zero context cost.

## Step 2: do not stop until green (12 min)
```
cp hook-configs/step2-guard-and-stop.json .claude/settings.local.json
```
New session, then: **"Read TASK.md and implement next_run. Work until it is done."**
The Stop hook runs the tests every time Claude wants to finish, and sends it back if they fail
(at most 3 times, so it cannot burn your limit).

## Step 3: the exit-code trap (5 min)
`hook-configs/step3-exit1-mistake.json` uses the same Stop hook, but it exits with **1**.
Reset the code (`git checkout -- cronnext.py`), copy step 3's config, start a new session, run Step 2's prompt again, and see that nothing stops.
Exit 1 is a non-blocking error in Claude Code. Use exit 2.

## Measure
`python3 ../../tools/cc_meter.py --sessions`: how many more calls and tokens did the Stop hook cost?
Post your branch in the chat and the trainer runs the 36 hidden tests.

Take home: `../../hook-pack/` (guard, stop-until-green, a formatter stub, `settings.example.json`).
