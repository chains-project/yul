from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from worldclock import convert, ensure_aware, offset_hours, to_utc


def test_convert_across_regions():
    utc = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
    tokyo = convert(utc, "Asia/Tokyo")
    assert tokyo.hour == 21
    assert tokyo.utcoffset().total_seconds() == 9 * 3600


def test_convert_rejects_naive():
    with pytest.raises(ValueError):
        convert(datetime(2024, 1, 1), "UTC")


def test_ensure_aware_assumes_utc():
    aware = ensure_aware(datetime(2024, 1, 1, 0, 0))
    assert aware.tzinfo == ZoneInfo("UTC")


def test_ensure_aware_is_idempotent():
    original = datetime(2024, 1, 1, tzinfo=ZoneInfo("Asia/Tokyo"))
    assert ensure_aware(original) is original


def test_offset_hours_new_york_winter():
    utc = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
    assert offset_hours(utc, "America/New_York") == -5.0


def test_offset_hours_new_york_summer_dst():
    utc = datetime(2024, 7, 15, 12, 0, tzinfo=timezone.utc)
    assert offset_hours(utc, "America/New_York") == -4.0


def test_to_utc_handles_bst():
    moment = datetime(2024, 6, 1, 9, 30, tzinfo=ZoneInfo("Europe/London"))
    assert to_utc(moment).hour == 8
