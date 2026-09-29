import unittest

from datalib import Table, analysis
from datalib.exceptions import DataLibError


def numbers_table():
    return Table(
        ["team", "points", "assists"],
        [
            {"team": "red", "points": 10, "assists": 1},
            {"team": "red", "points": 20, "assists": 3},
            {"team": "blue", "points": 30, "assists": 5},
            {"team": "blue", "points": 40, "assists": 7},
            {"team": "blue", "points": None, "assists": 9},
        ],
    )


class AnalysisTests(unittest.TestCase):
    def test_numeric_and_categorical_columns(self):
        table = numbers_table()
        self.assertEqual(analysis.numeric_columns(table), ["points", "assists"])
        self.assertEqual(analysis.categorical_columns(table), ["team"])

    def test_basic_statistics(self):
        table = numbers_table()
        self.assertEqual(analysis.count(table, "points"), 4)
        self.assertEqual(analysis.missing_count(table, "points"), 1)
        self.assertEqual(analysis.mean(table, "points"), 25.0)
        self.assertEqual(analysis.median(table, "points"), 25.0)
        self.assertEqual(analysis.minimum(table, "points"), 10)
        self.assertEqual(analysis.maximum(table, "points"), 40)
        self.assertEqual(analysis.total(table, "points"), 100.0)

    def test_stdev_and_variance(self):
        table = numbers_table()
        self.assertAlmostEqual(analysis.variance(table, "assists"), 10.0)
        self.assertAlmostEqual(analysis.stdev(table, "assists"), 10 ** 0.5, places=6)

    def test_quantile(self):
        self.assertEqual(analysis.quantile([1, 2, 3, 4], 0.5), 2.5)
        self.assertEqual(analysis.quantile([1, 2, 3, 4], 0.0), 1)
        self.assertEqual(analysis.quantile([1, 2, 3, 4], 1.0), 4)

    def test_mean_rejects_non_numeric(self):
        with self.assertRaises(DataLibError):
            analysis.mean(numbers_table(), "team")

    def test_value_counts(self):
        table = Table(["x"], [["a"], ["b"], ["a"], ["a"], ["b"]])
        self.assertEqual(
            analysis.value_counts(table, "x"), [("a", 3), ("b", 2)]
        )
        normalized = analysis.value_counts(table, "x", normalize=True)
        self.assertAlmostEqual(normalized[0][1], 0.6)

    def test_value_counts_table(self):
        table = Table(["x"], [["a"], ["b"], ["a"]])
        result = analysis.value_counts_table(table, "x")
        self.assertEqual(result.columns, ["x", "count"])
        self.assertEqual(result.to_rows(), [["a", 2], ["b", 1]])

    def test_correlation(self):
        table = Table(["a", "b"], [[1, 2], [2, 4], [3, 6]])
        self.assertAlmostEqual(analysis.correlation(table, "a", "b"), 1.0)

    def test_correlation_matrix(self):
        table = Table(["a", "b"], [[1, 2], [2, 4], [3, 6]])
        matrix = analysis.correlation_matrix(table)
        self.assertEqual(matrix["a"]["a"], 1.0)
        self.assertAlmostEqual(matrix["a"]["b"], 1.0)

    def test_describe(self):
        info = analysis.describe(numbers_table())
        self.assertEqual(info["points"]["count"], 4)
        self.assertEqual(info["points"]["missing"], 1)
        self.assertEqual(info["points"]["mean"], 25.0)
        self.assertEqual(info["team"]["top"], "blue")
        self.assertEqual(info["team"]["unique"], 2)

    def test_group_by_builtin_aggregations(self):
        table = numbers_table()
        result = analysis.group_by(
            table,
            by="team",
            aggregations={
                "n": ("points", "count"),
                "total_points": ("points", "sum"),
                "avg_points": ("points", "mean"),
                "max_assists": ("assists", "max"),
            },
        )
        rows = {row["team"]: row for row in result}
        self.assertEqual(rows["red"]["n"], 2)
        self.assertEqual(rows["red"]["total_points"], 30.0)
        self.assertEqual(rows["blue"]["avg_points"], 35.0)
        self.assertEqual(rows["blue"]["max_assists"], 9)

    def test_group_by_callable_aggregation(self):
        table = numbers_table()
        result = analysis.group_by(
            table,
            by="team",
            aggregations={
                "spread": (
                    "points",
                    lambda vs: max(v for v in vs if v is not None)
                    - min(v for v in vs if v is not None),
                )
            },
        )
        rows = {row["team"]: row for row in result}
        self.assertEqual(rows["red"]["spread"], 10)

    def test_group_by_multiple_keys(self):
        table = Table(["a", "b", "v"], [[1, 1, 10], [1, 1, 20], [1, 2, 5]])
        result = analysis.group_by(table, by=["a", "b"], aggregations={"s": ("v", "sum")})
        self.assertEqual(result.to_rows(), [[1, 1, 30.0], [1, 2, 5.0]])

    def test_group_by_bad_spec_raises(self):
        with self.assertRaises(DataLibError):
            analysis.group_by(numbers_table(), by="team", aggregations={"x": "sum"})


if __name__ == "__main__":
    unittest.main()
