import argparse
from datetime import datetime

from worldtime.core import convert, ensure_aware, now_in

DEFAULT_ZONES = [
    "America/Los_Angeles",
    "America/New_York",
    "Europe/London",
    "Asia/Kolkata",
    "Asia/Tokyo",
    "Australia/Sydney",
]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Show a moment in time across regions.")
    parser.add_argument("zones", nargs="*", default=DEFAULT_ZONES, help="IANA zone names")
    parser.add_argument("--at", help="ISO datetime (default: now)")
    parser.add_argument("--from-zone", default="UTC", help="zone for a naive --at value")
    args = parser.parse_args(argv)

    moment = (
        ensure_aware(datetime.fromisoformat(args.at), args.from_zone)
        if args.at
        else now_in("UTC")
    )
    for zone in args.zones:
        local = convert(moment, zone)
        print(f"{zone:<22} {local:%Y-%m-%d %H:%M %Z (UTC%z)}")


if __name__ == "__main__":
    main()
