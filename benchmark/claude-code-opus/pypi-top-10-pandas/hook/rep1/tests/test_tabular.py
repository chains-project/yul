import datetime as dt
import os
import tempfile
import unittest

import tabular as tb


def write(content: str, suffix: str = ".csv", encoding: str = "utf-8") -> str:
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w", encoding=encoding, newline="") as f:
        f.write(content)
    return path


class CsvFileTestCase(unittest.TestCase):
    def csv(self, content: str, **kwargs) -> str:
        path = write(content, **kwargs)
        self.addCleanup(os.remove, path)
        return path


class TestTable(unittest.TestCase):
    def test_rejects_mismatched_lengths(self):
        with self.assertRaises(ValueError):
            tb.Table({"a": [1, 2], "b": [1]})

    def test_from_rows_and_accessors(self):
        t = tb.Table.from_rows([{"a": 1, "b": 2}, {"a": 3, "c": 4}])
        self.assertEqual(t.columns, ["a", "b", "c"])
        self.assertEqual(t.shape, (2, 3))
        self.assertEqual(t["b"], [2, None])
        self.assertEqual(t.row(1), {"a": 3, "b": None, "c": 4})

    def test_sort_puts_missing_last(self):
        t = tb.Table({"x": [3, None, 1, 2]})
        self.assertEqual(t.sort("x")["x"], [1, 2, 3, None])
        self.assertEqual(t.sort("x", descending=True)["x"], [3, 2, 1, None])

    def test_filter_select_drop(self):
        t = tb.Table({"a": [1, 2, 3], "b": ["x", "y", "z"]})
        self.assertEqual(t.filter(lambda r: r["a"] > 1)["b"], ["y", "z"])
        self.assertEqual(t.select(["b"]).columns, ["b"])
        self.assertEqual(t.drop(["b"]).columns, ["a"])
        with self.assertRaises(KeyError):
            t.select(["nope"])


class TestLoadCsv(CsvFileTestCase):
    def test_type_inference(self):
        path = self.csv(
            "id,price,active,joined,name,zip\n"
            "1,9.5,yes,2024-01-02,Ann,02134\n"
            "2,,no,2024-02-03,Bob,10001\n"
            "3,\"1,200.25\",true,NA,Cy,94110\n")
        t = tb.load_csv(path)
        self.assertEqual(t["id"], [1, 2, 3])
        self.assertEqual(t["price"], [9.5, None, 1200.25])
        self.assertEqual(t["active"], [True, False, True])
        self.assertEqual(t["joined"], [dt.date(2024, 1, 2), dt.date(2024, 2, 3), None])
        self.assertEqual(t["name"], ["Ann", "Bob", "Cy"])
        # Leading zeros mean an identifier, not a number.
        self.assertEqual(t["zip"], ["02134", "10001", "94110"])

    def test_sniffs_delimiter_and_strips_bom(self):
        path = self.csv("﻿a;b\n1;2\n3;4\n")
        t = tb.load_csv(path)
        self.assertEqual(t.columns, ["a", "b"])
        self.assertEqual(t["b"], [2, 4])

    def test_short_rows_padded_long_rows_rejected(self):
        t = tb.load_csv(self.csv("a,b,c\n1,2\n\n4,5,6\n"))
        self.assertEqual(t["c"], [None, 6])
        with self.assertRaisesRegex(ValueError, "row 2"):
            tb.load_csv(self.csv("a,b\n1,2,3\n"))

    def test_no_header_duplicate_names_and_usecols(self):
        t = tb.load_csv(self.csv("1,2\n3,4\n"), header=False)
        self.assertEqual(t.columns, ["column_1", "column_2"])
        t = tb.load_csv(self.csv("a,a,\n1,2,3\n"))
        self.assertEqual(t.columns, ["a", "a_1", "unnamed_3"])
        t = tb.load_csv(self.csv("a,b,c\n1,2,3\n"), usecols=["c", "a"])
        self.assertEqual(t.columns, ["c", "a"])

    def test_infer_types_off(self):
        t = tb.load_csv(self.csv("a\n1\n"), infer_types=False)
        self.assertEqual(t["a"], ["1"])

    def test_empty_file(self):
        self.assertEqual(tb.load_csv(self.csv("")).shape, (0, 0))

    def test_round_trip(self):
        original = tb.Table({"a": [1, None], "d": [dt.date(2024, 1, 1), None], "s": ["x,y", "z"]})
        path = self.csv("")
        tb.save_csv(original, path)
        self.assertEqual(tb.load_csv(path), original)


