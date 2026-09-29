import io
import tempfile
import unittest
from pathlib import Path

from csvlab import Table


SAMPLE = """name,age,score,active,city
 Alice,30,91.5,true,Paris
Bob,25,88,false,London
Carla,,77.5,true,Paris
Bob,25,88,false,London
Dave,40,,true,Berlin
"""


class LoadingTests(unittest.TestCase):
    def setUp(self):
        self.csv_text = SAMPLE

    def test_from_csv_infers_types_and_missing(self):
        table = Table.from_csv(io.StringIO(self.csv_text))
        self.assertEqual(table.columns, ["name", "age", "score", "active", "city"])
        self.assertEqual(len(table), 5)
        self.assertEqual(table["age"][0], 30)
        self.assertIs(table["active"][0], True)
        self.assertEqual(table["score"][2], 77.5)
        self.assertIsNone(table["age"][2])
        self.assertIsNone(table["score"][4])

    def test_from_csv_can_disable_inference(self):
        table = Table.from_csv(io.StringIO(self.csv_text), infer_types=False)
        self.assertEqual(table["age"][0], "30")

    def test_from_dict(self):
        table = Table.from_dict({"a": [1, 2], "b": ["x", "y"]})
        self.assertEqual(table.columns, ["a", "b"])
        self.assertEqual(table.rows[1], {"a": 2, "b": "y"})

    def test_from_dict_length_mismatch(self):
        with self.assertRaises(ValueError):
            Table.from_dict({"a": [1, 2], "b": ["x"]})

    def test_csv_roundtrip(self):
        table = Table.from_csv(io.StringIO(self.csv_text))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "out.csv"
            table.to_csv(path)
            reloaded = Table.from_csv(path)
        self.assertEqual(reloaded.to_records(), table.to_records())

    def test_column_lookup_missing(self):
        table = Table.from_csv(io.StringIO(self.csv_text))
        with self.assertRaises(KeyError):
            table["nope"]


class CleaningTests(unittest.TestCase):
    def setUp(self):
        self.table = Table.from_csv(io.StringIO(SAMPLE))

    def test_drop_duplicates(self):
        cleaned = self.table.drop_duplicates()
        self.assertEqual(len(cleaned), 4)

    def test_drop_duplicates_subset(self):
        cleaned = self.table.drop_duplicates(subset=["name"])
        self.assertEqual(len(cleaned), 4)

    def test_drop_missing_any(self):
        cleaned = self.table.drop_missing()
        self.assertEqual(len(cleaned), 3)

    def test_drop_missing_all(self):
        cleaned = self.table.drop_missing(how="all")
        self.assertEqual(len(cleaned), 5)

    def test_drop_missing_threshold(self):
        cleaned = self.table.drop_missing(threshold=0.2)
        self.assertEqual(len(cleaned), 5)

    def test_fill_missing_constant(self):
        filled = self.table.fill_missing(0, columns=["age"])
        self.assertEqual(filled["age"][2], 0)

    def test_fill_missing_mean_ignores_non_numeric(self):
        table = Table.from_dict({"name": ["Alice", None], "age": [30, None]})
        filled = table.fill_missing(columns=["name", "age"], strategy="mean")
        self.assertIsNone(filled["name"][1])
        self.assertAlmostEqual(filled["age"][1], 30.0)

    def test_fill_missing_requires_value_or_strategy(self):
        with self.assertRaises(ValueError):
            self.table.fill_missing()

    def test_strip_whitespace(self):
        stripped = self.table.strip_whitespace()
        self.assertEqual(stripped["name"][0], "Alice")

    def test_rename_columns(self):
        renamed = self.table.rename_columns({"name": "full_name"})
        self.assertIn("full_name", renamed.columns)
        self.assertNotIn("name", renamed.columns)

    def test_rename_columns_unknown(self):
        with self.assertRaises(KeyError):
            self.table.rename_columns({"nope": "x"})

    def test_normalize_headers(self):
        table = Table.from_dict({"First Name": [1], "Total $": [2]})
        normalized = table.normalize_headers()
        self.assertEqual(normalized.columns, ["first_name", "total"])

    def test_cast_column(self):
        table = Table.from_dict({"n": ["1", "2", None]})
        casted = table.cast_column("n", "int")
        self.assertEqual(casted["n"], [1, 2, None])

    def test_cast_column_invalid(self):
        table = Table.from_dict({"n": ["x"]})
        with self.assertRaises(ValueError):
            table.cast_column("n", "int")

    def test_replace_values(self):
        replaced = self.table.replace_values("city", {"Paris": "PARIS"})
        self.assertEqual(replaced["city"][0], "PARIS")


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.table = Table.from_dict(
            {
                "g": ["a", "a", "b", "b"],
                "x": [1, 2, 3, 4],
                "y": [2, 4, 6, 8],
            }
        )

    def test_numeric_and_categorical_columns(self):
        self.assertEqual(self.table.numeric_columns(), ["x", "y"])
        self.assertEqual(self.table.categorical_columns(), ["g"])

    def test_describe(self):
        summary = self.table.describe()
        self.assertEqual(summary["x"]["count"], 4)
        self.assertAlmostEqual(summary["x"]["mean"], 2.5)
        self.assertAlmostEqual(summary["x"]["median"], 2.5)
        self.assertEqual(summary["g"]["unique"], 2)
        self.assertEqual(summary["g"]["top"], "a")

    def test_value_counts(self):
        counts = self.table.value_counts("g")
        self.assertEqual(counts, [("a", 2), ("b", 2)])

    def test_statistics(self):
        self.assertAlmostEqual(self.table.mean("x"), 2.5)
        self.assertAlmostEqual(self.table.median("x"), 2.5)
        self.assertGreater(self.table.stdev("x"), 0)

    def test_statistics_requires_numeric(self):
        with self.assertRaises(TypeError):
            self.table.mean("g")

    def test_correlation(self):
        self.assertAlmostEqual(self.table.correlation("x", "y"), 1.0)

    def test_group_by(self):
        groups = self.table.group_by(["g"])
        self.assertEqual(set(groups), {("a",), ("b",)})
        self.assertEqual(len(groups[("a",)]), 2)

    def test_aggregate(self):
        agg = self.table.aggregate(["g"], {"x": "sum", "y": "mean"})
        self.assertEqual(agg.columns, ["g", "x_sum", "y_mean"])
        rows = {row["g"]: row for row in agg.rows}
        self.assertEqual(rows["a"]["x_sum"], 3)
        self.assertAlmostEqual(rows["a"]["y_mean"], 3.0)

    def test_aggregate_callable(self):
        agg = self.table.aggregate(["g"], {"x": max})
        self.assertEqual({row["g"]: row["x_max"] for row in agg.rows}, {"a": 2, "b": 4})


if __name__ == "__main__":
    unittest.main()
