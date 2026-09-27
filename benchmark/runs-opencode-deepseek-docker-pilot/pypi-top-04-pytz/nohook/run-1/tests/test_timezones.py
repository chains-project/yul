from datetime import datetime, timedelta, timezone

import pytest

from worldclock.timezones import format_iso, list_zones, now, parse_iso, to_zone


def test_now_is_aware():
    dt = now("Asia/Tokyo")
    assert dt.tzinfo is not None
    assert dt.utcoffset() is not None


def test_to_zone_preserves_the_instant():
    start = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
    tokyo = to_zone(start, "Asia/Tokyo")
    assert tokyo == start
    assert tokyo.hour == 21
    assert tokyo.utcoffset() == timedelta(hours=9)


def test_to_zone_rejects_naive_datetime():
    with pytest.raises(ValueError):
        to_zone(datetime(2024, 1, 1), "UTC")


def test_parse_iso_accepts_utc_z_suffix():
    dt = parse_iso("2024-03-10T07:30:00Z")
    assert dt.utcoffset().total_seconds() == 0


def test_parse_iso_rejects_naive_timestamp():
    with pytest.raises(ValueError):
        parse_iso("2024-03-10T07:30:00")


def test_format_iso_roundtrips_through_parse():
    original = now("America/New_York")
    assert parse_iso(format_iso(original)) == original


def test_dst_spring_forward_in_new_york():
    before = parse_iso("2024-03-10T06:30:00Z")
    after = parse_iso("2024-03-10T07:30:00Z")
    assert to_zone(before, "America/New_York").hour == 1
    assert to_zone(after, "America/New_York").hour == 3


def test_half_hour_offset_region():
    instant = parse_iso("2024-01-01T00:00:00Z")
    kolkata = to_zone(instant, "Asia/Kolkata")
    assert kolkata.hour == 5
    assert kolkata.minute == 30


def test_list_zones_filters_by_prefix():
    assert "Europe/Paris" in list_zones("Europe/")
    assert all(zone.startswith("Asia/") for zone in list_zones("Asia/"))
