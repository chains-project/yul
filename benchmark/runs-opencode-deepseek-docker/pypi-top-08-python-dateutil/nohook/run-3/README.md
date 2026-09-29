# dateflex

Parse flexible, human-written date strings and compute relative date
arithmetic such as *"the first Monday of next month"*.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```python
from datetime import datetime
from dateflex import parse_when, parse_date

base = datetime(2024, 3, 15)  # a Friday

parse_when("first Monday of next month", base)   # 2024-04-01 00:00:00
parse_when("last day of February 2027")          # 2027-02-28 00:00:00
parse_date("in 3 weeks", base)                   # 2024-04-05
```

### Command line

```bash
dateflex "first Monday of next month"
dateflex "next friday" --base 2024-03-15 --date-only
```

## Supported expressions

- **Ordinal weekdays in a month**: `first Monday of next month`,
  `last Friday of this month`, `third Wednesday in January`,
  `first Monday of January 2027`.
- **First/last day of a month**: `first day of next month`,
  `last day of February 2027`.
- **Relative offsets**: `tomorrow`, `next friday`, `in 3 days`, `3 weeks ago`,
  `2 months from now`.
- **Explicit dates**: `2024-01-05`, `Jan 5, 2024`.

Relative expressions are evaluated against the current time by default, or
against a `base` value passed by the caller. Timezone awareness of `base` is
preserved in the result.

Weekday qualifiers follow these conventions: `next <weekday>` is strictly in
the future, `this <weekday>` (or `coming`) is the next occurrence including
today, and `last`/`previous <weekday>` is strictly in the past.

## Development

```bash
pip install -e ".[dev]"
pytest
```
