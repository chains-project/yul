from datewise.core import nth_weekday_of_month, nth_weekday_of_relative_month, parse, shift

__all__ = ["parse", "nth_weekday_of_month", "nth_weekday_of_relative_month", "shift"]


def main() -> None:
    import sys

    from datewise.core import parse

    if len(sys.argv) < 2:
        print('usage: datewise "<date expression>"', file=sys.stderr)
        raise SystemExit(2)
    try:
        print(parse(" ".join(sys.argv[1:])).isoformat())
    except ValueError as exc:
        print(exc, file=sys.stderr)
        raise SystemExit(1)
