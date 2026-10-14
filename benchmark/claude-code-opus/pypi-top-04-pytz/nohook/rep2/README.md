# worldtime

Timezone-aware datetime utilities for working across world regions, built on
the standard-library [`zoneinfo`](https://docs.python.org/3/library/zoneinfo.html)
module. The `tzdata` package is a dependency so the IANA database is available
even where the OS doesn't ship one (Windows, slim containers).

## Setup

```sh
uv sync
```

## Usage

```sh
uv run worldtime                                   # current time in a sample of world zones
uv run worldtime Asia/Kolkata Europe/Paris         # specific zones
uv run worldtime --at 2026-03-29T01:30:00+00:00    # a specific instant
```

```python
from datetime import datetime
from worldtime import convert, localize, now_utc

meeting = localize(datetime(2026, 11, 3, 9, 0), "America/New_York")
convert(meeting, "Asia/Tokyo")
```

## Conventions

- Store and compute in UTC; convert to local zones only at the edges.
- Use IANA names (`Europe/Berlin`), not abbreviations (`CET`, `EST`).
- Naive datetimes are rejected by `convert`/`ensure_aware`.
- `localize` handles DST: `fold=` picks between repeated times, and times
  skipped by DST raise `ValueError`.

## Tests

```sh
uv run pytest
```
