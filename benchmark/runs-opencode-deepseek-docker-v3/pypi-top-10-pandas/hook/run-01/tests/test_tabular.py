import io
import math
import os
import tempfile
import unittest

import tabular as tb
from tabular import Table


CSV = """\
Name, Age ,City,Score,Code,Active
 Alice ,30,NYC,1.5,01234,true
Bob,25,LA,2.0,00042,false
Carol,,NYC,3.5,12345,true
Bob,25,LA,2.0,00042,false
,,,,
"""


class LoaderTests(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".csv")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(CSV)

    def tearDown(self):
        os.unlink(self.path)

    def test_load_path_infers_types(self):
        table = tb.load_csv(self.path)
        self.assertEqual(
            table.columns, ["Name", "Age", "City", "Score", "Code", "Active"]
        )
        self.assertEqual(table.shape, (5, 6))
        self.assertEqual(table.column("Age")[:3], [30, 25, None])
        self.assertEqual(table.column("Score")[:2], [1.5, 2.0])
        # leading zeros preserved as strings
        self.assertEqual(table.column("Code")[0], "01234")

    def test_load_string_stream(self):
        table = tb.load_csv(io.StringIO(CSV), skip_blank_lines=True)
        self.assertEqual(len(table), 5)

    def test_no_header(self):
        table = tb.load_csv(
            io.StringIO("1,2\n3,4\n"), has_header=False, infer_types=True
        )
        self.assertEqual(table.columns, ["column_1", "column_2"])
        self.assertEqual(table[0], {"column_1": 1, "column_2": 2})

    def test_disable_inference(self):
        table = tb.load_csv(io.StringIO(CSV), infer_types=False)
        self.assertEqual(table.column("Age")[0], "30")

    def test_tsv(self):
        table = tb.load_csv(io.StringIO("a\tb\n1\t2\n"), delimiter="\t")
        self.assertEqual(table[0], {"a": 1, "b": 2})

    def test_infer_type_helper(self):
        self.assertIsNone(tb.infer_type(""))
        self.assertIsNone(tb.infer_type("N/A"))
        self.assertEqual(tb.infer_type("42"), 42)
        self.assertEqual(tb.infer_type("-3.5"), -3.5)
        self.assertEqual(tb.infer_type("007"), "007")
        self.assertEqual(tb.infer_type("hello"), "hello")


class CleanerTests(unittest.TestCase):
    def _table(self):
        return Table(
            ["Name", "Age", "City"],
            [[" Alice ", 30, "NYC"], ["Bob", None, "LA"], ["Bob", None, "LA"]],
        )

    def test_strip_whitespace(self):
        table = tb.strip_whitespace(self._table())
        self.assertEqual(table.column("Name")[0], "Alice")

    def test_drop_duplicates(self):
        table = tb.drop_duplicates(self._table())
        self.assertEqual(len(table), 2)

    def test_drop_missing_any(self):
        table = tb.drop_missing(self._table())
        self.assertEqual(len(table), 1)

    def test_drop_missing_all(self):
        table = Table(["a", "b"], [[None, None], [1, None], [None, 2]])
        self.assertEqual(len(tb.drop_missing(table, how="all")), 2)
        self.assertEqual(len(tb.drop_missing(table, how="any")), 0)

    def test_fill_missing_value(self):
        table = tb.fill_missing(self._table(), 0, column="Age")
        self.assertEqual(table.column("Age"), [30, 0, 0])

    def test_fill_missing_mean(self):
        table = Table(["x"], [[1.0], [None], [3.0]])
        filled = tb.fill_missing(table, method="mean")
        self.assertEqual(filled.column("x"), [1.0, 2.0, 3.0])

    def test_replace_values(self):
        table = tb.replace_values(self._table(), "City", {"NYC": "New York"})
        self.assertEqual(table.column("City")[0], "New York")

    def test_replace_values_regex(self):
        table = Table(["x"], [["a1"], ["b2"]])
        out = tb.replace_values(table, "x", {r"\d": ""}, regex=True)
        self.assertEqual(out.column("x"), ["a", "b"])

    def test_cast_and_coerce(self):
        table = Table(["x"], [["1"], ["2"], ["3"]])
        self.assertEqual(tb.cast_column(table, "x", int).column("x"), [1, 2, 3])
        dirty = Table(["x"], [["1"], ["oops"], ["3"]])
        with self.assertRaises(ValueError):
            tb.cast_column(dirty, "x", int)
        coerced = tb.coerce_column(dirty, "x", int, on_error=0)
        self.assertEqual(coerced.column("x"), [1, 0, 3])

    def test_drop_empty_columns(self):
        table = Table(["a", "b"], [[1, None], [2, ""]])
        self.assertEqual(tb.drop_empty_columns(table).columns, ["a"])

    def test_normalize_headers(self):
        table = Table([" First Name ", "A-B"], [[1, 2]])
        out = tb.normalize_headers(table, lower=True)
        self.assertEqual(out.columns, ["first_name", "a-b"])

    def test_rename_columns(self):
        out = tb.rename_columns(self._table(), {"Name": "full_name"})
        self.assertIn("full_name", out.columns)


class AnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.table = Table(
            ["region", "sales", "units"],
            [
                ["east", 10.0, 1],
                ["east", 20.0, 2],
                ["west", 30.0, 3],
                ["west", None, 4],
            ],
        )

    def test_column_types(self):
        types = tb.column_types(self.table)
        self.assertEqual(types["region"], "str")
        self.assertEqual(types["sales"], "float")
        self.assertEqual(types["units"], "int")

    def test_describe(self):
        stats = tb.describe(self.table)
        sales = stats["sales"]
        self.assertEqual(sales.count, 3)
        self.assertEqual(sales.missing, 1)
        self.assertEqual(sales.mean, 20.0)
        self.assertEqual(sales.median, 20.0)
        self.assertAlmostEqual(sales.stdev, 10.0, places=6)

    def test_value_counts(self):
        counts = tb.value_counts(self.table, "region")
        self.assertEqual(counts, {"east": 2, "west": 2})
        self.assertEqual(tb.value_counts(self.table, "region", top=1), {"east": 2})

    def test_correlation_perfect(self):
        table = Table(["x", "y"], [[1, 2], [2, 4], [3, 6]])
        self.assertAlmostEqual(tb.correlation(table, "x", "y"), 1.0, places=9)

    def test_correlation_undefined(self):
        table = Table(["x", "y"], [[1, 5], [1, 6]])
        self.assertIsNone(tb.correlation(table, "x", "y"))

    def test_group_by_and_aggregate(self):
        groups = tb.group_by(self.table, "region")
        self.assertEqual(set(groups), {"east", "west"})
        summed = tb.aggregate(
            self.table,
            "region",
            {"total": ("sales", lambda vs: sum(v for v in vs if v is not None))},
        )
        result = {row["region"]: row["total"] for row in summed}
        self.assertEqual(result, {"east": 30.0, "west": 30.0})


class TableTests(unittest.TestCase):
    def test_select_filter_sort(self):
        table = Table(
            ["a", "b"], [[3, "x"], [1, "y"], [2, "z"]]
        )
        self.assertEqual(table.select(["b"]).columns, ["b"])
        self.assertEqual(len(table.filter(lambda r: r["a"] > 1)), 2)
        self.assertEqual(table.sort_by("a").column("a"), [1, 2, 3])
        self.assertEqual(table.head(1).column("a"), [3])

    def test_add_remove_rename(self):
        table = Table(["a"], [[1], [2]])
        table.add_column("b", [10, 20])
        self.assertEqual(table.columns, ["a", "b"])
        table.rename_column("b", "c")
        self.assertEqual(table.columns, ["a", "c"])
        table.remove_column("c")
        self.assertEqual(table.columns, ["a"])

    def test_rejects_mismatched_rows(self):
        with self.assertRaises(ValueError):
            Table(["a", "b"], [[1]])

    def test_eq_and_repr(self):
        a = Table(["a"], [[1]])
        b = Table(["a"], [[1]])
        self.assertEqual(a, b)
        self.assertIn("Table(", repr(a))


if __name__ == "__main__":
    unittest.main()
