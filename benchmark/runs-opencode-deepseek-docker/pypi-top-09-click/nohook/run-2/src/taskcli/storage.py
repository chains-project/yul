from __future__ import annotations

import json
import os
from pathlib import Path

from .models import Task


class StorageError(RuntimeError):
    """Raised when the task store cannot be read or written."""


def default_data_file() -> Path:
    override = os.environ.get("TASKCLI_DATA")
    if override:
        return Path(override).expanduser()
    base = os.environ.get("XDG_DATA_HOME")
    root = Path(base).expanduser() if base else Path.home() / ".local" / "share"
    return root / "taskcli" / "tasks.json"


class Storage:
    def __init__(self, path: Path | None = None) -> None:
        self.path = Path(path) if path else default_data_file()

    def load(self) -> list[Task]:
        if not self.path.exists():
            return []
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise StorageError(f"could not read {self.path}: {exc}") from exc
        return [Task.from_dict(item) for item in raw.get("tasks", [])]

    def save(self, tasks: list[Task]) -> None:
        payload = {"tasks": [task.to_dict() for task in tasks]}
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(self.path.suffix + ".tmp")
            tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            tmp.replace(self.path)
        except OSError as exc:
            raise StorageError(f"could not write {self.path}: {exc}") from exc

    @staticmethod
    def next_id(tasks: list[Task]) -> int:
        return max((task.id for task in tasks), default=0) + 1
