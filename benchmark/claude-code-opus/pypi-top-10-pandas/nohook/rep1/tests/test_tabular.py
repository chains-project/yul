import os
import tempfile
import unittest
from datetime import date

from tabular import Table, load_csv, read_csv_text, write_csv

SAMPLE = """\
Order ID, Region ,Unit Price,Qty,Shipped,Order Date
1,North,10.5,2,yes,2024-01-05
2, South ,20,,no,2024-01-06
3,North,N/A,4,yes,2024-01-07
3,North,N/A,4,yes,2024-01-07
4,South,15,1,no,

5,East,30,3,yes,2024-01-09
"""


class LoadTests(unittest.TestCase):
    def setUp(self):
        self.t = read_csv_text(SAMPLE)

    def test_shape_and_blank_lines_skipped(self):
        self.assertEqual(self.t.shape, (6, 6))

    def test_type_inference(self):
        self.assertEqual(self.t["Order ID"], [1, 2, 3, 3, 4, 5])
        self.assertEqual(self.t["Unit Price"], [10.5, 20.0, None, None, 15.0, 30.0])
        self.assertEqual(self.t["Qty"], [2, None, 4, 4, 1, 3])
        self.assertEqual(self.t["Shipped"][:2], [True, False])
        self.assertEqual(self.t["Order Date"][0], date(2024, 1, 5))
        self.assertIsNone(self.t["Order Date"][4])

    def test_thousands_separators(self):
        t = read_csv_text('n;f;eu\n"1,234";"1,234.5";"1,5"\n', delimiter=";")
        self.assertEqual(t.row(0), {"n": 1234, "f": 1234.5, "eu": "1,5"})

    def test_header_whitespace_stripped(self):
        self.assertIn("Region", self.t)

    def test_delimiter_sniffing(self):
        t = read_csv_text("a;b\n1;x\n2;y\n")
        self.assertEqual(t.columns, ["a", "b"])
        self.assertEqual(t["a"], [1, 2])

    def test_no_header_and_ragged_rows(self):
        t = read_csv_text("1,2,3\n4,5\n", header=False)
        self.assertEqual(t.columns, ["column_0", "column_1", "column_2"])
        self.assertEqual(t["column_2"], [3, None])

    def test_too_many_fields_raises(self):
        with self.assertRaises(ValueError):
            read_csv_text("a,b\n1,2,3\n")

    def test_duplicate_headers(self):
        self.assertEqual(read_csv_text("a,a,b\n1,2,3\n").columns, ["a", "a_1", "b"])

    def test_disable_inference(self):
        t = read_csv_text("a\n1\n", infer_types=False)
        self.assertEqual(t["a"], ["1"])

    def test_file_roundtrip_with_bom(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "in.csv")
            with open(path, "w", encoding="utf-8-sig", newline="") as f:
                f.write(SAMPLE)
            t = load_csv(path)
            self.assertEqual(t.columns[0], "Order ID")
            out = os.path.join(d, "out.csv")
            write_csv(t, out)
            self.assertEqual(load_csv(out), t)

    def test_empty(self):
        self.assertEqual(read_csv_text("").shape, (0, 0))


