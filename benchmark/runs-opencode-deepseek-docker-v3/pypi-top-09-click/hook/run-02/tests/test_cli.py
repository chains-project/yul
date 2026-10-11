from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout

from mytool.cli import main


class CliTestCase(unittest.TestCase):
    def invoke(self, argv: list[str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(argv)
        return code, stdout.getvalue(), stderr.getvalue()


class GreetTests(CliTestCase):
    def test_defaults(self) -> None:
        code, out, _ = self.invoke(["greet"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "Hello, world!\n")

    def test_options(self) -> None:
        code, out, _ = self.invoke(
            ["greet", "Ada", "--greeting", "Hi", "--uppercase"]
        )
        self.assertEqual(code, 0)
        self.assertEqual(out, "HI, ADA!\n")


class ConfigTests(CliTestCase):
    def test_list(self) -> None:
        code, out, _ = self.invoke(["config", "list"])
        self.assertEqual(code, 0)
        self.assertIn("color=auto\n", out)

    def test_set_then_get(self) -> None:
        self.invoke(["config", "set", "color", "never"])
        code, out, _ = self.invoke(["config", "get", "color"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "never\n")

    def test_get_unknown_key(self) -> None:
        code, _, err = self.invoke(["config", "get", "missing"])
        self.assertEqual(code, 1)
        self.assertIn("unknown key", err)


class RunTests(CliTestCase):
    def test_task_and_targets(self) -> None:
        code, out, _ = self.invoke(["run", "build", "a", "b"])
        self.assertEqual(code, 0)
        self.assertIn("build: jobs=1 targets=['a', 'b']", out)

    def test_repeatable_tag(self) -> None:
        _, out, _ = self.invoke(["run", "test", "-t", "x", "-t", "y"])
        self.assertIn("tags=['x', 'y']", out)

    def test_invalid_choice_exits(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            self.invoke(["run", "bogus"])
        self.assertEqual(ctx.exception.code, 2)

    def test_mutually_exclusive_output_flags(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            self.invoke(["run", "build", "-q", "--no-color"])
        self.assertEqual(ctx.exception.code, 2)


class ParserTests(CliTestCase):
    def test_missing_command_exits(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            self.invoke([])
        self.assertEqual(ctx.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
