import sys

from dateutil import parser
from dateutil.relativedelta import MO, relativedelta


def parse_date(text: str):
    return parser.parse(text, fuzzy=True)


def first_monday_of_next_month(reference):
    next_month = reference + relativedelta(months=1, day=1)
    return next_month + relativedelta(weekday=MO(1))


def main():
    text = " ".join(sys.argv[1:]) or "today"
    reference = parse_date(text)
    result = first_monday_of_next_month(reference)
    print(f"Parsed: {reference.date()}")
    print(f"First Monday of next month: {result.date()}")


if __name__ == "__main__":
    main()
