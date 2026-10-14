from datecalc.core import DateParseError, nth_weekday_of_month, parse

__all__ = ["DateParseError", "nth_weekday_of_month", "parse", "main"]


def main() -> None:
    import argparse
    from datetime import datetime

    ap = argparse.ArgumentParser(description="Resolve human-written date expressions.")
    ap.add_argument("expression", nargs="+", help='e.g. "the first Monday of next month"')
    ap.add_argument("--base", type=datetime.fromisoformat, help="reference date (ISO format); defaults to now")
    args = ap.parse_args()

    try:
        print(parse(" ".join(args.expression), base=args.base).isoformat())
    except DateParseError as e:
        ap.exit(1, f"error: {e}\n")
