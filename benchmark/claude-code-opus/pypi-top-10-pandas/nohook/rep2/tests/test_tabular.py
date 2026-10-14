import io
import os
import tempfile
import unittest
from datetime import date

from tabular import Table, analyze, clean, load_csv, loads_csv, save_csv

SAMPLE = """\
Order ID,Customer Name,Region,Amount,Shipped,Order Date
1,  Alice ,North,120.5,yes,2024-01-03
2,Bob,South,80,no,2024-01-04
3,Carol,North,,yes,2024-01-05
3,Carol,North,,yes,2024-01-05
4,Dan,N/A,300,no,2024-01-06

5,Eve,South,95.25,yes,
"""


class LoadTests(unittest.TestCase):
    def test_types_are_inferred(self):
        t = loads_csv(SAMPLE)
        self.assertEqual(t.shape, (6, 6))
        self.assertEqual(t["Order ID"], [1, 2, 3, 3, 4, 5])
        self.assertEqual(t["Amount"], [120.5, 80.0, None, None, 300.0, 95.25])
        self.assertEqual(t["Shipped"][:2], [True, False])
        self.assertEqual(t["Order Date"][0], date(2024, 1, 3))
        self.assertIsNone(t["Order Date"][-1])
        self.assertIsNone(t["Region"][4])
        self.assertEqual(t["Customer Name"][0], "Alice")

    def test_no_inference_keeps_strings(self):
        t = loads_csv(SAMPLE, infer_types=False)
        self.assertEqual(t["Order ID"][0], "1")
        self.assertEqual(t["Customer Name"][0], "  Alice ")

    def test_delimiter_sniffing(self):
        t = loads_csv("a;b\n1;x\n2;y\n")
        self.assertEqual(t.columns, ["a", "b"])
        self.assertEqual(t["a"], [1, 2])

    def test_short_rows_padded_long_rows_rejected(self):
        self.assertEqual(loads_csv("a,b,c\n1,2\n")["c"], [None])
        with self.assertRaises(ValueError):
            loads_csv("a,b\n1,2,3\n")

    def test_mixed_column_stays_string(self):
        self.assertEqual(loads_csv("a\n1\nx\n")["a"], ["1", "x"])

    def test_underscored_and_special_numbers_stay_strings(self):
        self.assertEqual(loads_csv("a\n1_000\n")["a"], ["1_000"])
        self.assertEqual(loads_csv("a\ninf\n")["a"], ["inf"])

    def test_empty_input(self):
        self.assertEqual(loads_csv("").shape, (0, 0))
        self.assertEqual(loads_csv("a,b\n").shape, (0, 2))

    def test_round_trip_through_file(self):
        t = loads_csv(SAMPLE)
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "out.csv")
            save_csv(t, path)
            self.assertEqual(load_csv(path), t)

    def test_load_from_stream(self):
        self.assertEqual(load_csv(io.StringIO("x\n1\n"))["x"], [1])


class TableTests(unittest.TestCase):
    def setUp(self):
        self.t = Table(["k", "v"], [{"k": "b", "v": 2}, {"k": "a", "v": None}, {"k": "c", "v": 1}])

    def test_sort_puts_missing_last(self):
        self.assertEqual(self.t.sort("v")["k"], ["c", "b", "a"])
        self.assertEqual(self.t.sort("v", descending=True)["k"], ["b", "c", "a"])

    def test_immutability(self):
        rows = self.t.rows
        rows[0]["k"] = "zzz"
        self.t.with_column("w", [1, 2, 3])
        self.assertEqual(self.t["k"][0], "b")
        self.assertEqual(self.t.columns, ["k", "v"])

    def test_unknown_column(self):
        with self.assertRaises(KeyError):
            self.t.select(["nope"])

    def test_with_column_function(self):
        t = self.t.with_column("double", lambda r: r["v"] * 2 if r["v"] is not None else None)
        self.assertEqual(t["double"], [4, None, 2])


