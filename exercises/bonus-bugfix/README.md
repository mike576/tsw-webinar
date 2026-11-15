# invoicing

Small helpers used by our billing service. All money is handled as **integer cents**.
This README is the specification; the code must behave exactly as described here.

## `split_amount(total_cents, weights) -> list[int]`

Splits `total_cents` into parts proportional to `weights`.

- The parts are integers and **always sum exactly to `total_cents`**.
- Uses the largest-remainder method: every part first gets the floor of its exact
  share, then the leftover cents go one each to the parts with the largest
  fractional remainder. Ties are broken in favour of the **lower index**.
- `total_cents` must be `>= 0`, every weight must be `>= 0`, and at least one
  weight must be positive; otherwise `ValueError`.

Example: `split_amount(100, [1, 1, 1]) == [34, 33, 33]`.

## `business_days(start, end, holidays=()) -> int`

Number of business days `d` with `start <= d < end` (end is **exclusive**).
A business day is Monday–Friday that is not in `holidays`. A holiday that falls on
a weekend or outside the range changes nothing, and listing the same holiday twice
counts it once. If `end <= start` the result is `0`.

## `parse_amount(text) -> int`

Parses a human-typed amount and returns cents.

- Optional currency code (`EUR`, `USD`, `HUF`, `GBP`, any case) before or after
  the number, optional leading `-`, spaces anywhere in the number are ignored.
- Both `.` and `,` may be used as thousands or decimal separators. The rule: the
  **last** separator in the number is the decimal separator **if and only if it is
  followed by exactly one or two digits**. Every other separator is a thousands
  separator. So `"1,234.56"` and `"1.234,56"` are both 123456 cents, `"12,5"` is
  1250 cents, and `"1,234"` and `"1.234"` are both 123400 cents.
- Anything else (empty string, letters, two minus signs, no digits) raises
  `ValueError` — never any other exception type.

## `apply_discounts(subtotal_cents, discounts) -> int`

`discounts` is a list of `(kind, value)` tuples, `kind` is `"percent"` or `"fixed"`.

- **All percentage discounts are applied first** (in the order given, each on the
  running amount), then all fixed discounts (in the order given).
- After each percentage step the amount is rounded to whole cents, **half up**
  (e.g. 12.5 cents -> 13 cents).
- The result is never negative: it is clamped at `0`.
- An unknown `kind` raises `ValueError`.

## `late_fee(days_late, amount_cents) -> int`

| days late | fee |
|---|---|
| `<= 0` | 0 |
| 1 – 30 | 2 % of the amount |
| 31 – 60 | 5 % of the amount |
| 61 or more | 10 % of the amount |

The fee is rounded to whole cents half up, then: if it is positive it is **at
least 100 cents**, and it is **never more than 5000 cents**.
