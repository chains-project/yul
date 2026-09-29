import unittest

from tabular import (
    Table,
    coerce_numeric,
    drop_duplicates,
    drop_empty_columns,
    drop_empty_rows,
    drop_missing,
    fill_missing,
    is_missing,
    replace_missing,
    standardize_headers,
    strip_whitespace,
)


class CleaningTest(unittest.TestCase):
    def test_strip_whitespace(self):
        table = Table(["a", "b"], [["  x ", " y"]])
        result = strip_whitespace(table)
        self.assertEqual(result.rows, [["x", "y"]])

    def test_standardize_headers(self):
        table = Table(["First Name", "Total-Amount"], [["a", "1"]])
        result = standardize_headers(table)
        self.assertEqual(result.headers, ["first_name", "total_amount"])

    def test_is_missing(self):
        self.assertTrue(is_missing(""))
        self.assertTrue(is_missing("N/A"))
        self.assertTrue(is_missing(None))
        self.assertFalse(is_missing("0"))
        self.assertFalse(is_missing(0))

    def test_replace_missing(self):
        table = Table(["a", "b"], [["1", ""], ["NA", "x"]])
        result = replace_missing(table)
        self.assertEqual(result.rows, [["1", None], [None, "x"]])

    def test_drop_empty_rows(self):
        table = Table(["a", "b"], [["1", "x"], ["", "  "], [None, None]])
        result = drop_empty_rows(table)
        self.assertEqual(result.rows, [["1", "x"]])

    def test_drop_empty_columns(self):
        table = Table(["a", "b", "c"], [["1", "", "x"], ["2", "  ", "y"]])
        result = drop_empty_columns(table)
        self.assertEqual(result.headers, ["a", "c"])

    def test_drop_missing_any(self):
        table = Table(["a", "b"], [["1", "x"], ["2", ""], ["", "y"]])
        result = drop_missing(table)
        self.assertEqual(result.rows, [["1", "x"]])

    def test_drop_missing_all(self):
        table = Table(["a", "b"], [["1", ""], ["", ""]])
        result = drop_missing(table, how="all")
        self.assertEqual(result.rows, [["1", ""]])

    def test_drop_missing_selected_columns(self):
        table = Table(["a", "b"], [["1", ""], ["", "y"]])
        result = drop_missing(table, columns=["a"])
        self.assertEqual(result.rows, [["1", ""]])

    def test_drop_missing_invalid_how(self):
        with self.assertRaises(ValueError):
            drop_missing(Table(["a"], [["1"]]), how="some")

    def test_fill_missing(self):
        table = Table(["a", "b"], [[None, "x"], ["", "y"]])
        result = fill_missing(table, 0)
        self.assertEqual(result.rows, [[0, "x"], [0, "y"]])

    def test_fill_missing_selected_columns(self):
        table = Table(["a", "b"], [[None, None]])
        result = fill_missing(table, 0, columns=["a"])
        self.assertEqual(result.rows, [[0, None]])

    def test_drop_duplicates(self):
        table = Table(["a", "b"], [["1", "x"], ["1", "x"], ["2", "y"]])
        result = drop_duplicates(table)
        self.assertEqual(result.rows, [["1", "x"], ["2", "y"]])

    def test_drop_duplicates_subset(self):
        table = Table(["a", "b"], [["1", "x"], ["1", "y"]])
        result = drop_duplicates(table, columns=["a"])
        self.assertEqual(result.rows, [["1", "x"]])

    def test_coerce_numeric(self):
        table = Table(["n", "f", "s"], [["10", "1.5", "x"], ["2", "-3", "y"]])
        result = coerce_numeric(table)
        self.assertEqual(result.rows, [[10, 1.5, "x"], [2, -3, "y"]])

    def test_coerce_numeric_selected_columns(self):
        table = Table(["a", "b"], [["1", "2"]])
        result = coerce_numeric(table, columns=["b"])
        self.assertEqual(result.rows, [["1", 2]])

    def test_functions_do_not_mutate_input(self):
        table = Table(["a"], [[" 1 "]])
        strip_whitespace(table)
        self.assertEqual(table.rows, [[" 1 "]])


if __name__ == "__main__":
    unittest.main()
