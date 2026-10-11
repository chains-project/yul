from datetime import datetime, timedelta, timezone

import pytest

from worldtime import convert, current_time, localize, parse, region_time, to_zone
from worldtime.core import is_ambiguous, is_nonexistent


def test_to_zone_accepts_name_and_instance():
    assert to_zone("Asia/Tokyo").key == "Asia/Tokyo"
    assert to_zone(to_zone("Asia/Tokyo")).key == "Asia/Tokyo"


def test_convert_preserves_instant_across_regions():
    ny = localize(datetime(2024, 1, 15, 9, 0), "America/New_York")
    tokyo = convert(ny, "Asia/Tokyo")
    kolkata = convert(ny, "Asia/Kolkata")

    assert ny.utcoffset() == timedelta(hours=-5)
    assert tokyo.utcoffset() == timedelta(hours=9)
    assert kolkata.utcoffset() == timedelta(hours=5, minutes=30)
    assert ny == tokyo == kolkata


def test_convert_rejects_naive_datetime():
    with pytest.raises(ValueError):
        convert(datetime(2024, 1, 1, 12, 0), "UTC")


def test_current_time_is_aware():
    moment = current_time("Europe/Berlin")
    assert moment.tzinfo is not None
    assert moment.utcoffset() is not None


def test_region_time_accepts_description_and_aware_at():
    at = datetime(2024, 6, 1, 12, 0, tzinfo=timezone.utc)
    assert region_time("japan", at=at).hour == 21
    assert region_time("US-WEST", at=at).hour == 5


def test_unknown_region_raises():
    with pytest.raises(KeyError):
        region_time("atlantis")


def test_parse_zulu_and_offset():
    assert parse("2024-03-10T07:00:00Z") == datetime(
        2024, 3, 10, 7, 0, tzinfo=timezone.utc
    )
    assert parse("2024-03-10T07:00:00+02:00").utcoffset() == timedelta(hours=2)


def test_parse_naive_uses_supplied_zone():
    moment = parse("2024-06-01T12:00:00", "Asia/Kolkata")
    assert moment.utcoffset() == timedelta(hours=5, minutes=30)


def test_spring_forward_gap_is_nonexistent():
    zone = to_zone("America/New_York")
    # 02:30 on 2024-03-10 never occurs; clocks jump 02:00 -> 03:00.
    gap = datetime(2024, 3, 10, 2, 30)
    assert is_nonexistent(gap, zone)
    assert not is_ambiguous(gap, zone)

    with pytest.raises(ValueError):
        localize(gap, zone, strict=True)


def test_fall_back_hour_is_ambiguous_and_fold_selects_offset():
    zone = to_zone("America/New_York")
    repeated = datetime(2024, 11, 3, 1, 30)
    assert is_ambiguous(repeated, zone)
    assert not is_nonexistent(repeated, zone)

    first = localize(repeated, zone, fold=0)
    second = localize(repeated, zone, fold=1)
    assert first.utcoffset() == timedelta(hours=-4)
    assert second.utcoffset() == timedelta(hours=-5)
    assert convert(second, "UTC") - convert(first, "UTC") == timedelta(hours=1)

    with pytest.raises(ValueError):
        localize(repeated, zone, strict=True)


def test_localize_rejects_aware_datetime():
    aware = datetime(2024, 1, 1, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        localize(aware, "UTC")
