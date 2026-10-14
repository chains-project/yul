from datetime import datetime

import pytest

from datecalc import DateParseError, nth_weekday_of_month, parse

BASE = datetime(2026, 10, 2, 9, 30)  # a Friday


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("the first Monday of next month", datetime(2026, 11, 2)),
        ("first Monday of this month", datetime(2026, 10, 5)),
        ("the last Friday of next month", datetime(2026, 11, 27)),
        ("2nd Tuesday of January 2027", datetime(2027, 1, 12)),
        ("next Friday", datetime(2026, 10, 9)),
        ("last Friday", datetime(2026, 9, 25)),
        ("this Friday", datetime(2026, 10, 2)),
        ("in 3 days", datetime(2026, 10, 5, 9, 30)),
        ("tomorrow at 5pm", datetime(2026, 10, 3, 17, 0)),
        ("March 5th 2027", datetime(2027, 3, 5)),
    ],
)
def test_parse(text, expected):
    assert parse(text, base=BASE) == expected


def test_nonexistent_fifth_weekday():
    with pytest.raises(DateParseError):
        nth_weekday_of_month(2026, 2, "monday", 5)


def test_unparseable():
    with pytest.raises(DateParseError):
        parse("whenever the cows come home", base=BASE)
