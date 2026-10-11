import datetime as dt

import pytest

from flexdates import add_to_date, nth_weekday_of_month, parse_date


def test_first_monday_of_next_month():
    base = dt.datetime(2026, 1, 15, 9, 30)
    assert parse_date("the first Monday of next month", base=base) == dt.datetime(
        2026, 2, 2, 9, 30
    )


def test_last_friday_of_named_month_with_year():
    base = dt.datetime(2026, 1, 1)
    assert parse_date("last friday of march 2027", base=base) == dt.datetime(2027, 3, 26)


def test_this_month_and_in_months():
    base = dt.datetime(2026, 6, 10)
    assert parse_date("first wednesday of this month", base=base) == dt.datetime(2026, 6, 3)
    assert parse_date("first sunday in 2 months", base=base) == dt.datetime(2026, 8, 2)


def test_numeric_ordinal():
    base = dt.datetime(2026, 1, 1)
    assert parse_date("3rd tuesday of january 2026", base=base) == dt.datetime(2026, 1, 20)


def test_nonexistent_occurrence_raises():
    with pytest.raises(ValueError):
        nth_weekday_of_month(2026, 2, "monday", 5)


def test_flexible_natural_language():
    base = dt.datetime(2026, 1, 15, 12, 0)
    assert parse_date("tomorrow", base=base) == dt.datetime(2026, 1, 16, 12, 0)
    assert parse_date("in 2 weeks", base=base) == dt.datetime(2026, 1, 29, 12, 0)


def test_blank_and_invalid_text():
    assert parse_date("   ") is None
    assert parse_date("definitely not a date") is None


def test_add_to_date_preserves_type():
    assert add_to_date(dt.date(2026, 1, 31), months=1) == dt.date(2026, 2, 28)
    assert add_to_date(dt.datetime(2026, 1, 31, 8), months=1, days=1) == dt.datetime(
        2026, 3, 1, 8
    )


def test_base_as_date_uses_midnight():
    assert parse_date("first monday of next month", base=dt.date(2026, 1, 15)) == dt.datetime(
        2026, 2, 2, 0, 0
    )
