import os
import tempfile
import unittest

import tablekit as tk


SAMPLE = """name,age,score,active
 Alice ,30,88.5,true
Bob,,72,false
Carol,25,,
Bob,,72,false
"""


class LoadTests(unittest.TestCase):
    def test_load_csv_string_infers_types(self):
        table = tk.load_csv_string(SAMPLE)
        self.assertEqual(table.columns, ["name", "age", "score", "active"])
        self.assertEqual(len(table), 4)
        self.assertEqual(table.rows[0]["age"], 30)
        self.assertEqual(table.rows[0]["score"], 88.5)
        self.assertIs(table.rows[0]["active"], True)
        self.assertIsNone(table.rows[1]["age"])

    def test_load_csv_from_path(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "data.csv")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(SAMPLE)
            table = tk.load_csv(path)
        self.assertEqual(len(table), 4)

    def test_headerless(self):
        table = tk.load_csv_string("1,2\n3,4\n", has_header=False)
        self.assertEqual(table.columns, ["col1", "col2"])
        self.assertEqual(table.rows[0], {"col1": 1, "col2": 2})

    def test_duplicate_and_blank_headers(self):
        table = tk.load_csv_string("a,a,\n1,2,3\n")
        self.assertEqual(table.columns, ["a", "a_1", "col3"])

    def test_infer_types_disabled(self):
        table = tk.load_csv_string("a\n1\n", infer_types=False)
        self.assertEqual(table.rows[0]["a"], "1")

    def test_empty_input(self):
        table = tk.load_csv_string("")
        self.assertEqual(table.columns, [])
        self.assertEqual(len(table), 0)


class TableTests(unittest.TestCase):
    def setUp(self):
        self.table = tk.load_csv_string(SAMPLE)

    def test_column_and_select(self):
        self.assertEqual(self.table.column("age"), [30, None, 25, None])
        selected = self.table.select("name", "age")
        self.assertEqual(selected.columns, ["name", "age"])
        self.assertNotIn("score", selected.rows[0])

    def test_filter(self):
        adults = self.table.filter(lambda row: (row["age"] or 0) >= 30)
        self.assertEqual(len(adults), 1)

    def test_unknown_column(self):
        with self.assertRaises(KeyError):
            self.table.column("missing")

    def test_equality_and_copy(self):
        clone = self.table.copy()
        self.assertEqual(clone, self.table)
        clone.rows[0]["age"] = 99
        self.assertNotEqual(clone, self.table)


class CleanTests(unittest.TestCase):
    def setUp(self):
        self.table = tk.load_csv_string(SAMPLE)

    def test_strip_whitespace(self):
        cleaned = tk.strip_whitespace(self.table)
        self.assertEqual(cleaned.rows[0]["name"], "Alice")

    def test_drop_duplicates(self):
        deduped = tk.drop_duplicates(self.table)
        self.assertEqual(len(deduped), 3)

    def test_drop_missing_any(self):
        complete = tk.drop_missing(self.table, columns=["age", "score"])
        self.assertEqual(len(complete), 1)

    def test_drop_missing_all(self):
        kept = tk.drop_missing(self.table, columns=["age", "score"], how="all")
        self.assertEqual(len(kept), 4)

    def test_drop_missing_invalid(self):
        with self.assertRaises(ValueError):
            tk.drop_missing(self.table, how="sometimes")

    def test_fill_missing(self):
        filled = tk.fill_missing(self.table, value=0, columns=["age"])
        self.assertEqual(filled.rows[1]["age"], 0)
        self.assertIsNone(filled.rows[2]["score"])

    def test_rename_columns(self):
        renamed = tk.rename_columns(self.table, {"age": "years"})
        self.assertIn("years", renamed.columns)
        self.assertNotIn("age", renamed.columns)

    def test_rename_unknown(self):
        with self.assertRaises(KeyError):
            tk.rename_columns(self.table, {"missing": "x"})


class AnalyzeTests(unittest.TestCase):
    def setUp(self):
        self.table = tk.load_csv_string(SAMPLE)

    def test_mean(self):
        self.assertAlmostEqual(tk.mean(self.table, "age"), 27.5)
        self.assertAlmostEqual(tk.mean(self.table, "score"), 77.5)

    def test_median(self):
        self.assertAlmostEqual(tk.median(self.table, "age"), 27.5)
        self.assertAlmostEqual(tk.median(self.table, "score"), 72)

    def test_mode(self):
        self.assertEqual(tk.mode(self.table, "name"), "Bob")

    def test_stdev(self):
        population = tk.stdev(self.table, "age", sample=False)
        sample = tk.stdev(self.table, "age", sample=True)
        self.assertAlmostEqual(population, 2.5)
        self.assertGreater(sample, population)

    def test_correlation(self):
        self.assertAlmostEqual(tk.correlation(self.table, "age", "age"), 1.0)

    def test_value_counts(self):
        counts = tk.value_counts(self.table, "name")
        self.assertEqual(counts["Bob"], 2)

    def test_describe(self):
        summary = tk.describe(self.table)
        self.assertEqual(summary["name"]["count"], 4)
        self.assertEqual(summary["age"]["missing"], 2)
        self.assertIn("mean", summary["score"])
        self.assertNotIn("mean", summary["name"])

    def test_mean_without_numbers(self):
        with self.assertRaises(ValueError):
            tk.mean(self.table, "name")


if __name__ == "__main__":
    unittest.main()
