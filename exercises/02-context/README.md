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
5. Open a **second terminal** and go to the same folder, then run the meter from there:
   ```
   cd claude-code-like-a-pro/exercises/02-context
   python3 ../../tools/cc_meter.py
   ```
   (The meter shows the newest session of the folder you run it in, so run it from
   `exercises/02-context`, not from the repo root.)
   Look at `cache_read` and `cache_write` turn by turn: `cache_read` grows every turn,
   `cache_write` stays small. `input` is always ~2 per call; that is normal, Claude Code caches everything.

## Part B: the experiment (Practice 2, 10:20)
Stay in the **same** Claude Code session as Part A. Split the room by first name:

- **First name A–M:** type **`/compact`** and wait until it is done.
- **First name N–Z:** press **Esc twice** on an empty prompt. A list of your earlier messages
  appears: pick the one **before your last question** and restore the conversation.

Then everyone asks: **"Which model had the highest output-token share?"**

Run the meter again in the second terminal (`python3 ../../tools/cc_meter.py`). Find the **first row
after** your /compact or Esc Esc (the first call of the new question) and post in the chat:
**/compact or Esc Esc, plus `cache_write` and `cache_read` of that row.**

What to expect (our dry run, Sonnet 5.5):
- **/compact:** `cache_read` drops (39k → 13k) and `cache_write` jumps (3k → 12k). The summary is a
  prefix the cache has never seen, so it is written again at full weight.
- **Esc Esc:** `cache_read` stays high and `cache_write` stays small. You jumped back to a prefix
  that is already in the cache.

## Part C: discuss (10 min)
What is your cache_read share? Ours, over a month of daily work, is 97.7%.

## Stretch
`TASK.md` is the full audit task from our model benchmark (12 numbers, graded by hidden tests).
