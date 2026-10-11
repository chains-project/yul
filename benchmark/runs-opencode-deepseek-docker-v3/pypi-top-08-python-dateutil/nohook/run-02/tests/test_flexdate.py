from datetime import datetime

import pytest

from flexdate import (
    first_weekday_of_month,
    last_weekday_of_month,
    nth_weekday_of_month,
    parse_date,
    resolve,
)

BASE = datetime(2026, 3, 15)


def test_parse_iso():
    assert parse_date("2026-03-03") == datetime(2026, 3, 3)


def test_parse_human_written():
    assert parse_date("March 3, 2026") == datetime(2026, 3, 3)
    assert parse_date("3 March 2026") == datetime(2026, 3, 3)


def test_resolve_relative_phrases():
    assert resolve("tomorrow", base=BASE) == datetime(2026, 3, 16)
    assert resolve("in 2 days", base=BASE) == datetime(2026, 3, 17)


def test_first_monday_of_next_month():
    assert resolve("the first Monday of next month", base=BASE) == datetime(2026, 4, 6)


def test_first_monday_without_article():
    assert resolve("first Monday of next month", base=BASE) == datetime(2026, 4, 6)


def test_last_friday_of_this_month():
    assert resolve("the last Friday of this month", base=BASE) == datetime(2026, 3, 27)


def test_nth_weekday_with_explicit_month():
    assert resolve("second Tuesday of April 2026", base=BASE) == datetime(2026, 4, 14)


def test_nth_weekday_of_month_helper():
    assert nth_weekday_of_month("first", "Monday", 2026, 3) == datetime(2026, 3, 2)
    assert nth_weekday_of_month(2, "tuesday", 2026, 4) == datetime(2026, 4, 14)
    assert nth_weekday_of_month(-1, 4, 2026, 3) == datetime(2026, 3, 27)


def test_first_and_last_helpers():
    assert first_weekday_of_month("Monday", 2026, 3) == datetime(2026, 3, 2)
    assert last_weekday_of_month("friday", 2026, 3) == datetime(2026, 3, 27)


def test_impossible_nth_weekday_raises():
    # March 2026 has five Mondays, but only four Wednesdays.
    with pytest.raises(ValueError):
        nth_weekday_of_month(5, "Wednesday", 2026, 3)


def test_unparseable_raises():
    with pytest.raises(ValueError):
        resolve("not a date at all", base=BASE)
