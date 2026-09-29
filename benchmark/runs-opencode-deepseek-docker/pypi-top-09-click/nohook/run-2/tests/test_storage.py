from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from taskcli.models import Task
from taskcli.storage import Storage, StorageError, default_data_file


class StorageTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "nested" / "tasks.json"
        self.storage = Storage(self.path)

    def test_load_missing_file_is_empty(self) -> None:
        self.assertEqual(self.storage.load(), [])

    def test_round_trip(self) -> None:
        tasks = [Task(id=1, title="a", priority="high", due="2030-01-01")]
        self.storage.save(tasks)
        self.assertEqual(self.storage.load(), tasks)

    def test_next_id(self) -> None:
        tasks = [Task(id=1, title="a"), Task(id=5, title="b")]
        self.assertEqual(self.storage.next_id(tasks), 6)
        self.assertEqual(self.storage.next_id([]), 1)

    def test_corrupt_file_raises_storage_error(self) -> None:
        self.path.parent.mkdir(parents=True)
        self.path.write_text("{not json", encoding="utf-8")
        with self.assertRaises(StorageError):
            self.storage.load()

    def test_default_data_file_env_override(self) -> None:
        with mock.patch.dict(
            "os.environ", {"TASKCLI_DATA": "/tmp/custom.json"}, clear=False
        ):
            self.assertEqual(default_data_file(), Path("/tmp/custom.json"))


if __name__ == "__main__":
    unittest.main()
