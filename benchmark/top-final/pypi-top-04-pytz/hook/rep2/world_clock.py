from datetime import datetime

import pytz

REGIONS = {
    "New York": "America/New_York",
    "London": "Europe/London",
    "Nairobi": "Africa/Nairobi",
    "Mumbai": "Asia/Kolkata",
    "Tokyo": "Asia/Tokyo",
    "Sydney": "Australia/Sydney",
}


def now_in(region: str) -> datetime:
    tz = pytz.timezone(REGIONS[region])
    return datetime.now(tz)


def main() -> None:
    utc_now = datetime.now(pytz.utc)
    print(f"UTC: {utc_now.isoformat()}")
    for region in REGIONS:
        local_time = now_in(region)
        print(f"{region:10s}: {local_time.isoformat()}")


if __name__ == "__main__":
    main()
