# worldtime

Utilities and a small CLI for working with timezone-aware datetimes across world regions.

Built on the standard library's `zoneinfo` (IANA tz database). The `tzdata`
package is a dependency so it works on systems without a tz database (Windows,
slim containers).

## Setup

```sh
uv sync
uv run worldtime                                  # now, in default zones
uv run worldtime Asia/Tokyo Europe/Paris --at 2026-03-29T01:30Z
uv run pytest
```

## Conventions

- Never use naive datetimes; `ensure_aware()` rejects them.
- Store and compare in UTC; convert to local zones only for display.
- Use IANA names (`Europe/Berlin`), not abbreviations (`CET`) or fixed offsets.
- Ambiguous wall times during DST fall-back are resolved with `datetime.fold`.
