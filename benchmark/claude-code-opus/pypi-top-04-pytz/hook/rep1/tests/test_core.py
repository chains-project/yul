from datetime import UTC, datetime, timedelta

import pytest

from worldtime import convert, ensure_aware, get_zone, to_utc


def test_naive_datetime_rejected():
    with pytest.raises(ValueError, match="naive"):
        ensure_aware(datetime(2026, 1, 1))


def test_unknown_zone_rejected():
    with pytest.raises(ValueError, match="Unknown timezone"):
        get_zone("Mars/Olympus_Mons")


def test_convert_preserves_instant():
    moment = datetime(2026, 7, 1, 12, 0, tzinfo=UTC)
    tokyo = convert(moment, "Asia/Tokyo")
    assert tokyo.hour == 21
    assert tokyo == moment


def test_half_hour_offset():
    india = convert(datetime(2026, 1, 1, tzinfo=UTC), "Asia/Kolkata")
    assert india.utcoffset() == timedelta(hours=5, minutes=30)


def test_dst_transition_berlin():
    berlin = get_zone("Europe/Berlin")
    before = datetime(2026, 3, 29, 0, 59, tzinfo=UTC).astimezone(berlin)
    after = datetime(2026, 3, 29, 1, 0, tzinfo=UTC).astimezone(berlin)
    assert before.utcoffset() == timedelta(hours=1)
    assert after.utcoffset() == timedelta(hours=2)


def test_southern_hemisphere_dst_is_opposite():
    sydney = get_zone("Australia/Sydney")
    jan = datetime(2026, 1, 15, tzinfo=sydney)
    jul = datetime(2026, 7, 15, tzinfo=sydney)
    assert jan.utcoffset() == timedelta(hours=11)
    assert jul.utcoffset() == timedelta(hours=10)


def test_ambiguous_wall_time_uses_fold():
    # 01:30 happens twice in New York on 2026-11-01.
    ny = get_zone("America/New_York")
    first = datetime(2026, 11, 1, 1, 30, tzinfo=ny, fold=0)
    second = datetime(2026, 11, 1, 1, 30, tzinfo=ny, fold=1)
    assert to_utc(second) - to_utc(first) == timedelta(hours=1)
