from datetime import datetime, timedelta, timezone

import pytest

from worldtime import zones


def test_zone_for_is_case_insensitive():
    assert zones.zone_for("US-Eastern").key == "America/New_York"


def test_zone_for_accepts_raw_iana_name():
    assert zones.zone_for("Asia/Tokyo").key == "Asia/Tokyo"


def test_zone_for_unknown_region_raises_keyerror():
    with pytest.raises(KeyError):
        zones.zone_for("atlantis")


def test_to_region_converts_between_far_flung_zones():
    utc_noon = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
    eastern = zones.to_region(utc_noon, "us-eastern")
    india = zones.to_region(utc_noon, "india")

    assert eastern.hour == 7
    assert eastern.utcoffset() == timedelta(hours=-5)
    assert india.hour == 17
    assert india.minute == 30
    assert india.utcoffset() == timedelta(hours=5, minutes=30)


def test_to_region_assumes_utc_for_naive_input():
    naive = datetime(2024, 1, 15, 12, 0)
    assert zones.to_region(naive, "utc") == datetime(
        2024, 1, 15, 12, 0, tzinfo=timezone.utc
    )


def test_localize_attaches_aware_timezone():
    result = zones.localize(datetime(2024, 6, 1, 9, 30), "japan")
    assert result.tzinfo is not None
    assert result.utcoffset() == timedelta(hours=9)


def test_localize_rejects_aware_input():
    aware = datetime(2024, 6, 1, 9, 30, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        zones.localize(aware, "japan")


def test_conversion_across_us_spring_forward():
    just_before = datetime(2024, 3, 10, 6, 59, tzinfo=timezone.utc)
    just_after = datetime(2024, 3, 10, 7, 0, tzinfo=timezone.utc)

    assert zones.to_region(just_before, "us-eastern").hour == 1
    assert zones.to_region(just_before, "us-eastern").utcoffset() == timedelta(hours=-5)
    assert zones.to_region(just_after, "us-eastern").hour == 3
    assert zones.to_region(just_after, "us-eastern").utcoffset() == timedelta(hours=-4)


def test_localize_resolves_spring_forward_gap():
    resolved = zones.localize(datetime(2024, 3, 10, 2, 30), "us-eastern")
    assert resolved.hour == 3
    assert resolved.minute == 30
    assert resolved.utcoffset() == timedelta(hours=-4)


def test_localize_honours_fold_for_repeated_hour():
    first = zones.localize(datetime(2024, 11, 3, 1, 30, fold=0), "us-eastern")
    second = zones.localize(datetime(2024, 11, 3, 1, 30, fold=1), "us-eastern")

    assert first.utcoffset() == timedelta(hours=-4)
    assert second.utcoffset() == timedelta(hours=-5)
    assert first.astimezone(timezone.utc) != second.astimezone(timezone.utc)


def test_wall_clock_arithmetic_tracks_dst_offset():
    before = zones.localize(datetime(2024, 3, 9, 12, 0), "us-eastern")
    after = before + timedelta(days=1)
    assert after.hour == 12
    assert after.utcoffset() == timedelta(hours=-4)


def test_absolute_arithmetic_across_dst_uses_utc():
    before = zones.localize(datetime(2024, 3, 9, 12, 0), "us-eastern")
    after = zones.to_region(before.astimezone(timezone.utc) + timedelta(hours=24), "us-eastern")
    assert after.hour == 13
    assert after.utcoffset() == timedelta(hours=-4)


def test_table_covers_every_region():
    rows = zones.table(at=datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc))
    assert len(rows) == len(zones.REGIONS)
    assert {row["region"] for row in rows} == set(zones.REGIONS)
    for row in rows:
        assert isinstance(row["dst"], bool)
        assert len(row["utc_offset"]) == 6
