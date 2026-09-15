from datetime import datetime
from zoneinfo import ZoneInfo

REGIONS = {
    "New York": "America/New_York",
    "London": "Europe/London",
    "Tokyo": "Asia/Tokyo",
    "Sydney": "Australia/Sydney",
    "Mumbai": "Asia/Kolkata",
}


def now_in(tz_name: str) -> datetime:
    """Current timezone-aware datetime for an IANA zone name."""
    return datetime.now(ZoneInfo(tz_name))


def convert(dt: datetime, tz_name: str) -> datetime:
    """Convert an aware datetime to another IANA zone."""
    if dt.tzinfo is None:
        raise ValueError("dt must be timezone-aware")
    return dt.astimezone(ZoneInfo(tz_name))


def main() -> None:
    reference = now_in("UTC")
    print(f"{'UTC':10s} {reference.isoformat()}")
    for city, tz_name in REGIONS.items():
        local = convert(reference, tz_name)
        print(f"{city:10s} {local.isoformat()}")


if __name__ == "__main__":
    main()
