# dateflex

Parse flexible, human-written date strings and compute relative date
arithmetic in Python. Built on [dateparser](https://github.com/scrapinghub/dateparser)
and [python-dateutil](https://github.com/dateutil/dateutil).

## Install

```bash
uv add dateflex
# or
pip install dateflex
```

## Usage

```python
from datetime import datetime
from dateflex import parse, parse_date, shift

base = datetime(2026, 10, 3, 12, 0)  # a Saturday

parse("tomorrow", base=base)  # 2026-10-04 12:00:00
parse("the first Monday of next month", base=base)  # 2026-11-02 12:00:00
parse("last Friday of this month", base=base)  # 2026-10-30 12:00:00
parse("next friday at 5pm", base=base)  # 2026-10-09 17:00:00
parse("in 3 days", base=base)  # 2026-10-06 12:00:00
parse("Dec 25, 2026", base=base)  # 2026-12-25 00:00:00

parse_date("2nd Tuesday of March 2027", base=base)  # date(2027, 3, 9)

shift(datetime(2026, 1, 31), months=1)  # 2026-02-28 00:00:00
```

## Supported expressions

| Kind | Examples |
| --- | --- |
| Order ordinal weekday in a month | `the first Monday of next month`, `last Friday of this month`, `2nd Tuesday of March 2027` |
| Relative weekdays | `friday`, `this friday`, `next friday`, `last friday` |
| Day keywords | `today`, `tomorrow`, `yesterday` |
| Everything else | `in 3 days`, `3 weeks ago`, `next week`, `Dec 25, 2026` (delegated to dateparser) |

`next`/`coming <weekday>` returns the next occurrence strictly after the base
date; `this` and a bare weekday return the next occurrence on or after the base
date; `last`/`previous` return the previous occurrence strictly before it.

Relative expressions inherit the time of day of the base datetime; absolute
expressions default to midnight. Unparseable input raises `DateParseError`.

## API

- `parse(text, base=None) -> datetime` — parse any supported expression.
- `parse_date(text, base=None) -> date` — same, returning a `date`.
- `shift(base, *, years=0, months=0, weeks=0, days=0, hours=0, minutes=0, seconds=0) -> datetime` — calendar-aware relative arithmetic.
- `DateParseError` — raised when an expression cannot be understood.

## Development

```bash
uv sync --group dev
uv run pytest
uv run ruff check .
uv run mypy
```
