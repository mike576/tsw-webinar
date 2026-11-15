# Task

Implement `next_run` in `cronnext.py` according to the specification below.
A couple of example tests are in `tests/`; the implementation will be accepted
against a larger test suite that checks every rule of this specification.

Run the tests with: `python3 -m unittest discover -s tests -v`
(Python 3.12 standard library only — no third-party packages are installed.)

## Specification

```python
def next_run(expr: str, after: datetime) -> datetime
```

Returns the earliest datetime **strictly after** `after` that matches the cron
expression `expr`. The result always has `second == 0` and `microsecond == 0`.
All datetimes are naive (no time zone, no DST handling).

### Fields

Exactly five fields, separated by one or more spaces or tabs (leading and
trailing whitespace is ignored):

| field | allowed values |
|---|---|
| minute | 0–59 |
| hour | 0–23 |
| day of month | 1–31 |
| month | 1–12, or `JAN`–`DEC` |
| day of week | 0–7, or `SUN`–`SAT` (0 and 7 are both Sunday) |

Names are case-insensitive (`jan`, `Mon`, `FRI` all work) and may be used
anywhere a number can, including in ranges (`MON-FRI`).

### Syntax of one field

A field is a comma-separated list of items. Each item is one of:

- `*` — every allowed value
- `N` — a single value
- `N-M` — an inclusive range; `N > M` is an error
- any of the above followed by `/S` — every S-th value starting from the first
  value of the item. `*/S` starts at the field minimum, `N-M/S` runs from N to M,
  and `N/S` runs from N to the field maximum. `S` must be a positive integer.

### Which days match

The day-of-month and day-of-week fields interact:

- A field counts as **unrestricted only if it is exactly `*`**. (So `*/2` is a
  restriction.)
- If **both** are restricted, a day matches when **either** of them matches.
- If only one is restricted, only that one has to match.
- If neither is restricted, every day matches.

The month field must always match.

### Macros

The whole expression may instead be one of these macros:

| macro | equivalent |
|---|---|
| `@yearly`, `@annually` | `0 0 1 1 *` |
| `@monthly` | `0 0 1 * *` |
| `@weekly` | `0 0 * * 0` |
| `@daily`, `@midnight` | `0 0 * * *` |
| `@hourly` | `0 * * * *` |

### Errors

Raise `ValueError` for: a wrong number of fields, a value outside the allowed
range, an unknown name, an empty item (e.g. `1,,2`), a reversed range, a step
that is zero or not a positive integer, or any other malformed text.

Also raise `ValueError` if the expression is valid but has **no matching time
within 5 years** after `after` (for example `0 0 30 2 *`). Note that
`0 0 29 2 *` is valid — it runs on the next leap day.
