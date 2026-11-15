# Task

You are auditing an LLM API bill. `usage.csv` is the raw usage export, one row
per API request; `prices.csv` is the price list in USD per million tokens.

Compute the figures below and write them to **`answers.json`** in this directory
(a single JSON object with exactly these keys). Python 3.12 with the standard
library is available (no third-party packages).

## Rules for reading the export

- Each request has a `request_id`. The export contains some requests **more
  than once** (exact duplicate rows) — count every request exactly once.
- Model names may carry a date suffix (`-YYYYMMDD`), different letter case, or
  surrounding whitespace. Normalise them to the names used in `prices.csv`.
- A model that is not in `prices.csv` is **unpriced**: exclude its requests from
  every cost and token figure below, and never guess its price.
- Empty token cells mean 0.
- `timestamp` is ISO 8601 with a UTC offset. **Days and months are UTC** — convert
  before grouping.
- Token classes are priced as follows (all relative to the model's prices):

| column | price |
|---|---|
| `input_tokens` | input price |
| `cache_write_5m` | 1.25 × input price |
| `cache_write_1h` | 2 × input price |
| `cache_read` | 0.1 × input price |
| `output_tokens` | output price |

## Keys of `answers.json`

| key | type | meaning |
|---|---|---|
| `total_cost_usd` | number | total cost of all priced requests |
| `cost_by_month` | object | `{"YYYY-MM": cost}` for every month present (priced requests) |
| `cost_by_model` | object | `{normalised model name: cost}` for every priced model present |
| `top_workspace` | string | the workspace with the highest cost |
| `busiest_day` | string | the UTC day (`YYYY-MM-DD`) with the highest cost |
| `duplicate_rows_removed` | integer | rows dropped because their `request_id` was already seen |
| `unpriced_requests` | integer | unique requests whose model is unpriced |
| `unpriced_models` | array | the normalised unpriced model names, sorted alphabetically |
| `cache_read_share` | number | `cache_read / (input_tokens + cache_write_5m + cache_write_1h + cache_read)`, summed over priced requests (0–1) |
| `output_cost_share` | number | share of `total_cost_usd` that comes from output tokens (0–1) |
| `cost_without_cache_usd` | number | what the priced requests would have cost if every cache-write and cache-read token had been billed at the plain input price |
| `savings_batch_jobs_to_sonnet_usd` | number | for workspace `batch-jobs` only: how much less its `claude-opus-5` requests would have cost at `claude-sonnet-5` prices (same tokens) |

Numbers are checked with a 0.1% relative tolerance; do not round shares to
fewer than 4 decimal places.
