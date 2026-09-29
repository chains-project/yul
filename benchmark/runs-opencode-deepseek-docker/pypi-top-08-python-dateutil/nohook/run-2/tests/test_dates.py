from datetime import date, datetime

import pytest

from datephrase import nth_weekday_of_month, parse, parse_date, relative_weekday

BASE = datetime(2026, 9, 29, 12, 0, 0)


def test_first_monday_of_next_month():
    # 2026-09-29 -> next month is October 2026; first Monday is the 5th.
    assert parse("the first Monday of next month", base=BASE) == datetime(2026, 10, 5, 12, 0)


def test_last_friday_of_this_month():
    # September 2026 ends on a Wednesday; last Friday is the 25th.
    assert parse("last Friday of this month", base=BASE) == datetime(2026, 9, 25, 12, 0)


def test_fifth_weekday_missing_returns_none():
    # October 2026 has five Mondays (5, 12, 19, 26) but only four Sundays.
    assert parse("fifth Sunday of next month", base=BASE) is None


def test_nth_weekday_of_month_explicit():
    assert nth_weekday_of_month(2026, 10, "Monday", 1) == datetime(2026, 10, 5)
    assert nth_weekday_of_month(2026, 10, "Monday", -1) == datetime(2026, 10, 26)


def test_anchor_with_named_month_and_year():
    assert parse("first Tuesday of March 2027", base=BASE) == datetime(2027, 3, 2, 12, 0)


def test_relative_weekdays():
    assert parse("next Monday", base=BASE) == datetime(2026, 10, 5, 12, 0)
    assert parse("last Friday", base=BASE) == datetime(2026, 9, 25, 12, 0)
    assert parse("this Monday", base=BASE) == datetime(2026, 10, 5, 12, 0)


def test_next_weekday_always_moves_forward():
    # BASE is itself a Tuesday; "next Tuesday" must be seven days later.
    assert relative_weekday(BASE, "Tuesday", "next") == datetime(2026, 10, 6, 12, 0)


def test_relative_periods():
    assert parse("next month", base=BASE) == datetime(2026, 10, 29, 12, 0, 0)
    assert parse("last year", base=BASE) == datetime(2025, 9, 29, 12, 0, 0)


@pytest.mark.parametrize(
    "phrase,expected",
    [
        ("tomorrow", date(2026, 9, 30)),
        ("in 3 days", date(2026, 10, 2)),
        ("2 weeks ago", date(2026, 9, 15)),
        ("January 2027", date(2027, 1, 29)),
    ],
)
def test_dateparser_fallbacks(phrase, expected):
    assert parse_date(phrase, base=BASE) == expected


def test_unparseable_returns_none():
    assert parse("not a real date", base=BASE) is None
    assert parse("", base=BASE) is None
