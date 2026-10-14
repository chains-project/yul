from datetime import UTC, datetime, timedelta

import pytest

from worldtime import (
    NaiveDatetimeError,
    is_ambiguous,
    localize,
    now_utc,
    to_utc,
    to_zone,
    world_clock,
)


def test_now_utc_is_aware():
    assert now_utc().utcoffset() == timedelta(0)


def test_naive_input_rejected():
    with pytest.raises(NaiveDatetimeError):
        to_zone(datetime(2026, 1, 1), "Asia/Tokyo")


def test_unknown_zone_rejected():
    with pytest.raises(ValueError, match="Unknown IANA timezone"):
        to_zone(now_utc(), "Mars/Olympus_Mons")


def test_same_instant_across_zones():
    instant = datetime(2026, 7, 1, 12, 0, tzinfo=UTC)
    clocks = world_clock(instant, ["America/New_York", "Asia/Kolkata", "Australia/Sydney"])
    assert clocks["America/New_York"].hour == 8  # EDT, UTC-4
    assert (clocks["Asia/Kolkata"].hour, clocks["Asia/Kolkata"].minute) == (17, 30)  # UTC+5:30
    assert clocks["Australia/Sydney"].hour == 22  # AEST (southern-hemisphere winter)
    assert all(to_utc(dt) == instant for dt in clocks.values())


def test_dst_changes_offset():
    winter = localize(datetime(2026, 1, 15, 12), "Europe/Berlin")
    summer = localize(datetime(2026, 7, 15, 12), "Europe/Berlin")
    assert winter.utcoffset() == timedelta(hours=1)
    assert summer.utcoffset() == timedelta(hours=2)


def test_nonexistent_time_rejected():
    # US clocks jump 02:00 -> 03:00 on 2026-03-08.
    with pytest.raises(ValueError, match="does not exist"):
        localize(datetime(2026, 3, 8, 2, 30), "America/New_York")


def test_ambiguous_time_uses_fold():
    # US clocks fall back 02:00 -> 01:00 on 2026-11-01, so 01:30 happens twice.
    wall = datetime(2026, 11, 1, 1, 30)
    assert is_ambiguous(wall, "America/New_York")
    first = localize(wall, "America/New_York", fold=0)
    second = localize(wall, "America/New_York", fold=1)
    assert to_utc(second) - to_utc(first) == timedelta(hours=1)
