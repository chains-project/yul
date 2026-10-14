"""Show the current time in several time zones."""

from __future__ import annotations

import argparse
from datetime import datetime

from worldtime.core import UTC, convert

DEFAULT_ZONES = [
    "America/Los_Angeles",
    "America/New_York",
    "Europe/London",
    "Asia/Kolkata",
    "Asia/Tokyo",
    "Australia/Sydney",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zones", nargs="*", default=DEFAULT_ZONES, help="IANA zone names")
    args = parser.parse_args(argv)

    now = datetime.now(UTC)
    for zone in args.zones:
        local = convert(now, zone)
        print(f"{zone:<22} {local:%Y-%m-%d %H:%M %Z (UTC%z)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
