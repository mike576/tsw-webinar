# Subagents, part 2 · Send scouts, keep your context (15 min)

Anna is happy with the numbers. Now she has a new colleague starting on Monday and asks you:
*"Can you tell them what the hooks in this repo do, and which exercise uses which?"*

You will answer twice: once reading everything yourself (run A), once sending subagents (run B).
Then you measure what each run cost and how long the subagents ran.

Work from the **repo root** (`claude-code-like-a-pro/`), not from this folder.

## Step 1: start clean (1 min)
```
cd claude-code-like-a-pro
claude
/model sonnet
```

## Step 2: run A, no subagents (4 min)
Ask:
**"Do not use subagents. Read every file in exercises/03-hooks, hook-pack and tools yourself.
Then answer in 8 lines: what does each hook do, and which exercise uses it?"**

When it is done: `/context`. Write down the total. That is run A.

## Step 3: run B, three subagents in parallel (4 min)
`/clear` (this starts a new session, so A and B are logged separately), then ask:
**"Use 3 Explore subagents in parallel: one for exercises/03-hooks, one for hook-pack, one for
tools. Each one reports back in at most 5 lines. Then give me the same 8-line answer."**

While it runs, you see each subagent and its tool calls live in the terminal.
When it is done: `/context`. Write down the total. That is run B.

## Step 4: the statistics (4 min)
In a **second terminal**, in the same repo root:
```
python3 tools/subagent_stats.py --last 2
```
You get one table per run. For every subagent: type, description, model, **how long it ran**,
API calls, tool calls, and tokens (input, cache write, cache read, output). Below it:

- how long the subagents ran in total vs on the clock (= how parallel they were),
- the longest subagent,
- what share of the tokens ran in subagents,
- your own context at the end: the subagents' file reads are **not** in it,
- how much of the subagent cache is the 5-minute kind.

**Post in chat:** `/context` A vs B · your longest subagent (seconds) · % of tokens in subagents

## What to look for
- **Your context is smaller in B.** The subagents read the files; you only got their 5 lines.
- **The total is usually higher in B.** Each subagent starts with its own system prompt and tools,
  and its cache lives only 5 minutes. A subagent saves *context*, not tokens.
- **Use them when** the reading is big and the answer is small: searching a large repo, reading
  logs, comparing many files. **Skip them** for a 2-file question.

## Bonus (if you have time)
`/clear`, then: **"Use one Haiku subagent to count the rows per workspace in
exercises/02-context/usage.csv, then tell me the result."** Run the stats again and look at the
model column.

Other options: `python3 tools/subagent_stats.py` (newest session only),
`python3 tools/subagent_stats.py <session-id>` (any session, a prefix is enough).
