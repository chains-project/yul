import math
import os
import tempfile
import unittest

from tabular import (
    Table,
    convert_types,
    correlation,
    describe,
    drop_duplicates,
    drop_missing,
    fill_missing,
    filter_rows,
    group_by,
    mean,
    median,
    normalize_column_names,
    quantile,
    read_csv,
    read_csv_string,
    replace_values,
    stdev,
    strip_whitespace,
    summary,
    value_counts,
    variance,
    write_csv,
)


class TableTests(unittest.TestCase):
    def test_from_rows_and_shape(self):
        table = Table.from_rows(["a", "b"], [[1, 2], [3, 4]])
        self.assertEqual(table.shape, (2, 2))
        self.assertEqual(table.columns, ["a", "b"])
        self.assertEqual(table.column("a"), [1, 3])
        self.assertEqual(table.row(1), {"a": 3, "b": 4})

    def test_from_dicts_orders_and_fills(self):
        table = Table.from_dicts([{"a": 1}, {"b": 2}, {"a": 3}])
        self.assertEqual(table.columns, ["a", "b"])
        self.assertEqual(table.column("b"), [None, 2, None])

    def test_from_rows_rejects_ragged(self):
        with self.assertRaises(ValueError):
            Table.from_rows(["a", "b"], [[1]])

    def test_select_drop_rename(self):
        table = Table.from_rows(["a", "b", "c"], [[1, 2, 3]])
        self.assertEqual(table.select(["a", "c"]).columns, ["a", "c"])
        self.assertEqual(table.drop(["b"]).columns, ["a", "c"])
        self.assertEqual(table.rename({"a": "x"}).columns, ["x", "b", "c"])

    def test_with_column_and_slice(self):
        table = Table.from_rows(["a"], [[1], [2], [3]])
        extended = table.with_column("b", [4, 5, 6])
        self.assertEqual(extended.column("b"), [4, 5, 6])
        self.assertEqual(table.head(2).column("a"), [1, 2])
        self.assertEqual(table.tail(1).column("a"), [3])

    def test_equality_and_iteration(self):
        table = Table.from_rows(["a"], [[1], [2]])
        self.assertEqual(list(table), [{"a": 1}, {"a": 2}])
        self.assertEqual(table, Table.from_rows(["a"], [[1], [2]]))

    def test_duplicate_columns_rejected(self):
        with self.assertRaises(ValueError):
            Table(["a", "a"])


class ReadCsvTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "data.csv")

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, text):
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write(text)

    def test_infers_types_and_missing(self):
        self._write("name,age,score,active\nAlice,30,1.5,true\nBob,,2,false\n")
        table = read_csv(self.path)
        self.assertEqual(table.columns, ["name", "age", "score", "active"])
        self.assertEqual(table.column("age"), [30, None])
        self.assertEqual(table.column("score"), [1.5, 2.0])
        self.assertEqual(table.column("active"), [True, False])

    def test_preserves_leading_zeros(self):
        self._write("code\n007\n42\n")
        table = read_csv(self.path)
        self.assertEqual(table.column("code"), ["007", 42])

    def test_without_header(self):
        self._write("1,2\n3,4\n")
        table = read_csv(self.path, header=False)
        self.assertEqual(table.columns, ["col_1", "col_2"])
        self.assertEqual(table.column("col_2"), [2, 4])

    def test_custom_delimiter_and_missing(self):
        self._write("a;b\n1;NA\n2;3\n")
        table = read_csv(self.path, delimiter=";", missing_values=["NA"])
        self.assertEqual(table.column("b"), [None, 3])

    def test_blank_lines_and_short_rows(self):
        self._write("a,b\n\n1,2\n3\n")
        table = read_csv(self.path)
        self.assertEqual(table.column("b"), [2, None])

    def test_duplicate_headers(self):
        self._write("a,a\n1,2\n")
        table = read_csv(self.path)
        self.assertEqual(table.columns, ["a", "a_1"])

    def test_no_inference_keeps_strings(self):
        self._write("a,b\n1,\n2,x\n")
        table = read_csv(self.path, infer_types=False)
        self.assertEqual(table.column("a"), ["1", "2"])
        self.assertEqual(table.column("b"), [None, "x"])

    def test_read_from_string(self):
        table = read_csv_string("a,b\n1,2\n")
        self.assertEqual(table.row(0), {"a": 1, "b": 2})

    def test_write_round_trip(self):
        table = Table.from_rows(["a", "b"], [[1, "x"], [None, "y"]])
        write_csv(table, self.path)
        self.assertEqual(read_csv(self.path), table)


