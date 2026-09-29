from datetime import date, datetime

import pytest

from flexdates import add_relative, nth_weekday_of_month, parse_date, resolve

BASE = datetime(2024, 1, 15, 9, 30)  # a Monday


def test_parse_date_absolute():
    assert parse_date("2024-03-05").date() == date(2024, 3, 5)


def test_parse_date_relative_to_base():
    assert parse_date("tomorrow", base=BASE).date() == date(2024, 1, 16)


def test_parse_date_rejects_empty():
    with pytest.raises(ValueError):
        parse_date("   ")


def test_parse_date_rejects_garbage():
    with pytest.raises(ValueError):
        parse_date("not a real date", base=BASE)


def test_add_relative_accepts_date():
    assert add_relative(date(2024, 1, 31), months=1).date() == date(2024, 2, 29)


def test_add_relative_mixed_units():
    assert add_relative(BASE, months=1, days=-3).date() == date(2024, 2, 12)


def test_nth_weekday_of_month_by_name():
    assert nth_weekday_of_month(2024, 2, "monday", 1).date() == date(2024, 2, 5)


def test_nth_weekday_of_month_last():
    assert nth_weekday_of_month(2024, 2, "monday", -1).date() == date(2024, 2, 26)


def test_nth_weekday_of_month_out_of_range():
    with pytest.raises(ValueError):
        nth_weekday_of_month(2024, 13, "monday", 1)


def test_resolve_first_monday_of_next_month():
    assert resolve("the first Monday of next month", base=BASE).date() == date(2024, 2, 5)


def test_resolve_last_friday_of_this_month():
    assert resolve("last Friday of this month", base=BASE).date() == date(2024, 1, 26)


def test_resolve_named_month():
    assert resolve("first Monday of March 2024", base=BASE).date() == date(2024, 3, 4)


def test_resolve_falls_back_to_parse_date():
    assert resolve("tomorrow", base=BASE).date() == date(2024, 1, 16)
