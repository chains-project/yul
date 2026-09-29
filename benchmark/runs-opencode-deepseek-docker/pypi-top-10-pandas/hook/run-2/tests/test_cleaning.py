import os
import unittest

from csvdata import (
    ColumnNotFoundError,
    Table,
    clean,
    coerce_types,
    drop_duplicates,
    drop_empty_rows,
    drop_missing,
    fill_missing,
    infer_dtype,
    load_csv,
    strip_whitespace,
)

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def sample_table():
    return load_csv(os.path.join(FIXTURES, "sample.csv"))


class CleanTests(unittest.TestCase):
    def test_strip_whitespace(self):
        table = strip_whitespace(sample_table())
        self.assertEqual(table["name"][0], "Alice")

    def test_infer_dtype(self):
        self.assertEqual(infer_dtype(["1", "2", "3"]), "int")
        self.assertEqual(infer_dtype(["1", "2.5"]), "float")
        self.assertEqual(infer_dtype(["true", "yes"]), "bool")
        self.assertEqual(infer_dtype(["a", "b"]), "str")
        self.assertEqual(infer_dtype([None, ""]), "str")

    def test_coerce_types(self):
        table = coerce_types(strip_whitespace(sample_table()))
        self.assertEqual(table.dtypes["age"], "int")
        self.assertEqual(table.dtypes["score"], "float")
        self.assertEqual(table.dtypes["active"], "bool")
        self.assertEqual(table["age"][0], 30)
        self.assertIs(table["active"][0], True)

    def test_drop_empty_rows(self):
        table = drop_empty_rows(sample_table())
        self.assertEqual(len(table), 4)

    def test_drop_duplicates(self):
        table = Table(["a", "b"], [["x", 1], ["x", 2], ["y", 3]])
        self.assertEqual(len(drop_duplicates(table)), 3)
        self.assertEqual(len(drop_duplicates(table, subset="a")), 2)
        self.assertEqual(len(drop_duplicates(table, subset=["a", "b"])), 3)

    def test_drop_missing(self):
        table = drop_missing(sample_table(), subset="score", how="any")
        self.assertEqual(len(table), 3)
        table_all = drop_missing(sample_table(), how="all")
        self.assertEqual(len(table_all), 4)

    def test_fill_missing_constant(self):
        table = fill_missing(sample_table(), strategy="constant", value=0, columns="score")
        self.assertEqual(table["score"][2], 0)

    def test_fill_missing_mean(self):
        table = coerce_types(strip_whitespace(sample_table()))
        table = fill_missing(table, strategy="mean", columns="score")
        self.assertAlmostEqual(table["score"][2], (91.5 + 88.0 + 88.0) / 3)

    def test_fill_missing_drop(self):
        table = fill_missing(sample_table(), strategy="drop", columns="score")
        self.assertEqual(len(table), 3)

    def test_fill_missing_ffill(self):
        table = Table(["a"], [["1"], [None], ["3"]], {"a": "str"})
        filled = fill_missing(table, strategy="ffill")
        self.assertEqual(filled["a"], ["1", "1", "3"])

    def test_clean_pipeline(self):
        table = clean(sample_table(), dedupe=True, missing="mean")
        self.assertEqual(len(table), 3)
        self.assertEqual(table.dtypes["age"], "int")
        self.assertEqual(table["name"][0], "Alice")
        self.assertAlmostEqual(table["score"][2], (91.5 + 88.0) / 2)

    def test_unknown_column_raises(self):
        with self.assertRaises(ColumnNotFoundError):
            coerce_types(sample_table(), columns=["nope"])

    def test_bad_strategy_raises(self):
        with self.assertRaises(ValueError):
            fill_missing(sample_table(), strategy="bogus")


if __name__ == "__main__":
    unittest.main()
