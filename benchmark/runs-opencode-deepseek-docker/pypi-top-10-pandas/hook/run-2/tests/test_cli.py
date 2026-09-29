import contextlib
import io
import json
import os
import tempfile
import unittest

from csvdata.cli import main

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
SAMPLE = os.path.join(FIXTURES, "sample.csv")


def run(*argv):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = main(list(argv))
    return code, buffer.getvalue()


class CliTests(unittest.TestCase):
    def test_head(self):
        code, output = run("head", SAMPLE, "-n", "2")
        self.assertEqual(code, 0)
        self.assertIn("| name", output)
        self.assertIn("Alice", output)

    def test_describe(self):
        code, output = run("describe", SAMPLE)
        self.assertEqual(code, 0)
        self.assertIn("dtype", output)
        self.assertIn("float", output)

    def test_summary_json(self):
        code, output = run("summary", SAMPLE, "--json")
        self.assertEqual(code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["rows"], 5)

    def test_value_counts(self):
        code, output = run("value-counts", SAMPLE, "name")
        self.assertEqual(code, 0)
        self.assertIn("Bob", output)

    def test_clean_writes_file(self):
        with tempfile.TemporaryDirectory() as directory:
            target = os.path.join(directory, "clean.csv")
            code, _ = run(
                "clean", SAMPLE, "--drop-duplicates", "--missing", "mean", "-o", target
            )
            self.assertEqual(code, 0)
            with open(target, encoding="utf-8") as handle:
                contents = handle.read()
            self.assertIn("Alice", contents)
            self.assertEqual(contents.count("Bob"), 1)

    def test_missing_file_returns_error(self):
        code, _ = run("head", os.path.join(FIXTURES, "nope.csv"))
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
