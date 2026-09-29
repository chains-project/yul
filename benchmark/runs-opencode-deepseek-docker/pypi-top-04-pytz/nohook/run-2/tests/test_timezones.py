from datetime import datetime, timedelta, timezone

import pytest

from worldclock import (
    UTC,
    UnknownTimeZoneError,
    available_regions,
    convert,
    get_zone,
    localize,
    now,
    parse,
    to_utc,
    world_clock,
)


def test_now_is_timezone_aware():
    moment = now("Asia/Tokyo")
    assert moment.tzinfo is not None
    assert moment.utcoffset() == timedelta(hours=9)


def test_get_zone_accepts_existing_zone():
    zone = get_zone("Europe/Paris")
    assert get_zone(zone) is zone


def test_get_zone_rejects_unknown_name():
    with pytest.raises(UnknownTimeZoneError):
        get_zone("Mars/Olympus_Mons")


def test_convert_preserves_the_instant():
    moment = datetime(2024, 1, 1, 12, 0, tzinfo=UTC)
    converted = convert(moment, "America/New_York")
    assert converted == moment
    assert converted.hour == 7


def test_convert_rejects_naive_datetime():
    with pytest.raises(ValueError):
        convert(datetime(2024, 1, 1, 12, 0), "UTC")


def test_localize_attaches_zone_to_naive_datetime():
    localized = localize(datetime(2024, 6, 1, 9, 30), "Europe/Berlin")
    assert localized.tzinfo == get_zone("Europe/Berlin")
    assert localized.utcoffset() == timedelta(hours=2)


def test_localize_converts_aware_datetime():
    moment = datetime(2024, 6, 1, 9, 30, tzinfo=UTC)
    localized = localize(moment, "Asia/Kolkata")
    assert localized == moment
    assert localized.utcoffset() == timedelta(hours=5, minutes=30)


def test_to_utc_normalizes_offset():
    moment = datetime(2024, 6, 1, 9, 30, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    assert to_utc(moment) == datetime(2024, 6, 1, 4, 0, tzinfo=UTC)


def test_dst_transition_in_new_york():
    before = convert(datetime(2024, 3, 10, 6, 59, tzinfo=UTC), "America/New_York")
    after = convert(datetime(2024, 3, 10, 7, 0, tzinfo=UTC), "America/New_York")
    assert before.strftime("%H:%M %Z") == "01:59 EST"
    assert after.strftime("%H:%M %Z") == "03:00 EDT"


def test_parse_uses_default_zone_for_naive_input():
    parsed = parse("2024-03-10T07:00:00", "America/New_York")
    assert parsed.tzinfo == get_zone("America/New_York")


def test_parse_keeps_explicit_offset():
    parsed = parse("2024-03-10T07:00:00+00:00")
    assert parsed == datetime(2024, 3, 10, 7, 0, tzinfo=UTC)


def test_world_clock_returns_each_zone():
    reference = datetime(2024, 1, 1, 12, 0, tzinfo=UTC)
    clock = world_clock(["UTC", "Asia/Tokyo", "America/Los_Angeles"], at=reference)
    assert set(clock) == {"UTC", "Asia/Tokyo", "America/Los_Angeles"}
    assert clock["Asia/Tokyo"].hour == 21
    assert clock["America/Los_Angeles"].hour == 4


def test_world_clock_rejects_naive_reference():
    with pytest.raises(ValueError):
        world_clock(["UTC"], at=datetime(2024, 1, 1, 12, 0))


def test_available_regions_is_filterable_and_sorted():
    regions = available_regions("Asia")
    assert regions
    assert all(name.startswith("Asia/") for name in regions)
    assert regions == sorted(regions)
