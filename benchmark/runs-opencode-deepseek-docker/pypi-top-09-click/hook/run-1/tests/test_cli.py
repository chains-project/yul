"""Tests for the clitool command-line interface."""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout

from clitool import __version__
from clitool.cli import main


def run_cli(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class GreetTests(unittest.TestCase):
    def test_default_greeting(self):
        code, out, _ = run_cli(["greet"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "Hello, world!\n")

    def test_name_and_uppercase(self):
        code, out, _ = run_cli(["greet", "ada", "--uppercase"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "HELLO, ADA!\n")

    def test_repeat(self):
        _, out, _ = run_cli(["greet", "bob", "-r", "3"])
        self.assertEqual(out, "Hello, bob!\n" * 3)

    def test_repeat_must_be_positive(self):
        with self.assertRaises(SystemExit) as ctx:
            run_cli(["greet", "--repeat", "0"])
        self.assertEqual(ctx.exception.code, 2)


class CalcTests(unittest.TestCase):
    def test_add(self):
        _, out, _ = run_cli(["calc", "add", "1", "2", "3"])
        self.assertEqual(out, "6\n")

    def test_sub(self):
        _, out, _ = run_cli(["calc", "sub", "5", "2"])
        self.assertEqual(out, "3\n")

    def test_mul_decimal(self):
        _, out, _ = run_cli(["calc", "mul", "2.5", "3"])
        self.assertEqual(out, "7.5\n")

    def test_precision(self):
        _, out, _ = run_cli(["calc", "div", "1", "3", "-p", "2"])
        self.assertEqual(out, "0.33\n")

    def test_division_by_zero(self):
        code, out, err = run_cli(["calc", "div", "1", "0"])
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("division by zero", err)


class TopLevelTests(unittest.TestCase):
    def test_missing_command_exits(self):
        with self.assertRaises(SystemExit) as ctx:
            run_cli([])
        self.assertEqual(ctx.exception.code, 2)

    def test_version(self):
        with self.assertRaises(SystemExit) as ctx:
            run_cli(["--version"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
