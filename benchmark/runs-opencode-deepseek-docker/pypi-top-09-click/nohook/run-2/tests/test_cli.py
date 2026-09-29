from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from taskcli.cli import main


class CliTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.data = Path(self.tmp.name) / "tasks.json"

    def run_cli(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(["--data-file", str(self.data), *argv])
        return code, out.getvalue(), err.getvalue()

    def test_add_then_list(self) -> None:
        code, out, _ = self.run_cli("add", "write docs")
        self.assertEqual(code, 0)
        self.assertIn("Added task 1", out)

        code, out, _ = self.run_cli("list")
        self.assertEqual(code, 0)
        self.assertIn("write docs", out)

    def test_add_persists_options(self) -> None:
        self.run_cli("add", "ship it", "--priority", "high", "--due", "2030-01-02")
        payload = json.loads(self.data.read_text(encoding="utf-8"))
        task = payload["tasks"][0]
        self.assertEqual(task["priority"], "high")
        self.assertEqual(task["due"], "2030-01-02")
        self.assertFalse(task["done"])

    def test_done_hides_task_from_default_list(self) -> None:
        self.run_cli("add", "task a")
        code, out, _ = self.run_cli("done", "1")
        self.assertEqual(code, 0)
        self.assertIn("completed", out)

        _, out, _ = self.run_cli("list")
        self.assertNotIn("task a", out)

        _, out, _ = self.run_cli("list", "--all")
        self.assertIn("task a", out)

    def test_done_undo(self) -> None:
        self.run_cli("add", "task a")
        self.run_cli("done", "1")
        self.run_cli("done", "1", "--undo")
        _, out, _ = self.run_cli("list")
        self.assertIn("task a", out)

    def test_list_priority_filter_and_json(self) -> None:
        self.run_cli("add", "low one", "--priority", "low")
        self.run_cli("add", "high one", "--priority", "high")
        _, out, _ = self.run_cli("list", "--priority", "high", "--json")
        tasks = json.loads(out)
        self.assertEqual([task["title"] for task in tasks], ["high one"])

    def test_remove(self) -> None:
        self.run_cli("add", "task a")
        code, out, _ = self.run_cli("remove", "1")
        self.assertEqual(code, 0)
        self.assertIn("Removed task 1", out)
        _, out, _ = self.run_cli("list", "--all")
        self.assertNotIn("task a", out)

    def test_missing_task_returns_error(self) -> None:
        code, _, err = self.run_cli("done", "42")
        self.assertEqual(code, 1)
        self.assertIn("no task with id 42", err)

    def test_invalid_due_date_exits_two(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            self.run_cli("add", "x", "--due", "not-a-date")
        self.assertEqual(ctx.exception.code, 2)

    def test_unknown_command_exits_two(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            self.run_cli("frobnicate")
        self.assertEqual(ctx.exception.code, 2)

    def test_no_command_prints_help(self) -> None:
        code, out, _ = self.run_cli()
        self.assertEqual(code, 2)
        self.assertIn("usage", out.lower())

    def test_version(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            self.run_cli("--version")
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
