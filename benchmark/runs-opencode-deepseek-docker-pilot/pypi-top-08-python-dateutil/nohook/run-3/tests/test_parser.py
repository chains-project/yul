from datetime import date, datetime, time, timezone

import pytest

from dateflex import parse_date, parse_when

# 2024-03-15 is a Friday.
BASE = datetime(2024, 3, 15, 14, 30)


@pytest.mark.parametrize(
    "expression, expected",
    [
        ("first Monday of next month", date(2024, 4, 1)),
        ("last Monday of next month", date(2024, 4, 29)),
        ("second Tuesday of this month", date(2024, 3, 12)),
        ("last Friday of this month", date(2024, 3, 29)),
        ("third Wednesday in January", date(2025, 1, 15)),
        ("first Monday of January 2027", date(2027, 1, 4)),
        ("first day of last month", date(2024, 2, 1)),
        ("last day of next month", date(2024, 4, 30)),
        ("1st day of next month", date(2024, 4, 1)),
        ("last day of February 2027", date(2027, 2, 28)),
        ("first monday of next month", date(2024, 4, 1)),
        ("the first Monday of next month", date(2024, 4, 1)),
    ],
)
def test_structured_expressions(expression, expected):
    assert parse_when(expression, BASE).date() == expected


@pytest.mark.parametrize(
    "expression, expected",
    [
        ("tomorrow", date(2024, 3, 16)),
        ("next friday", date(2024, 3, 22)),
        ("this friday", date(2024, 3, 15)),
        ("last monday", date(2024, 3, 11)),
        ("previous monday", date(2024, 3, 11)),
        ("in 3 days", date(2024, 3, 18)),
        ("3 weeks ago", date(2024, 2, 23)),
        ("2024-01-05", date(2024, 1, 5)),
        ("Jan 5, 2024", date(2024, 1, 5)),
    ],
)
def test_flexible_expressions(expression, expected):
    assert parse_date(expression, BASE) == expected


def test_returns_datetime_at_midnight_by_default():
    result = parse_when("first Monday of next month", BASE)
    assert result == datetime(2024, 4, 1, 0, 0)


def test_default_time_is_applied():
    result = parse_when("first Monday of next month", BASE, default_time=time(9, 30))
    assert result == datetime(2024, 4, 1, 9, 30)


def test_timezone_awareness_is_preserved():
    aware_base = BASE.replace(tzinfo=timezone.utc)
    result = parse_when("tomorrow", aware_base)
    assert result.tzinfo is timezone.utc
    assert result.date() == date(2024, 3, 16)


@pytest.mark.parametrize("bad", ["", "   ", "not a date at all", "flurble"])
def test_unparseable_input_raises(bad):
    with pytest.raises(ValueError):
        parse_when(bad, BASE)
