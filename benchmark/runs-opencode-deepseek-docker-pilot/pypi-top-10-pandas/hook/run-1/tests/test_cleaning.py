import unittest

from datalib import Table
from datalib import cleaning
from datalib.exceptions import SchemaError


def sample():
    return Table(
        ["name", "age", "score"],
        [
            {"name": " Ada ", "age": "36", "score": 9.5},
            {"name": "Grace", "age": "45", "score": None},
            {"name": "Grace", "age": "45", "score": None},
            {"name": None, "age": "", "score": ""},
        ],
    )


class CleaningTests(unittest.TestCase):
    def test_strip_whitespace(self):
        result = cleaning.strip_whitespace(sample())
        self.assertEqual(result.column("name")[0], "Ada")

    def test_drop_missing_any_and_all(self):
        table = Table(["a", "b"], [[1, None], [None, None], [2, 3]])
        self.assertEqual(len(cleaning.drop_missing(table, how="any")), 1)
        self.assertEqual(len(cleaning.drop_missing(table, how="all")), 2)

    def test_drop_missing_subset(self):
        table = Table(["a", "b"], [[1, None], [None, 3]])
        self.assertEqual(len(cleaning.drop_missing(table, subset=["a"])), 1)
        self.assertEqual(len(cleaning.drop_missing(table, subset=["b"])), 1)

    def test_drop_duplicates(self):
        table = Table(["a", "b"], [[1, 2], [1, 2], [3, 4]])
        self.assertEqual(len(cleaning.drop_duplicates(table)), 2)
        self.assertEqual(len(cleaning.drop_duplicates(table, keep=False)), 1)

    def test_drop_duplicates_subset(self):
        table = Table(["a", "b"], [[1, 2], [1, 3]])
        result = cleaning.drop_duplicates(table, subset=["a"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result.column("b"), [2])

    def test_fill_missing_value(self):
        table = Table(["a"], [[1], [None]])
        self.assertEqual(cleaning.fill_missing(table, value=0).column("a"), [1, 0])

    def test_fill_missing_mean_median_mode(self):
        table = Table(["a"], [[1], [None], [3]])
        self.assertEqual(cleaning.fill_missing(table, strategy="mean").column("a"), [1, 2.0, 3])
        self.assertEqual(cleaning.fill_missing(table, strategy="median").column("a"), [1, 2, 3])
        table2 = Table(["a"], [["x"], [None], ["x"]])
        self.assertEqual(cleaning.fill_missing(table2, strategy="mode").column("a"), ["x", "x", "x"])

    def test_fill_missing_ffill_bfill(self):
        table = Table(["a"], [[1], [None], [None], [4]])
        self.assertEqual(cleaning.fill_missing(table, strategy="ffill").column("a"), [1, 1, 1, 4])
        self.assertEqual(cleaning.fill_missing(table, strategy="bfill").column("a"), [1, 4, 4, 4])

    def test_replace_values(self):
        table = Table(["a"], [["yes"], ["no"]])
        result = cleaning.replace_values(table, {"yes": 1, "no": 0})
        self.assertEqual(result.column("a"), [1, 0])

    def test_rename_and_drop_columns(self):
        table = sample()
        self.assertIn("label", cleaning.rename_columns(table, {"name": "label"}).columns)
        self.assertNotIn("age", cleaning.drop_columns(table, ["age"]).columns)

    def test_coerce_types_schema(self):
        table = Table(["a", "b"], [["1", "2.5"], ["3", "4.0"]])
        result = cleaning.coerce_types(table, schema={"a": "int", "b": "float"})
        self.assertEqual(result.column("a"), [1, 3])
        self.assertEqual(result.column("b"), [2.5, 4.0])

    def test_coerce_invalid_raises(self):
        table = Table(["a"], [["abc"]])
        with self.assertRaises(SchemaError):
            cleaning.coerce_types(table, schema={"a": "int"})

    def test_infer_column_type(self):
        self.assertEqual(cleaning.infer_column_type(["1", "2"]), "int")
        self.assertEqual(cleaning.infer_column_type(["1.5", "2"]), "float")
        self.assertEqual(cleaning.infer_column_type(["yes", "no"]), "bool")
        self.assertEqual(cleaning.infer_column_type(["2020-01-01"]), "date")
        self.assertEqual(cleaning.infer_column_type(["a", "b"]), "str")

    def test_clean_pipeline(self):
        result = cleaning.clean(
            sample(),
            drop_dupes=True,
            subset=["name"],
            fill_strategy="mean",
            schema={"age": "int"},
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result.column("name"), ["Ada", "Grace"])
        self.assertEqual(result.column("age"), [36, 45])


if __name__ == "__main__":
    unittest.main()
