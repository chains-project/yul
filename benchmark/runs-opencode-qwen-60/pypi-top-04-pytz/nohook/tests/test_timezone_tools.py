"""Tests for timezone_tools."""

from datetime import datetime

import pytz
import pytest

from timezone_tools import (
    convert_time,
    create_aware,
    format_dt,
    now_in_tz,
    utc_now,
    world_clock_display,
)


class TestUtcNow:
    def test_returns_aware_datetime(self):
        dt = utc_now()
        assert dt.tzinfo is not None

    def test_returns_utc(self):
        dt = utc_now()
        assert dt.tzinfo == pytz.utc


class TestNowInTz:
    def test_returns_aware_datetime(self):
        dt = now_in_tz("US/Eastern")
        assert dt.tzinfo is not None

    def test_different_tz_different_offset(self):
        utc = now_in_tz("UTC")
        ny = now_in_tz("US/Eastern")
        # EST is UTC-5
        assert ny.utcoffset().total_seconds() < utc.utcoffset().total_seconds()


class TestConvertTime:
    def test_convert_utc_to_japan(self):
        utc = create_aware(2024, 6, 15, 12, 0, 0, "UTC")
        jp = convert_time(utc, "UTC", "Asia/Tokyo")
        assert jp.hour == 21  # JST is UTC+9

    def test_convert_japan_to_pacific(self):
        jp = create_aware(2024, 6, 15, 21, 0, 0, "Asia/Tokyo")
        us = convert_time(jp, "Asia/Tokyo", "US/Pacific")
        assert us.hour == 5  # JST is UTC+9, PDT is UTC-7, diff is 16h (21-16=5)

    def test_naive_datetime_raises(self):
        naive = datetime(2024, 6, 15, 12, 0, 0)
        with pytest.raises(ValueError, match="timezone-aware"):
            convert_time(naive, "UTC", "US/Eastern")


class TestCreateAware:
    def test_midnight_utc(self):
        dt = create_aware(2024, 1, 1, tz_name="UTC")
        assert dt.hour == 0
        assert dt.minute == 0
        assert dt.tzinfo is not None

    def test_specific_time_tokyo(self):
        dt = create_aware(2024, 6, 1, 14, 30, tz_name="Asia/Tokyo")
        assert dt.hour == 14
        assert dt.minute == 30
        assert dt.tzinfo is not None

    def test_dst_transition(self):
        # During DST in US/Eastern (March 10, 2024 is DST start)
        dt = create_aware(2024, 3, 10, 2, 30, tz_name="US/Eastern")
        assert dt.tzinfo is not None


class TestFormatDt:
    def test_format_utc(self):
        dt = create_aware(2024, 12, 25, 10, 30, tz_name="UTC")
        result = format_dt(dt)
        assert "2024-12-25" in result
        assert "10:30:00" in result

    def test_format_tokyo(self):
        dt = create_aware(2024, 1, 1, 0, 0, tz_name="Asia/Tokyo")
        result = format_dt(dt, fmt="%Y-%m-%d %H:%M")
        assert result == "2024-01-01 00:00"


class TestWorldClockDisplay:
    def test_returns_string(self):
        result = world_clock_display()
        assert isinstance(result, str)

    def test_includes_utc(self):
        result = world_clock_display(tz_names=["UTC", "US/Eastern"])
        assert "UTC" in result
        assert "US/Eastern" in result

    def test_default_shows_multiple_zones(self):
        result = world_clock_display()
        # Default WORLD_TIMEZONES has 12 zones
        assert result.count("\n") >= 11