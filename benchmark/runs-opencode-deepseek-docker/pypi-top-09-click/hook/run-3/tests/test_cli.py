"""Tests for the mytool command-line interface."""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from mytool.cli import main


def run_cli(*argv: str) -> tuple[int, str, str]:
    """Invoke ``main`` and capture (exit_code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(list(argv))
    return code, out.getvalue(), err.getvalue()


class VersionTests(unittest.TestCase):
    def test_version_flag(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            run_cli("--version")
        self.assertEqual(ctx.exception.code, 0)


class GreetTests(unittest.TestCase):
    def test_default_greeting(self) -> None:
        code, out, _ = run_cli("greet")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "Hello, world!")

    def test_named_and_shouted(self) -> None:
        code, out, _ = run_cli("greet", "Ada", "--shout")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "HELLO, ADA!")

    def test_count_repeats(self) -> None:
        _, out, _ = run_cli("greet", "--count", "3")
        self.assertEqual(out.count("Hello, world!"), 3)

    def test_invalid_count_is_rejected(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            run_cli("greet", "--count", "0")
        self.assertEqual(ctx.exception.code, 2)


class FilesTests(unittest.TestCase):
    def test_extension_filter_and_hidden(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.py").write_text("")
            (root / "b.txt").write_text("")
            (root / ".hidden").write_text("")

            code, out, _ = run_cli("files", str(root))
            self.assertEqual(code, 0)
            self.assertEqual(out.split(), ["a.py", "b.txt"])

            _, out, _ = run_cli("files", str(root), "--all")
            self.assertEqual(sorted(out.split()), [".hidden", "a.py", "b.txt"])

            _, out, _ = run_cli("files", str(root), "-e", ".py")
            self.assertEqual(out.split(), ["a.py"])

    def test_missing_directory_fails(self) -> None:
        code, _, err = run_cli("files", "/definitely/not/here")
        self.assertEqual(code, 1)
        self.assertIn("not a directory", err)


class ConfigTests(unittest.TestCase):
    def test_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = str(Path(tmp) / "config.json")
            code, out, _ = run_cli("--config", cfg, "config", "set", "color", "blue")
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(Path(cfg).read_text()), {"color": "blue"})

            code, out, _ = run_cli("--config", cfg, "config", "get", "color")
            self.assertEqual((code, out.strip()), (0, "blue"))

    def test_unknown_key(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg = str(Path(tmp) / "config.json")
            code, _, err = run_cli("--config", cfg, "config", "get", "nope")
            self.assertEqual(code, 1)
            self.assertIn("unknown key", err)


class ParserTests(unittest.TestCase):
    def test_no_command_is_an_error(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            run_cli()
        self.assertEqual(ctx.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
