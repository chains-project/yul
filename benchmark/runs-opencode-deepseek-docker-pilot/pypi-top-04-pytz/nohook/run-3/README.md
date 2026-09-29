# worldtime

Convert timezone-aware datetimes across regions of the world, built on the
standard library [`zoneinfo`](https://docs.python.org/3/library/zoneinfo.html).
No third-party runtime dependencies beyond `tzdata` on Windows.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Usage as a library

```python
from worldtime import now_in, parse_iso, to_zone

meeting = parse_iso("2026-09-29T14:00:00")  # naive input is treated as UTC
print(to_zone(meeting, "America/New_York").isoformat())
print(to_zone(meeting, "Asia/Tokyo").isoformat())

print(now_in("Europe/London"))
```

Functions intentionally require timezone-aware datetimes: `to_zone` rejects
naive values so ambiguous wall-clock times are never converted silently.

## Usage as a CLI

```bash
# Current time in several regions
worldtime America/New_York Europe/London Asia/Tokyo

# Convert a specific instant
worldtime --at 2026-09-29T14:00:00 --from UTC America/New_York Asia/Tokyo
```

Zone names are IANA identifiers (e.g. `America/New_York`, `Europe/London`,
`Asia/Kolkata`, `Australia/Sydney`).

## Tests

```bash
python -m unittest discover -s tests -v
```