class CleanTests(unittest.TestCase):
    def setUp(self):
        self.t = loads_csv(SAMPLE)

    def test_normalize_column_names(self):
        t = clean.normalize_column_names(Table(["Order ID", " customerName", "a-b", "a b"]))
        self.assertEqual(t.columns, ["order_id", "customer_name", "a_b", "a_b_2"])

    def test_strip_whitespace(self):
        t = Table(["s"], [{"s": "  a   b "}, {"s": "   "}, {"s": 3}])
        self.assertEqual(clean.strip_whitespace(t)["s"], ["a   b", None, 3])
        self.assertEqual(clean.strip_whitespace(t, collapse=True)["s"], ["a b", None, 3])

    def test_drop_duplicates(self):
        self.assertEqual(len(clean.drop_duplicates(self.t)), 5)
        self.assertEqual(clean.drop_duplicates(self.t, subset=["Region"])["Region"], ["North", "South", None])

    def test_drop_missing(self):
        self.assertEqual(len(clean.drop_missing(self.t)), 2)
        self.assertEqual(len(clean.drop_missing(self.t, subset=["Amount"])), 4)
        self.assertEqual(len(clean.drop_missing(self.t, subset=["Amount", "Region"], how="all")), 6)

    def test_fill_missing_constant_and_mapping(self):
        self.assertEqual(clean.fill_missing(self.t, 0, columns=["Amount"])["Amount"][2], 0)
        t = clean.fill_missing(self.t, {"Region": "Unknown"})
        self.assertEqual(t["Region"][4], "Unknown")
        self.assertIsNone(t["Amount"][2])

    def test_fill_missing_strategies(self):
        amounts = Table(["x"], [{"x": v} for v in [1, None, 3, None]])
        self.assertEqual(clean.fill_missing(amounts, strategy="mean")["x"], [1, 2.0, 3, 2.0])
        self.assertEqual(clean.fill_missing(amounts, strategy="median")["x"], [1, 2.0, 3, 2.0])
        self.assertEqual(clean.fill_missing(amounts, strategy="ffill")["x"], [1, 1, 3, 3])
        self.assertEqual(clean.fill_missing(amounts, strategy="bfill")["x"], [1, 3, 3, None])
        self.assertEqual(clean.fill_missing(self.t, strategy="mode", columns=["Region"])["Region"][4], "North")
        with self.assertRaises(TypeError):
            clean.fill_missing(self.t, strategy="mean", columns=["Region"])
        with self.assertRaises(ValueError):
            clean.fill_missing(self.t)

    def test_cast_column(self):
        t = Table(["x"], [{"x": "1"}, {"x": "oops"}, {"x": None}])
        self.assertEqual(clean.cast_column(t, "x", int, errors="null")["x"], [1, None, None])
        with self.assertRaises(ValueError):
            clean.cast_column(t, "x", int)

    def test_replace_values(self):
        t = clean.replace_values(self.t, {"North": "N", "South": "S"}, columns=["Region"])
        self.assertEqual(t["Region"], ["N", "S", "N", "N", None, "S"])

    def test_remove_outliers(self):
        t = Table(["x"], [{"x": v} for v in [10, 11, 12, 13, 12, 11, 1000, None]])
        self.assertEqual(clean.remove_outliers(t, "x")["x"], [10, 11, 12, 13, 12, 11, None])

    def test_drop_columns(self):
        self.assertEqual(clean.drop_columns(self.t, ["Amount", "Shipped"]).columns,
                         ["Order ID", "Customer Name", "Region", "Order Date"])


class AnalyzeTests(unittest.TestCase):
    def setUp(self):
        self.t = clean.drop_duplicates(loads_csv(SAMPLE))

    def test_describe(self):
        d = {r["column"]: r for r in analyze.describe(self.t)}
        amount = d["Amount"]
        self.assertEqual((amount["count"], amount["missing"]), (4, 1))
        self.assertAlmostEqual(amount["mean"], (120.5 + 80 + 300 + 95.25) / 4)
        self.assertEqual((amount["min"], amount["max"]), (80.0, 300.0))
        self.assertEqual(d["Region"]["top"], "North")
        self.assertEqual(d["Region"]["freq"], 2)
        self.assertNotIn("mean", analyze.describe(self.t, ["Region"]).columns)

    def test_value_counts(self):
        vc = analyze.value_counts(self.t, "Region")
        self.assertEqual(vc.rows, [{"Region": "North", "count": 2}, {"Region": "South", "count": 2}])
        vc = analyze.value_counts(self.t, "Region", dropna=False, normalize=True)
        self.assertAlmostEqual(sum(vc["proportion"]), 1.0)

    def test_group_by(self):
        g = analyze.group_by(self.t, "Region", {"Amount": ["sum", "count", max], "Order ID": "nunique"})
        self.assertEqual(g.columns, ["Region", "Amount_sum", "Amount_count", "Amount_max", "Order ID_nunique"])
        north = g.rows[0]
        self.assertEqual(north, {"Region": "North", "Amount_sum": 120.5, "Amount_count": 1,
                                 "Amount_max": 120.5, "Order ID_nunique": 2})
        self.assertIsNone(g.rows[2]["Region"])
        with self.assertRaises(ValueError):
            analyze.group_by(self.t, "Region", {"Amount": "bogus"})

    def test_correlation(self):
        t = Table(["x", "y", "z"], [{"x": i, "y": 2 * i + 1, "z": -i} for i in range(5)])
        self.assertAlmostEqual(analyze.correlation(t, "x", "y"), 1.0)
        m = analyze.correlation_matrix(t)
        self.assertAlmostEqual(m.rows[0]["z"], -1.0)
        const = Table(["a", "b"], [{"a": 1, "b": i} for i in range(3)])
        self.assertIsNone(analyze.correlation(const, "a", "b"))
        with self.assertRaises(TypeError):
            analyze.correlation(self.t, "Region", "Amount")

    def test_missing_report(self):
        r = {row["column"]: row for row in analyze.missing_report(self.t)}
        self.assertEqual(r["Amount"]["missing"], 1)
        self.assertAlmostEqual(r["Amount"]["fraction"], 0.2)

    def test_format_table(self):
        text = analyze.format_table(self.t.select(["Region", "Amount"]), max_rows=2)
        lines = text.splitlines()
        self.assertTrue(lines[0].startswith("Region"))
        self.assertIn("120.5", lines[2])
        self.assertEqual(lines[-1], "... (3 more rows)")


if __name__ == "__main__":
    unittest.main()