class CleanTests(unittest.TestCase):
    def _table(self):
        return Table.from_rows(
            ["name", "age", "city"],
            [
                [" Alice ", 30, "NY"],
                ["bob", None, "NY"],
                ["Carol", 25, None],
                ["bob", None, "LA"],
            ],
        )

    def test_strip_whitespace(self):
        table = strip_whitespace(self._table(), ["name"])
        self.assertEqual(table.column("name"), ["Alice", "bob", "Carol", "bob"])

    def test_normalize_column_names(self):
        table = Table.from_rows(["First Name", "Total $"], [[1, 2]])
        normalized = normalize_column_names(table)
        self.assertEqual(normalized.columns, ["first_name", "total"])

    def test_normalize_column_names_dedupes(self):
        table = Table.from_rows(["A B", "a-b"], [[1, 2]])
        self.assertEqual(normalize_column_names(table).columns, ["a_b", "a_b_1"])

    def test_drop_missing_any(self):
        table = drop_missing(self._table(), ["age"], how="any")
        self.assertEqual(table.num_rows, 2)
        self.assertEqual(table.column("name"), [" Alice ", "Carol"])

    def test_drop_missing_all(self):
        table = Table.from_rows(
            ["a", "b", "c"],
            [[1, 2, 3], [None, 2, 3], [None, None, 3], [None, None, None]],
        )
        dropped_all = drop_missing(table, ["a", "b"], how="all")
        self.assertEqual(dropped_all.num_rows, 2)
        dropped_any = drop_missing(table, ["a", "b"], how="any")
        self.assertEqual(dropped_any.num_rows, 1)

    def test_fill_missing_value_and_mode(self):
        filled = fill_missing(self._table(), columns=["city"], strategy="mode")
        self.assertEqual(filled.column("city"), ["NY", "NY", "NY", "LA"])
        value_filled = fill_missing(self._table(), columns=["age"], value=0)
        self.assertEqual(value_filled.column("age"), [30, 0, 25, 0])

    def test_fill_missing_mean(self):
        table = Table.from_rows(["x"], [[1], [3], [None]])
        self.assertEqual(fill_missing(table, columns=["x"], strategy="mean").column("x"), [1, 3, 2.0])

    def test_fill_missing_ffill(self):
        table = Table.from_rows(["x"], [[1], [None], [3]])
        self.assertEqual(fill_missing(table, columns=["x"], strategy="ffill").column("x"), [1, 1, 3])

    def test_fill_missing_bfill(self):
        table = Table.from_rows(["x"], [[1], [None], [3]])
        self.assertEqual(fill_missing(table, columns=["x"], strategy="bfill").column("x"), [1, 3, 3])

    def test_drop_duplicates_first_and_last(self):
        table = Table.from_rows(["k", "v"], [["x", 1], ["x", 2], ["y", 3]])
        first = drop_duplicates(table, columns=["k"], keep="first")
        self.assertEqual(list(first.rows()), [["x", 1], ["y", 3]])
        last = drop_duplicates(table, columns=["k"], keep="last")
        self.assertEqual(list(last.rows()), [["x", 2], ["y", 3]])

    def test_drop_duplicates_all(self):
        table = self._table()
        dropped = drop_duplicates(table, columns=["name"], keep=False)
        self.assertEqual(dropped.column("name"), [" Alice ", "Carol"])

    def test_convert_types(self):
        table = Table.from_rows(["a", "b", "c"], [["1", "2.5", "true"]])
        converted = convert_types(table, {"a": "int", "b": "float", "c": "bool"})
        self.assertEqual(converted.row(0), {"a": 1, "b": 2.5, "c": True})

    def test_convert_types_auto_and_missing(self):
        table = Table.from_rows(["a"], [["12"], [""]])
        self.assertEqual(convert_types(table, {"a": "auto"}).column("a"), [12, None])

    def test_replace_values(self):
        table = replace_values(self._table(), {"NY": "New York"}, ["city"])
        self.assertEqual(table.column("city"), ["New York", "New York", None, "LA"])

    def test_filter_rows(self):
        table = filter_rows(self._table(), lambda row: row["age"] is not None)
        self.assertEqual(table.num_rows, 2)


class AnalysisTests(unittest.TestCase):
    def _table(self):
        return Table.from_rows(
            ["group", "value"],
            [
                ["a", 1],
                ["a", 3],
                ["b", 5],
                ["b", None],
            ],
        )

    def test_basic_statistics(self):
        values = [1, 2, 3, 4]
        self.assertEqual(mean(values), 2.5)
        self.assertEqual(median(values), 2.5)
        self.assertAlmostEqual(variance(values), 5 / 3)
        self.assertAlmostEqual(stdev(values), math.sqrt(5 / 3))
        self.assertEqual(quantile(values, 0.5), 2.5)

    def test_statistics_ignore_missing(self):
        self.assertEqual(mean([1, None, 3]), 2.0)
        self.assertIsNone(stdev([1]))
        self.assertIsNone(median([]))

    def test_value_counts(self):
        counts = value_counts(Table.from_rows(["x"], [["a"], ["b"], ["a"]]), "x")
        self.assertEqual(counts, {"a": 2, "b": 1})

    def test_value_counts_normalized(self):
        counts = value_counts(Table.from_rows(["x"], [["a"], ["b"], ["a"]]), "x", normalize=True)
        self.assertEqual(counts, {"a": 2 / 3, "b": 1 / 3})

    def test_correlation(self):
        table = Table.from_rows(["x", "y"], [[1, 2], [2, 4], [3, 6]])
        self.assertAlmostEqual(correlation(table, "x", "y"), 1.0)
        self.assertIsNone(correlation(Table.from_rows(["x", "y"], [[1, 1]]), "x", "y"))

    def test_summary(self):
        stats = summary(self._table())
        self.assertEqual(stats["value"]["count"], 3)
        self.assertEqual(stats["value"]["missing"], 1)
        self.assertEqual(stats["value"]["max"], 5)

    def test_describe(self):
        described = describe(self._table())
        self.assertEqual(described.columns[0], "column")
        self.assertEqual(described.num_rows, 2)

    def test_group_by(self):
        result = group_by(
            self._table(),
            "group",
            {"value": ["mean", "count", "max"]},
        )
        self.assertEqual(result.columns, ["group", "value_mean", "value_count", "value_max"])
        rows = {row["group"]: row for row in result.rows(named=True)}
        self.assertEqual(rows["a"]["value_mean"], 2.0)
        self.assertEqual(rows["b"]["value_count"], 1)
        self.assertEqual(rows["b"]["value_max"], 5)

    def test_group_by_default_count(self):
        result = group_by(self._table(), "group")
        self.assertEqual(result.columns, ["group", "count"])
        self.assertEqual([row["count"] for row in result.rows(named=True)], [2, 2])


if __name__ == "__main__":
    unittest.main()
