import os
import tempfile
import unittest

from tabular import (
    Table,
    clean,
    correlation,
    describe,
    drop_duplicates,
    drop_missing,
    fill_missing,
    group_by,
    load_csv,
    normalize_column_names,
    save_csv,
    strip_whitespace,
    value_counts,
)


class CsvTestCase(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)

    def write(self, text, name="data.csv"):
        path = os.path.join(self._dir.name, name)
        with open(path, "w", newline="", encoding="utf-8") as f:
            f.write(text)
        return path


class LoadCsvTest(CsvTestCase):
    def test_infers_column_types(self):
        path = self.write("id,price,active,name,zip\n1,2.5,yes,Ann,02134\n2,3,no,Bob,10001\n")
        table = load_csv(path)
        self.assertEqual(table["id"], [1, 2])
        self.assertEqual(table["price"], [2.5, 3.0])
        self.assertEqual(load_csv(self.write("f\n0.5\n-0.25\n"))["f"], [0.5, -0.25])
        self.assertEqual(table["active"], [True, False])
        self.assertEqual(table["name"], ["Ann", "Bob"])
        self.assertEqual(table["zip"], ["02134", "10001"])  # leading zero keeps it text

    def test_missing_tokens_become_none(self):
        table = load_csv(self.write("a,b\n1,NA\n,x\nnull,y\n"))
        self.assertEqual(table["a"], [1, None, None])
        self.assertEqual(table["b"], [None, "x", "y"])

    def test_mixed_column_stays_text(self):
        table = load_csv(self.write("a\n1\ntwo\n"))
        self.assertEqual(table["a"], ["1", "two"])

    def test_thousands_separators(self):
        table = load_csv(self.write('amount\n"1,234"\n"12,345.5"\n'))
        self.assertEqual(table["amount"], [1234.0, 12345.5])

    def test_sniffs_delimiter_and_strips_bom(self):
        path = os.path.join(self._dir.name, "semi.csv")
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            f.write("a;b\n1;2\n3;4\n")
        table = load_csv(path)
        self.assertEqual(table.columns, ["a", "b"])
        self.assertEqual(table["b"], [2, 4])

    def test_short_rows_padded_and_long_rows_rejected(self):
        self.assertEqual(load_csv(self.write("a,b\n1\n"))["b"], [None])
        with self.assertRaises(ValueError):
            load_csv(self.write("a,b\n1,2,3\n"))

    def test_duplicate_and_blank_headers(self):
        table = load_csv(self.write("a,a,\n1,2,3\n"))
        self.assertEqual(table.columns, ["a", "a_2", "column_3"])

    def test_empty_file(self):
        self.assertEqual(load_csv(self.write("")).shape, (0, 0))

    def test_no_type_inference(self):
        self.assertEqual(load_csv(self.write("a\n1\n"), infer_types=False)["a"], ["1"])

    def test_round_trip(self):
        table = Table({"a": [1, None], "b": ["x", "y"]})
        path = os.path.join(self._dir.name, "out.csv")
        save_csv(table, path)
        self.assertEqual(load_csv(path), table)


class TableTest(unittest.TestCase):
    def setUp(self):
        self.table = Table({"name": ["b", "a", "c"], "n": [2, None, 1]})

    def test_unequal_columns_rejected(self):
        with self.assertRaises(ValueError):
            Table({"a": [1], "b": [1, 2]})

    def test_basic_operations(self):
        self.assertEqual(self.table.shape, (3, 2))
        self.assertEqual(self.table.select("n").columns, ["n"])
        self.assertEqual(len(self.table.filter(lambda r: r["n"] is not None)), 2)
        self.assertEqual(self.table.sort_by("n")["name"], ["c", "b", "a"])
        self.assertEqual(self.table.sort_by("n", descending=True)["name"], ["b", "c", "a"])
        doubled = self.table.with_column("n2", lambda r: r["n"] and r["n"] * 2)
        self.assertEqual(doubled["n2"], [4, None, 2])

    def test_from_rows_fills_missing_keys(self):
        table = Table.from_rows([{"a": 1}, {"b": 2}])
        self.assertEqual(table.to_rows(), [{"a": 1, "b": None}, {"a": None, "b": 2}])

    def test_to_string(self):
        text = self.table.to_string(max_rows=2)
        self.assertIn("name  n", text)
        self.assertIn("1 more rows", text)


