import io
import os
import tempfile
import unittest

import csvlib
from csvlib import Table


class TableTests(unittest.TestCase):
    def test_shape_and_columns(self):
        table = Table(["a", "b"], [[1, 2], [3, 4]])
        self.assertEqual(table.shape, (2, 2))
        self.assertEqual(table.columns, ["a", "b"])
        self.assertEqual(table.num_rows, 2)
        self.assertEqual(len(table), 2)

    def test_getitem_by_name_and_index(self):
        table = Table(["a", "b"], [[1, 2], [3, 4]])
        self.assertEqual(table["a"], [1, 3])
        self.assertEqual(table[0], {"a": 1, "b": 2})
        self.assertEqual(table[0:1], [{"a": 1, "b": 2}])

    def test_from_records_orders_columns_by_appearance(self):
        table = Table.from_records([{"b": 1, "a": 2}, {"a": 3, "c": 4}])
        self.assertEqual(table.columns, ["b", "a", "c"])
        self.assertEqual(table["c"], [None, 4])

    def test_duplicate_columns_rejected(self):
        with self.assertRaises(ValueError):
            Table(["a", "a"], [])

    def test_select_drop_rename(self):
        table = Table(["a", "b", "c"], [[1, 2, 3]])
        self.assertEqual(table.select("c", "a").columns, ["c", "a"])
        self.assertEqual(table.drop("b").columns, ["a", "c"])
        self.assertEqual(table.rename({"a": "x"}).columns, ["x", "b", "c"])

    def test_add_column(self):
        table = Table(["a"], [[1], [2]])
        grown = table.add_column("b", [3, 4])
        self.assertEqual(grown["b"], [3, 4])
        self.assertEqual(table.columns, ["a"])

    def test_head_tail_and_equality(self):
        table = Table(["a"], [[1], [2], [3]])
        self.assertEqual(table.head(2).to_rows(), [[1], [2]])
        self.assertEqual(table.tail(2).to_rows(), [[2], [3]])
        self.assertEqual(table, Table(["a"], [[1], [2], [3]]))


