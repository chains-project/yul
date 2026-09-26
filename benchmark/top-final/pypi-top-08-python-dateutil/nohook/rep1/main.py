import sys
from datetime import datetime

from dateutil import parser
from dateutil.relativedelta import MO, relativedelta


def first_monday_of_next_month(reference: datetime) -> datetime:
    next_month = reference + relativedelta(months=1, day=1)
    return next_month + relativedelta(weekday=MO(1))


def main() -> None:
    text = " ".join(sys.argv[1:]) or "next Friday"
    reference = parser.parse(text, fuzzy=True, default=datetime.now())
    print(f"Parsed '{text}' as: {reference.date()}")
    print(f"First Monday of next month: {first_monday_of_next_month(reference).date()}")


if __name__ == "__main__":
    main()
