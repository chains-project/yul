from datetime import date

import pytest

from datecalc import DateParseError, resolve

BASE = date(2026, 10, 2)  # a Friday


@pytest.mark.parametrize(
    "text, expected",
    [
        ("the first Monday of next month", date(2026, 11, 2)),
        ("first monday of this month", date(2026, 10, 5)),
        ("2nd Tuesday of next month", date(2026, 11, 10)),
        ("last Friday of this month", date(2026, 10, 30)),
        ("last friday in last month", date(2026, 9, 25)),
        ("third Wed of March 2027", date(2027, 3, 17)),
        ("first sunday of 2 months from now", date(2026, 12, 6)),
        ("first Monday of January", date(2027, 1, 4)),
    ],
)
def test_ordinal_weekday(text, expected):
    assert resolve(text, base=BASE) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("next friday", date(2026, 10, 9)),
        ("next monday", date(2026, 10, 5)),
        ("last friday", date(2026, 9, 25)),
        ("this wednesday", date(2026, 9, 30)),
    ],
)
def test_relative_weekday(text, expected):
    assert resolve(text, base=BASE) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("tomorrow", date(2026, 10, 3)),
        ("in 3 days", date(2026, 10, 5)),
        ("2 weeks ago", date(2026, 9, 18)),
        ("March 5, 2027", date(2027, 3, 5)),
        ("2026-12-25", date(2026, 12, 25)),
    ],
)
def test_dateparser_fallback(text, expected):
    assert resolve(text, base=BASE) == expected


def test_nonexistent_fifth_weekday():
    with pytest.raises(DateParseError):
        resolve("fifth Tuesday of next month", base=BASE)  # Nov 2026 has 4


def test_garbage():
    with pytest.raises(DateParseError):
        resolve("blorp", base=BASE)
