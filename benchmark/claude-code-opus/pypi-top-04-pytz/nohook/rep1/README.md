# worldtime

Utilities and a small CLI for timezone-aware datetimes across world regions.

## Setup

```sh
uv sync            # creates .venv, installs deps + dev tools
uv run worldtime   # current time in a default set of zones
uv run worldtime Asia/Singapore Pacific/Auckland
uv run pytest
uv run ruff check .
```

## Conventions

- Use IANA zone names (`Europe/Paris`), never abbreviations (`CET`, `IST` are ambiguous) or fixed offsets for regions.
- Never create naive datetimes: use `datetime.now(tz)`, not `datetime.now()` / `utcnow()`. Ruff's `DTZ` rules enforce this.
- Store/compare in UTC; convert to local zones at the edges (input parsing, display).
- Wall-clock times near DST transitions can be ambiguous (use `fold`) or nonexistent (check with `is_valid_local`).
- Timezone rules change; keep `tzdata` up to date.
