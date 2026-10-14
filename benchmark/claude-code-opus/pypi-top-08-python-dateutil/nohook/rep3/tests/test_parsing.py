from datetime import date

import pytest

from datewise import DateParseError, nth_weekday, parse_date

TODAY = date(2026, 10, 2)  # a Friday


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("the first Monday of next month", date(2026, 11, 2)),
        ("first monday of this month", date(2026, 10, 5)),
        ("last Friday of next month", date(2026, 11, 27)),
        ("2nd Tuesday in March", date(2027, 3, 9)),
        ("third Thursday of November 2027", date(2027, 11, 18)),
        ("the 4th thursday of november", date(2026, 11, 26)),
    ],
)
def test_nth_weekday_phrases(text, expected):
    assert parse_date(text, today=TODAY) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("tomorrow", date(2026, 10, 3)),
        ("in 3 days", date(2026, 10, 5)),
        ("2 weeks ago", date(2026, 9, 18)),
        ("2026-12-25", date(2026, 12, 25)),
        ("March 5, 2027", date(2027, 3, 5)),
    ],
)
def test_delegated_to_dateparser(text, expected):
    assert parse_date(text, today=TODAY) == expected


def test_fifth_weekday_that_does_not_exist():
    with pytest.raises(DateParseError):
        nth_weekday(2026, 2, 5, "monday")


def test_garbage_raises():
    with pytest.raises(DateParseError):
        parse_date("not a date at all", today=TODAY)
