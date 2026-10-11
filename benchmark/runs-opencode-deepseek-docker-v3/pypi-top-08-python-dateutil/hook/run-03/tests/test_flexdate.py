from datetime import date, datetime

import pytest

from flexdate import DateParseError, nth_weekday_of_month, parse, parse_date, shift
from flexdate.ordinals import FRIDAY, MONDAY, TUESDAY

BASE = datetime(2026, 10, 3, 12, 0)  # a Saturday


def test_first_monday_of_next_month():
    assert parse("the first Monday of next month", base=BASE) == datetime(2026, 11, 2)


def test_first_monday_of_this_month():
    assert parse("first Monday of this month", base=BASE) == datetime(2026, 10, 5)


def test_second_tuesday_of_this_month():
    assert parse("the 2nd Tuesday of this month", base=BASE) == datetime(2026, 10, 13)


def test_last_friday_of_named_month_with_year():
    assert parse("last Friday of March 2027", base=BASE) == datetime(2027, 3, 26)


def test_ordinal_without_period_defaults_to_current_month():
    assert parse("first Monday", base=BASE) == datetime(2026, 10, 5)


def test_last_month():
    assert parse("first Thursday of last month", base=BASE) == datetime(2026, 9, 3)


def test_missing_occurrence_raises():
    with pytest.raises(DateParseError):
        parse("fifth Monday of February 2027", base=BASE)


def test_fallback_to_general_parser():
    assert parse_date("tomorrow", base=BASE) == date(2026, 10, 4)
    assert parse_date("in 3 days", base=BASE) == date(2026, 10, 6)


def test_empty_and_garbage_raise():
    with pytest.raises(DateParseError):
        parse("   ", base=BASE)
    with pytest.raises(DateParseError):
        parse("not a date at all", base=BASE)


def test_shift_handles_month_arithmetic():
    assert shift(date(2026, 10, 31), months=1) == date(2026, 11, 30)
    assert shift(datetime(2026, 10, 3), weeks=2, days=1) == datetime(2026, 10, 18)


def test_nth_weekday_of_month_helper():
    assert nth_weekday_of_month(2026, 10, MONDAY, 1) == date(2026, 10, 5)
    assert nth_weekday_of_month(2026, 10, TUESDAY, 2) == date(2026, 10, 13)
    assert nth_weekday_of_month(2027, 3, FRIDAY, -1) == date(2027, 3, 26)
