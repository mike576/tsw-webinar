# Practice 1 + 2 · Context and the cache, measured (09:35–10:35)

`usage.csv` is a synthetic LLM API usage export (4,300 rows), `prices.csv` the price list.

## Part A: read, extract, measure (Practice 1, 09:35)
Start a fresh session here: `cd exercises/02-context && claude`, then `/model sonnet`.

1. `/context` and write down the total.
2. Ask: **"Read usage.csv and prices.csv. Which model is responsible for most of the cost? Rough numbers are fine."**
3. `/context` again. What grew?
4. Ask three more questions about the same file, one by one:
   - "Which workspace spent the most?"
   - "Which day was the busiest?"
   - "How much of the input came from the cache?"
5. In a second terminal, in the repo root: `python3 tools/cc_meter.py` won't find this session
   (it looks at the current folder), so run it from here: `python3 ../../tools/cc_meter.py`.
   Look at `cr` (cache read) and `in` (fresh input) turn by turn.

## Part B: the experiment (Practice 2, 10:20)
Half the room (odd seat number in Zoom) runs **`/compact`**, the other half presses **Esc Esc**
and rewinds to before the last question. Then everyone asks:
"Which model had the highest output-token share?"

Run the meter again and post in the chat: **cw and cr of your last turn**.

## Part C: discuss (10 min)
What is your cache-read share? Ours, over a month of daily work, is 97.7%.

## Stretch
`TASK.md` is the full audit task from our model benchmark (12 numbers, graded by hidden tests).
