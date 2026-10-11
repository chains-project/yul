from datetime import datetime, timedelta

import pytest

from worldtime.timezones import (
    UTC,
    UnknownRegionError,
    at_local_time,
    convert,
    local_time_status,
    now_in,
    parse_iso,
    zone_for,
)


def test_now_in_is_aware():
    moment = now_in("tokyo")
    assert moment.utcoffset() == timedelta(hours=9)
    assert moment.tzname() == "JST"


def test_convert_preserves_the_instant():
    source = datetime(2024, 1, 1, 12, 0, tzinfo=UTC)
    converted = convert(source, "new-york")
    assert converted.astimezone(UTC) == source
    assert converted.hour == 7  # EST is UTC-5 in January


def test_convert_rejects_naive_datetime():
    with pytest.raises(ValueError, match="timezone-aware"):
        convert(datetime(2024, 1, 1, 12, 0), "london")


def test_parse_iso_requires_an_offset():
    assert parse_iso("2024-01-01T12:00:00Z").tzinfo is not None
    with pytest.raises(ValueError, match="timezone-aware"):
        parse_iso("2024-01-01T12:00:00")


def test_nonexistent_local_time_uses_offset_before_gap():
    # America/New_York springs forward on 2024-03-10; 02:30 never happened.
    assert local_time_status("new-york", 2024, 3, 10, 2, 30) == "nonexistent"
    before_gap = at_local_time("new-york", 2024, 3, 10, 2, 30, fold=0)
    after_gap = at_local_time("new-york", 2024, 3, 10, 2, 30, fold=1)
    assert before_gap.utcoffset() == timedelta(hours=-5)
    assert after_gap.utcoffset() == timedelta(hours=-4)


def test_ambiguous_local_time_folds_to_distinct_instants():
    # America/New_York falls back on 2024-11-03; 01:30 happens twice.
    assert local_time_status("new-york", 2024, 11, 3, 1, 30) == "ambiguous"
    earlier = at_local_time("new-york", 2024, 11, 3, 1, 30, fold=0)
    later = at_local_time("new-york", 2024, 11, 3, 1, 30, fold=1)
    assert earlier.utcoffset() == timedelta(hours=-4)
    assert later.utcoffset() == timedelta(hours=-5)
    # Aware subtraction is naive when both share one tzinfo, so compare UTC.
    assert later.astimezone(UTC) - earlier.astimezone(UTC) == timedelta(hours=1)


def test_ordinary_local_time_is_unique():
    assert local_time_status("london", 2024, 6, 1, 12, 0) == "unique"


def test_region_aliases_and_raw_iana_keys_both_resolve():
    assert zone_for("new-york").key == "America/New_York"
    assert zone_for("America/New_York").key == "America/New_York"


def test_unknown_region_raises_with_helpful_message():
    with pytest.raises(UnknownRegionError, match="unknown region"):
        zone_for("atlantis")
