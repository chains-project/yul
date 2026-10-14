from datetime import date

import pytest

from datewise import DateParseError, parse_date

TODAY = date(2026, 10, 2)  # a Friday


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("the first Monday of next month", date(2026, 11, 2)),
        ("first monday of this month", date(2026, 10, 5)),
        ("the last Friday of this month", date(2026, 10, 30)),
        ("second Tuesday of last month", date(2026, 9, 8)),
        ("the 3rd Thursday of November", date(2026, 11, 19)),  # Thanksgiving
        ("last Monday of May", date(2027, 5, 31)),  # bare month -> next one
        ("first Sunday in Feb 2028", date(2028, 2, 6)),
        ("first Monday of December", date(2026, 12, 7)),
    ],
)
def test_ordinal_weekday(text, expected):
    assert parse_date(text, today=TODAY) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("next Tuesday", date(2026, 10, 6)),
        ("next Friday", date(2026, 10, 9)),  # strictly after today
        ("this Friday", date(2026, 10, 2)),  # may be today
        ("last Friday", date(2026, 9, 25)),
        ("last wednesday", date(2026, 9, 30)),
    ],
)
def test_relative_weekday(text, expected):
    assert parse_date(text, today=TODAY) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("today", date(2026, 10, 2)),
        ("tomorrow", date(2026, 10, 3)),
        ("in 3 days", date(2026, 10, 5)),
        ("2 weeks ago", date(2026, 9, 18)),
        ("12 Jan 2027", date(2027, 1, 12)),
        ("2026-11-05", date(2026, 11, 5)),
    ],
)
def test_general_expressions(text, expected):
    assert parse_date(text, today=TODAY) == expected


def test_fifth_weekday_that_does_not_exist():
    # December 2026 has only four Mondays (7, 14, 21, 28).
    with pytest.raises(DateParseError, match="no fifth Monday"):
        parse_date("fifth Monday of December", today=TODAY)


def test_unparseable():
    with pytest.raises(DateParseError):
        parse_date("whenever, man", today=TODAY)
