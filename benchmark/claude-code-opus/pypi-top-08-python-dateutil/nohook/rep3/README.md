# datewise

Parse flexible, human-written date strings and resolve relative date arithmetic.

```console
$ uv run datewise the first Monday of next month
2026-11-02 (Monday)
$ uv run datewise "in 3 weeks" --today 2026-10-02
2026-10-23 (Friday)
```

```python
from datewise import parse_date
parse_date("last friday of december")
```

- **Nth-weekday phrases** (`first|2nd|...|last <weekday> of|in <this/next/last month | month name [year]>`)
  are handled in `src/datewise/parsing.py` using `dateutil.relativedelta`.
- **Everything else** (`tomorrow`, `2 weeks ago`, `next friday`, `March 5, 2027`, ISO dates, many languages)
  goes to [`dateparser`](https://dateparser.readthedocs.io/), preferring future dates.

## Development

```console
uv sync
uv run pytest
```
