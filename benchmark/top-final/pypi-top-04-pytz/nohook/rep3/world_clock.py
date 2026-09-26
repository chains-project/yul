"""Show the current time in a set of world timezones."""

from datetime import datetime
from zoneinfo import ZoneInfo

REGIONS = {
    "New York": "America/New_York",
    "London": "Europe/London",
    "Nairobi": "Africa/Nairobi",
    "Mumbai": "Asia/Kolkata",
    "Tokyo": "Asia/Tokyo",
    "Sydney": "Australia/Sydney",
}


def current_times(regions: dict[str, str] = REGIONS) -> dict[str, datetime]:
    now_utc = datetime.now(ZoneInfo("UTC"))
    return {name: now_utc.astimezone(ZoneInfo(tz)) for name, tz in regions.items()}


def main() -> None:
    for name, local_time in current_times().items():
        print(f"{name:10} {local_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")


if __name__ == "__main__":
    main()
