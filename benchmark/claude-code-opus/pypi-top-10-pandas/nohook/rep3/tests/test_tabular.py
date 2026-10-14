import os
import tempfile
import unittest
from datetime import date

from tabular import Table, infer_type, load_csv, normalize_name, parse_value, read_csv_text

MESSY = """\
 Order ID ,Region,  Unit Price ,Qty,Shipped,Order Date,Zip
1, North ,10.50,3,yes,2024-01-05,02134
2,South,N/A,5,no,2024-01-06,10001
2,South,N/A,5,no,2024-01-06,10001
3,  north,7.25,,yes,2024-02-10,
4,East,1000,1,NO,2024-02-11,60601
,,,,,,
5,East,12,2,yes,,60601
"""


class ParsingTests(unittest.TestCase):
    def test_parse_value(self):
        self.assertEqual(parse_value("42"), 42)
        self.assertEqual(parse_value("1,234.5"), 1234.5)
        self.assertEqual(parse_value("25%"), 0.25)
        self.assertIs(parse_value("Yes"), True)
        self.assertEqual(parse_value("2024-03-01"), date(2024, 3, 1))
        self.assertIsNone(parse_value(" NA "))
        self.assertEqual(parse_value("00501"), "00501")
        self.assertEqual(parse_value(" hi "), "hi")

    def test_infer_type(self):
        self.assertEqual(infer_type(["1", "2", ""]), "int")
        self.assertEqual(infer_type(["1", "2.5"]), "float")
        self.assertEqual(infer_type(["true", "F"]), "bool")
        self.assertEqual(infer_type(["2024-01-01", "null"]), "date")
        self.assertEqual(infer_type(["1", "x"]), "str")
        self.assertEqual(infer_type(["", "NA"]), "str")

    def test_normalize_name(self):
        self.assertEqual(normalize_name(" Total Sales ($) "), "total_sales")
        self.assertEqual(normalize_name("orderID"), "order_id")
        self.assertEqual(normalize_name("!!!"), "column")


class LoadingTests(unittest.TestCase):
    def test_load_file_with_types(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "data.csv")
            with open(path, "w", encoding="utf-8-sig") as f:  # BOM is stripped
                f.write("name,age,score\nAda,36,9.5\nBob,,7\n")
            t = load_csv(path)
        self.assertEqual(t.columns, ["name", "age", "score"])
        self.assertEqual(t["age"], [36, None])
        self.assertEqual(t["score"], [9.5, 7.0])
        self.assertEqual(t.dtypes(), {"name": "str", "age": "int", "score": "float"})

    def test_sniffs_delimiter(self):
        t = read_csv_text("a;b\n1;2\n3;4\n")
        self.assertEqual(t["b"], [2, 4])

    def test_no_type_inference(self):
        t = read_csv_text("a,b\n1,2\n", infer_types=False)
        self.assertEqual(t["a"], ["1"])

    def test_duplicate_and_blank_headers(self):
        t = read_csv_text("a,a,\n1,2,3\n")
        self.assertEqual(t.columns, ["a", "a_1", "column_3"])

    def test_short_rows_are_padded_long_rows_rejected(self):
        self.assertEqual(read_csv_text("a,b\n1\n")["b"], [None])
        with self.assertRaises(ValueError):
            read_csv_text("a,b\n1,2,3\n", delimiter=",")

    def test_empty_input(self):
        self.assertEqual(read_csv_text("").shape, (0, 0))

    def test_roundtrip(self):
        t = Table({"a": [1, None], "b": ["x", "y"]})
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "out.csv")
            t.to_csv(path)
            self.assertEqual(load_csv(path), t)


