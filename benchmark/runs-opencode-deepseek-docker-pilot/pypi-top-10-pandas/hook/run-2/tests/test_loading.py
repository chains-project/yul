import io
import os
import unittest

from csvdata import CsvLoadError, Table, load_csv, load_csvs

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class LoadCsvTests(unittest.TestCase):
    def test_loads_columns_and_rows(self):
        table = load_csv(os.path.join(FIXTURES, "sample.csv"))
        self.assertEqual(table.columns, ["name", "age", "score", "active"])
        self.assertEqual(len(table), 5)
        self.assertEqual(table.shape, (5, 4))

    def test_missing_tokens_become_none(self):
        table = load_csv(os.path.join(FIXTURES, "sample.csv"))
        self.assertIsNone(table["score"][2])
        self.assertTrue(all(value is None for value in table.rows[-1]))

    def test_custom_delimiter(self):
        table = load_csv(os.path.join(FIXTURES, "semicolon.csv"), delimiter=";")
        self.assertEqual(table.columns, ["city", "population"])
        self.assertEqual(table["city"], ["Paris", "Berlin", "Rome"])

    def test_headerless_source(self):
        table = load_csv(os.path.join(FIXTURES, "no_header.csv"), has_header=False)
        self.assertEqual(table.columns, ["column_1", "column_2", "column_3"])
        self.assertEqual(table.rows[0], ["1", "2", "3"])

    def test_loads_from_bytes(self):
        table = load_csv(b"a,b\n1,2\n")
        self.assertEqual(table.columns, ["a", "b"])
        self.assertEqual(table.rows, [["1", "2"]])

    def test_loads_from_file_object(self):
        handle = io.StringIO("a,b\n1,2\n")
        table = load_csv(handle)
        self.assertEqual(table["a"], ["1"])

    def test_duplicate_headers_are_renamed(self):
        table = load_csv(b"a,a,a\n1,2,3\n")
        self.assertEqual(table.columns, ["a", "a_1", "a_2"])

    def test_short_rows_are_padded(self):
        table = load_csv(b"a,b,c\n1,2\n")
        self.assertEqual(table.rows, [["1", "2", None]])

    def test_overlong_row_raises(self):
        with self.assertRaises(CsvLoadError):
            load_csv(b"a,b\n1,2,3\n")

    def test_missing_file_raises(self):
        with self.assertRaises(CsvLoadError):
            load_csv(os.path.join(FIXTURES, "does-not-exist.csv"))

    def test_max_rows(self):
        table = load_csv(os.path.join(FIXTURES, "sample.csv"), max_rows=2)
        self.assertEqual(len(table), 2)

    def test_load_csvs(self):
        paths = [
            os.path.join(FIXTURES, "sample.csv"),
            os.path.join(FIXTURES, "semicolon.csv"),
        ]
        loaded = load_csvs(paths)
        self.assertEqual(len(loaded), 2)
        self.assertTrue(all(isinstance(t, Table) for t in loaded.values()))


if __name__ == "__main__":
    unittest.main()
