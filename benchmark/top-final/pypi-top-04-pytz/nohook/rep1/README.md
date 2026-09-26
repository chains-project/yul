# worldclock

Prints the current time in a handful of timezones around the world, using
timezone-aware `datetime` objects.

Uses the standard library's `zoneinfo` module (Python 3.9+) rather than
`pytz`, plus the `tzdata` package so the IANA timezone database is available
even on platforms that don't ship one (e.g. Windows).

## Setup

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Run

```sh
python main.py
```
