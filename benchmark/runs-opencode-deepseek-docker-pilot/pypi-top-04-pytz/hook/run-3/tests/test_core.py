from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from worldtime import convert, format_in_zone, now, now_in, parse_datetime
from worldtime.core import local_times, resolve_zone


def test_now_is_utc_aware():
    moment = now()
    assert moment.tzinfo is not None
    assert moment.utcoffset() == timezone.utc.utcoffset(moment)


def test_resolve_zone_alias_and_iana_name():
    assert str(resolve_zone("tokyo")) == "Asia/Tokyo"
    assert str(resolve_zone("Europe/Paris")) == "Europe/Paris"


def test_resolve_unknown_zone_raises():
    with pytest.raises(Exception):
        resolve_zone("Mars/Olympus_Mons")


def test_parse_naive_attaches_zone():
    moment = parse_datetime("2026-09-29 14:30", "new_york")
    assert str(moment.tzinfo) == "America/New_York"


def test_parse_with_offset_keeps_offset():
    moment = parse_datetime("2026-09-29T14:30:00+02:00", "tokyo")
    assert moment.utcoffset().total_seconds() == 2 * 3600


def test_convert_between_zones():
    utc = datetime(2026, 9, 29, 12, 0, tzinfo=timezone.utc)
    assert format_in_zone(utc, "tokyo", "%H:%M") == "21:00"
    assert format_in_zone(utc, "los_angeles", "%H:%M") == "05:00"


def test_convert_rejects_naive_datetime():
    with pytest.raises(ValueError):
        convert(datetime(2026, 9, 29, 12, 0), "tokyo")


def test_dst_offset_changes_across_seasons():
    winter = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
    summer = datetime(2026, 7, 15, 12, 0, tzinfo=timezone.utc)
    ny = ZoneInfo("America/New_York")
    assert winter.astimezone(ny).utcoffset().total_seconds() == -5 * 3600
    assert summer.astimezone(ny).utcoffset().total_seconds() == -4 * 3600


def test_local_times_renders_each_region():
    at = datetime(2026, 9, 29, 12, 0, tzinfo=timezone.utc)
    rows = dict(local_times(at, ["utc", "kolkata"], fmt="%H:%M"))
    assert rows["utc"] == "12:00"
    assert rows["kolkata"] == "17:30"
