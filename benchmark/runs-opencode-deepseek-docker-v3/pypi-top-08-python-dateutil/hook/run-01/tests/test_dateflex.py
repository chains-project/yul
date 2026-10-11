from datetime import UTC, date, datetime

import pytest

from dateflex import DateParseError, parse, parse_date, shift

BASE = datetime(2026, 10, 3, 12, 30)  # a Saturday


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("today", datetime(2026, 10, 3, 12, 30)),
        ("tomorrow", datetime(2026, 10, 4, 12, 30)),
        ("yesterday", datetime(2026, 10, 2, 12, 30)),
    ],
)
def test_day_keywords(text, expected):
    assert parse(text, base=BASE) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("the first Monday of next month", date(2026, 11, 2)),
        ("first monday of the next month", date(2026, 11, 2)),
        ("last Friday of this month", date(2026, 10, 30)),
        ("2nd Tuesday of March 2027", date(2027, 3, 9)),
        ("third Wednesday of December 2026", date(2026, 12, 16)),
    ],
)
def test_ordinal_weekday_of_month(text, expected):
    assert parse_date(text, base=BASE) == expected


def test_ordinal_weekday_preserves_base_time():
    assert parse("first Monday of next month", base=BASE).time() == BASE.time()


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("friday", date(2026, 10, 9)),
        ("this friday", date(2026, 10, 9)),
        ("next friday", date(2026, 10, 9)),
        ("last friday", date(2026, 10, 2)),
        ("next monday", date(2026, 10, 5)),
        ("this monday", date(2026, 10, 5)),
    ],
)
def test_relative_weekdays(text, expected):
    assert parse_date(text, base=BASE) == expected


def test_next_weekday_when_base_is_that_weekday():
    friday = datetime(2026, 10, 9, 9, 0)
    assert parse_date("today", base=friday) == date(2026, 10, 9)
    assert parse_date("this friday", base=friday) == date(2026, 10, 9)
    assert parse_date("next friday", base=friday) == date(2026, 10, 16)
    assert parse_date("last friday", base=friday) == date(2026, 10, 2)


def test_weekday_with_time_clause():
    assert parse("next friday at 5pm", base=BASE) == datetime(2026, 10, 9, 17, 0)


def test_absolute_fallback():
    assert parse("Dec 25, 2026", base=BASE) == datetime(2026, 12, 25, 0, 0)


def test_relative_fallback():
    assert parse("in 3 days", base=BASE) == datetime(2026, 10, 6, 12, 30)
    assert parse("3 weeks ago", base=BASE) == datetime(2026, 9, 12, 12, 30)


def test_unparseable_raises():
    with pytest.raises(DateParseError):
        parse("banana", base=BASE)


def test_nonexistent_ordinal_raises():
    with pytest.raises(DateParseError):
        parse("fifth Monday of February 2027", base=BASE)


def test_empty_string_raises():
    with pytest.raises(DateParseError):
        parse("   ", base=BASE)


def test_passthrough_date_and_datetime():
    assert parse(BASE) == BASE
    assert parse(date(2026, 1, 2)) == datetime(2026, 1, 2)


def test_base_accepts_plain_date():
    assert parse_date("tomorrow", base=date(2026, 10, 3)) == date(2026, 10, 4)


def test_timezone_is_preserved():
    aware = datetime(2026, 10, 3, 12, 0, tzinfo=UTC)
    assert parse("first Monday of next month", base=aware).tzinfo == UTC


def test_shift_is_calendar_aware():
    assert shift(datetime(2026, 1, 31), months=1) == datetime(2026, 2, 28)
    assert shift(BASE, weeks=2, days=1) == datetime(2026, 10, 18, 12, 30)
    assert shift(datetime(2024, 2, 29), years=1) == datetime(2025, 2, 28)
