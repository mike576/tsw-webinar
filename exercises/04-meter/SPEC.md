# SPEC: my Claude Code meter

## Input
A folder of Claude Code session logs (`*.jsonl`, searched recursively).

## Output (edit this list: keep what you need, add what you want)
- [ ] Tokens per day: fresh input, cache write, cache read, output
- [ ] Cache-read share = cache_read / (input + cache_write + cache_read)
- [ ] Split by model
- [ ] The 5 most expensive sessions
- [ ] Sessions where cache read dropped to 0 in the middle (a cache break: model switch, /compact ...)

## Rules
- Dedupe API calls on `message.id` + `requestId`.
- Python 3 standard library only.

## Known facts about sample-logs/ (use them in the tests)
- 3 sessions, 32 unique API calls (more lines than that: duplicates)
- `bbbb2222-switch`: model changes from sonnet-5-5 to opus-5-5 at call 6, cache read is 0 there
- `cccc3333-compact`: cache read is 0 at call 7 (the /compact)
- Cache-read share: aaaa1111 90.9%, bbbb2222 78.9%, cccc3333 81.2%
