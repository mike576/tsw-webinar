# Block 4 · Build your own meter (11:20–11:55)

Every Claude Code call is logged on your own machine in `~/.claude/projects/**/*.jsonl`.
One line per content block; assistant lines carry `message.usage`:
`input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `output_tokens`,
plus `message.model`, `message.id`, `requestId`, `timestamp`, `sessionId`.
**Gotcha:** the same API call appears on 2–3 lines. Dedupe on `message.id` + `requestId`.

## Do it with Claude Code, using what you learned this morning
1. `cd exercises/04-meter && claude`, `/model sonnet`.
2. Fill in `SPEC.md` (5 min, by hand or with Claude). Keep it short.
3. **Tests first, hooks off:** ask Claude to write `tests/test_meter.py` against `sample-logs/`,
   using the known facts in `SPEC.md`. (They will fail: there is no `meter.py` yet.)
4. **Now lock the tests:** `/exit`, then
   `mkdir -p .claude && cp ../03-hooks/hook-configs/step2-guard-and-stop.json .claude/settings.local.json`
   and start a new session.
5. Ask: "Write meter.py per SPEC.md so the tests in tests/ pass." The guard keeps the tests
   as you wrote them; the Stop hook keeps Claude working until they pass.
6. Run it on your real logs: `python3 meter.py ~/.claude/projects`

**Post one number in the chat: your own cache-read share.**

Did not finish? `python3 ../../tools/cc_meter.py --days --all` is our version.
