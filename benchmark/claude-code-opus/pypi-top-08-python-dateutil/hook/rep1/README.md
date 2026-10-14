# datewise

Parse flexible, human-written date strings into dates.

```sh
uv run datewise the first Monday of next month          # 2026-11-02
uv run datewise "last friday of February 2027"          # 2027-02-26
uv run datewise --base 2026-01-15 "3 days ago"          # 2026-01-12
```

```python
from datewise import parse_date
parse_date("2nd Tuesday of March")
```

- **Nth-weekday expressions** ("first/2nd/.../last <weekday> of <month>") are
  handled in-house with `dateutil.relativedelta`. `<month>` can be `this/next/last
  month`, `month after next`, a month name (next occurrence), or `March 2027`.
- **Everything else** ("tomorrow", "in 2 weeks", "Dec 25", ISO dates) goes to
  [`dateparser`](https://dateparser.readthedocs.io/), preferring future dates.

Run tests: `uv run pytest`
