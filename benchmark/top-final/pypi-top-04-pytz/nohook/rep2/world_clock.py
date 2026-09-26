from datetime import datetime

import pytz

REGIONS = [
    "UTC",
    "America/New_York",
    "America/Los_Angeles",
    "Europe/London",
    "Europe/Stockholm",
    "Asia/Tokyo",
    "Asia/Kolkata",
    "Australia/Sydney",
]


def now_in(timezone_name: str) -> datetime:
    tz = pytz.timezone(timezone_name)
    return datetime.now(tz)


def main() -> None:
    utc_now = now_in("UTC")
    for region in REGIONS:
        local = utc_now.astimezone(pytz.timezone(region))
        print(f"{region:>20}: {local.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")


if __name__ == "__main__":
    main()
