# worldtime

Timezone-aware datetime helpers built on the standard library's `zoneinfo` module (no `pytz`).

## Setup

```sh
uv sync            # creates .venv with Python 3.13, tzdata, and pytest
uv run pytest      # run the tests
uv run worldtime   # show "now" in a sample of world timezones
uv run worldtime --at "2026-03-29 09:00" --from-zone Europe/Berlin America/New_York Asia/Tokyo
```

## Rules this project follows

- **Always use aware datetimes.** Helpers raise `NaiveDatetimeError` instead of guessing a zone.
- **Store and calculate in UTC**, and convert to local time only for input and display.
- **Use IANA zone names** (`America/Sao_Paulo`), not abbreviations (`EST`, `IST`) or fixed offsets.
- **Use `datetime.now(UTC)`** (`now_utc()`), never the deprecated `datetime.utcnow()`.
- **Handle DST edge cases explicitly.** `localize()` rejects wall-clock times skipped by DST,
  and takes `fold=` to choose between the two occurrences of a repeated time.
- **`tzdata` is a dependency** so the IANA database is available on systems without one
  (for example Windows or slim containers). Upgrade it to pick up new timezone rules.
