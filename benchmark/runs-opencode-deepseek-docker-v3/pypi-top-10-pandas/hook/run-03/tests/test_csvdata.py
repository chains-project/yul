import io
import os
import tempfile
import unittest

from csvdata import (
    Table,
    coerce_types,
    correlation,
    describe,
    drop_duplicates,
    drop_missing,
    fill_missing,
    load_csv,
    normalize_headers,
    read_csv,
    strip_whitespace,
    value_counts,
)

CSV = """name,age,score,City
 Alice ,30,88.5,NYC
Bob,25,92,LA
Carol,25,,LA
dave,40,75,NYC
dave,40,75,NYC
"""


class LoaderTests(unittest.TestCase):
    def test_read_csv_from_stream(self):
        table = read_csv(io.StringIO(CSV))
        self.assertEqual(table.shape, (5, 4))
        self.assertEqual(table.columns, ["name", "age", "score", "City"])
        self.assertEqual(table.head(1)[0]["name"], " Alice ")

    def test_load_csv_from_path(self):
        handle, path = tempfile.mkstemp(suffix=".csv")
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as fh:
                fh.write(CSV)
            table = load_csv(path)
            self.assertEqual(len(table), 5)
        finally:
            os.unlink(path)

    def test_headerless_and_dedupe(self):
        table = read_csv(io.StringIO("a,b,a\n1,2,3\n"), has_header=True)
        self.assertEqual(table.columns, ["a", "b", "a_1"])

    def test_empty_input(self):
        self.assertEqual(read_csv(io.StringIO("")).shape, (0, 0))


class CleanTests(unittest.TestCase):
    def setUp(self):
        self.table = read_csv(io.StringIO(CSV))

    def test_strip_whitespace(self):
        cleaned = strip_whitespace(self.table)
        self.assertEqual(cleaned.head(1)[0]["name"], "Alice")
        self.assertEqual(self.table.head(1)[0]["name"], " Alice ")

    def test_normalize_headers(self):
        table = Table(["First Name", "Age (yrs)"], [{"First Name": "A", "Age (yrs)": 1}])
        self.assertEqual(normalize_headers(table).columns, ["first_name", "age_yrs"])

    def test_coerce_types(self):
        coerced = coerce_types(self.table)
        self.assertEqual(coerced.head(1)[0]["age"], 30)
        self.assertEqual(coerced.head(1)[0]["score"], 88.5)
        self.assertEqual(coerced.head(1)[0]["name"], " Alice ")

    def test_coerce_leaves_mixed_columns(self):
        table = Table(["v"], [{"v": "1"}, {"v": "x"}])
        self.assertEqual(coerce_types(table).head(1)[0]["v"], "1")

    def test_drop_missing_any(self):
        self.assertEqual(len(drop_missing(self.table)), 4)

    def test_drop_missing_all(self):
        self.assertEqual(len(drop_missing(self.table, how="all")), 5)

    def test_fill_missing_mean(self):
        filled = fill_missing(coerce_types(self.table), strategy="mean", columns=["score"])
        self.assertAlmostEqual(filled.column("score")[2], (88.5 + 92 + 75 + 75) / 4)

    def test_fill_missing_constant(self):
        filled = fill_missing(self.table, value="n/a")
        self.assertEqual(filled.column("score")[2], "n/a")

    def test_drop_duplicates(self):
        self.assertEqual(len(drop_duplicates(self.table)), 4)


class AnalyzeTests(unittest.TestCase):
    def setUp(self):
        self.table = coerce_types(read_csv(io.StringIO(CSV)))

    def test_describe_numeric(self):
        stats = describe(self.table)
        self.assertEqual(stats["age"]["type"], "numeric")
        self.assertEqual(stats["age"]["mean"], 32.0)
        self.assertEqual(stats["score"]["missing"], 1)

    def test_describe_categorical(self):
        stats = describe(self.table)
        self.assertEqual(stats["City"]["type"], "categorical")
        self.assertEqual(stats["City"]["top"], "NYC")
        self.assertEqual(stats["City"]["freq"], 3)

    def test_value_counts(self):
        self.assertEqual(value_counts(self.table, "City"), [("NYC", 3), ("LA", 2)])

    def test_correlation(self):
        self.assertAlmostEqual(correlation(self.table, "age", "score"), -0.9934, places=3)

    def test_correlation_insufficient(self):
        self.assertIsNone(correlation(self.table, "name", "age"))


if __name__ == "__main__":
    unittest.main()
