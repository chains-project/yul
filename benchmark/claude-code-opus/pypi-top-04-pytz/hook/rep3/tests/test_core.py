from datetime import datetime, timedelta

import pytest

from worldtime.core import UTC, NaiveDatetimeError, convert, get_zone, localize, to_utc


def test_rejects_naive():
    with pytest.raises(NaiveDatetimeError):
        to_utc(datetime(2026, 1, 1))


def test_unknown_zone():
    with pytest.raises(ValueError):
        get_zone("Mars/Olympus_Mons")


def test_convert_across_regions():
    dt = datetime(2026, 7, 1, 12, 0, tzinfo=UTC)
    assert convert(dt, "Asia/Tokyo").hour == 21
    assert convert(dt, "America/New_York").hour == 8  # EDT, UTC-4
    assert convert(dt, "Asia/Kolkata").minute == 30  # UTC+5:30


def test_southern_hemisphere_dst():
    summer = localize(2026, 1, 15, 12, zone="Australia/Sydney")
    winter = localize(2026, 7, 15, 12, zone="Australia/Sydney")
    assert summer.utcoffset() == timedelta(hours=11)
    assert winter.utcoffset() == timedelta(hours=10)


def test_ambiguous_fall_back_uses_fold():
    # 01:30 occurs twice in New York on 2026-11-01.
    first = localize(2026, 11, 1, 1, 30, zone="America/New_York", fold=0)
    second = localize(2026, 11, 1, 1, 30, zone="America/New_York", fold=1)
    assert to_utc(second) - to_utc(first) == timedelta(hours=1)
