import unittest

from datalib import Table
from datalib.exceptions import DataLibError, MissingColumnError


class TableTests(unittest.TestCase):
    def setUp(self):
        self.table = Table(
            ["name", "age", "city"],
            [
                {"name": "Ada", "age": 36, "city": "London"},
                {"name": "Grace", "age": 45, "city": "NYC"},
                {"name": "Alan", "age": 41, "city": "London"},
            ],
        )

    def test_shape_and_len(self):
        self.assertEqual(self.table.shape, (3, 3))
        self.assertEqual(len(self.table), 3)

    def test_column(self):
        self.assertEqual(self.table.column("name"), ["Ada", "Grace", "Alan"])
        self.assertEqual(self.table["age"], [36, 45, 41])

    def test_missing_column_raises(self):
        with self.assertRaises(MissingColumnError):
            self.table.column("nope")

    def test_select_and_drop(self):
        selected = self.table.select("city", "name")
        self.assertEqual(selected.columns, ["city", "name"])
        dropped = self.table.drop_column("age")
        self.assertEqual(dropped.columns, ["name", "city"])

    def test_filter(self):
        result = self.table.filter(lambda row: row["age"] > 40)
        self.assertEqual([r["name"] for r in result], ["Grace", "Alan"])

    def test_sort_by_puts_none_last(self):
        table = Table(["x"], [[3], [None], [1]])
        self.assertEqual(table.sort_by("x").column("x"), [1, 3, None])
        self.assertEqual(table.sort_by("x", reverse=True).column("x"), [3, 1, None])

    def test_add_column_callable_and_values(self):
        with_flag = self.table.add_column("adult", lambda row: row["age"] >= 40)
        self.assertEqual(with_flag.column("adult"), [False, True, True])
        with_index = self.table.add_column("i", range(3))
        self.assertEqual(with_index.column("i"), [0, 1, 2])

    def test_add_column_length_mismatch(self):
        with self.assertRaises(DataLibError):
            self.table.add_column("bad", [1, 2])

    def test_map_column_does_not_mutate_original(self):
        upper = self.table.map_column("name", str.upper)
        self.assertEqual(upper.column("name"), ["ADA", "GRACE", "ALAN"])
        self.assertEqual(self.table.column("name"), ["Ada", "Grace", "Alan"])

    def test_rename(self):
        renamed = self.table.rename({"name": "first_name"})
        self.assertIn("first_name", renamed.columns)
        self.assertNotIn("name", renamed.columns)

    def test_equality(self):
        self.assertEqual(self.table, self.table.head(3))
        self.assertNotEqual(self.table, self.table.head(1))

    def test_duplicate_columns_rejected(self):
        with self.assertRaises(DataLibError):
            Table(["a", "a"], [])

    def test_row_sequence_input(self):
        table = Table(["a", "b"], [[1, 2], [3, 4]])
        self.assertEqual(table.column("b"), [2, 4])


if __name__ == "__main__":
    unittest.main()