class CleaningTests(unittest.TestCase):
    def setUp(self):
        self.raw = read_csv_text(MESSY, infer_types=False)

    def test_clean_pipeline(self):
        t = self.raw.clean()
        self.assertEqual(
            t.columns,
            ["order_id", "region", "unit_price", "qty", "shipped", "order_date", "zip"],
        )
        self.assertEqual(len(t), 5)  # blank row and duplicate row removed
        self.assertEqual(t["order_id"], [1, 2, 3, 4, 5])
        self.assertEqual(t["region"], ["North", "South", "north", "East", "East"])
        self.assertEqual(t["unit_price"], [10.5, None, 7.25, 1000.0, 12.0])
        self.assertEqual(t["shipped"], [True, False, True, False, True])
        self.assertEqual(t["zip"], ["02134", "10001", None, "60601", "60601"])
        self.assertEqual(t["order_date"][-1], None)

    def test_fillna(self):
        t = Table({"x": [1, None, 3, None], "s": ["a", None, "a", "b"]})
        self.assertEqual(t.fillna(0)["x"], [1, 0, 3, 0])
        self.assertEqual(t.fillna({"s": "?"})["x"], [1, None, 3, None])
        self.assertEqual(t.fillna(strategy="mean")["x"], [1, 2.0, 3, 2.0])
        self.assertEqual(t.fillna(strategy="mean")["s"], ["a", None, "a", "b"])
        self.assertEqual(t.fillna(strategy="mode")["s"], ["a", "a", "a", "b"])
        self.assertEqual(t.fillna(strategy="ffill")["x"], [1, 1, 3, 3])
        self.assertEqual(t.fillna(strategy="bfill")["x"], [1, 3, 3, None])
        with self.assertRaises(ValueError):
            t.fillna(strategy="bogus")

    def test_dropna(self):
        t = Table({"a": [1, None, None], "b": [1, 2, None]})
        self.assertEqual(len(t.dropna()), 1)
        self.assertEqual(len(t.dropna(how="all")), 2)
        self.assertEqual(len(t.dropna(subset=["b"])), 2)

    def test_drop_duplicates_subset(self):
        t = Table({"k": [1, 1, 2], "v": ["a", "b", "c"]})
        self.assertEqual(t.drop_duplicates(["k"])["v"], ["a", "c"])

    def test_astype_and_outliers(self):
        t = Table({"v": ["1", "2", "3", "2", "x", "100"]}).astype({"v": "int"})
        self.assertEqual(t["v"], [1, 2, 3, 2, None, 100])
        self.assertEqual(t.remove_outliers("v")["v"], [1, 2, 3, 2, None])
        self.assertEqual(len(t.remove_outliers("v", method="zscore", threshold=1.5)), 5)

    def test_sort_and_filter(self):
        t = Table({"a": [3, None, 1, 2], "b": ["x", "y", "x", "y"]})
        self.assertEqual(t.sort("a")["a"], [1, 2, 3, None])
        self.assertEqual(t.sort("a", descending=True)["a"], [3, 2, 1, None])
        self.assertEqual(t.sort(["b", "a"])["a"], [1, 3, 2, None])
        self.assertEqual(t.filter(lambda r: r["b"] == "y")["a"], [None, 2])

    def test_mismatched_lengths_rejected(self):
        with self.assertRaises(ValueError):
            Table({"a": [1], "b": [1, 2]})


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.t = Table({
            "region": ["N", "S", "N", "S", "E"],
            "sales": [10, 20, 30, None, 50],
            "units": [1, 2, 3, 4, 5],
        })

    def test_describe(self):
        d = {r["column"]: r for r in self.t.describe().rows()}
        s = d["sales"]
        self.assertEqual((s["count"], s["missing"], s["min"], s["max"]), (4, 1, 10, 50))
        self.assertAlmostEqual(s["mean"], 27.5)
        self.assertAlmostEqual(s["50%"], 25.0)
        self.assertEqual(d["region"]["unique"], 3)
        self.assertIsNone(d["region"]["mean"])

    def test_missing_report(self):
        r = {row["column"]: row for row in self.t.missing_report().rows()}
        self.assertEqual(r["sales"]["missing"], 1)
        self.assertEqual(r["sales"]["percent"], 20.0)

    def test_value_counts(self):
        vc = self.t.value_counts("region")
        self.assertEqual(vc.to_dicts()[0], {"region": "N", "count": 2})
        shares = self.t.value_counts("region", normalize=True)["share"]
        self.assertAlmostEqual(sum(shares), 1.0)

    def test_group_by(self):
        g = self.t.group_by("region", {"sales": ["sum", "mean", "count"], "units": "max"})
        self.assertEqual(g["region"], ["N", "S", "E"])
        self.assertEqual(g["sales_sum"], [40, 20, 50])
        self.assertEqual(g["sales_count"], [2, 1, 1])
        self.assertEqual(g["units_max"], [3, 4, 5])
        with self.assertRaises(TypeError):
            self.t.group_by("units", {"region": "sum"})

    def test_corr(self):
        c = {r["column"]: r for r in self.t.corr().rows()}
        self.assertEqual(c.keys(), {"sales", "units"})
        self.assertAlmostEqual(c["sales"]["units"], 1.0)
        sp = Table({"x": [1, 2, 3, 4], "y": [1, 4, 9, 100]}).corr("spearman")
        self.assertAlmostEqual(sp["y"][0], 1.0)

    def test_str_output(self):
        out = str(self.t.head(2))
        self.assertIn("region", out.splitlines()[0])
        self.assertEqual(len(out.splitlines()), 4)


if __name__ == "__main__":
    unittest.main()
