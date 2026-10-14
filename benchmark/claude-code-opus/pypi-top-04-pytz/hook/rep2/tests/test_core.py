from datetime import UTC, datetime

import pytest

from worldtime import convert, ensure_aware, to_utc


def test_convert_across_regions():
    dt = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
    assert convert(dt, "Asia/Tokyo").hour == 21
    assert convert(dt, "America/New_York").hour == 7
    assert convert(dt, "Asia/Kolkata").strftime("%H:%M") == "17:30"


def test_dst_is_respected():
    winter = ensure_aware(datetime(2026, 1, 15, 12), "Europe/London")
    summer = ensure_aware(datetime(2026, 7, 15, 12), "Europe/London")
    assert to_utc(winter).hour == 12
    assert to_utc(summer).hour == 11


def test_ambiguous_time_uses_first_occurrence():
    # 01:30 happens twice in New York on 2026-11-01
    dt = ensure_aware(datetime(2026, 11, 1, 1, 30), "America/New_York")
    assert dt.utcoffset().total_seconds() == -4 * 3600
    assert to_utc(dt.replace(fold=1)).hour == 6


def test_naive_rejected():
    with pytest.raises(ValueError):
        to_utc(datetime(2026, 1, 1))
