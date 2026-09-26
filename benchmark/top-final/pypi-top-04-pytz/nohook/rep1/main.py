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


def current_times() -> dict[str, datetime]:
    now_utc = datetime.now(ZoneInfo("UTC"))
    return {region: now_utc.astimezone(ZoneInfo(tz)) for region, tz in REGIONS.items()}


def main() -> None:
    for region, local_time in current_times().items():
        print(f"{region:10} {local_time:%Y-%m-%d %H:%M:%S %Z (%z)}")


if __name__ == "__main__":
    main()
