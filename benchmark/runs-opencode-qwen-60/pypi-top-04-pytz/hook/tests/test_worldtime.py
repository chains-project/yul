"""Tests for worldtime package."""

import unittest
from datetime import datetime
import pytz

from worldtime import (
    TIMEZONES,
    get_timezone,
    now_in_tz,
    convert_time,
    list_timezones,
)
from worldtime.formatter import format_dt, format_comparison


class TestTimezoneAliases(unittest.TestCase):
    """Test timezone alias resolution."""

    def test_list_timezones_returns_dict(self):
        tzs = list_timezones()
        self.assertIsInstance(tzs, dict)
        self.assertGreater(len(tzs), 0)

    def test_all_aliases_resolve(self):
        for alias in TIMEZONES:
            tz = get_timezone(alias)
            self.assertIsNotNone(tz)

    def test_unknown_timezone_raises(self):
        with self.assertRaises(ValueError):
            get_timezone("nonexistent/timezone")

    def test_timezone_is_pytz_tzinfo(self):
        tz = get_timezone("utc")
        self.assertIsInstance(tz, pytz.BaseTzInfo)


class TestNowInTz(unittest.TestCase):
    """Test getting current time in various timezones."""

    def test_utc_now_has_tzinfo(self):
        dt = now_in_tz("utc")
        self.assertIsNotNone(dt.tzinfo)

    def test_utc_now_is_utc(self):
        dt = now_in_tz("utc")
        self.assertEqual(dt.tzname(), "UTC")

    def test_pacific_now_has_offset(self):
        dt = now_in_tz("pst")
        self.assertIsNotNone(dt.tzinfo)
        self.assertTrue("PST" in dt.tzname() or "PDT" in dt.tzname())


class TestConvertTime(unittest.TestCase):
    """Test timezone conversion."""

    def test_convert_utc_to_pacific(self):
        dt = datetime(2024, 1, 15, 12, 0, 0, tzinfo=pytz.UTC)
        converted = convert_time(dt, "utc", "pst")
        self.assertEqual(converted.hour, 4)

    def test_convert_pacific_to_utc(self):
        pacific = pytz.timezone("US/Pacific")
        dt = pacific.localize(datetime(2024, 1, 15, 4, 0, 0))
        converted = convert_time(dt, "pst", "utc")
        self.assertEqual(converted.hour, 12)

    def test_naive_datetime_gets_localized(self):
        dt = datetime(2024, 6, 15, 12, 0, 0)
        converted = convert_time(dt, "utc", "pst")
        self.assertIsNotNone(converted.tzinfo)

    def test_conversion_preserves_instant(self):
        dt = datetime(2024, 1, 25, 0, 0, 0, tzinfo=pytz.UTC)
        converted = convert_time(dt, "utc", "jst")
        self.assertEqual(converted.hour, 9)


class TestFormatter(unittest.TestCase):
    """Test formatting utilities."""

    def test_format_dt_utc(self):
        dt = datetime(2024, 6, 15, 12, 0, 0, tzinfo=pytz.UTC)
        formatted = format_dt(dt, "utc")
        self.assertIn("UTC", formatted)

    def test_format_comparison_multiple(self):
        dt = datetime(2024, 6, 15, 12, 0, 0, tzinfo=pytz.UTC)
        results = format_comparison(dt, ["utc", "pst", "jst"])
        self.assertEqual(len(results), 3)
        self.assertIn("utc", results)
        self.assertIn("pst", results)
        self.assertIn("jst", results)


if __name__ == "__main__":
    unittest.main()