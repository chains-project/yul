from __future__ import annotations

from datetime import date, datetime

import pytest

from humandate import parse, parse_date, shift

BASE = datetime(2026, 10, 3, 9, 30)


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("the first Monday of next month", date(2026, 11, 2)),
        ("first monday next month", date(2026, 11, 2)),
        ("last Friday of this month", date(2026, 10, 30)),
        ("second Tuesday of March 2027", date(2027, 3, 9)),
        ("3rd Wednesday of next month", date(2026, 11, 18)),
        ("first Monday of next year", date(2027, 1, 4)),
    ],
)
def test_nth_weekday(expression, expected):
    assert parse_date(expression, base=BASE) == expected


def test_parse_returns_datetime():
    result = parse("the first Monday of next month", base=BASE)
    assert isinstance(result, datetime)
    assert result.time() == datetime.min.time()


def test_shift_months_clamps_day():
    assert shift(datetime(2026, 1, 31), months=1) == datetime(2026, 2, 28)


def test_shift_weeks_and_days():
    assert shift(datetime(2026, 1, 1), weeks=2, days=-1) == datetime(2026, 1, 14)


def test_dateparser_fallback():
    assert parse_date("tomorrow", base=BASE) == date(2026, 10, 4)
    assert parse_date("December 25, 2026", base=BASE) == date(2026, 12, 25)


def test_empty_input_raises():
    with pytest.raises(ValueError):
        parse("   ", base=BASE)


def test_unparseable_raises():
    with pytest.raises(ValueError):
        parse("not a date at all", base=BASE)
