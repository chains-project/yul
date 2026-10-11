from datetime import date, datetime

import pytest

from flexdates import (
    first_weekday_of_month,
    last_weekday_of_month,
    nth_weekday,
    resolve,
)

BASE = datetime(2026, 10, 3, 12, 0)  # Saturday


def test_nth_weekday_first_and_last():
    assert nth_weekday(2026, 10, 0, 1) == date(2026, 10, 5)
    assert last_weekday_of_month(2026, 10, 0) == date(2026, 10, 26)
    assert first_weekday_of_month(2026, 10, 4) == date(2026, 10, 2)


def test_nth_weekday_missing_occurrence_raises():
    with pytest.raises(ValueError):
        nth_weekday(2026, 2, 0, 5)  # February 2026 has only four Mondays


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("the first Monday of next month", datetime(2026, 11, 2)),
        ("last Friday of this month", datetime(2026, 10, 30)),
        ("second Tuesday of January 2027", datetime(2027, 1, 12)),
        ("first Monday of January", datetime(2027, 1, 4)),
        ("next friday", datetime(2026, 10, 9)),
        ("next monday", datetime(2026, 10, 5)),
        ("this friday", datetime(2026, 10, 2)),
    ],
)
def test_resolve_phrases(text, expected):
    assert resolve(text, base=BASE) == expected


def test_resolve_delegates_to_dateparser():
    assert resolve("tomorrow", base=BASE) == datetime(2026, 10, 4, 12, 0)
    assert resolve("in 3 weeks", base=BASE) == datetime(2026, 10, 24, 12, 0)


def test_resolve_returns_none_for_gibberish():
    assert resolve("definitely not a date", base=BASE) is None
