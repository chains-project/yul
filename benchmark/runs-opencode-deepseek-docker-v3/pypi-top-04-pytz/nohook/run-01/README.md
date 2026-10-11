# worldclock

Timezone-aware datetime utilities for working across world regions.

Built on Python's standard-library `zoneinfo` so conversions are DST-correct.
The `tzdata` package supplies the IANA database on platforms that lack one
(e.g. Windows, minimal containers).

## Setup

```sh
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```sh
worldclock
worldclock America/New_York Europe/London Asia/Tokyo
worldclock --at 2024-07-15T12:00:00+00:00 Asia/Tokyo
```

```python
from datetime import datetime, timezone
from worldclock import now_in, to_zone, local_time_in_zones

now_in("Asia/Tokyo")                                  # aware datetime
to_zone(datetime(2024, 1, 15, 12, tzinfo=timezone.utc), "Europe/Paris")
local_time_in_zones(["UTC", "America/New_York"])      # same instant, many zones
```

## Conventions

- Always keep datetimes **timezone-aware**; `ensure_aware` handles naive input.
- Store/transmit in UTC, convert to a region only for display.
- Use IANA names (`America/New_York`), never fixed offsets, to stay DST-safe.

## Tests

```sh
pytest
```
