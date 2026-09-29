import os
import tempfile
import unittest

from tabular import (
    ColumnNotFoundError,
    CSVLoadError,
    DataTable,
    load_csv,
    load_csv_string,
)


SAMPLE = "name,age,city\nAda,36,London\nGrace,,London\nAlan,41,Cambridge\nAda,36,London\n"


class LoadingTests(unittest.TestCase):
    def test_load_csv_string(self):
        table = load_csv_string(SAMPLE)
        self.assertEqual(table.columns, ("name", "age", "city"))
        self.assertEqual(len(table), 4)

    def test_values_are_strings(self):
        table = load_csv_string(SAMPLE)
        self.assertEqual(table["age"], ["36", "", "41", "36"])

    def test_missing_cell_becomes_none_when_ragged(self):
        table = load_csv_string("a,b,c\n1,2\n")
        self.assertEqual(table.to_dicts(), [{"a": "1", "b": "2", "c": None}])

    def test_extra_fields_raise(self):
        with self.assertRaises(CSVLoadError):
            load_csv_string("a,b\n1,2,3\n")

    def test_empty_source_raises(self):
        with self.assertRaises(CSVLoadError):
            load_csv_string("\n\n")

    def test_no_header_generates_names(self):
        table = load_csv_string("1,2\n3,4\n", has_header=False)
        self.assertEqual(table.columns, ("column_1", "column_2"))
        self.assertEqual(len(table), 2)

    def test_header_sanitised(self):
        table = load_csv_string(",name,name\n1,2,3\n")
        self.assertEqual(table.columns, ("column_1", "name", "name_1"))

    def test_blank_lines_skipped(self):
        table = load_csv_string("a,b\n\n1,2\n\n")
        self.assertEqual(len(table), 1)

    def test_load_from_path(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "data.csv")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(SAMPLE)
            table = load_csv(path)
            self.assertEqual(len(table), 4)

    def test_load_missing_file_raises(self):
        with self.assertRaises(CSVLoadError):
            load_csv("/nonexistent/path/data.csv")


class CleaningTests(unittest.TestCase):
    def setUp(self):
        self.table = load_csv_string(SAMPLE)

    def test_select_columns(self):
        selected = self.table.select_columns(["city", "name"])
        self.assertEqual(selected.columns, ("city", "name"))
        self.assertEqual(selected.to_dicts()[0], {"city": "London", "name": "Ada"})

    def test_select_unknown_column_raises(self):
        with self.assertRaises(ColumnNotFoundError):
            self.table.select_columns(["nope"])

    def test_drop_columns(self):
        dropped = self.table.drop_columns(["city"])
        self.assertEqual(dropped.columns, ("name", "age"))

    def test_drop_all_columns_raises(self):
        with self.assertRaises(ValueError):
            self.table.drop_columns(["name", "age", "city"])

    def test_rename_columns(self):
        renamed = self.table.rename_columns({"name": "full_name"})
        self.assertIn("full_name", renamed.columns)
        self.assertEqual(renamed.to_dicts()[0]["full_name"], "Ada")

    def test_rename_to_duplicate_raises(self):
        with self.assertRaises(ValueError):
            self.table.rename_columns({"name": "age"})

    def test_drop_duplicates(self):
        deduped = self.table.drop_duplicates()
        self.assertEqual(len(deduped), 3)

    def test_drop_duplicates_subset(self):
        deduped = self.table.drop_duplicates(subset=["name"])
        self.assertEqual([row["name"] for row in deduped], ["Ada", "Grace", "Alan"])

    def test_drop_missing_any(self):
        cleaned = self.table.drop_missing()
        self.assertEqual(len(cleaned), 3)

    def test_drop_missing_all(self):
        cleaned = self.table.drop_missing(how="all")
        self.assertEqual(len(cleaned), 4)

    def test_fill_missing_scalar(self):
        filled = self.table.fill_missing(0, subset=["age"])
        self.assertEqual(filled["age"], ["36", 0, "41", "36"])

    def test_fill_missing_mapping(self):
        filled = self.table.fill_missing({"age": "0"})
        self.assertEqual(filled["age"][1], "0")

    def test_strip_whitespace(self):
        table = load_csv_string("a,b\n  x  , y\n")
        stripped = table.strip_whitespace()
        self.assertEqual(stripped.to_dicts(), [{"a": "x", "b": "y"}])

    def test_convert_types(self):
        converted = self.table.convert_types()
        self.assertEqual(converted["age"], [36, "", 41, 36])

    def test_convert_types_leaves_text(self):
        converted = self.table.convert_types()
        self.assertEqual(converted["name"], ["Ada", "Grace", "Alan", "Ada"])

    def test_cleaning_does_not_mutate(self):
        self.table.drop_duplicates()
        self.assertEqual(len(self.table), 4)


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.table = load_csv_string(SAMPLE).convert_types()

    def test_count_rows_and_column(self):
        self.assertEqual(self.table.count(), 4)
        self.assertEqual(self.table.count("age"), 3)

    def test_sum_mean_median(self):
        self.assertEqual(self.table.sum("age"), 113)
        self.assertAlmostEqual(self.table.mean("age"), 113 / 3)
        self.assertEqual(self.table.median("age"), 36)

    def test_min_max(self):
        self.assertEqual(self.table.min("age"), 36)
        self.assertEqual(self.table.max("age"), 41)

    def test_stdev(self):
        self.assertAlmostEqual(self.table.stdev("age"), 2.886751345948129, places=9)

    def test_stdev_requires_two_values(self):
        table = load_csv_string("a\n1\n")
        with self.assertRaises(Exception):
            table.stdev("a")

    def test_non_numeric_column_raises(self):
        with self.assertRaises(Exception):
            self.table.mean("name")

    def test_value_counts(self):
        counts = self.table.value_counts("city")
        self.assertEqual(counts["London"], 3)
        self.assertEqual(next(iter(counts)), "London")

    def test_value_counts_dropna_false(self):
        counts = self.table.value_counts("age", dropna=False)
        self.assertEqual(counts[""], 1)

    def test_describe_numeric(self):
        summary = self.table.describe()["age"]
        self.assertEqual(summary["count"], 3)
        self.assertAlmostEqual(summary["mean"], 113 / 3)
        self.assertEqual(summary["min"], 36)
        self.assertEqual(summary["max"], 41)

    def test_describe_text(self):
        summary = self.table.describe()["city"]
        self.assertEqual(summary["unique"], 2)
        self.assertEqual(summary["top"], "London")
        self.assertEqual(summary["freq"], 3)

    def test_correlation(self):
        table = load_csv_string("x,y\n1,2\n2,4\n3,6\n")
        self.assertAlmostEqual(table.correlation("x", "y"), 1.0)


class OutputTests(unittest.TestCase):
    def test_to_csv_string_round_trip(self):
        table = DataTable(["a", "b"], [[1, 2], [3, None]])
        rendered = table.to_csv_string()
        reloaded = load_csv_string(rendered)
        self.assertEqual(reloaded.columns, ("a", "b"))
        self.assertEqual(reloaded["a"], ["1", "3"])

    def test_from_rows(self):
        table = DataTable.from_rows(["a", "b"], [[1, 2], [3, 4]])
        self.assertEqual(table["b"], [2, 4])

    def test_duplicate_columns_rejected(self):
        with self.assertRaises(ValueError):
            DataTable(["a", "a"], [[1, 2]])


if __name__ == "__main__":
    unittest.main()
