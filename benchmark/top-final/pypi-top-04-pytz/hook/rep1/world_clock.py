"""Show the current time in a handful of timezones around the world."""

from datetime import datetime

import pytz

REGIONS = [
    "UTC",
    "US/Eastern",
    "US/Pacific",
    "Europe/London",
    "Europe/Stockholm",
    "Asia/Tokyo",
    "Asia/Kolkata",
    "Australia/Sydney",
]


def now_in(zone_name: str) -> datetime:
    return datetime.now(pytz.timezone(zone_name))


def main() -> None:
    for zone_name in REGIONS:
        local_time = now_in(zone_name)
        print(f"{zone_name:20} {local_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")


if __name__ == "__main__":
    main()