class CleanTests(unittest.TestCase):
    def setUp(self):
        self.t = read_csv_text(SAMPLE).clean_column_names()

    def test_clean_column_names(self):
        self.assertEqual(self.t.columns, ["order_id", "region", "unit_price", "qty", "shipped", "order_date"])
        t = Table({"camelCase": [], "2nd col": [], "a b": [], "a-b": []}).clean_column_names()
        self.assertEqual(t.columns, ["camel_case", "_2nd_col", "a_b", "a_b_1"])

    def test_strip_whitespace(self):
        t = self.t.strip_whitespace()
        self.assertEqual(t["region"][1], "South")
        self.assertIsNone(Table({"x": ["   "]}).strip_whitespace()["x"][0])

    def test_drop_duplicates(self):
        self.assertEqual(len(self.t.drop_duplicates()), 5)
        self.assertEqual(self.t.strip_whitespace().drop_duplicates(["region"])["order_id"], [1, 2, 5])

    def test_drop_missing(self):
        self.assertEqual(self.t.drop_missing()["order_id"], [1, 5])
        self.assertEqual(len(self.t.drop_missing(["unit_price"])), 4)
        t = Table({"a": [None, 1, None], "b": [None, None, 2]})
        self.assertEqual(len(t.drop_missing(how="all")), 2)

    def test_fill_constant_and_dict(self):
        self.assertEqual(self.t.fill_missing(0, columns=["qty"])["qty"][1], 0)
        t = self.t.fill_missing({"qty": -1, "unit_price": 0.0})
        self.assertEqual(t["qty"][1], -1)
        self.assertEqual(t["unit_price"][2], 0.0)
        self.assertIsNone(t["order_date"][4])

    def test_fill_strategies(self):
        t = Table({"x": [1, None, 3, None], "s": ["a", None, "a", "b"]})
        self.assertEqual(t.fill_missing(strategy="mean")["x"], [1, 2.0, 3, 2.0])
        self.assertEqual(t.fill_missing(strategy="mean")["s"], ["a", None, "a", "b"])
        self.assertEqual(t.fill_missing(strategy="mode")["s"], ["a", "a", "a", "b"])
        self.assertEqual(t.fill_missing(strategy="ffill")["x"], [1, 1, 3, 3])
        self.assertEqual(t.fill_missing(strategy="bfill")["x"], [1, 3, 3, None])

    def test_fill_requires_one_argument(self):
        with self.assertRaises(ValueError):
            self.t.fill_missing()
        with self.assertRaises(ValueError):
            self.t.fill_missing(0, strategy="mean")

    def test_cast_column(self):
        t = Table({"x": ["1", "oops", None]})
        self.assertEqual(t.cast_column("x", int, errors="coerce")["x"], [1, None, None])
        with self.assertRaises(ValueError):
            t.cast_column("x", int)

    def test_filter_and_sort(self):
        t = self.t.filter_rows(lambda r: r["qty"] is not None and r["qty"] > 1)
        self.assertEqual(t["order_id"], [1, 3, 3, 5])
        self.assertEqual(self.t.sort_by("unit_price", reverse=True)["unit_price"],
                         [30.0, 20.0, 15.0, 10.5, None, None])


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.t = read_csv_text(SAMPLE).clean_column_names().strip_whitespace().drop_duplicates()

    def test_describe_numeric(self):
        d = self.t.describe()["unit_price"]
        self.assertEqual(d["count"], 4)
        self.assertEqual(d["missing"], 1)
        self.assertAlmostEqual(d["mean"], 18.875)
        self.assertEqual(d["min"], 10.5)
        self.assertEqual(d["max"], 30.0)
        self.assertAlmostEqual(d["50%"], 17.5)
        self.assertAlmostEqual(d["25%"], 13.875)

    def test_describe_categorical(self):
        d = self.t.describe(["region"])["region"]
        self.assertEqual(d, {"count": 5, "missing": 0, "unique": 3, "top": "North", "freq": 2})

    def test_value_counts(self):
        self.assertEqual(self.t.value_counts("region")[0], ("North", 2))
        self.assertIn((None, 1), self.t.value_counts("qty", dropna=False))

    def test_correlation(self):
        t = Table({"a": [1, 2, 3, 4], "b": [2, 4, 6, 8], "c": [4, 3, 2, 1], "k": [5, 5, 5, 5], "s": list("wxyz")})
        corr = t.correlation()
        self.assertEqual(set(corr), {"a", "b", "c", "k"})
        self.assertAlmostEqual(corr["a"]["b"], 1.0)
        self.assertAlmostEqual(corr["a"]["c"], -1.0)
        self.assertIsNone(corr["a"]["k"])

    def test_group_by(self):
        g = self.t.group_by("region", {"qty": ["sum", "count"], "unit_price": "mean", "order_id": len})
        self.assertEqual(g.columns, ["region", "qty_sum", "qty_count", "unit_price_mean", "order_id_len"])
        self.assertEqual(g["region"], ["North", "South", "East"])
        self.assertEqual(g["qty_sum"], [6, 1, 3])
        self.assertEqual(g["qty_count"], [2, 1, 1])
        self.assertEqual(g["unit_price_mean"], [10.5, 17.5, 30.0])
        self.assertEqual(g["order_id_len"], [2, 2, 1])

    def test_group_by_unknown_agg(self):
        with self.assertRaises(ValueError):
            self.t.group_by("region", {"qty": "bogus"})


class TableTests(unittest.TestCase):
    def test_mismatched_lengths(self):
        with self.assertRaises(ValueError):
            Table({"a": [1], "b": [1, 2]})

    def test_from_rows_and_access(self):
        t = Table.from_rows([{"a": 1}, {"a": 2, "b": "x"}])
        self.assertEqual(t.columns, ["a", "b"])
        self.assertEqual(t.row(0), {"a": 1, "b": None})
        self.assertEqual(list(t)[1], {"a": 2, "b": "x"})

    def test_with_column_and_select(self):
        t = Table({"a": [1, 2]}).with_column("b", lambda r: r["a"] * 10)
        self.assertEqual(t.select("b")["b"], [10, 20])
        self.assertEqual(t.drop("b").columns, ["a"])

    def test_to_string(self):
        s = Table({"a": [1, None], "bb": ["x", "y"]}).to_string()
        self.assertEqual(s.splitlines()[0], "a  bb")


if __name__ == "__main__":
    unittest.main()