class CleaningTest(unittest.TestCase):
    def test_strip_whitespace(self):
        table = strip_whitespace(Table({"a": ["  x ", "   ", 3]}))
        self.assertEqual(table["a"], ["x", None, 3])

    def test_normalize_column_names(self):
        table = normalize_column_names(Table({"Unit Price ($)": [], "firstName": [], "unit price": [], "2nd": []}))
        self.assertEqual(table.columns, ["unit_price", "first_name", "unit_price_2", "_2nd"])

    def test_drop_duplicates(self):
        table = Table({"a": [1, 1, 2], "b": ["x", "x", "x"]})
        self.assertEqual(len(drop_duplicates(table)), 2)
        self.assertEqual(len(drop_duplicates(table, subset=["b"])), 1)

    def test_drop_missing(self):
        table = Table({"a": [1, None, None], "b": [1, 2, None]})
        self.assertEqual(len(drop_missing(table)), 1)
        self.assertEqual(len(drop_missing(table, how="all")), 2)
        self.assertEqual(len(drop_missing(table, subset=["b"])), 2)

    def test_fill_missing(self):
        table = Table({"n": [1, None, 3], "s": ["x", None, "x"]})
        self.assertEqual(fill_missing(table, 0)["s"], ["x", 0, "x"])
        self.assertEqual(fill_missing(table, {"s": "?"})["n"], [1, None, 3])
        by_mean = fill_missing(table, strategy="mean")
        self.assertEqual(by_mean["n"], [1, 2, 3])
        self.assertEqual(by_mean["s"], ["x", None, "x"])  # non-numeric untouched
        self.assertEqual(fill_missing(table, strategy="mode")["s"], ["x", "x", "x"])
        with self.assertRaises(ValueError):
            fill_missing(table)

    def test_clean_pipeline(self):
        table = Table({
            " Full Name ": [" Ann ", " Ann ", None, "Bob"],
            "Empty": [None, None, None, None],
        })
        cleaned = clean(table)
        self.assertEqual(cleaned.columns, ["full_name"])
        self.assertEqual(cleaned["full_name"], ["Ann", "Bob"])


class AnalysisTest(unittest.TestCase):
    def setUp(self):
        self.sales = Table({
            "region": ["east", "west", "east", "west", "east"],
            "amount": [10, 20, 30, None, 50],
            "units": [1, 2, 3, 4, 5],
        })

    def test_describe(self):
        summary = {row["column"]: row for row in describe(self.sales).rows()}
        amount = summary["amount"]
        self.assertEqual((amount["count"], amount["missing"]), (4, 1))
        self.assertEqual(amount["mean"], 27.5)
        self.assertEqual((amount["min"], amount["50%"], amount["max"]), (10, 25.0, 50))
        self.assertEqual((summary["region"]["top"], summary["region"]["freq"]), ("east", 3))
        self.assertIsNone(summary["region"]["mean"])

    def test_value_counts(self):
        counts = value_counts(self.sales, "region")
        self.assertEqual(counts.to_rows(), [{"region": "east", "count": 3}, {"region": "west", "count": 2}])
        props = value_counts(self.sales, "region", normalize=True)
        self.assertAlmostEqual(props["proportion"][0], 0.6)

    def test_group_by(self):
        result = group_by(self.sales, "region", {"amount": ["sum", "mean", "count"], "units": max})
        self.assertEqual(result.columns, ["region", "amount_sum", "amount_mean", "amount_count", "units_max"])
        self.assertEqual(result.to_rows(), [
            {"region": "east", "amount_sum": 90, "amount_mean": 30, "amount_count": 3, "units_max": 5},
            {"region": "west", "amount_sum": 20, "amount_mean": 20, "amount_count": 1, "units_max": 4},
        ])
        with self.assertRaises(ValueError):
            group_by(self.sales, "region", {"amount": "bogus"})

    def test_correlation(self):
        matrix = correlation(self.sales)
        self.assertEqual(matrix["column"], ["amount", "units"])
        # The row with a missing amount is skipped; the rest are exactly linear.
        self.assertAlmostEqual(matrix["units"][0], 1.0)
        self.assertAlmostEqual(matrix["units"][1], 1.0)

    def test_correlation_partial_and_constant(self):
        matrix = correlation(Table({"x": [1, 2, 3], "y": [1, 3, 2], "c": [5, 5, 5]}))
        self.assertAlmostEqual(matrix["y"][0], 0.5)
        self.assertIsNone(matrix["c"][0])


if __name__ == "__main__":
    unittest.main()
