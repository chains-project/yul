from datetime import date, datetime

import pytest
from dateutil.relativedelta import MO

from flexdate import parse, shift

NOW = datetime(2026, 9, 27, 12, 0)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("2026-09-27", datetime(2026, 9, 27)),
        ("Sept 27 2026", datetime(2026, 9, 27)),
        ("27 September 2026", datetime(2026, 9, 27)),
        ("first Monday of next month", datetime(2026, 10, 5)),
        ("the first Monday of next month", datetime(2026, 10, 5)),
        ("last Friday of March 2027", datetime(2027, 3, 26)),
        ("second Tuesday of this month", datetime(2026, 9, 8)),
        ("1st Wednesday of next year", datetime(2027, 1, 6)),
        ("last Sunday of this month", datetime(2026, 9, 27)),
    ],
)
def test_parse(text, expected):
    assert parse(text, default=NOW).date() == expected.date()


def test_parse_accepts_date_objects():
    assert parse(date(2026, 9, 27)) == datetime(2026, 9, 27)


def test_parse_empty_raises():
    with pytest.raises(ValueError):
        parse("   ", default=NOW)


def test_shift_months_clamps_to_month_end():
    assert shift("2026-01-31", months=1).date() == date(2026, 2, 28)


def test_shift_weekday():
    assert shift("2026-09-01", weekday=MO(1)).date() == date(2026, 9, 7)
