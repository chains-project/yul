import os
import unittest

from csvdata import (
    AnalysisError,
    Table,
    aggregate,
    clean,
    correlation,
    describe,
    load_csv,
    numeric_columns,
    summary,
    value_counts,
)

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def cleaned():
    return clean(load_csv(os.path.join(FIXTURES, "sample.csv")), dedupe=True)


class DescribeTests(unittest.TestCase):
    def test_describe_reports_counts(self):
        report = describe(cleaned())
        self.assertEqual(list(report["column"]), ["name", "age", "score", "active"])
        age = {row["column"]: row for row in report.to_dicts()}
        self.assertEqual(age["age"]["count"], 3)
        self.assertEqual(age["age"]["missing"], 0)
        self.assertEqual(age["score"]["missing"], 1)
        self.assertAlmostEqual(age["age"]["mean"], (30 + 25 + 41) / 3)

    def test_numeric_columns(self):
        self.assertEqual(numeric_columns(cleaned()), ["age", "score"])

    def test_describe_infers_types_without_cleaning(self):
        report = describe(load_csv(os.path.join(FIXTURES, "sample.csv")))
        dtypes = dict(zip(report["column"], report["dtype"]))
        self.assertEqual(dtypes["age"], "int")
        self.assertEqual(dtypes["score"], "float")
        self.assertEqual(dtypes["active"], "bool")

    def test_value_counts(self):
        counts = value_counts(cleaned(), "name")
        self.assertEqual(counts.rows[0], ["Alice", 1])
        self.assertEqual(sum(counts["count"]), 3)

    def test_value_counts_normalized(self):
        counts = value_counts(cleaned(), "name", normalize=True)
        proportions = counts["proportion"]
        self.assertAlmostEqual(sum(proportions), 1.0)

    def test_correlation_perfect(self):
        table = Table(["x", "y"], [[1, 2], [2, 4], [3, 6]], {"x": "int", "y": "int"})
        self.assertAlmostEqual(correlation(table, "x", "y"), 1.0)

    def test_correlation_zero_variance_raises(self):
        table = Table(["x", "y"], [[1, 2], [1, 4]], {"x": "int", "y": "int"})
        with self.assertRaises(AnalysisError):
            correlation(table, "x", "y")

    def test_aggregate(self):
        result = aggregate(cleaned(), "name", {"total": ("age", "sum")})
        lookup = {row["name"]: row["total"] for row in result.to_dicts()}
        self.assertEqual(lookup["Alice"], 30)
        self.assertEqual(lookup["Carol"], 41)

    def test_summary(self):
        info = summary(cleaned())
        self.assertEqual(info["rows"], 3)
        self.assertEqual(info["columns"], 4)
        self.assertEqual(info["dtypes"]["age"], "int")


if __name__ == "__main__":
    unittest.main()
