from datetime import datetime, timezone

import pytest

from worldclock import (
    UnknownTimeZoneError,
    convert,
    is_ambiguous,
    is_nonexistent,
    local_times,
    localize,
    now_in,
    parse_iso,
    to_utc,
)
from worldclock.cli import main


def test_utc_to_new_york_winter():
    moment = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
    result = convert(moment, "America/New_York")
    assert result.hour == 7
    assert result.utcoffset().total_seconds() == -5 * 3600


def test_utc_to_new_york_summer_applies_dst():
    moment = datetime(2024, 7, 15, 12, 0, tzinfo=timezone.utc)
    result = convert(moment, "America/New_York")
    assert result.hour == 8
    assert result.utcoffset().total_seconds() == -4 * 3600


def test_utc_to_tokyo_has_no_dst():
    moment = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
    result = convert(moment, "Asia/Tokyo")
    assert (result.hour, result.day) == (21, 15)


def test_convert_preserves_the_instant():
    moment = datetime(2024, 6, 1, 9, 30, tzinfo=timezone.utc)
    for zone in ("Europe/London", "Australia/Sydney", "America/Sao_Paulo"):
        assert convert(moment, zone).timestamp() == moment.timestamp()


def test_naive_datetime_requires_source():
    with pytest.raises(ValueError):
        convert(datetime(2024, 1, 1, 0, 0), "Asia/Tokyo")


def test_naive_datetime_uses_source_zone():
    naive = datetime(2024, 1, 15, 12, 0)
    result = convert(naive, "UTC", source="America/New_York")
    assert result == datetime(2024, 1, 15, 17, 0, tzinfo=timezone.utc)


def test_parse_iso_accepts_zulu():
    parsed = parse_iso("2024-01-15T12:00:00Z")
    assert parsed == datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)


def test_parse_iso_naive_uses_assumed_zone():
    parsed = parse_iso("2024-01-15T12:00:00", assume="Europe/Paris")
    assert parsed.utcoffset().total_seconds() == 3600


def test_localize_selects_dst_fold():
    ambiguous = datetime(2024, 11, 3, 1, 30)
    first = localize(ambiguous, "America/New_York", fold=0).astimezone(timezone.utc)
    second = localize(ambiguous, "America/New_York", fold=1).astimezone(timezone.utc)
    assert first == datetime(2024, 11, 3, 5, 30, tzinfo=timezone.utc)
    assert second == datetime(2024, 11, 3, 6, 30, tzinfo=timezone.utc)


def test_dst_overlap_is_ambiguous():
    assert is_ambiguous(datetime(2024, 11, 3, 1, 30), "America/New_York")
    assert not is_ambiguous(datetime(2024, 11, 3, 3, 30), "America/New_York")


def test_spring_forward_gap_is_nonexistent():
    assert is_nonexistent(datetime(2024, 3, 10, 2, 30), "America/New_York")
    assert not is_nonexistent(datetime(2024, 3, 10, 3, 30), "America/New_York")


def test_now_in_is_aware():
    for zone in ("UTC", "Asia/Kathmandu", "Pacific/Chatham"):
        current = now_in(zone)
        assert current.tzinfo is not None
        assert current.utcoffset() is not None


def test_to_utc_normalizes_offsets():
    moment = datetime(2024, 1, 1, 9, 0, tzinfo=timezone.utc)
    assert to_utc(convert(moment, "Asia/Kolkata")) == moment


def test_local_times_maps_zone_names():
    moment = datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc)
    table = local_times(moment, ["UTC", "America/New_York", "Asia/Tokyo"])
    assert table["America/New_York"].hour == 7
    assert table["Asia/Tokyo"].hour == 21


def test_unknown_zone_raises():
    with pytest.raises(UnknownTimeZoneError):
        convert(datetime(2024, 1, 1, tzinfo=timezone.utc), "Mars/Olympus_Mons")


def test_cli_convert(capsys):
    code = main(["convert", "2024-01-15T12:00:00Z", "--to", "Asia/Tokyo"])
    assert code == 0
    out = capsys.readouterr().out
    assert "21:00:00" in out


def test_cli_zones_filters(capsys):
    code = main(["zones", "Kathmandu"])
    assert code == 0
    assert capsys.readouterr().out.strip() == "Asia/Kathmandu"


def test_cli_unknown_zone_exit_code(capsys):
    code = main(["now", "Not/AZone"])
    assert code == 2
    assert "unknown timezone" in capsys.readouterr().err
