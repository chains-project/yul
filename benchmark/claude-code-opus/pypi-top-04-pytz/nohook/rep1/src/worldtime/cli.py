"""Show the current time in several zones: `worldtime [ZONE ...]`."""

import sys

from worldtime.core import now_in

DEFAULT_ZONES = [
    "UTC",
    "America/Los_Angeles",
    "America/New_York",
    "America/Sao_Paulo",
    "Europe/London",
    "Europe/Berlin",
    "Africa/Lagos",
    "Asia/Kolkata",
    "Asia/Tokyo",
    "Australia/Sydney",
]


def main(argv: list[str] | None = None) -> int:
    zones = (argv if argv is not None else sys.argv[1:]) or DEFAULT_ZONES
    for tz in zones:
        print(f"{tz:<22} {now_in(tz):%Y-%m-%d %H:%M %Z (UTC%z)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
