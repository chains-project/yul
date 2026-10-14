# datecalc

Resolve human-written date expressions to concrete dates.

```console
$ uv run datecalc "the first Monday of next month"
2026-11-02
$ uv run datecalc last friday of december --base 2026-10-02
2026-12-25
```

```python
from datecalc import resolve
resolve("2nd Tuesday of next month")          # -> datetime.date
resolve("in 3 days", base=date(2026, 1, 1))
```

## How it works

- **Ordinal weekday of a month**: `first|second|…|fifth|last <weekday> of|in <month>`,
  where `<month>` is `this/next/last month`, `N months from now`, or anything
  dateparser understands (`March`, `January 2028`). Computed with
  `dateutil.relativedelta`. Raises `DateParseError` if the day doesn't exist
  (e.g. a fifth Tuesday in a four-Tuesday month).
- **`next/last/this <weekday>`**: next = first one strictly after the base date,
  last = most recent strictly before, this = within the current Mon–Sun week.
- **Everything else** goes to [dateparser](https://dateparser.readthedocs.io/)
  (`tomorrow`, `in 3 days`, `2 weeks ago`, `March 5, 2027`, ISO dates…),
  preferring future dates when the input is ambiguous.

## Development

```console
uv sync
uv run pytest
```
