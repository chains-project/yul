import unittest

from tabular import (
    Table,
    correlation,
    describe,
    infer_types,
    missing_report,
    numeric_summary,
    to_number,
    value_counts,
)


class AnalysisTest(unittest.TestCase):
    def test_to_number(self):
        self.assertEqual(to_number("42"), 42.0)
        self.assertEqual(to_number(" 3.5 "), 3.5)
        self.assertIsNone(to_number("abc"))
        self.assertIsNone(to_number(""))
        self.assertIsNone(to_number(True))

    def test_numeric_summary(self):
        table = Table(["x"], [["1"], ["2"], ["3"], ["4"]])
        summary = numeric_summary(table, "x")
        self.assertEqual(summary["count"], 4)
        self.assertEqual(summary["mean"], 2.5)
        self.assertEqual(summary["median"], 2.5)
        self.assertEqual(summary["minimum"], 1)
        self.assertEqual(summary["maximum"], 4)
        self.assertEqual(summary["total"], 10)

    def test_numeric_summary_ignores_non_numeric(self):
        table = Table(["x"], [["1"], ["n/a"], ["3"]])
        summary = numeric_summary(table, "x")
        self.assertEqual(summary["count"], 2)

    def test_numeric_summary_empty(self):
        table = Table(["x"], [["a"], ["b"]])
        summary = numeric_summary(table, "x")
        self.assertEqual(summary["count"], 0)
        self.assertNotIn("mean", summary)

    def test_missing_report(self):
        table = Table(["a", "b"], [["1", ""], ["", "x"], ["3", None]])
        report = missing_report(table)
        self.assertEqual(report, {"a": 1, "b": 2})

    def test_value_counts(self):
        table = Table(["color"], [["red"], ["blue"], ["red"], ["red"]])
        self.assertEqual(value_counts(table, "color"), [("red", 3), ("blue", 1)])

    def test_value_counts_top_and_normalize(self):
        table = Table(["c"], [["a"], ["a"], ["b"], ["c"]])
        self.assertEqual(value_counts(table, "c", top=1), [("a", 2)])
        counts = value_counts(table, "c", normalize=True)
        self.assertEqual(counts[0], ("a", 0.5))

    def test_correlation_perfect_positive(self):
        table = Table(["x", "y"], [["1", "2"], ["2", "4"], ["3", "6"]])
        self.assertAlmostEqual(correlation(table, "x", "y"), 1.0)

    def test_correlation_perfect_negative(self):
        table = Table(["x", "y"], [["1", "6"], ["2", "4"], ["3", "2"]])
        self.assertAlmostEqual(correlation(table, "x", "y"), -1.0)

    def test_correlation_undefined(self):
        table = Table(["x", "y"], [["1", "2"]])
        self.assertIsNone(correlation(table, "x", "y"))

    def test_correlation_zero_variance(self):
        table = Table(["x", "y"], [["1", "2"], ["1", "4"]])
        self.assertIsNone(correlation(table, "x", "y"))

    def test_infer_types(self):
        table = Table(
            ["num", "flag", "text", "empty"],
            [["1", "true", "abc", ""], ["2", "false", "def", ""]],
        )
        self.assertEqual(
            infer_types(table),
            {"num": "numeric", "flag": "boolean", "text": "text", "empty": "empty"},
        )

    def test_describe(self):
        table = Table(
            ["num", "name"],
            [["1", "a"], ["2", "a"], ["3", "b"]],
        )
        report = describe(table)
        self.assertEqual(report["num"]["mean"], 2.0)
        self.assertEqual(report["name"]["unique"], 2)
        self.assertEqual(report["name"]["top"], "a")
        self.assertEqual(report["name"]["freq"], 2)


if __name__ == "__main__":
    unittest.main()
