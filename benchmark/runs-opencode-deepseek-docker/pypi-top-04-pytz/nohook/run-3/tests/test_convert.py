import unittest
from datetime import datetime, timedelta, timezone

from worldtime import UTC, convert_all, convert_iso, parse_iso, resolve_zone, to_zone


class ParseIsoTests(unittest.TestCase):
    def test_offset_is_preserved(self):
        moment = parse_iso("2026-09-29T14:00:00+02:00")
        self.assertEqual(moment.utcoffset(), timedelta(hours=2))

    def test_naive_is_treated_as_utc(self):
        moment = parse_iso("2026-09-29T14:00:00")
        self.assertEqual(moment.tzinfo, UTC)


class ToZoneTests(unittest.TestCase):
    def test_rejects_naive_datetime(self):
        with self.assertRaises(ValueError):
            to_zone(datetime(2026, 9, 29, 14, 0), "Asia/Tokyo")

    def test_same_instant_across_regions(self):
        moment = parse_iso("2026-09-29T12:00:00Z")
        self.assertEqual(to_zone(moment, "UTC").hour, 12)
        self.assertEqual(to_zone(moment, "Asia/Tokyo").hour, 21)
        self.assertEqual(to_zone(moment, "America/New_York").hour, 8)

    def test_result_is_aware_and_preserves_instant(self):
        moment = parse_iso("2026-01-01T00:00:00Z")
        local = to_zone(moment, "Europe/London")
        self.assertIsNotNone(local.tzinfo)
        self.assertEqual(local, moment)

    def test_half_hour_offset(self):
        moment = parse_iso("2026-09-29T00:00:00Z")
        self.assertEqual(to_zone(moment, "Asia/Kolkata").strftime("%H:%M"), "05:30")


class DstTests(unittest.TestCase):
    def test_spring_forward_boundary_new_york(self):
        before = parse_iso("2024-03-10T06:59:00Z")
        after = parse_iso("2024-03-10T07:00:00Z")
        self.assertEqual(to_zone(before, "America/New_York").strftime("%H:%M %Z"), "01:59 EST")
        self.assertEqual(to_zone(after, "America/New_York").strftime("%H:%M %Z"), "03:00 EDT")

    def test_southern_hemisphere_dst_is_inverted(self):
        january = parse_iso("2026-01-15T00:00:00Z")
        july = parse_iso("2026-07-15T00:00:00Z")
        self.assertEqual(to_zone(january, "Australia/Sydney").tzname(), "AEDT")
        self.assertEqual(to_zone(july, "Australia/Sydney").tzname(), "AEST")


class ResolveZoneTests(unittest.TestCase):
    def test_unknown_zone_raises_value_error(self):
        with self.assertRaises(ValueError):
            resolve_zone("Mars/Olympus_Mons")


class HelperTests(unittest.TestCase):
    def test_convert_iso(self):
        result = convert_iso("2026-09-29T12:00:00Z", "Asia/Tokyo")
        self.assertEqual(result.hour, 21)

    def test_convert_all(self):
        moment = parse_iso("2026-09-29T12:00:00Z")
        result = convert_all(moment, ["UTC", "Asia/Tokyo"])
        self.assertEqual(set(result), {"UTC", "Asia/Tokyo"})
        self.assertEqual(result["Asia/Tokyo"].hour, 21)

    def test_datetimes_compare_across_zones(self):
        a = parse_iso("2026-09-29T12:00:00Z")
        b = to_zone(a, "America/New_York")
        self.assertEqual(a, b)
        self.assertEqual(b.tzinfo.utcoffset(b), timezone(timedelta(hours=-4)).utcoffset(None))


if __name__ == "__main__":
    unittest.main()