class LoaderTests(unittest.TestCase):
    def test_parse_basic(self):
        table = csvlib.parse_csv("a,b\n1,2\n3,4\n")
        self.assertEqual(table.columns, ["a", "b"])
        self.assertEqual(table.to_rows(), [["1", "2"], ["3", "4"]])

    def test_sniffs_semicolon_delimiter(self):
        table = csvlib.parse_csv("a;b\n1;2\n")
        self.assertEqual(table.columns, ["a", "b"])
        self.assertEqual(table.to_rows(), [["1", "2"]])

    def test_explicit_delimiter(self):
        table = csvlib.parse_csv("a|b\n1|2\n", sniff=False, delimiter="|")
        self.assertEqual(table.columns, ["a", "b"])

    def test_without_header(self):
        table = csvlib.parse_csv("1,2\n3,4\n", has_header=False)
        self.assertEqual(table.columns, ["column_1", "column_2"])

    def test_missing_tokens_become_none(self):
        table = csvlib.parse_csv("a,b\n1,\nNA,x\n")
        self.assertEqual(table["b"], [None, "x"])
        self.assertEqual(table["a"], ["1", None])

    def test_missing_can_be_disabled(self):
        table = csvlib.parse_csv('a,b\n"",x\n', missing=())
        self.assertEqual(table["a"], [""])

    def test_blank_and_duplicate_headers(self):
        table = csvlib.parse_csv(",a,a\n1,2,3\n")
        self.assertEqual(table.columns, ["column_1", "a", "a_2"])

    def test_quoted_values_with_newline(self):
        table = csvlib.parse_csv('a,b\n1,"x\ny"\n')
        self.assertEqual(table["b"], ["x\ny"])

    def test_ragged_rows_are_padded_and_truncated(self):
        table = csvlib.parse_csv("a,b\n1\n2,3,4\n")
        self.assertEqual(table.to_rows(), [["1", None], ["2", "3"]])

    def test_headers_are_stripped(self):
        table = csvlib.parse_csv("  a  , b\n1,2\n")
        self.assertEqual(table.columns, ["a", "b"])

    def test_empty_input(self):
        self.assertEqual(csvlib.parse_csv("").shape, (0, 0))
        self.assertEqual(csvlib.parse_csv("   ").shape, (0, 0))

    def test_load_from_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "data.csv")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("a,b\n1,2\n")
            self.assertEqual(csvlib.load_csv(path).to_rows(), [["1", "2"]])

    def test_load_from_bytes_and_file_object(self):
        self.assertEqual(csvlib.load_csv(b"a\n1\n")["a"], ["1"])
        self.assertEqual(csvlib.load_csv(io.StringIO("a\n1\n"))["a"], ["1"])

    def test_bom_is_stripped(self):
        self.assertEqual(csvlib.load_csv(b"\xef\xbb\xbfa\n1\n").columns, ["a"])

    def test_load_csvs_unions_columns(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = os.path.join(tmp, "one.csv")
            second = os.path.join(tmp, "two.csv")
            with open(first, "w", encoding="utf-8") as fh:
                fh.write("a,b\n1,2\n")
            with open(second, "w", encoding="utf-8") as fh:
                fh.write("b,c\n3,4\n")
            table = csvlib.load_csvs([first, second], source_column="src")
            self.assertEqual(table.columns, ["a", "b", "c", "src"])
            self.assertEqual(table["a"], ["1", None])
            self.assertEqual(table["c"], [None, "4"])
            self.assertEqual(table["src"], [first, second])


class CleaningTests(unittest.TestCase):
    def make(self):
        return Table(
            ["name", "age", "city"],
            [
                ["  Ada  ", "36", "London"],
                ["Bob", None, "Paris"],
                [None, "41", None],
                ["Bob", None, "Paris"],
            ],
        )

    def test_strip_whitespace(self):
        table = csvlib.strip_whitespace(self.make())
        self.assertEqual(table["name"], ["Ada", "Bob", None, "Bob"])

    def test_fill_missing(self):
        table = csvlib.fill_missing(self.make(), "unknown")
        self.assertEqual(table["city"], ["London", "Paris", "unknown", "Paris"])

    def test_replace_values(self):
        table = csvlib.replace_values(self.make(), {"Bob": "Robert"})
        self.assertEqual(table["name"][1], "Robert")

    def test_drop_empty_rows(self):
        table = csvlib.drop_empty_rows(Table(["a", "b"], [[None, ""], [1, None]]))
        self.assertEqual(table.to_rows(), [[1, None]])

    def test_drop_empty_columns(self):
        table = csvlib.drop_empty_columns(Table(["a", "b"], [[None, 1], ["", 2]]))
        self.assertEqual(table.columns, ["b"])

    def test_drop_missing_rows_any_and_all(self):
        table = self.make()
        self.assertEqual(csvlib.drop_missing_rows(table, how="any").num_rows, 1)
        self.assertEqual(csvlib.drop_missing_rows(table, how="all").num_rows, 4)

    def test_drop_missing_columns_threshold(self):
        table = Table(["a", "b"], [[None, 1], [None, 2]])
        self.assertEqual(csvlib.drop_missing_columns(table).columns, ["b"])
        self.assertEqual(csvlib.drop_missing_columns(table, threshold=0.5).columns, ["b"])

    def test_drop_duplicates(self):
        table = csvlib.drop_duplicates(self.make())
        self.assertEqual(table.num_rows, 3)

    def test_drop_duplicates_subset(self):
        table = csvlib.drop_duplicates(self.make(), subset=["name"])
        self.assertEqual(table.num_rows, 3)

    def test_normalize_columns_snake_case(self):
        table = Table(["First Name", "Total $"], [[1, 2]])
        self.assertEqual(
            csvlib.normalize_columns(table).columns, ["first_name", "total"]
        )

    def test_convert_column(self):
        table = csvlib.convert_column(Table(["a"], [["1"], ["x"]]), "a", int, errors="coerce")
        self.assertEqual(table["a"], [1, None])

    def test_coerce_types(self):
        table = csvlib.coerce_types(
            Table(
                ["i", "f", "b", "mixed", "code", "text"],
                [["1", "1.5", "true", "1", "001", "x"],
                 ["2", "2", "false", "2.5", "002", "y"]],
            )
        )
        self.assertEqual(table["i"], [1, 2])
        self.assertEqual(table["f"], [1.5, 2.0])
        self.assertEqual(table["b"], [True, False])
        self.assertEqual(table["mixed"], [1.0, 2.5])
        self.assertEqual(table["code"], ["001", "002"])
        self.assertEqual(table["text"], ["x", "y"])

    def test_coerce_keeps_missing_as_none(self):
        table = csvlib.coerce_types(Table(["a"], [["1"], [None]]))
        self.assertEqual(table["a"], [1, None])

    def test_select_columns_unknown_raises(self):
        with self.assertRaises(KeyError):
            csvlib.select_columns(self.make(), ["nope"])


class AnalysisTests(unittest.TestCase):
    def make(self):
        return csvlib.coerce_types(
            Table(
                ["team", "points", "assists", "active"],
                [
                    ["red", "10", "5", "true"],
                    ["red", "20", "7", "false"],
                    ["blue", "5", "3", "true"],
                    ["blue", None, "3", "true"],
                ],
            )
        )

    def test_missing_report(self):
        report = csvlib.missing_report(self.make())
        self.assertEqual(report["points"]["missing"], 1)
        self.assertEqual(report["assists"]["missing"], 0)
        self.assertAlmostEqual(report["points"]["fraction"], 0.25)

    def test_numeric_and_categorical_columns(self):
        table = self.make()
        self.assertEqual(set(csvlib.numeric_columns(table)), {"points", "assists"})
        self.assertIn("team", csvlib.categorical_columns(table))

    def test_value_counts(self):
        counts = csvlib.value_counts(self.make(), "team")
        self.assertEqual(counts, {"red": 2, "blue": 2})

    def test_value_counts_normalize(self):
        counts = csvlib.value_counts(self.make(), "active", normalize=True)
        self.assertAlmostEqual(counts[True], 0.75)
        self.assertAlmostEqual(counts[False], 0.25)

    def test_value_counts_dropna(self):
        counts = csvlib.value_counts(self.make(), "points", dropna=False)
        self.assertEqual(counts[None], 1)

    def test_column_stats_numeric(self):
        stats = csvlib.column_stats(self.make(), "points")
        self.assertEqual(stats["count"], 3)
        self.assertEqual(stats["missing"], 1)
        self.assertEqual(stats["min"], 5.0)
        self.assertEqual(stats["max"], 20.0)
        self.assertAlmostEqual(stats["mean"], 35 / 3)

    def test_column_stats_categorical(self):
        stats = csvlib.column_stats(self.make(), "team")
        self.assertEqual(stats["unique"], 2)
        self.assertEqual(stats["freq"], 2)

    def test_describe_and_summary(self):
        described = csvlib.describe(self.make())
        self.assertEqual(set(described), {"team", "points", "assists", "active"})
        summary = csvlib.summary(self.make())
        self.assertEqual(summary.num_rows, 4)
        self.assertIn("column", summary.columns)

    def test_correlation(self):
        table = Table(["x", "y"], [[1, 2], [2, 4], [3, 6]])
        self.assertAlmostEqual(csvlib.correlation(table, "x", "y"), 1.0)

    def test_correlation_undefined(self):
        table = Table(["x", "y"], [[1, 2], [1, 4]])
        self.assertIsNone(csvlib.correlation(table, "x", "y"))

    def test_group_by(self):
        table = csvlib.group_by(
            self.make(),
            "team",
            {"total": ("points", "sum"), "avg_assists": ("assists", "mean")},
        )
        rows = {row["team"]: row for row in table}
        self.assertEqual(rows["red"]["total"], 30)
        self.assertEqual(rows["blue"]["total"], 5)
        self.assertAlmostEqual(rows["red"]["avg_assists"], 6.0)

    def test_group_by_count_and_custom_callable(self):
        table = csvlib.group_by(
            self.make(),
            "team",
            {"n": ("points", "count"), "spread": ("points", lambda v: max(v) - min(v))},
        )
        rows = {row["team"]: row for row in table}
        self.assertEqual(rows["red"]["n"], 2)
        self.assertEqual(rows["blue"]["n"], 1)
        self.assertEqual(rows["blue"]["spread"], 0.0)

    def test_group_by_requires_numeric(self):
        with self.assertRaises(ValueError):
            csvlib.group_by(self.make(), "team", {"bad": ("team", "sum")})


class IntegrationTests(unittest.TestCase):
    def test_load_clean_analyze_pipeline(self):
        raw = "name, score ,team\n  Ada ,10,red\nBob,,blue\nBob,20,red\n"
        table = csvlib.load_csv(io.StringIO(raw))
        table = csvlib.strip_whitespace(table)
        table = csvlib.normalize_columns(table)
        table = csvlib.coerce_types(table)
        self.assertEqual(table.columns, ["name", "score", "team"])
        self.assertEqual(table["score"], [10, None, 20])
        grouped = csvlib.group_by(table, "team", {"total": ("score", "sum")})
        self.assertEqual(grouped["total"], [30, None])


if __name__ == "__main__":
    unittest.main()
