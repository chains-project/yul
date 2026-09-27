import os
import tempfile
import unittest

from datalib import Table, load_csv, load_csv_string, load_csvs
from datalib.exceptions import CSVParseError


class LoadCSVTests(unittest.TestCase):
    def test_basic_load_and_strip(self):
        table = load_csv_string("a,b\n 1 , hello \n2,world\n")
        self.assertEqual(table.columns, ["a", "b"])
        self.assertEqual(table.column("a"), ["1", "2"])
        self.assertEqual(table.column("b"), ["hello", "world"])

    def test_null_tokens_become_none(self):
        table = load_csv_string("a,b\n1,NA\n2,\n3,n/a\n")
        self.assertEqual(table.column("b"), [None, None, None])

    def test_custom_na_values(self):
        table = load_csv_string("a\nx\n-\n", na_values={"-", "x"})
        self.assertEqual(table.column("a"), [None, None])

    def test_infer_types(self):
        table = load_csv_string("i,f,b,d\n1,1.5,true,2020-01-01\n2,2.5,no,2020-02-01\n", infer_types=True)
        self.assertEqual(table.column("i"), [1, 2])
        self.assertIsInstance(table.column("i")[0], int)
        self.assertEqual(table.column("f"), [1.5, 2.5])
        self.assertEqual(table.column("b"), [True, False])
        self.assertEqual(table.column("d")[0].year, 2020)

    def test_delimiter_and_no_header(self):
        table = load_csv_string("1;2\n3;4\n", delimiter=";", has_header=False)
        self.assertEqual(table.columns, ["col_0", "col_1"])
        self.assertEqual(table.column("col_1"), ["2", "4"])

    def test_duplicate_headers_are_disambiguated(self):
        table = load_csv_string("a,a,a\n1,2,3\n")
        self.assertEqual(table.columns, ["a", "a_2", "a_3"])

    def test_blank_lines_skipped(self):
        table = load_csv_string("a\n1\n\n2\n")
        self.assertEqual(table.column("a"), ["1", "2"])

    def test_ragged_rows_padded_when_not_strict(self):
        table = load_csv_string("a,b,c\n1,2\n")
        self.assertEqual(table.rows[0], {"a": "1", "b": "2", "c": None})

    def test_strict_mode_raises(self):
        with self.assertRaises(CSVParseError):
            load_csv_string("a,b\n1,2,3\n", strict=True)

    def test_load_from_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "d.csv")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("a,b\n1,2\n")
            table = load_csv(path)
            self.assertEqual(table.to_dicts(), [{"a": "1", "b": "2"}])

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            load_csv("/no/such/file.csv")

    def test_bom_is_stripped(self):
        table = load_csv_string("\ufeffa,b\n1,2\n")
        self.assertEqual(table.columns, ["a", "b"])

    def test_load_csvs_unions_columns(self):
        with tempfile.TemporaryDirectory() as tmp:
            p1 = os.path.join(tmp, "1.csv")
            p2 = os.path.join(tmp, "2.csv")
            with open(p1, "w", encoding="utf-8") as handle:
                handle.write("a,b\n1,2\n")
            with open(p2, "w", encoding="utf-8") as handle:
                handle.write("b,c\n3,4\n")
            table = load_csvs([p1, p2])
            self.assertEqual(table.columns, ["a", "b", "c"])
            self.assertEqual(table.column("a"), ["1", None])


if __name__ == "__main__":
    unittest.main()
