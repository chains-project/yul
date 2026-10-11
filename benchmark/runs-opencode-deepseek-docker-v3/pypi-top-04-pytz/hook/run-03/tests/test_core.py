from __future__ import annotations

from datetime import datetime, timezone

import pytest

from worldtime.core import convert, ensure_aware, now_in, to_utc


def test_convert_between_regions() -> None:
    utc_dt = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
    tokyo = convert(utc_dt, "Asia/Tokyo")
    assert tokyo.hour == 21
    assert tokyo.utcoffset() is not None
    assert tokyo.utcoffset().total_seconds() == 9 * 3600


def test_dst_boundary_new_york() -> None:
    winter = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
    summer = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
    winter_offset = convert(winter, "America/New_York").utcoffset()
    summer_offset = convert(summer, "America/New_York").utcoffset()
    assert winter_offset is not None and winter_offset.total_seconds() == -5 * 3600
    assert summer_offset is not None and summer_offset.total_seconds() == -4 * 3600


def test_naive_datetime_rejected() -> None:
    with pytest.raises(ValueError):
        ensure_aware(datetime(2026, 1, 1))


def test_roundtrip_to_utc() -> None:
    moment = now_in("Europe/Paris")
    assert to_utc(moment).tzinfo == timezone.utc
