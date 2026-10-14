# datecalc

Parse flexible, human-written date strings and resolve relative expressions
such as "the first Monday of next month".

- General free-form parsing ("tomorrow at 5pm", "in 3 days", "March 5th 2027")
  uses [dateparser](https://dateparser.readthedocs.io/).
- Expressions dateparser can't handle ("the 2nd Tuesday of January 2027",
  "last Friday of next month", "next Friday", "last Friday") are computed with
  `dateutil.relativedelta`.

## Usage

```sh
uv sync
uv run datecalc the first Monday of next month
uv run datecalc --base 2026-10-02 "last Friday of next month"
```

```python
from datetime import datetime
from datecalc import parse

parse("the first Monday of next month", base=datetime(2026, 10, 2))
# datetime(2026, 11, 2, 0, 0)
```

## Tests

```sh
uv run pytest
```
