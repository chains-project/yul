"""Tests for date parsing functionality."""

import pytest
from datetime import datetime

from flexidate.parser import parse_date, parse_date_range, parse_multiple_dates


class TestParseDate:
    def test_iso_format(self):
        result = parse_date("2024-01-15")
        assert result == datetime(2024, 1, 15)

    def test_written_month(self):
        result = parse_date("January 15, 2024")
        assert result == datetime(2024, 1, 15)

    def test_short_month(self):
        result = parse_date("Jan 15, 2024")
        assert result == datetime(2024, 1, 15)

    def test_european_format(self):
        result = parse_date("15/01/2024")
        assert result == datetime(2024, 1, 15)

    def test_relative_day(self):
        base = datetime(2024, 1, 15)
        result = parse_date("tomorrow", default=base)
        assert result == datetime(2024, 1, 16)

    def test_next_weekday(self):
        base = datetime(2024, 1, 15)  # Monday
        result = parse_date("next Friday", default=base)
        assert result == datetime(2024, 1, 19)

    def test_in_days(self):
        base = datetime(2024, 1, 15)
        result = parse_date("in 3 days", default=base)
        assert result == datetime(2024, 1, 18)

    def test_with_time(self):
        result = parse_date("2024-01-15 14:30:00")
        assert result == datetime(2024, 1, 15, 14, 30)

    def test_month_name(self):
        result = parse_date("March 1, 2024")
        assert result == datetime(2024, 3, 1)


class TestParseDateRange:
    def test_basic_range(self):
        start, end = parse_date_range("2024-01-01", "2024-12-31")
        assert start == datetime(2024, 1, 1)
        assert end == datetime(2024, 12, 31)

    def test_named_months(self):
        start, end = parse_date_range("January 1, 2024", "March 31, 2024")
        assert start == datetime(2024, 1, 1)
        assert end == datetime(2024, 3, 31)


class TestParseMultipleDates:
    def test_multiple(self):
        dates = parse_multiple_dates([
            "2024-01-15",
            "2024-02-20",
            "March 5, 2024",
        ])
        assert dates[0] == datetime(2024, 1, 15)
        assert dates[1] == datetime(2024, 2, 20)
        assert dates[2] == datetime(2024, 3, 5)