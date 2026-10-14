# worldtime

Timezone-aware datetime utilities built on the standard-library `zoneinfo`
module (Python 3.9+), with the `tzdata` package as a dependency so the IANA
database is available on every platform, including Windows.

## Setup

```sh
uv sync
uv run pytest
uv run worldtime                              # default set of world cities
uv run worldtime Europe/Berlin Asia/Singapore
```

## Conventions

- Always use aware datetimes; helpers raise `NaiveDatetimeError` on naive input.
- Store and compare in UTC; convert to local zones only for display.
- Use IANA names (`Europe/Paris`), never abbreviations (`CET`, `IST` are ambiguous).
- Use `fold=1` to select the second occurrence of a repeated wall-clock time at DST fall-back.
