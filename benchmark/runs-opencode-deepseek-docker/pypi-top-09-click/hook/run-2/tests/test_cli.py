import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from clitool.cli import main


class CliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.data = Path(self.tmp.name) / "tasks.json"

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(["--data-file", str(self.data), *argv])
        return code, out.getvalue(), err.getvalue()

    def test_add_and_list(self):
        code, out, _ = self.run_cli("add", "Write tests", "--priority", "high")
        self.assertEqual(code, 0)
        self.assertIn("Write tests", out)

        code, out, _ = self.run_cli("list")
        self.assertEqual(code, 0)
        self.assertIn("Write tests", out)
        self.assertIn("high", out)

    def test_add_persists_tags_and_priority(self):
        self.run_cli("add", "Task", "-t", "a", "-t", "b")
        data = json.loads(self.data.read_text(encoding="utf-8"))
        self.assertEqual(data[0]["tags"], ["a", "b"])
        self.assertEqual(data[0]["priority"], "medium")

    def test_ids_increment(self):
        self.run_cli("add", "First")
        code, out, _ = self.run_cli("add", "Second")
        self.assertIn("2", out)

    def test_done_filters_from_default_list(self):
        self.run_cli("add", "Task")
        code, out, _ = self.run_cli("done", "1")
        self.assertEqual(code, 0)
        self.assertIn("Task", out)

        _, out, _ = self.run_cli("list")
        self.assertIn("No tasks.", out)

        _, out, _ = self.run_cli("list", "--all")
        self.assertIn("Task", out)

    def test_done_missing_id(self):
        code, _, err = self.run_cli("done", "99")
        self.assertEqual(code, 1)
        self.assertIn("99", err)

    def test_remove(self):
        self.run_cli("add", "Task")
        code, out, _ = self.run_cli("remove", "1")
        self.assertEqual(code, 0)
        self.assertIn("Removed", out)

        _, out, _ = self.run_cli("list", "--all")
        self.assertIn("No tasks.", out)

    def test_remove_dry_run_keeps_task(self):
        self.run_cli("add", "Task")
        code, out, _ = self.run_cli("remove", "1", "--dry-run")
        self.assertEqual(code, 0)
        self.assertIn("Would remove", out)

        _, out, _ = self.run_cli("list", "--all")
        self.assertIn("Task", out)

    def test_status_filter(self):
        self.run_cli("add", "A")
        self.run_cli("add", "B")
        self.run_cli("done", "1")

        _, out, _ = self.run_cli("list", "--status", "done")
        self.assertIn("A", out)
        self.assertNotIn("B", out)

        _, out, _ = self.run_cli("list", "--status", "open")
        self.assertIn("B", out)
        self.assertNotIn("A", out)

    def test_list_json(self):
        self.run_cli("add", "Task")
        _, out, _ = self.run_cli("list", "--json")
        payload = json.loads(out)
        self.assertEqual(payload[0]["title"], "Task")

    def test_invalid_priority_exits(self):
        with self.assertRaises(SystemExit):
            with redirect_stderr(io.StringIO()):
                main(["--data-file", str(self.data), "add", "x", "--priority", "urgent"])

    def test_requires_subcommand(self):
        with self.assertRaises(SystemExit):
            with redirect_stderr(io.StringIO()):
                main(["--data-file", str(self.data)])


if __name__ == "__main__":
    unittest.main()
