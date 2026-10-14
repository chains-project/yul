from datetime import UTC, datetime, timedelta

import pytest

from worldtime import convert, ensure_aware, get_zone, localize, now_in, now_utc


def test_now_is_aware():
    assert now_utc().tzinfo is UTC
    assert now_in("Asia/Tokyo").utcoffset() == timedelta(hours=9)


def test_unknown_zone():
    with pytest.raises(ValueError, match="Unknown IANA"):
        get_zone("Mars/Olympus_Mons")


def test_naive_rejected():
    with pytest.raises(ValueError, match="naive"):
        ensure_aware(datetime(2026, 1, 1))
    with pytest.raises(ValueError, match="naive"):
        convert(datetime(2026, 1, 1), "UTC")


def test_convert_preserves_instant():
    utc = datetime(2026, 7, 1, 12, 0, tzinfo=UTC)
    kolkata = convert(utc, "Asia/Kolkata")  # half-hour offset
    assert (kolkata.hour, kolkata.minute) == (17, 30)
    assert kolkata == utc


def test_dst_aware_offsets():
    ny = "America/New_York"
    assert convert(datetime(2026, 1, 15, tzinfo=UTC), ny).utcoffset() == timedelta(hours=-5)
    assert convert(datetime(2026, 7, 15, tzinfo=UTC), ny).utcoffset() == timedelta(hours=-4)
    # Southern hemisphere is the opposite.
    syd = "Australia/Sydney"
    assert convert(datetime(2026, 1, 15, tzinfo=UTC), syd).utcoffset() == timedelta(hours=11)
    assert convert(datetime(2026, 7, 15, tzinfo=UTC), syd).utcoffset() == timedelta(hours=10)


def test_localize_ambiguous_fall_back():
    # 2026-11-01 01:30 happens twice in New York.
    wall = datetime(2026, 11, 1, 1, 30)
    first = localize(wall, "America/New_York", fold=0)
    second = localize(wall, "America/New_York", fold=1)
    assert first.utcoffset() == timedelta(hours=-4)
    assert second.utcoffset() == timedelta(hours=-5)
    assert second.astimezone(UTC) - first.astimezone(UTC) == timedelta(hours=1)


def test_localize_nonexistent_spring_forward():
    # 2026-03-08 02:30 is skipped in New York.
    with pytest.raises(ValueError, match="does not exist"):
        localize(datetime(2026, 3, 8, 2, 30), "America/New_York")
