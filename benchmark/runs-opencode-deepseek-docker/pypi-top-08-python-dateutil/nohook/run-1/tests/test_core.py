from datetime import date, datetime

import pytest

from datephrase import nth_weekday_of_month, parse, parse_date


def test_first_monday_of_next_month():
    result = parse("the first Monday of next month", base=date(2026, 9, 27))
    assert result.date() == date(2026, 10, 5)


def test_last_friday_of_this_month():
    result = parse("last friday of this month", base=date(2026, 9, 27))
    assert result.date() == date(2026, 9, 25)


def test_nth_weekday_accepts_iso_date_base():
    result = parse("second tuesday in March", base=date(2027, 1, 1))
    assert result.date() == date(2027, 3, 9)


def test_parse_relative_expression():
    result = parse("2 weeks ago", base=date(2026, 9, 27))
    assert result.date() == date(2026, 9, 13)


def test_parse_next_friday():
    result = parse("next friday", base=date(2026, 9, 27))
    assert result.date() == date(2026, 10, 2)


def test_parse_date_returns_date():
    result = parse_date("tomorrow", base=datetime(2026, 9, 27, 15, 30))
    assert result == date(2026, 9, 28)
    assert isinstance(result, date) and not isinstance(result, datetime)


def test_empty_input_returns_none():
    assert parse("") is None
    assert parse("   ") is None


def test_nth_weekday_overflow_raises():
    with pytest.raises(ValueError):
        nth_weekday_of_month(2026, 2, 5, 0)


def test_nth_weekday_helper():
    assert nth_weekday_of_month(2026, 10, 1, 0) == date(2026, 10, 5)
    assert nth_weekday_of_month(2026, 9, -1, 4) == date(2026, 9, 25)
