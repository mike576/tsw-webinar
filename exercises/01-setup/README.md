# Practice 1 · Setup and your zero point (09:35–10:05)

1. `cd exercises/02-context && claude`
2. `/model sonnet` (the exercises are sized for Sonnet 5.5 on a Pro plan)
3. Optional but recommended: `/statusline show context size and session cost`
4. Before you type anything: **`/context`**. Write down the total. This is what every
   single turn costs you before you have asked anything.
5. Ask one thing: `What is in this folder? One sentence.`
6. Exit (`/exit`), go back to the repo root and run:
   ```
   python3 tools/cc_meter.py --sessions --all | tail -3
   ```
   Find your session. Note `cw` (cache write) and `cr` (cache read).

Post in the chat: your `/context` total from step 4.
