# datewise

Parse flexible, human-written date strings, including relative expressions
like "the first Monday of next month".

- General phrases ("tomorrow", "in 3 weeks", "12 Jan 2027") go to
  [dateparser](https://dateparser.readthedocs.io/).
- Weekday phrases ("the last Friday of this month", "next Tuesday", "3rd Thursday of
  November") are handled in `src/datewise/parse.py`, with
  `dateutil.relativedelta` doing the arithmetic.

## Setup

```sh
uv sync
```

## Usage

```sh
uv run datewise the first Monday of next month
uv run datewise --today 2026-10-02 "last Friday of December"
```

```python
from datewise import parse_date
parse_date("the first Monday of next month")
```

## Tests

```sh
uv run pytest
```
