from datetime import datetime, timezone

import pytest

from worldtime import (
    AmbiguousTimeError,
    NaiveDatetimeError,
    NonExistentTimeError,
    UnknownTimezoneError,
    ensure_aware,
    get_zone,
    localize,
    now,
    parse_iso,
    to_iso,
    to_utc,
    to_zone,
    world_clock,
)


def test_to_zone_converts_same_instant():
    utc = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    tokyo = to_zone(utc, "Asia/Tokyo")
    assert tokyo.hour == 21
    assert tokyo.utcoffset().total_seconds() == 9 * 3600


def test_to_zone_across_many_regions():
    utc = datetime(2026, 7, 1, 0, 0, tzinfo=timezone.utc)
    assert to_zone(utc, "America/Los_Angeles").hour == 17  # previous day, PDT
    assert to_zone(utc, "Australia/Sydney").hour == 10  # AEST
    assert to_zone(utc, "Asia/Kolkata").minute == 30


def test_to_utc_round_trip():
    original = datetime(2026, 5, 20, 8, 30, tzinfo=timezone.utc)
    assert to_utc(to_zone(original, "Europe/Berlin")) == original


def test_naive_datetime_rejected():
    with pytest.raises(NaiveDatetimeError):
        ensure_aware(datetime(2026, 1, 1, 0, 0))
    with pytest.raises(NaiveDatetimeError):
        to_zone(datetime(2026, 1, 1, 0, 0), "UTC")


def test_unknown_timezone():
    with pytest.raises(UnknownTimezoneError):
        get_zone("Mars/Olympus_Mons")


def test_get_zone_passthrough():
    zone = get_zone("UTC")
    assert get_zone(zone) is zone


def test_localize_nonexistent_dst_gap():
    with pytest.raises(NonExistentTimeError):
        localize(datetime(2026, 3, 8, 2, 30), "America/New_York")


def test_localize_ambiguous_dst_fold():
    with pytest.raises(AmbiguousTimeError):
        localize(datetime(2026, 11, 1, 1, 30), "America/New_York")
    first = localize(datetime(2026, 11, 1, 1, 30), "America/New_York", fold=0)
    second = localize(datetime(2026, 11, 1, 1, 30), "America/New_York", fold=1)
    assert first.utcoffset() != second.utcoffset()


def test_parse_iso_requires_offset():
    parsed = parse_iso("2026-03-08T01:30:00-05:00")
    assert parsed.tzinfo is not None
    with pytest.raises(NaiveDatetimeError):
        parse_iso("2026-03-08T01:30:00")


def test_to_iso_round_trip():
    dt = parse_iso("2026-03-08T01:30:00-05:00")
    assert parse_iso(to_iso(dt)) == dt


def test_now_is_aware():
    assert now("Pacific/Auckland").tzinfo is not None


def test_world_clock_snapshot():
    instant = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    clock = world_clock(instant, {"Tokyo": "Asia/Tokyo", "London": "Europe/London"})
    assert set(clock) == {"Tokyo", "London"}
    assert all(dt.tzinfo is not None for dt in clock.values())
    assert clock["Tokyo"].hour == 21
    assert clock["London"].hour == 12
