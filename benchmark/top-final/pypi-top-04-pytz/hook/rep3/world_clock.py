"""Show the current time across a set of world regions."""

from datetime import datetime

import pytz

REGIONS = {
    "New York": "America/New_York",
    "Sao Paulo": "America/Sao_Paulo",
    "London": "Europe/London",
    "Nairobi": "Africa/Nairobi",
    "Dubai": "Asia/Dubai",
    "Kolkata": "Asia/Kolkata",
    "Singapore": "Asia/Singapore",
    "Tokyo": "Asia/Tokyo",
    "Sydney": "Australia/Sydney",
}


def now_in(zone_name: str) -> datetime:
    return datetime.now(pytz.timezone(zone_name))


def convert(dt: datetime, zone_name: str) -> datetime:
    if dt.tzinfo is None:
        raise ValueError("dt must already be timezone-aware")
    return dt.astimezone(pytz.timezone(zone_name))


def main() -> None:
    utc_now = datetime.now(pytz.utc)
    print(f"UTC now: {utc_now.strftime('%Y-%m-%d %H:%M:%S %Z')}\n")
    for city, zone_name in REGIONS.items():
        local = convert(utc_now, zone_name)
        print(f"{city:12} {local.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")


if __name__ == "__main__":
    main()
