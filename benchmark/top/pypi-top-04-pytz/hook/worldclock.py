"""Show the current time in a set of IANA timezones around the world."""

from datetime import datetime
from zoneinfo import ZoneInfo

REGIONS = [
    "America/New_York",
    "Europe/London",
    "Europe/Berlin",
    "Asia/Kolkata",
    "Asia/Tokyo",
    "Australia/Sydney",
]


def now_in(zone_name: str) -> datetime:
    return datetime.now(ZoneInfo(zone_name))


def main() -> None:
    for zone_name in REGIONS:
        local_time = now_in(zone_name)
        print(f"{zone_name:20s} {local_time.isoformat(timespec='seconds')}")


if __name__ == "__main__":
    main()
