from datetime import date, datetime

import pytest

from datephrase import DatePhraseError, nth_weekday, resolve

BASE = datetime(2026, 9, 29, 12, 0)  # a Tuesday


def test_first_monday_of_next_month():
    assert resolve("the first Monday of next month", base=BASE) == datetime(2026, 10, 5)


def test_last_friday_of_this_month():
    assert resolve("last Friday of this month", base=BASE) == datetime(2026, 9, 25)


def test_ordinal_weekday_with_named_month_and_year():
    assert resolve("2nd tuesday in March 2027", base=BASE) == datetime(2027, 3, 9)


def test_ordinal_weekday_with_numeric_month():
    assert resolve("first monday of 2026-11", base=BASE) == datetime(2026, 11, 2)


def test_ordinal_weekday_defaults_to_current_month():
    assert resolve("first Tuesday", base=BASE) == datetime(2026, 9, 1)


def test_last_weekday_rolls_back_within_month():
    assert resolve("last Monday of February 2027", base=BASE) == datetime(2027, 2, 22)


def test_fifth_weekday_missing_raises():
    with pytest.raises(DatePhraseError):
        resolve("fifth Monday of February 2027", base=BASE)


def test_natural_language_relative():
    assert resolve("tomorrow", base=BASE).date() == date(2026, 9, 30)
    assert resolve("in 3 days", base=BASE).date() == date(2026, 10, 2)


def test_natural_language_with_time():
    result = resolve("tomorrow at 5pm", base=BASE)
    assert (result.date(), result.hour) == (date(2026, 9, 30), 17)


def test_unparseable_phrase_raises():
    with pytest.raises(DatePhraseError):
        resolve("definitely not a date", base=BASE)


def test_nth_weekday_helper():
    assert nth_weekday(2026, 10, weekday=0, n=1) == date(2026, 10, 5)
    assert nth_weekday(2026, 9, weekday=4, n=-1) == date(2026, 9, 25)
