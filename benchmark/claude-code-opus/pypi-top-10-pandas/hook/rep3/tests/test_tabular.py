import io
import math
import os
import tempfile
import unittest

import tabular as tb

SAMPLE = """\
Order ID,Customer Name,Region,Amount,Paid
1, Alice ,North,100.5,yes
2,Bob,South,NA,no
3,Carol,North,200,yes
3,Carol,North,200,yes
4,,South,50,
5,Eve,East,,yes
"""


def load(text=SAMPLE, **kw):
    return tb.read_csv(io.StringIO(text), **kw)


class TestTable(unittest.TestCase):
    def setUp(self):
        self.t = tb.Table(["a", "b"], [[1, "x"], [None, "y"], [3, "z"]])

    def test_basics(self):
        self.assertEqual(self.t.shape, (3, 2))
        self.assertEqual(self.t["a"], [1, None, 3])
        self.assertEqual(self.t.to_dicts()[0], {"a": 1, "b": "x"})
        self.assertEqual(tb.Table.from_dicts(self.t.to_dicts()), self.t)

    def test_validation(self):
        with self.assertRaises(ValueError):
            tb.Table(["a", "a"])
        with self.assertRaises(ValueError):
            tb.Table(["a"], [[1, 2]])
        with self.assertRaises(KeyError):
            self.t.column("nope")

    def test_transforms_return_new_tables(self):
        self.assertEqual(self.t.select("b").columns, ["b"])
        self.assertEqual(self.t.drop("b").columns, ["a"])
        self.assertEqual(self.t.rename({"a": "A"}).columns, ["A", "b"])
        self.assertEqual(len(self.t.filter(lambda r: r["b"] != "y")), 2)
        self.assertEqual(self.t.with_column("c", lambda r: r["b"] * 2)["c"], ["xx", "yy", "zz"])
        self.assertEqual(self.t.with_column("a", [0, 0, 0])["a"], [0, 0, 0])
        self.assertEqual(self.t["a"], [1, None, 3])

    def test_sort_puts_missing_last(self):
        self.assertEqual(self.t.sort_by("a", reverse=True)["a"], [3, 1, None])


class TestLoader(unittest.TestCase):
    def test_type_inference_and_missing(self):
        t = load()
        self.assertEqual(t.columns, ["Order ID", "Customer Name", "Region", "Amount", "Paid"])
        self.assertEqual(t["Order ID"], [1, 2, 3, 3, 4, 5])
        self.assertEqual(t["Amount"], [100.5, None, 200.0, 200.0, 50.0, None])
        self.assertEqual(t["Paid"], [True, False, True, True, None, True])
        self.assertEqual(t["Customer Name"][0], " Alice ")
        self.assertIsNone(t["Customer Name"][4])

    def test_sniffs_delimiter_and_strips_bom(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "x.csv")
            with open(path, "w", encoding="utf-8-sig") as f:
                f.write("a;b\n1;2,5\n3;4\n")
            t = tb.read_csv(path)
        self.assertEqual(t.columns, ["a", "b"])
        self.assertEqual(t["a"], [1, 3])
        self.assertEqual(t["b"], ["2,5", "4"])  # no silent decimal-comma guessing

    def test_options(self):
        t = load("1,2\n3,4\n", header=False)
        self.assertEqual(t.columns, ["column_1", "column_2"])
        self.assertEqual(load("a\n1\n", infer_types=False)["a"], ["1"])
        self.assertEqual(load("a\n1\n", dtypes={"a": "float"})["a"], [1.0])
        self.assertEqual(load("a\nmissing\n1\n", na_values=["missing"])["a"], [None, 1])
        self.assertEqual(load("a\n1_000\n")["a"], ["1_000"])

    def test_ragged_rows_and_names(self):
        t = load("a,a,\n1\n\n2,3,4\n")
        self.assertEqual(t.columns, ["a", "a_2", "unnamed_3"])
        self.assertEqual(t.rows, [[1, None, None], [2, 3, 4]])
        with self.assertRaises(ValueError):
            load("a,b\n1,2,3\n")

    def test_bad_dtype(self):
        with self.assertRaises(ValueError):
            load("a\nx\n", dtypes={"a": "int"})
        with self.assertRaises(KeyError):
            load("a\n1\n", dtypes={"b": "int"})

    def test_empty(self):
        self.assertEqual(load("").shape, (0, 0))
        self.assertEqual(load("a,b\n").shape, (0, 2))

    def test_round_trip(self):
        t = load()
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "out.csv")
            tb.write_csv(t, path)
            self.assertEqual(tb.read_csv(path), t)


