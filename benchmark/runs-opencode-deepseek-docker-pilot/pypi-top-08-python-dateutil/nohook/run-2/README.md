# datephrase

Parse flexible, human-written date strings and compute relative date
arithmetic such as *"the first Monday of next month"*.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Library usage

```python
from datetime import datetime
from datephrase import parse, parse_date

base = datetime(2026, 9, 29, 12, 0, 0)

parse("the first Monday of next month", base=base)  # 2026-10-05 12:00:00
parse("last Friday of this month", base=base)        # 2026-09-25 12:00:00
parse("in 3 days", base=base)                        # 2026-10-02 12:00:00
parse_date("2 weeks ago", base=base)                 # 2026-09-15
```

Supported phrases include:

- Ordinal weekdays: `first Monday of next month`, `last Friday of this month`,
  `third Thursday of November 2027`, `fifth Sunday of next month` (returns
  `None` when that occurrence does not exist).
- Relative weekdays: `next Monday`, `last Friday`, `this Monday`.
- Relative periods: `this month`, `next week`, `last year`.
- Everything else is delegated to [`dateparser`](https://dateparser.readthedocs.io/),
  e.g. `tomorrow`, `in 3 days`, `2 weeks ago`, `January 2027`.

`parse` returns a `datetime` (or `None` if the phrase is not understood) and
accepts an optional `base` reference date/time, defaulting to now.

## CLI usage

```bash
$ datephrase --base 2026-09-29 "the first Monday of next month"
2026-10-05

$ printf 'next Friday\nin 2 weeks\n' | datephrase -b 2026-09-29
2026-10-02
2026-10-13
```

Run the tests with:

```bash
pytest
```
