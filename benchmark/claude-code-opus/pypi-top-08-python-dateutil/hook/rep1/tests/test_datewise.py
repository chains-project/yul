from datetime import date

import pytest

from datewise import parse_date

BASE = date(2026, 10, 2)  # a Friday


@pytest.mark.parametrize(
    "text, expected",
    [
        ("the first Monday of next month", date(2026, 11, 2)),
        ("first monday of this month", date(2026, 10, 5)),
        ("last Friday of next month", date(2026, 11, 27)),
        ("2nd Tuesday of March", date(2027, 3, 9)),
        ("third Thursday in November 2026", date(2026, 11, 19)),
        ("the last sunday of the month after next", date(2026, 12, 27)),
    ],
)
def test_nth_weekday(text, expected):
    assert parse_date(text, BASE) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("tomorrow", date(2026, 10, 3)),
        ("3 days ago", date(2026, 9, 29)),
        ("in 2 weeks", date(2026, 10, 16)),
        ("March 5th 2027", date(2027, 3, 5)),
        ("2026-12-25", date(2026, 12, 25)),
    ],
)
def test_freeform(text, expected):
    assert parse_date(text, BASE) == expected


def test_no_fifth_weekday():
    with pytest.raises(ValueError):
        parse_date("fifth Monday of December", BASE)  # Dec 2026 has only four
