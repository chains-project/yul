import io
import os
import tempfile
import unittest

from csvlab import (
    ColumnNotFoundError,
    Table,
    coerce_types,
    correlation,
    describe,
    drop_duplicates,
    drop_empty_columns,
    drop_empty_rows,
    drop_missing,
    fill_missing,
    group_by,
    load_csv,
    load_csvs,
    missing_counts,
    normalize_column_names,
    replace_values,
    strip_whitespace,
    value_counts,
)
from csvlab.analysis import mean

CSV = """name,age,score,active,note
 alice ,30,9.5,true,hello
bob,25,8.0,yes,world
"carol",,7.25,false,
dave,40,,no,NA
eve,30,9.5,true,hello
"""


class LoaderTests(unittest.TestCase):
    def test_load_infers_types_and_missing(self):
        table = load_csv(io.StringIO(CSV))
        self.assertEqual(table.columns, ["name", "age", "score", "active", "note"])
        self.assertEqual(table.n_rows, 5)
        self.assertEqual(table.shape, (5, 5))
        self.assertEqual(table.column("age"), [30, 25, None, 40, 30])
        self.assertIsInstance(table.column("age")[0], int)
        self.assertEqual(table.column("score")[0], 9.5)
        self.assertEqual(table.column("active"), [True, True, False, False, True])
        self.assertEqual(table.column("note")[2], None)
        self.assertEqual(table.column("note")[3], None)
        self.assertEqual(table.column("name")[0], "alice")

    def test_load_without_header(self):
        table = load_csv(io.StringIO("1,2\n3,4\n"), has_header=False)
        self.assertEqual(table.columns, ["column_1", "column_2"])
        self.assertEqual(table.to_rows(), [[1, 2], [3, 4]])

    def test_load_skips_blank_lines(self):
        table = load_csv(io.StringIO("a,b\n1,2\n\n3,4\n"))
        self.assertEqual(table.n_rows, 2)

    def test_load_from_path(self):
        fd, path = tempfile.mkstemp(suffix=".csv")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write("x,y\n1,2\n3,4\n")
            table = load_csv(path)
            self.assertEqual(table.column("x"), [1, 3])
        finally:
            os.remove(path)

    def test_load_empty(self):
        table = load_csv(io.StringIO(""))
        self.assertEqual(table.columns, [])
        self.assertEqual(table.n_rows, 0)

    def test_load_csvs_concatenates(self):
        combined = load_csvs(
            [io.StringIO("a,b\n1,2\n"), io.StringIO("a,b\n3,4\n")]
        )
        self.assertEqual(combined.to_rows(), [[1, 2], [3, 4]])

    def test_load_csvs_rejects_column_mismatch(self):
        with self.assertRaises(ValueError):
            load_csvs([io.StringIO("a,b\n1,2\n"), io.StringIO("a,c\n3,4\n")])


class TableTests(unittest.TestCase):
    def setUp(self):
        self.table = load_csv(io.StringIO(CSV))

    def test_select_filter_sort(self):
        selected = self.table.select("name", "age")
        self.assertEqual(selected.columns, ["name", "age"])
        adults = self.table.filter(lambda row: (row["age"] or 0) >= 30)
        self.assertEqual([r["name"] for r in adults], ["alice", "dave", "eve"])
        ordered = self.table.sort_by("age")
        self.assertEqual(ordered.column("age"), [25, 30, 30, 40, None])

    def test_rename_add_drop(self):
        renamed = self.table.rename({"age": "years"})
        self.assertIn("years", renamed.columns)
        added = self.table.add_column("double_age", lambda row: (
            None if row["age"] is None else row["age"] * 2
        ))
        self.assertEqual(added.column("double_age")[0], 60)
        dropped = self.table.drop_columns("note")
        self.assertNotIn("note", dropped.columns)

    def test_head_tail(self):
        self.assertEqual(self.table.head(2).n_rows, 2)
        self.assertEqual(self.table.tail(1).column("name"), ["eve"])

    def test_missing_column(self):
        with self.assertRaises(ColumnNotFoundError):
            self.table.column("nope")

    def test_duplicate_columns_rejected(self):
        with self.assertRaises(ValueError):
            Table(["a", "a"], [])

    def test_row_width_validated(self):
        with self.assertRaises(ValueError):
            Table(["a", "b"], [[1]])

    def test_iteration_and_getitem(self):
        records = list(self.table)
        self.assertEqual(records[0]["name"], "alice")
        self.assertEqual(self.table["age"][1], 25)
        self.assertEqual(self.table[0][0], "alice")


