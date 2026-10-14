from datetime import UTC, datetime

import pytest

from worldtime.core import convert, ensure_aware, is_valid_local, localize, to_utc


def test_convert_across_regions():
    dt = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
    assert convert(dt, "Asia/Tokyo").hour == 21
    assert convert(dt, "America/New_York").hour == 7
    assert convert(dt, "Asia/Kolkata").minute == 30  # UTC+05:30


def test_dst_changes_offset():
    winter = localize(datetime(2026, 1, 15, 12), "Europe/Berlin")
    summer = localize(datetime(2026, 7, 15, 12), "Europe/Berlin")
    assert winter.utcoffset().total_seconds() == 3600
    assert summer.utcoffset().total_seconds() == 7200


def test_ambiguous_time_fold():
    # 2026-11-01 01:30 happens twice in New York
    first = localize(datetime(2026, 11, 1, 1, 30), "America/New_York", fold=0)
    second = localize(datetime(2026, 11, 1, 1, 30), "America/New_York", fold=1)
    assert to_utc(first).hour == 5 and to_utc(second).hour == 6


def test_nonexistent_time_detected():
    # 2026-03-08 02:30 is skipped in New York
    assert not is_valid_local(localize(datetime(2026, 3, 8, 2, 30), "America/New_York"))
    assert is_valid_local(localize(datetime(2026, 3, 8, 3, 30), "America/New_York"))


def test_naive_rejected():
    with pytest.raises(ValueError):
        ensure_aware(datetime(2026, 1, 1))
    with pytest.raises(ValueError):
        localize(datetime(2026, 1, 1, tzinfo=UTC), "UTC")
