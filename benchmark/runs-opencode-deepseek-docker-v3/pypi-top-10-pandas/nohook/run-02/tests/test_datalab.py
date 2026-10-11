import io
import unittest

import datalab as dl
from datalab import Column, Table


CSV_TEXT = """name, region ,amount,notes
 alice , north ,"$1,200.50",
bob,south,800,
carol,north,1200.5, vip 
dave,,,
alice,north,"$1,200.50",
"""


class LoadTests(unittest.TestCase):
    def test_load_csv_from_file_object(self):
        table = dl.load_csv(io.StringIO(CSV_TEXT))
        self.assertEqual(table.headers, ["name", "region", "amount", "notes"])
        self.assertEqual(table.height, 5)

    def test_load_csv_strips_bom_and_unique_headers(self):
        table = dl.load_csv(io.StringIO("\ufeffa,b,a\n1,2,3"))
        self.assertEqual(table.headers, ["a", "b", "a_2"])

    def test_load_csv_without_header(self):
        table = dl.load_csv(io.StringIO("1,2\n3,4"), has_header=False)
        self.assertEqual(table.headers, ["column_1", "column_2"])
        self.assertEqual(table.to_rows(), [["1", "2"], ["3", "4"]])

    def test_blank_lines_skipped(self):
        table = dl.load_csv(io.StringIO("a,b\n\n1,2\n,\n3,4\n"))
        self.assertEqual(table.to_rows(), [["1", "2"], ["3", "4"]])

    def test_load_rows(self):
        table = dl.load_rows([["x", "y"], [1, 2], [3, 4]])
        self.assertEqual(table.headers, ["x", "y"])
        self.assertEqual(len(table), 2)


class TableTests(unittest.TestCase):
    def setUp(self):
        self.table = Table(["a", "b"], [[1, "x"], [2, "y"], [3, "z"]])

    def test_column_and_indexing(self):
        self.assertEqual(list(self.table["a"]), [1, 2, 3])
        self.assertIsInstance(self.table.column("b"), Column)

    def test_missing_column_raises(self):
        with self.assertRaises(dl.ColumnNotFoundError):
            self.table.column("nope")

    def test_select_and_with_column(self):
        selected = self.table.select("b", "a")
        self.assertEqual(selected.headers, ["b", "a"])
        extended = self.table.with_column("c", [7, 8, 9])
        self.assertEqual(extended.headers, ["a", "b", "c"])
        self.assertEqual(list(extended["c"]), [7, 8, 9])

    def test_duplicate_headers_rejected(self):
        with self.assertRaises(ValueError):
            Table(["a", "a"], [[1, 2]])

    def test_row_width_validated(self):
        with self.assertRaises(ValueError):
            Table(["a", "b"], [[1]])

    def test_from_dicts_and_iter(self):
        table = Table.from_dicts([{"a": 1, "b": 2}, {"b": 3, "a": 4}])
        self.assertEqual(table.headers, ["a", "b"])
        self.assertEqual(list(table), [{"a": 1, "b": 2}, {"a": 4, "b": 3}])

    def test_to_number_variants(self):
        self.assertEqual(dl.to_number("1,234.5"), 1234.5)
        self.assertEqual(dl.to_number("$1,200"), 1200)
        self.assertEqual(dl.to_number("(50)"), -50)
        self.assertEqual(dl.to_number("50%"), 0.5)
        self.assertIsNone(dl.to_number(""))
        self.assertIsNone(dl.to_number("abc"))

    def test_is_missing(self):
        for value in (None, "", "  ", "NA", "n/a", "NULL", "-"):
            self.assertTrue(dl.is_missing(value), value)
        self.assertFalse(dl.is_missing("0"))
        self.assertFalse(dl.is_missing("value"))