class TestCleaning(unittest.TestCase):
    def test_snake_case(self):
        self.assertEqual(tb.snake_case("Order ID"), "order_id")
        self.assertEqual(tb.snake_case("totalAmount ($)"), "total_amount")
        self.assertEqual(tb.snake_case("!!!"), "column")
        t = tb.normalize_column_names(tb.Table(["A b", "a-b"]))
        self.assertEqual(t.columns, ["a_b", "a_b_2"])

    def test_strip_and_reinfer(self):
        t = tb.Table(["n", "s"], [[" 1 ", " x "], ["  ", "y"]])
        t = tb.infer_types(tb.strip_whitespace(t))
        self.assertEqual(t["n"], [1, None])
        self.assertEqual(t["s"], ["x", "y"])

    def test_drop_missing(self):
        t = load()
        self.assertEqual(len(tb.drop_missing(t)), 3)
        self.assertEqual(len(tb.drop_missing(t, ["Amount"])), 4)
        self.assertEqual(len(tb.drop_missing(t, ["Amount", "Paid"], how="all")), 6)

    def test_fill_missing(self):
        t = load()
        self.assertEqual(tb.fill_missing(t, 0, columns=["Amount"])["Amount"][1], 0)
        self.assertEqual(tb.fill_missing(t, {"Paid": False})["Paid"][4], False)
        self.assertAlmostEqual(tb.fill_missing(t, strategy="mean", columns=["Amount"])["Amount"][1], 137.625)
        self.assertEqual(tb.fill_missing(t, strategy="median", columns=["Amount"])["Amount"][5], 150.25)
        self.assertEqual(tb.fill_missing(t, strategy="ffill")["Amount"], [100.5, 100.5, 200, 200, 50, 50])
        self.assertEqual(tb.fill_missing(t, strategy="bfill")["Amount"][1], 200)
        self.assertEqual(tb.fill_missing(t, strategy="mode")["Region"], t["Region"])
        # Non-numeric columns are skipped unless named explicitly.
        self.assertEqual(tb.fill_missing(t, strategy="mean")["Customer Name"][4], None)
        with self.assertRaises(TypeError):
            tb.fill_missing(t, strategy="mean", columns=["Region"])
        with self.assertRaises(ValueError):
            tb.fill_missing(t)

    def test_drop_duplicates(self):
        t = load()
        self.assertEqual(len(tb.drop_duplicates(t)), 5)
        t2 = tb.drop_duplicates(t, ["Region"], keep="last")
        self.assertEqual(t2["Order ID"], [3, 4, 5])  # last occurrence kept, original order

    def test_convert_types(self):
        t = tb.Table(["x"], [["1"], ["a"], [2.0]])
        self.assertEqual(tb.convert_types(t, {"x": "int"}, errors="coerce")["x"], [1, None, 2])
        with self.assertRaises(ValueError):
            tb.convert_types(t, {"x": "int"})

    def test_remove_outliers(self):
        t = tb.Table(["v"], [[v] for v in [10, 11, 12, 11, 10, 500, None]])
        self.assertEqual(tb.remove_outliers(t, "v")["v"], [10, 11, 12, 11, 10, None])
        self.assertEqual(len(tb.remove_outliers(t, "v", method="zscore", threshold=1)), 6)
        with self.assertRaises(TypeError):
            tb.remove_outliers(tb.Table(["s"], [["a"], ["b"]]), "s")

    def test_clean_pipeline(self):
        t = tb.clean(load("Name, Score ,Empty\n Ann ,1,\n Ann ,1,\n,,\nBob, 2 ,\n"))
        self.assertEqual(t.columns, ["name", "score"])
        self.assertEqual(t.rows, [["Ann", 1], ["Bob", 2]])


class TestAnalysis(unittest.TestCase):
    def setUp(self):
        self.t = tb.drop_duplicates(load())

    def test_describe(self):
        d = tb.describe(self.t)
        amt = d["Amount"]
        self.assertEqual((amt["count"], amt["missing"], amt["min"], amt["max"]), (3, 2, 50.0, 200.0))
        self.assertAlmostEqual(amt["mean"], 116.8333, places=3)
        self.assertEqual(amt["50%"], 100.5)
        self.assertEqual(d["Region"]["top"], "North")
        self.assertEqual(d["Region"]["freq"], 2)
        self.assertIn("Amount", tb.format_describe(d))
        self.assertIsNone(tb.summarize_column([5])["std"])

    def test_missing_report(self):
        r = tb.missing_report(self.t)
        self.assertEqual(r["Amount"], {"missing": 2, "fraction": 0.4})

    def test_value_counts(self):
        self.assertEqual(tb.value_counts(self.t, "Region"), [("North", 2), ("South", 2), ("East", 1)])
        self.assertEqual(tb.value_counts(self.t, "Paid", normalize=True)[0], (True, 0.75))
        self.assertIn((None, 1), tb.value_counts(self.t, "Paid", dropna=False))

    def test_group_by(self):
        g = tb.group_by(self.t, "Region", {"Amount": ["sum", "mean", "count"], "Order ID": "nunique"})
        self.assertEqual(g.columns, ["Region", "Amount_sum", "Amount_mean", "Amount_count", "Order ID_nunique"])
        self.assertEqual(g.rows[0], ["North", 300.5, 150.25, 2, 2])
        self.assertEqual(g.rows[2], ["East", 0, None, 0, 1])
        g2 = tb.group_by(self.t, ["Region", "Paid"], {"Amount": len})
        self.assertIn("Amount_len", g2.columns)
        with self.assertRaises(ValueError):
            tb.group_by(self.t, "Region", {"Amount": "bogus"})
        with self.assertRaises(KeyError):
            tb.group_by(self.t, "nope", {"Amount": "sum"})

    def test_correlation(self):
        t = tb.Table(["x", "y", "z", "c"], [[1, 2, 3, 7], [2, 4, 2, 7], [3, 6, 1, 7], [None, 1, 0, 7]])
        self.assertAlmostEqual(tb.correlation(t, "x", "y"), 1.0)
        self.assertAlmostEqual(tb.correlation(t, "x", "z"), -1.0)
        self.assertIsNone(tb.correlation(t, "x", "c"))
        m = tb.correlation_matrix(t)
        self.assertEqual(set(m), {"x", "y", "z", "c"})
        self.assertEqual(m["x"]["x"], 1.0)
        self.assertEqual(tb.numeric_columns(self.t), ["Order ID", "Amount"])

    def test_nan_counts_as_missing(self):
        s = tb.summarize_column([1.0, math.nan, 3.0])
        self.assertEqual((s["count"], s["missing"], s["mean"]), (2, 1, 2.0))


if __name__ == "__main__":
    unittest.main()
