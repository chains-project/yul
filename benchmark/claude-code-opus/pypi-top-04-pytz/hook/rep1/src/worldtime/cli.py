import argparse
from datetime import datetime

from worldtime.core import convert, get_zone, now_in

DEFAULT_ZONES = [
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


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Show a moment in time across world timezones.")
    parser.add_argument("zones", nargs="*", default=DEFAULT_ZONES, help="IANA timezone names")
    parser.add_argument(
        "--at",
        help="ISO 8601 datetime with offset (e.g. 2026-03-29T01:30+00:00); defaults to now",
    )
    args = parser.parse_args(argv)

    if args.at:
        moment = datetime.fromisoformat(args.at)
        if moment.tzinfo is None:
            parser.error("--at must include a UTC offset or 'Z'")
    else:
        moment = now_in("UTC")

    for name in args.zones:
        try:
            get_zone(name)
        except ValueError as exc:
            parser.error(str(exc))
        local = convert(moment, name)
        print(f"{name:<22} {local:%Y-%m-%d %H:%M %Z (%z)}")


if __name__ == "__main__":
    main()
