from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from worldclock import (
    ensure_aware,
    format_in_zone,
    get_zone,
    local_time_in_zones,
    now_in,
    to_zone,
)


def test_get_zone_returns_zoneinfo():
    assert get_zone("Asia/Tokyo") == ZoneInfo("Asia/Tokyo")


def test_get_zone_rejects_unknown_name():
    with pytest.raises(ValueError, match="Unknown timezone"):
        get_zone("Mars/Olympus_Mons")


def test_now_in_is_aware_and_localized():
    moment = now_in("Europe/London")
    assert moment.tzinfo is not None
    assert moment.utcoffset() is not None


def test_to_zone_conversion_preserves_instant():
    utc = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
    tokyo = to_zone(utc, "Asia/Tokyo")
    assert tokyo.hour == 21
    assert tokyo.utcoffset() == timedelta(hours=9)
    assert tokyo == utc


def test_dst_offsets_differ_summer_and_winter():
    winter = to_zone(datetime(2024, 1, 15, 12, tzinfo=timezone.utc), "America/New_York")
    summer = to_zone(datetime(2024, 7, 15, 12, tzinfo=timezone.utc), "America/New_York")
    assert winter.utcoffset() == timedelta(hours=-5)
    assert summer.utcoffset() == timedelta(hours=-4)


def test_ensure_aware_assumes_utc_for_naive():
    naive = datetime(2024, 1, 15, 12)
    aware = ensure_aware(naive)
    assert aware.tzinfo is not None
    assert aware.utcoffset() == timedelta(0)


def test_format_in_zone_includes_offset():
    utc = datetime(2024, 1, 15, 12, tzinfo=timezone.utc)
    assert format_in_zone(utc, "Asia/Kolkata") == "2024-01-15 17:30:00 IST+0530"


def test_local_time_in_zones_all_equal_same_instant():
    when = datetime(2024, 1, 15, 12, tzinfo=timezone.utc)
    rows = local_time_in_zones(["UTC", "Asia/Tokyo"], when)
    assert rows["UTC"] == when
    assert rows["Asia/Tokyo"] == when
    assert rows["Asia/Tokyo"].hour == 21