class TestCleaning(unittest.TestCase):
    def test_normalize_column_names(self):
        t = tb.Table({" Unit Price ($)": [1], "customerID": [2], "Order-Date": [3]})
        self.assertEqual(tb.normalize_column_names(t).columns,
                         ["unit_price", "customer_id", "order_date"])
        with self.assertRaises(ValueError):
            tb.normalize_column_names(tb.Table({"A B": [1], "a_b": [2]}))

    def test_strip_whitespace(self):
        t = tb.strip_whitespace(tb.Table({"s": ["  a   b ", None, 3]}))
        self.assertEqual(t["s"], ["a b", None, 3])

    def test_drop_duplicates(self):
        t = tb.Table({"k": [1, 1, 2, 1], "v": ["a", "a", "b", "c"]})
        self.assertEqual(tb.drop_duplicates(t)["v"], ["a", "b", "c"])
        self.assertEqual(tb.drop_duplicates(t, subset=["k"])["v"], ["a", "b"])
        self.assertEqual(tb.drop_duplicates(t, subset=["k"], keep="last")["v"], ["b", "c"])

    def test_drop_missing_and_empty_columns(self):
        t = tb.Table({"a": [1, None, None], "b": [1, 2, None], "c": [None] * 3})
        self.assertEqual(len(tb.drop_missing(t, subset=["a", "b"])), 1)
        self.assertEqual(len(tb.drop_missing(t, subset=["a", "b"], how="all")), 2)
        self.assertEqual(tb.drop_empty_columns(t).columns, ["a", "b"])
        self.assertEqual(tb.drop_empty_columns(t, threshold=0.5).columns, ["b"])

    def test_fill_missing(self):
        t = tb.Table({"n": [1, None, 5], "s": ["x", None, "x"]})
        self.assertEqual(tb.fill_missing(t, value=0)["n"], [1, 0, 5])
        self.assertEqual(tb.fill_missing(t, value={"s": "?"})["s"], ["x", "?", "x"])
        filled = tb.fill_missing(t, strategy="mean")
        self.assertEqual(filled["n"], [1, 3.0, 5])
        self.assertEqual(filled["s"], ["x", None, "x"])  # non-numeric skipped
        self.assertEqual(tb.fill_missing(t, strategy="mode")["s"], ["x", "x", "x"])
        self.assertEqual(tb.fill_missing(t, strategy="ffill")["n"], [1, 1, 5])
        self.assertEqual(tb.fill_missing(t, strategy="bfill")["n"], [1, 5, 5])
        with self.assertRaises(TypeError):
            tb.fill_missing(t, strategy="median", columns=["s"])
        with self.assertRaises(ValueError):
            tb.fill_missing(t)

    def test_convert_types(self):
        t = tb.Table({"a": ["1", "x", None]})
        self.assertEqual(tb.convert_types(t, {"a": int}, errors="coerce")["a"], [1, None, None])
        with self.assertRaises(ValueError):
            tb.convert_types(t, {"a": int})

    def test_remove_outliers(self):
        t = tb.Table({"v": [10, 11, 12, 11, 10, 500, None]})
        self.assertEqual(tb.remove_outliers(t, "v")["v"], [10, 11, 12, 11, 10, None])
        t = tb.Table({"v": [10] * 20 + [500]})
        self.assertNotIn(500, tb.remove_outliers(t, "v", method="zscore")["v"])

    def test_clean_pipeline(self):
        t = tb.Table({
            "Full Name": [" Ann ", "Bob", "Bob", None],
            "Age": ["30", " 41", " 41", None],
            "Empty": [None, None, None, None],
        })
        cleaned = tb.clean(t)
        self.assertEqual(cleaned.columns, ["full_name", "age"])
        self.assertEqual(cleaned["full_name"], ["Ann", "Bob"])
        self.assertEqual(cleaned["age"], [30, 41])


class TestAnalysis(unittest.TestCase):
    def setUp(self):
        self.t = tb.Table({
            "region": ["N", "S", "N", "S", None],
            "sales": [10, 20, 30, None, 50],
            "units": [1, 2, 3, 4, 5],
        })

    def test_describe(self):
        d = tb.describe(self.t)
        self.assertEqual(d["sales"]["count"], 4)
        self.assertEqual(d["sales"]["missing"], 1)
        self.assertEqual(d["sales"]["mean"], 27.5)
        self.assertEqual(d["sales"]["min"], 10)
        self.assertEqual(d["sales"]["50%"], 25.0)
        self.assertEqual(d["region"]["unique"], 2)
        self.assertEqual(d["region"]["freq"], 2)
        self.assertIn("sales", tb.format_describe(d))

    def test_missing_report_and_types(self):
        report = tb.missing_report(self.t)
        self.assertEqual(report["missing"], [1, 1, 0])
        self.assertEqual(report["percent"], [20.0, 20.0, 0.0])
        self.assertEqual(tb.column_types(self.t), {"region": "str", "sales": "int", "units": "int"})
        self.assertEqual(tb.numeric_columns(self.t), ["sales", "units"])

    def test_value_counts(self):
        self.assertEqual(tb.value_counts(self.t, "region"), [("N", 2), ("S", 2)])
        self.assertEqual(tb.value_counts(self.t, "region", normalize=True)[0], ("N", 0.5))
        self.assertIn((None, 1), tb.value_counts(self.t, "region", dropna=False))

    def test_group_by(self):
        g = tb.group_by(self.t, "region", {"sales": ["sum", "mean", "count"], "units": max})
        self.assertEqual(g["region"], ["N", "S", None])
        self.assertEqual(g["sales_sum"], [40, 20, 50])
        self.assertEqual(g["sales_mean"], [20.0, 20.0, 50.0])
        self.assertEqual(g["sales_count"], [2, 1, 1])
        self.assertEqual(g["units_max"], [3, 4, 5])

    def test_correlation(self):
        self.assertAlmostEqual(tb.correlation(self.t, "sales", "units"), 1.0)
        self.assertIsNone(tb.correlation(tb.Table({"a": [1, 1], "b": [1, 2]}), "a", "b"))
        m = tb.correlation_matrix(self.t)
        self.assertEqual(set(m), {"sales", "units"})
        self.assertEqual(m["units"]["units"], 1.0)

    def test_histogram(self):
        h = tb.histogram(self.t, "units", bins=2)
        self.assertEqual([c for _, _, c in h], [2, 3])
        self.assertEqual(tb.histogram(tb.Table({"x": [7, 7]}), "x"), [(7, 7, 2)])


if __name__ == "__main__":
    unittest.main()
