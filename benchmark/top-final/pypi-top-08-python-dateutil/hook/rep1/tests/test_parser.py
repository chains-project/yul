from datetime import datetime

from dateexpr.parser import parse_date

BASE = datetime(2026, 9, 24)  # a Thursday


def test_absolute_date():
    assert parse_date("March 5, 2026", base=BASE) == datetime(2026, 3, 5)


def test_today_tomorrow_yesterday():
    assert parse_date("today", base=BASE) == BASE
    assert parse_date("tomorrow", base=BASE) == datetime(2026, 9, 25)
    assert parse_date("yesterday", base=BASE) == datetime(2026, 9, 23)


def test_next_last_weekday():
    assert parse_date("next monday", base=BASE) == datetime(2026, 9, 28)
    assert parse_date("last friday", base=BASE) == datetime(2026, 9, 18)


def test_in_n_units():
    assert parse_date("in 3 days", base=BASE) == datetime(2026, 9, 27)
    assert parse_date("in 2 weeks", base=BASE) == datetime(2026, 10, 8)
    assert parse_date("in 1 month", base=BASE) == datetime(2026, 10, 24)


def test_first_monday_of_next_month():
    # October 2026's first Monday is Oct 5.
    assert parse_date("first monday of next month", base=BASE) == datetime(2026, 10, 5)


def test_last_friday_of_this_month():
    # September 2026's last Friday is Sep 25.
    assert parse_date("last friday of this month", base=BASE) == datetime(2026, 9, 25)


def test_second_tuesday_of_named_month():
    # December 2026's second Tuesday is Dec 8.
    assert parse_date("second tuesday of december", base=BASE) == datetime(2026, 12, 8)
