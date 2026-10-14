# worldtime

Timezone-aware datetime helpers using the standard-library `zoneinfo` module
(IANA tz database, supplied by the `tzdata` package where the OS lacks it).

```sh
uv sync
uv run worldtime                                    # now, across default regions
uv run worldtime --at 2026-03-29T09:00 --from-zone Europe/Berlin Asia/Tokyo America/Chicago
uv run pytest
```

Conventions:
- Use IANA names (`Europe/Paris`), never abbreviations like `CET`/`EST`.
- Keep datetimes aware; store and compare in UTC, convert only for display.
- Don't use `pytz`; `zoneinfo` replaces it.
- Keep `tzdata` updated, since governments change timezone rules often.
