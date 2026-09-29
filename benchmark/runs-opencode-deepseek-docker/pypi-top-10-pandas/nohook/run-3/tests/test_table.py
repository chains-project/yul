import unittest

from tabular import Table


class TableTest(unittest.TestCase):
    def setUp(self):
        self.table = Table(
            ["name", "age"],
            [["alice", 30], ["bob", 25], ["carol", 35]],
        )

    def test_shape_and_len(self):
        self.assertEqual(self.table.shape, (3, 2))
        self.assertEqual(len(self.table), 3)

    def test_column(self):
        self.assertEqual(self.table.column("age"), [30, 25, 35])

    def test_missing_column_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.table.column("height")

    def test_row_width_mismatch_raises(self):
        with self.assertRaises(ValueError):
            Table(["a", "b"], [[1]])

    def test_add_column(self):
        result = self.table.add_column("city", ["x", "y", "z"])
        self.assertEqual(result.headers, ["name", "age", "city"])
        self.assertEqual(result.column("city"), ["x", "y", "z"])

    def test_add_column_wrong_length_raises(self):
        with self.assertRaises(ValueError):
            self.table.add_column("city", ["x"])

    def test_drop_columns(self):
        result = self.table.drop_columns("age")
        self.assertEqual(result.headers, ["name"])

    def test_rename_columns(self):
        result = self.table.rename_columns({"age": "years"})
        self.assertEqual(result.headers, ["name", "years"])

    def test_select(self):
        result = self.table.select("age", "name")
        self.assertEqual(result.headers, ["age", "name"])
        self.assertEqual(result.rows[0], [30, "alice"])

    def test_filter(self):
        result = self.table.filter(lambda row: row["age"] > 26)
        self.assertEqual(result.column("name"), ["alice", "carol"])

    def test_sort_by(self):
        result = self.table.sort_by("age")
        self.assertEqual(result.column("age"), [25, 30, 35])

    def test_sort_by_reverse_with_key(self):
        result = self.table.sort_by("name", reverse=True, key=str.lower)
        self.assertEqual(result.column("name"), ["carol", "bob", "alice"])

    def test_head_and_tail(self):
        self.assertEqual(self.table.head(2).column("name"), ["alice", "bob"])
        self.assertEqual(self.table.tail(1).column("name"), ["carol"])

    def test_to_dicts_and_from_dicts_roundtrip(self):
        records = self.table.to_dicts()
        self.assertEqual(Table.from_dicts(records), self.table)

    def test_from_dicts_with_explicit_headers(self):
        table = Table.from_dicts([{"a": 1, "b": 2}], headers=["b", "a"])
        self.assertEqual(table.headers, ["b", "a"])
        self.assertEqual(table.rows, [[2, 1]])

    def test_equality(self):
        self.assertEqual(self.table, self.table.copy())
        self.assertNotEqual(self.table, Table(["name"], [["alice"]]))

    def test_iteration(self):
        self.assertEqual(list(self.table), self.table.rows)


if __name__ == "__main__":
    unittest.main()
