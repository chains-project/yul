import datetime as dt

import pytest

from datewise import nth_weekday_of_month, nth_weekday_of_relative_month, parse, shift

BASE = dt.date(2026, 10, 2)  # a Friday


@pytest.mark.parametrize(
    "text, expected",
    [
        ("tomorrow", dt.date(2026, 10, 3)),
        ("in 3 days", dt.date(2026, 10, 5)),
        ("2 weeks ago", dt.date(2026, 9, 18)),
        ("12 Jan 2027", dt.date(2027, 1, 12)),
        ("2026-12-25", dt.date(2026, 12, 25)),
        ("next friday", dt.date(2026, 10, 9)),
        ("last friday", dt.date(2026, 9, 25)),
        ("this friday", dt.date(2026, 10, 2)),
        ("next Monday", dt.date(2026, 10, 5)),
        ("the first Monday of next month", dt.date(2026, 11, 2)),
        ("last Friday of this month", dt.date(2026, 10, 30)),
        ("second tuesday of last month", dt.date(2026, 9, 8)),
    ],
)
def test_parse(text, expected):
    assert parse(text, base=BASE) == expected


def test_parse_garbage():
    with pytest.raises(ValueError):
        parse("not a date at all", base=BASE)


def test_first_monday_of_next_month():
    assert nth_weekday_of_relative_month("monday", 1, base=BASE) == dt.date(2026, 11, 2)


def test_last_friday_of_this_month():
    assert nth_weekday_of_relative_month("friday", -1, months=0, base=BASE) == dt.date(2026, 10, 30)


def test_first_monday_across_year_boundary():
    assert nth_weekday_of_relative_month("monday", 1, base=dt.date(2026, 12, 15)) == dt.date(2027, 1, 4)


def test_no_fifth_weekday():
    with pytest.raises(ValueError):
        nth_weekday_of_month(2026, 2, "monday", 5)


def test_shift_clamps_month_end():
    assert shift(dt.date(2026, 1, 31), months=1) == dt.date(2026, 2, 28)
