import io
import os
import tempfile
import unittest

from csvdata import ColumnNotFoundError, Table, format_table, load_csv

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


class TableTests(unittest.TestCase):
    def setUp(self):
        self.table = Table(
            ["name", "age"],
            [["Alice", 30], ["Bob", 25]],
            {"name": "str", "age": "int"},
        )

    def test_shape_and_len(self):
        self.assertEqual(self.table.shape, (2, 2))
        self.assertEqual(len(self.table), 2)

    def test_getitem_and_get(self):
        self.assertEqual(self.table["age"], [30, 25])
        self.assertEqual(self.table.get("nope", "fallback"), "fallback")

    def test_missing_column_raises(self):
        with self.assertRaises(ColumnNotFoundError):
            self.table["missing"]

    def test_to_dicts_and_from_dicts(self):
        records = self.table.to_dicts()
        self.assertEqual(records[0], {"name": "Alice", "age": 30})
        rebuilt = Table.from_dicts(records)
        self.assertEqual(rebuilt.columns, ["name", "age"])

    def test_head_select_where(self):
        self.assertEqual(len(self.table.head(1)), 1)
        selected = self.table.select(["age"])
        self.assertEqual(selected.columns, ["age"])
        adults = self.table.where(lambda row: row["age"] >= 30)
        self.assertEqual(len(adults), 1)

    def test_with_column(self):
        extended = self.table.with_column("senior", [True, False], dtype="bool")
        self.assertEqual(extended.columns, ["name", "age", "senior"])
        self.assertIs(extended["senior"][0], True)

    def test_duplicate_columns_rejected(self):
        with self.assertRaises(ValueError):
            Table(["a", "a"], [[1, 2]])

    def test_ragged_row_rejected(self):
        with self.assertRaises(ValueError):
            Table(["a", "b"], [[1]])

    def test_to_csv_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "out.csv")
            self.table.to_csv(path)
            reloaded = load_csv(path)
            self.assertEqual(reloaded.columns, ["name", "age"])
            self.assertEqual(reloaded.rows, [["Alice", "30"], ["Bob", "25"]])

    def test_to_csv_file_object(self):
        buffer = io.StringIO()
        self.table.to_csv(buffer)
        self.assertIn("name,age", buffer.getvalue())

    def test_format_table(self):
        rendered = format_table(self.table)
        self.assertIn("| name ", rendered)
        self.assertIn("Bob", rendered)


if __name__ == "__main__":
    unittest.main()
