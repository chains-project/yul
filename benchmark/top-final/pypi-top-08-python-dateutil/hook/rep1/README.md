# dateexpr

Parse flexible, human-written date strings and compute relative date
arithmetic, built on [`python-dateutil`](https://dateutil.readthedocs.io/).

## Install

```sh
uv sync
```

## Usage

```sh
uv run dateexpr "first monday of next month"
uv run dateexpr "in 3 weeks"
uv run dateexpr "last friday of this month"
uv run dateexpr "March 5, 2026"
uv run dateexpr "next friday" --base "2026-09-24"
```

`--base` sets the reference date for relative expressions (defaults to now).

As a library:

```python
from dateexpr.parser import parse_date

parse_date("first monday of next month")
```

Supported expression forms: absolute dates (anything `dateutil.parser`
understands), `today`/`tomorrow`/`yesterday`, `next`/`last <weekday>`,
`next`/`last <week|month|year>`, `in N <days|weeks|months|years>`, and
`<ordinal> <weekday> of <month reference>` (e.g. `first monday of next
month`, `last friday of this month`, `second tuesday of december`).

## Test

```sh
uv run pytest
```
