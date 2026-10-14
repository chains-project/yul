# datewise

Parse human-written date strings and do calendar-aware relative date arithmetic.

```bash
uv sync
uv run datewise "the first Monday of next month"   # -> 2026-11-02
uv run pytest
```

```python
from datewise import parse, nth_weekday_of_relative_month, shift

parse("next friday")
parse("in 3 weeks")
parse("last Friday of this month")
nth_weekday_of_relative_month("monday", 1)          # first Monday of next month
shift(date(2026, 1, 31), months=1)                  # 2026-02-28 (clamped)
```

`parse()` first tries a few built-in rules ("next/last/this <weekday>",
"<ordinal> <weekday> of <this/next/last> month"), then falls back to
[dateparser](https://dateparser.readthedocs.io/) for everything else.
Arithmetic uses `dateutil.relativedelta`.