class CleanTests(unittest.TestCase):
    def test_strip_whitespace(self):
        table = load_csv(io.StringIO("a,b\n  x  ,  y \n"))
        self.assertEqual(strip_whitespace(table).to_rows(), [["x", "y"]])

    def test_drop_empty_rows_and_columns(self):
        table = Table(["a", "b", "c"], [[1, None, None], [None, None, None]])
        self.assertEqual(drop_empty_rows(table).n_rows, 1)
        self.assertEqual(drop_empty_columns(table).columns, ["a"])

    def test_drop_duplicates(self):
        table = Table(["a", "b"], [[1, "x"], [1, "x"], [2, "y"]])
        self.assertEqual(drop_duplicates(table).n_rows, 2)
        self.assertEqual(drop_duplicates(table, keep="last").to_rows(), [[1, "x"], [2, "y"]])
        self.assertEqual(drop_duplicates(table, keep="none").to_rows(), [[2, "y"]])
        self.assertEqual(drop_duplicates(table, subset=["a"]).n_rows, 2)

    def test_drop_missing(self):
        table = Table(["a", "b"], [[1, None], [None, None], [2, 3]])
        self.assertEqual(drop_missing(table, how="any").to_rows(), [[2, 3]])
        self.assertEqual(drop_missing(table, how="all").n_rows, 2)
        self.assertEqual(drop_missing(table, thresh=1).n_rows, 2)

    def test_fill_missing_value_and_stats(self):
        table = Table(["a"], [[1], [None], [3]])
        self.assertEqual(fill_missing(table, 0).column("a"), [1, 0, 3])
        self.assertEqual(fill_missing(table, strategy="mean").column("a"), [1, 2.0, 3])
        self.assertEqual(fill_missing(table, strategy="median").column("a"), [1, 2, 3])
        self.assertEqual(fill_missing(table, strategy="mode").column("a"), [1, 1, 3])

    def test_fill_missing_forward_backward(self):
        table = Table(["a"], [[1], [None], [None], [4]])
        self.assertEqual(fill_missing(table, strategy="ffill").column("a"), [1, 1, 1, 4])
        self.assertEqual(fill_missing(table, strategy="bfill").column("a"), [1, 4, 4, 4])

    def test_replace_and_coerce(self):
        table = Table(["a", "b"], [["1", "x"], ["2", "y"]])
        coerced = coerce_types(table, {"a": "int"})
        self.assertEqual(coerced.column("a"), [1, 2])
        replaced = replace_values(table, {"x": "z"}, columns=["b"])
        self.assertEqual(replaced.column("b"), ["z", "y"])

    def test_normalize_column_names(self):
        table = Table(["First Name", "E-mail!"], [[1, 2]])
        self.assertEqual(normalize_column_names(table).columns, ["first_name", "e_mail"])


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.table = load_csv(io.StringIO(
            "dept,salary,years\neng,100,1\neng,200,2\nsales,150,3\nsales,250,5\n"
        ))

    def test_describe(self):
        stats = describe(self.table)
        self.assertEqual(set(stats), {"salary", "years"})
        self.assertEqual(stats["salary"]["count"], 4)
        self.assertEqual(stats["salary"]["mean"], 175.0)
        self.assertEqual(stats["salary"]["median"], 175.0)
        self.assertEqual(stats["salary"]["min"], 100)
        self.assertEqual(stats["salary"]["max"], 250)

    def test_value_counts(self):
        counts = value_counts(self.table, "dept")
        self.assertEqual(counts, [("eng", 2), ("sales", 2)])
        normalised = value_counts(self.table, "dept", normalize=True)
        self.assertEqual(normalised[0][1], 0.5)

    def test_missing_counts(self):
        table = Table(["a", "b"], [[1, None], [None, None]])
        self.assertEqual(missing_counts(table), {"a": 1, "b": 2})

    def test_correlation(self):
        perfect = Table(["a", "b"], [[1, 2], [2, 4], [3, 6]])
        self.assertAlmostEqual(correlation(perfect, "a", "b"), 1.0)
        inverse = Table(["a", "b"], [[1, 6], [2, 4], [3, 2]])
        self.assertAlmostEqual(correlation(inverse, "a", "b"), -1.0)
        flat = Table(["a", "b"], [[1, 5], [1, 6], [1, 7]])
        self.assertIsNone(correlation(flat, "a", "b"))

    def test_group_by(self):
        grouped = group_by(
            self.table,
            "dept",
            {
                "n": ("salary", len),
                "avg_salary": ("salary", mean),
            },
        )
        self.assertEqual(grouped.columns, ["dept", "n", "avg_salary"])
        rows = {row["dept"]: row for row in grouped}
        self.assertEqual(rows["eng"]["avg_salary"], 150.0)
        self.assertEqual(rows["sales"]["n"], 2)


if __name__ == "__main__":
    unittest.main()
