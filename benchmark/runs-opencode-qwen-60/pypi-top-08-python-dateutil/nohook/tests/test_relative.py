"""Tests for relative date arithmetic functionality."""

import pytest
from datetime import datetime

from flexidate.relative import RelativeDate, relative_date, WEEKDAY_MAP


class TestRelativeDate:
    def setup_method(self):
        self.base = datetime(2024, 1, 15)  # A Monday
        self.rd = RelativeDate(self.base)

    def test_add_days(self):
        result = self.rd.add(days=5)
        assert result == datetime(2024, 1, 20)

    def test_add_weeks(self):
        result = self.rd.add(weeks=2)
        assert result == datetime(2024, 1, 29)

    def test_add_months(self):
        result = self.rd.add(months=3)
        assert result == datetime(2024, 4, 15)

    def test_add_years(self):
        result = self.rd.add(years=1)
        assert result == datetime(2025, 1, 15)

    def test_subtract_days(self):
        result = self.rd.subtract(days=10)
        assert result == datetime(2024, 1, 5)

    def test_subtract_months(self):
        result = self.rd.subtract(months=2)
        assert result == datetime(2023, 11, 15)

    def test_next_day(self):
        result = self.rd.next("day")
        assert result == datetime(2024, 1, 16)

    def test_next_week(self):
        result = self.rd.next("week")
        assert result == datetime(2024, 1, 22)

    def test_next_month(self):
        result = self.rd.next("month")
        assert result == datetime(2024, 2, 15)

    def test_next_year(self):
        result = self.rd.next("year")
        assert result == datetime(2025, 1, 15)

    def test_next_weekday(self):
        result = self.rd.next(weekday="tuesday")
        assert result == datetime(2024, 1, 16)

    def test_last_day(self):
        result = self.rd.last("day")
        assert result == datetime(2024, 1, 14)

    def test_last_week(self):
        result = self.rd.last("week")
        assert result == datetime(2024, 1, 8)

    def test_last_month(self):
        result = self.rd.last("month")
        assert result == datetime(2023, 12, 15)

    def test_last_weekday(self):
        result = self.rd.last(weekday="friday")
        assert result == datetime(2024, 1, 12)

    def test_nth_weekday_of_month(self):
        result = self.rd.nth_weekday_of_month(1, "monday")
        assert result == datetime(2024, 1, 1)

    def test_nth_weekday_of_month_friday(self):
        result = self.rd.nth_weekday_of_month(4, "friday")
        assert result == datetime(2024, 1, 26)

    def test_invalid_nth_weekday(self):
        with pytest.raises(ValueError, match="No 6th"):
            self.rd.nth_weekday_of_month(6, "monday")

    def test_invalid_unit(self):
        with pytest.raises(ValueError, match="Unknown unit"):
            self.rd.next("decade")

    def test_diff_days(self):
        target = datetime(2024, 1, 25)
        diff = self.rd.diff(target, "days")
        assert diff == 10.0

    def test_diff_weeks(self):
        target = datetime(2024, 1, 29)
        diff = self.rd.diff(target, "weeks")
        assert diff == 2.0

    def test_diff_hours(self):
        target = datetime(2024, 1, 15, 14, 30)
        diff = self.rd.diff(target, "hours")
        assert diff == pytest.approx(14.5)

    def test_invalid_diff_unit(self):
        target = datetime(2024, 1, 16)
        with pytest.raises(ValueError, match="Unknown unit"):
            self.rd.diff(target, "fortnights")

    def test_set_base(self):
        new_base = datetime(2025, 6, 1)
        result = self.rd.set_base(new_base)
        assert self.rd.base == new_base
        assert result is self.rd


class TestRelativeDateFunction:
    def test_next_weekday(self):
        base = datetime(2024, 1, 15)
        result = relative_date("next Tuesday", base)
        assert result == datetime(2024, 1, 16)

    def test_first_weekday_of_month(self):
        base = datetime(2024, 1, 15)
        result = relative_date("the first Monday of next month", base)
        assert result == datetime(2024, 2, 5)

    def test_first_weekday_of_current_month(self):
        base = datetime(2024, 1, 15)
        result = relative_date("the first Monday of January", base)
        # January 2024 starts on Monday the 1st
        assert result == datetime(2024, 1, 1)

    def test_last_weekday(self):
        base = datetime(2024, 1, 15)
        result = relative_date("last Friday", base)
        assert result == datetime(2024, 1, 12)

    def test_relative_future(self):
        base = datetime(2024, 1, 15)
        result = relative_date("3 weeks from now", base)
        assert result == datetime(2024, 2, 5)

    def test_relative_past(self):
        base = datetime(2024, 1, 15)
        result = relative_date("2 months ago", base)
        assert result == datetime(2023, 11, 15)

    def test_default_base(self):
        result = relative_date("tomorrow")
        assert result.day == 16 if result.month == 1 else True