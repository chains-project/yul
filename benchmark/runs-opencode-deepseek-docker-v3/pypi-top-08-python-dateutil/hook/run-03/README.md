# flexdate

Parse flexible, human-written date strings and compute relative date
arithmetic — including phrases that most libraries get wrong, such as
`"the first Monday of next month"`.

## Why this exists

`dateparser` returns `None` and `parsedatetime` silently ignores the
`"first Monday"` part for ordinal-weekday phrases. `flexdate` resolves those
phrases itself and falls back to `dateparser` for everything else.

## Install

```bash
uv sync          # or: pip install -e .
```

## Usage

```python
from datetime import datetime
from flexdate import parse, parse_date, shift

parse("the first Monday of next month")        # datetime(2026, 11, 2, 0, 0)
parse("last Friday of March 2027")             # datetime(2027, 3, 26, 0, 0)
parse("tomorrow at 5pm")                       # dateparser fallback
parse_date("in 3 weeks")

# anchor relative phrases to a fixed moment (handy in tests)
parse("first Monday of next month", base=datetime(2026, 10, 3))

# relative arithmetic on any date/datetime
shift(date(2026, 10, 31), months=1)            # date(2026, 11, 30)
```

### Command line

```bash
$ flexdate "the first Monday of next month"
2026-11-02
$ flexdate -f "%A %d %B %Y" "last Friday of March 2027"
Friday 26 March 2027
```

## Supported ordinal phrases

`first`…`fifth`, `1st`…`5th`, and `last`, followed by a weekday, optionally
followed by `of <period>`. Periods: `this month`, `next month`, `last month`,
a month name, or a month name plus a year (e.g. `March 2027`). With no period
the current month is used.

## Development

```bash
uv run pytest
```

## Design notes

- `src/flexdate/parser.py` — public `parse`/`parse_date`, ordinal matching, fallback.
- `src/flexdate/ordinals.py` — pure `nth_weekday_of_month` calculation.
- `src/flexdate/arithmetic.py` — `shift`, a thin wrapper over `relativedelta`.