class CleanTests(unittest.TestCase):
    def setUp(self):
        self.table = dl.load_csv(io.StringIO(CSV_TEXT))

    def test_strip_whitespace(self):
        cleaned = dl.strip_whitespace(self.table)
        self.assertEqual(cleaned.to_rows()[0][0], "alice")
        self.assertEqual(cleaned.to_rows()[0][1], "north")
        self.assertEqual(cleaned.to_rows()[2][3], "vip")

    def test_drop_empty_rows(self):
        table = Table(["a", "b"], [["1", "2"], ["", ""], [None, None]])
        self.assertEqual(dl.drop_empty_rows(table).height, 1)

    def test_drop_duplicates(self):
        table = dl.strip_whitespace(self.table)
        cleaned = dl.drop_duplicates(table)
        self.assertEqual(cleaned.height, 4)
        cleaned_last = dl.drop_duplicates(table, keep="last")
        self.assertEqual(cleaned_last.height, 4)

    def test_drop_missing_any_and_all(self):
        any_dropped = dl.drop_missing(self.table, ["region"], how="any")
        self.assertEqual(any_dropped.height, 4)
        all_dropped = dl.drop_missing(self.table, ["region", "amount"], how="all")
        self.assertEqual(all_dropped.height, 4)

    def test_drop_missing_threshold(self):
        kept = dl.drop_missing(self.table, ["region", "amount"], threshold=1)
        self.assertEqual(kept.height, 4)
        kept_frac = dl.drop_missing(self.table, ["region", "amount"], threshold=0.5)
        self.assertEqual(kept_frac.height, 4)

    def test_fill_missing_constant_and_strategy(self):
        filled = dl.fill_missing(self.table, "unknown", columns=["region"])
        self.assertEqual(filled.to_rows()[3][1], "unknown")

        numeric = dl.load_rows([["v"], ["1"], ["3"], [""]], skip_blank_lines=False)
        mean_filled = dl.fill_missing(numeric, strategy="mean", columns=["v"])
        self.assertAlmostEqual(float(mean_filled.to_rows()[2][0]), 2.0)
        median_filled = dl.fill_missing(numeric, strategy="median")
        self.assertEqual(float(median_filled.to_rows()[2][0]), 2.0)

    def test_fill_missing_mode(self):
        data = Table(["k"], [["a"], ["a"], ["b"], [None]])
        filled = dl.fill_missing(data, strategy="mode")
        self.assertEqual(filled.to_rows()[3][0], "a")

    def test_rename_and_drop_columns(self):
        renamed = dl.rename_columns(self.table, {"name": "person"})
        self.assertIn("person", renamed.headers)
        dropped = dl.drop_columns(self.table, ["notes", "region"])
        self.assertEqual(dropped.headers, ["name", "amount"])
        with self.assertRaises(ValueError):
            dl.drop_columns(Table(["a"], [[1]]), ["a"])

    def test_replace_values(self):
        replaced = dl.replace_values(self.table, {"north": "N"}, columns=["region"])
        self.assertIn("N", list(replaced["region"]))
        upper = dl.replace_values(self.table, lambda v: v.upper(), columns=["name"])
        self.assertEqual(upper.to_rows()[0][0], " ALICE ")

    def test_convert_types(self):
        converted = dl.convert_types(self.table, {"amount": dl.to_number})
        self.assertEqual(converted.to_rows()[0][2], 1200.5)
        failed = dl.convert_types(self.table, {"amount": int}, on_error="none")
        self.assertIsNone(failed.to_rows()[0][2])
        kept = dl.convert_types(self.table, {"amount": int}, on_error="keep")
        self.assertEqual(kept.to_rows()[0][2], "$1,200.50")
        with self.assertRaises(ValueError):
            dl.convert_types(self.table, {"amount": int}, on_error="raise")

    def test_coerce_numeric(self):
        coerced = dl.coerce_numeric(self.table, ["amount"])
        self.assertEqual(coerced.to_rows()[0][2], 1200.5)
        self.assertIsNone(coerced.to_rows()[3][2])


class AnalyzeTests(unittest.TestCase):
    def setUp(self):
        self.table = dl.load_rows(
            [
                ["region", "sales", "units"],
                ["north", "100", "2"],
                ["south", "200", "4"],
                ["north", "300", "6"],
                ["south", "400", "8"],
            ]
        )

    def test_count(self):
        self.assertEqual(dl.count(self.table), 4)
        self.assertEqual(dl.count(self.table, "sales"), 4)

    def test_value_counts(self):
        counts = dl.value_counts(self.table, "region")
        self.assertEqual(counts, {"north": 2, "south": 2})
        normalized = dl.value_counts(self.table, "region", normalize=True)
        self.assertAlmostEqual(normalized["north"], 0.5)

    def test_describe_numeric_and_categorical(self):
        summary = dl.describe(self.table)
        self.assertEqual(summary["sales"]["mean"], 250.0)
        self.assertEqual(summary["sales"]["min"], 100.0)
        self.assertEqual(summary["sales"]["max"], 400.0)
        self.assertEqual(summary["region"]["unique"], 2)
        self.assertEqual(summary["region"]["top"], "north")

    def test_correlation_perfect(self):
        self.assertAlmostEqual(dl.correlation(self.table, "sales", "units"), 1.0)
        self.assertAlmostEqual(dl.covariance(self.table, "sales", "units"), 1000 / 3)

    def test_correlation_none_when_insufficient(self):
        table = dl.load_rows([["x", "y"], ["1", "2"]])
        self.assertIsNone(dl.correlation(table, "x", "y"))

    def test_quantile(self):
        self.assertAlmostEqual(dl.quantile(self.table["sales"], 0.5), 250.0)
        self.assertAlmostEqual(dl.quantile(self.table["sales"], 0.25), 175.0)

    def test_group_by(self):
        grouped = dl.group_by(
            self.table, "region", {"sales": ["sum", "mean"], "*": "count"}
        )
        self.assertEqual(grouped.headers, ["region", "sales_sum", "sales_mean", "count"])
        rows = {row[0]: row for row in grouped.to_rows()}
        self.assertEqual(rows["north"], ["north", 400.0, 200.0, 2])
        self.assertEqual(rows["south"], ["south", 600.0, 300.0, 2])

    def test_group_by_single_aggregation(self):
        grouped = dl.group_by(self.table, "region", {"units": "max"})
        self.assertEqual(grouped.headers, ["region", "units_max"])


if __name__ == "__main__":
    unittest.main()
